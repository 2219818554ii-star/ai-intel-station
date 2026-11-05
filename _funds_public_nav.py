"""Evidence-bound public NAV updates; account and cash snapshots are immutable."""
import copy
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent
TZ = dt.timezone(dt.timedelta(hours=8))
CODES = ('012920', '024480', '022432', '016452')

def now():
    return dt.datetime.now(TZ).isoformat(timespec='seconds')

def digest(text):
    return hashlib.sha256(text.encode('utf8')).hexdigest()

def read_values(source):
    script = "let s={window:{}};require('vm').runInNewContext(require('fs').readFileSync(0,'utf8'),s);process.stdout.write(JSON.stringify(s.window));"
    return json.loads(subprocess.check_output(['node', '-e', script], input=source.encode('utf8')))

def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)

def parse_nav(body, code, day):
    identity = re.search(r'fS_code\s*=\s*"([^"]+)"', body)
    name = re.search(r'fS_name\s*=\s*"([^"]+)"', body)
    if not identity or identity[1] != code or not name or not name[1].strip():
        raise ValueError('Fund identity missing or mismatched: ' + code)
    match = re.search(r'Data_netWorthTrend\s*=\s*(\[.*?\]);', body, re.S)
    if not match:
        raise ValueError('Published NAV trend missing: ' + code)
    rows = json.loads(match[1])
    valid = [r for r in rows if isinstance(r, dict) and number(r.get('x')) and number(r.get('y')) and r['y'] > 0]
    if not valid:
        raise ValueError('Published NAV rows missing: ' + code)
    last = max(valid, key=lambda r: r['x'])
    if not number(last.get('equityReturn')):
        raise ValueError('Observed daily return missing: ' + code)
    nav_day = dt.datetime.fromtimestamp(last['x'] / 1000, TZ).date().isoformat()
    if nav_day > day:
        raise ValueError('Future NAV rejected: ' + code)
    return {'sourceName': name[1], 'rawLast': last,
            'nav': {'unit': last['y'], 'dayPct': round(last['equityReturn'] / 100, 8), 'navDate': nav_day}}

def collect(code, day):
    url = 'https://fund.eastmoney.com/pingzhongdata/' + code + '.js'
    row = {'code': code, 'url': url, 'checkedAtTime': now()}
    try:
        p = subprocess.run(['curl.exe', '-L', '-sS', '--compressed', '--connect-timeout', '15', '--max-time', '60',
                            '-A', 'Mozilla/5.0', '-w', '\n@@STATUS@@%{http_code}', url], capture_output=True, timeout=65)
        raw, sep, status = p.stdout.rpartition(b'\n@@STATUS@@')
        row.update(httpStatus=status.decode() if sep else None, curlExit=p.returncode,
                   complete=bool(sep and p.returncode == 0 and status == b'200'), bytes=len(raw),
                   sha256=hashlib.sha256(raw).hexdigest())
        if not row['complete']:
            raise ValueError(p.stderr.decode('utf8', 'replace').strip() or 'Incomplete HTTP response')
        row['rawBody'] = raw.decode('utf8')
        row.update(parse_nav(row['rawBody'], code, day))
    except (ValueError, subprocess.TimeoutExpired, OSError) as error:
        row['error'] = str(error)[:350]
    row['completedAt'] = now()
    return row

def evidence(report, source, day):
    if report.get('schema') != 2 or report.get('sourceSHA256') != digest(source):
        raise ValueError('Legacy or stale refresh file rejected; collect complete current evidence first')
    if report.get('checkedAt', '')[:10] != day:
        raise ValueError('Refresh evidence must be from this Beijing day')
    rows = report.get('observations', [])
    if len(rows) != len(CODES) or {r.get('code') for r in rows} != set(CODES):
        raise ValueError('All four distinct fund identities are required')
    clean = []
    for row in rows:
        code = row['code']
        if row.get('error') or row.get('httpStatus') != '200' or row.get('curlExit') != 0 or row.get('complete') is not True:
            raise ValueError('Incomplete source evidence: ' + code)
        if row.get('url') != 'https://fund.eastmoney.com/pingzhongdata/' + code + '.js':
            raise ValueError('Unexpected public NAV source: ' + code)
        for field in ('checkedAtTime', 'completedAt'):
            stamp = dt.datetime.fromisoformat(row[field])
            if stamp.tzinfo is None or stamp.astimezone(TZ).date().isoformat() != day or stamp > dt.datetime.now(TZ):
                raise ValueError('Wrong or future source timestamp: ' + code)
        if row['completedAt'] < row['checkedAtTime']:
            raise ValueError('Source completion precedes request: ' + code)
        body = row.get('rawBody')
        if not isinstance(body, str) or digest(body) != row.get('sha256') or len(body.encode('utf8')) != row.get('bytes'):
            raise ValueError('Raw source digest/length mismatch: ' + code)
        parsed = parse_nav(body, code, day)
        if any(row.get(k) != v for k, v in parsed.items()):
            raise ValueError('Parsed values differ from complete raw evidence: ' + code)
        clean.append({k: v for k, v in row.items() if k != 'rawBody'})
    return clean

def scalar(source, key, value):
    assignment = 'window.' + key + ' = ' + json.dumps(value, ensure_ascii=False) + ';'
    pattern = r'window\.' + re.escape(key) + r'\s*=\s*[^\n;]*;'
    if not re.search(pattern, source):
        return source + '\n' + assignment + '\n'
    return re.sub(pattern, lambda _: assignment, source, count=1)

def apply_report(source, report, fixture, day):
    observations = evidence(report, source, day)
    before = read_values(source)
    changed = False
    for row in observations:
        code, nav = row['code'], row['nav']
        old = next(h for h in before['FUNDS_HOLD'] if h['code'] == code)
        row['before'] = {k: old[k] for k in ('unit', 'dayPct', 'navDate')}
        if nav['navDate'] < old['navDate']:
            raise ValueError('NAV date regression rejected: ' + code)
        row['changed'] = row['before'] != nav
        changed |= row['changed']
        hold = re.compile(r'("code":\s*"' + code + r'"[\s\S]*?"unit":\s*)[^,]+(,\s*"dayPct":\s*)[^,]+(,\s*"navDate":\s*)"[^"]+"')
        source, count = hold.subn(lambda m: m[1] + str(nav['unit']) + m[2] + str(nav['dayPct']) + m[3] + json.dumps(nav['navDate']), source)
        if count != 1:
            raise ValueError('Unique holding location missing: ' + code)
        deep = re.compile(r'("' + code + r'":\s*\{[\s\S]*?nav:\s*)[^,]+(,\s*navDate:\s*)"[^"]+"(,\s*dayPct:\s*)[^,]+')
        source, count = deep.subn(lambda m: m[1] + str(nav['unit']) + m[2] + json.dumps(nav['navDate']) + m[3] + str(nav['dayPct']), source)
        if count != 1:
            raise ValueError('Unique deep NAV location missing: ' + code)
    if changed:
        source = scalar(source, 'FUNDS_UPDATED', day)
        source, count = re.subn(r'navCheckedAt:\s*"[^"]+"', 'navCheckedAt: ' + json.dumps(day), source, count=1)
        if count != 1:
            raise ValueError('NAV application date missing')
        source, count = re.subn(r'(window\.FUNDS_META\s*=\s*\{[\s\S]*?"date":\s*)"[^"]+"', lambda m: m[1] + json.dumps(day), source, count=1)
        if count != 1:
            raise ValueError('Public metadata date missing')
        note = day + ' 实抓复核4只基金已公布公开净值，原净值日见逐条navDate；账户及余额宝仍为2026-10-15快照。股票、阶段业绩和持仓档案保留旧值、旧日期。'
        source, count = re.subn(r'(window\.FUNDS_META\s*=\s*\{[\s\S]*?"note":\s*)"(?:\\.|[^"\\])*"', lambda m: m[1] + json.dumps(note, ensure_ascii=False), source, count=1)
        if count != 1:
            raise ValueError('Public metadata note missing')
    else:
        note = day + ' 完整实抓4只基金公开净值，与收录值一致，未发现新公布值；最近成功内容更新仍为' + before['FUNDS_UPDATED'] + '。原净值日、账户及余额宝快照、股票和档案日期不变。'
    source = scalar(scalar(source, 'FUNDS_CHECKED', day), 'FUNDS_CHECK_NOTE', note)
    after = read_values(source)
    allowed = copy.deepcopy(before)
    for row in observations:
        code, nav = row['code'], row['nav']
        next(h for h in allowed['FUNDS_HOLD'] if h['code'] == code).update(nav)
        allowed['FUNDS_DEEP']['byCode'][code].update(nav=nav['unit'], dayPct=nav['dayPct'], navDate=nav['navDate'])
    if changed:
        allowed['FUNDS_UPDATED'] = day
        allowed['FUNDS_DEEP']['navCheckedAt'] = day
        allowed['FUNDS_META'].update(date=day, note=note)
    allowed.update(FUNDS_CHECKED=day, FUNDS_CHECK_NOTE=note)
    if allowed != after:
        raise ValueError('Changes outside the public NAV/check metadata allowlist')
    for fixed in fixture['funds']:
        hold = next(h for h in after['FUNDS_HOLD'] if h['code'] == fixed['code'])
        if any(hold.get(k) != v for k, v in fixed.items()):
            raise ValueError('Immutable account snapshot mismatch')
    if fixture['cash'] != after['FUNDS_CASH']:
        raise ValueError('Immutable cash snapshot mismatch')
    clean = {k: v for k, v in report.items() if k != 'observations'}
    clean.update(observations=observations, written=changed, publicNAVChanged=changed, checkMetadataWritten=True,
                 contentUpdatedAt=after['FUNDS_UPDATED'], navAppliedEvidenceDate=after['FUNDS_DEEP']['navCheckedAt'],
                 accountComparison='Every pre-existing global equals the baseline except public NAV and explicit check metadata; fixed account and entire cash fixture match.')
    return source, clean
