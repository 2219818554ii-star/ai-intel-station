"""Fetch published NAV evidence; --write applies only reviewed public NAV fields.

Account, cash, stock quotes, manager/holding profiles and opinions are immutable.
"""
import concurrent.futures
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
NODE = r'C:/Users/22198/.workbuddy/binaries/node/versions/22.22.2-6/node.exe'
TODAY = dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).date().isoformat()
REPORT = ROOT / '_funds_review_2026-10-26.json'
if TODAY != '2026-10-26':
    raise RuntimeError('Dated review: use a new report for a new date')
CODES = ['012920', '024480', '022432', '016452']


def read_values(source):
    script = 'const vm=require("vm");let s={window:{}};vm.runInNewContext(require("fs").readFileSync(0,"utf8"),s);process.stdout.write(JSON.stringify(s.window));'
    return json.loads(subprocess.check_output([NODE, '-e', script], input=source, text=True, encoding='utf-8'))


def fetch(code):
    url = f'https://fund.eastmoney.com/pingzhongdata/{code}.js'
    p = subprocess.run(['curl.exe', '-L', '-sS', '--max-time', '25', '-A', 'Mozilla/5.0', '-w', '\n%{http_code}', url], capture_output=True, timeout=30)
    body, _, status = p.stdout.rpartition(b'\n')
    result = {'code': code, 'url': url, 'httpStatus': status.decode(), 'sha256': hashlib.sha256(body).hexdigest(), 'bytes': len(body)}
    if p.returncode or status != b'200':
        result['error'] = p.stderr.decode(errors='replace')
        return result
    text = body.decode('utf-8-sig')
    source_code = re.search(r'fS_code\s*=\s*"([^"]+)"', text)
    if not source_code or source_code.group(1) != code:
        result['error'] = 'Fund identity missing or mismatched'
        return result
    name = re.search(r'fS_name\s*=\s*"([^"]+)"', text)
    result['sourceName'] = name.group(1) if name else None
    match = re.search(r'Data_netWorthTrend\s*=\s*(\[.*?\]);', text, re.S)
    if not match:
        result['error'] = 'No published NAV trend in source'
        return result
    rows = [r for r in json.loads(match.group(1)) if isinstance(r, dict) and isinstance(r.get('y'), (int, float)) and r['y'] > 0]
    last = max(rows, key=lambda r: r['x'])
    nav_date = dt.datetime.fromtimestamp(last['x'] / 1000, dt.timezone(dt.timedelta(hours=8))).date().isoformat()
    if nav_date > TODAY:
        result['error'] = 'Rejected future NAV date'
        return result
    if not isinstance(last.get('equityReturn'), (int, float)):
        result['error'] = 'Missing observed daily return'
        return result
    result['rawLast'] = last
    result['nav'] = {'unit': last['y'], 'dayPct': round(last['equityReturn'] / 100, 6), 'navDate': nav_date}
    result['previousPublished'] = rows[-2] if len(rows) > 1 else None
    return result


source = (ROOT / 'funds.js').read_text(encoding='utf-8')
before = read_values(source)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    fetched = list(pool.map(fetch, CODES))
report = {'checkedAt': dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(), 'source': 'Eastmoney Tiantian Fund published NAV feed', 'observations': fetched, 'unchangedScope': 'All account and cash data; stock quotes; manager, portfolio, performance and opinion archives retain their original dates/values.'}
for item in fetched:
    old = next(v for v in before['FUNDS_HOLD'] if v['code'] == item['code'])
    item['before'] = {k: old[k] for k in ('unit', 'dayPct', 'navDate')}
    item['changed'] = item.get('nav') != item['before']
if '--write' in sys.argv:
    if any('nav' not in x for x in fetched):
        report['written'] = False
        REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        raise RuntimeError('Incomplete evidence; no write')
    if not any(x['changed'] for x in fetched):
        check_note = TODAY + ' 实际完整获取4只基金公开净值，与当前收录值全部一致，未发现新公布净值；各基金原净值日期保持。最近成功内容更新仍为' + before['FUNDS_UPDATED'] + '，账户快照仍2026-10-15；旧股票和档案不作为本次更新。'
        for key, value in [('FUNDS_CHECKED', TODAY), ('FUNDS_CHECK_NOTE', check_note)]:
            assignment = 'window.' + key + ' = ' + json.dumps(value, ensure_ascii=False) + ';'
            pattern = r'window\.' + key + r' = \"[^\n]*\";'
            if re.search(pattern, source):
                source = re.sub(pattern, lambda match: assignment, source, count=1)
            else:
                source += '\n' + assignment + '\n'
        after = read_values(source)
        assert before['FUNDS_UPDATED'] == after['FUNDS_UPDATED']
        for key in before:
            if key not in ('FUNDS_CHECKED', 'FUNDS_CHECK_NOTE'):
                assert before[key] == after[key], 'Existing fund state changed on an unchanged NAV check: ' + key
        baseline = json.loads((ROOT / '_funds_snapshot_2026-10-15.json').read_text(encoding='utf-8'))
        for expected in baseline['funds']:
            actual = next(x for x in after['FUNDS_HOLD'] if x['code'] == expected['code'])
            assert all(actual[k] == v for k, v in expected.items()), 'Account snapshot mismatch'
        assert baseline['cash'] == after['FUNDS_CASH'], 'Cash snapshot mismatch'
        report.update(written=False, publicNAVChanged=False, checkMetadataWritten=True,
                      contentUpdatedAt=before['FUNDS_UPDATED'], navAppliedEvidenceDate=before['FUNDS_DEEP']['navCheckedAt'],
                      snapshotFixtureComparison='All protected account fields and entire cash snapshot match the fixed October15 fixture.',
                      accountComparison='All pre-existing globals, holdings, cash, stocks and deep archive equal before/after; only separate check globals added.')
        (ROOT / 'funds.js').write_text(source, encoding='utf-8')
        REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({'newNAVs': 0, 'contentUpdatedAt': before['FUNDS_UPDATED'], 'checkedAt': TODAY, 'accountAndArchiveUnchanged': True}, ensure_ascii=False))
        sys.exit(0)
    for item in fetched:
        code, n = item['code'], item['nav']
        if n['navDate'] < item['before']['navDate']:
            raise RuntimeError(f'Rejected NAV date regression: {code}')
        hold = re.compile(r'("code": "' + code + r'"[\s\S]*?"unit": )[^,]+(,\s*"dayPct": )[^,]+(,\s*"navDate": )"[^"]+"')
        source, count = hold.subn(lambda m: m[1] + str(n['unit']) + m[2] + str(n['dayPct']) + m[3] + json.dumps(n['navDate']), source)
        assert count == 1, (code, 'hold', count)
        deep = re.compile(r'("' + code + r'":\s*\{[\s\S]*?nav: )[^,]+(, navDate: )"[^"]+"(, dayPct: )[^,]+')
        source, count = deep.subn(lambda m: m[1] + str(n['unit']) + m[2] + json.dumps(n['navDate']) + m[3] + str(n['dayPct']), source)
        assert count == 1, (code, 'deep', count)
    source = re.sub(r'window.FUNDS_UPDATED = "[^"]+";', f'window.FUNDS_UPDATED = "{TODAY}";', source, count=1)
    if re.search(r'navCheckedAt: "[^"]+"', source):
        source = re.sub(r'navCheckedAt: "[^"]+"', f'navCheckedAt: "{TODAY}"', source, count=1)
    else:
        source = source.replace('window.FUNDS_DEEP = {', f'window.FUNDS_DEEP = {{\n  navCheckedAt: "{TODAY}",', 1)
    # Only the public NAV review date changes. Account snapshot date remains 10/15.
    source = source.replace('window.FUNDS_META = {', '/* ' + TODAY + '：4只基金公开净值经天天基金数据源实抓核验；账户/余额宝、个股行情和旧档案未刷新。详见 _funds_review_2026-10-26.json。 */\nwindow.FUNDS_META = {', 1)
    source = re.sub(r'(window.FUNDS_META = \{[\s\S]*?"date": )"[^"]+"', lambda m: m[1] + json.dumps(TODAY), source, count=1)
    note = TODAY + ' 已实抓复核4只基金公开净值；净值日期见各基金navDate。账户快照仍为2026-10-15；旧个股行情、阶段业绩和持仓档案保持原日期，不视为本次刷新。'
    source = re.sub(r'(window.FUNDS_META = \{[\s\S]*?"note": )"[^"]+"', lambda m: m[1] + json.dumps(note, ensure_ascii=False), source, count=1)
    fresh_note = TODAY + ' 实际完整复核4只基金公开净值，已应用新公布值；原净值日期见各基金navDate。账户快照仍2026-10-15；股票和旧档案保持原核验日期。'
    for key, value in [('FUNDS_CHECKED', TODAY), ('FUNDS_CHECK_NOTE', fresh_note)]:
        assignment = 'window.' + key + ' = ' + json.dumps(value, ensure_ascii=False) + ';'
        pattern = r'window\.' + key + r' = \"[^\n]*\";'
        if re.search(pattern, source):
            source = re.sub(pattern, lambda match: assignment, source, count=1)
        else:
            source += '\n' + assignment + '\n'
    report.update(publicNAVChanged=True, checkMetadataWritten=True)
    after = read_values(source)
    for a, b in zip(before['FUNDS_HOLD'], after['FUNDS_HOLD']):
        assert {k: v for k, v in a.items() if k not in ('unit', 'dayPct', 'navDate')} == {k: v for k, v in b.items() if k not in ('unit', 'dayPct', 'navDate')}, 'Account field changed'
    assert before['FUNDS_CASH'] == after['FUNDS_CASH'], 'Cash changed'
    assert before['FUNDS_STOCKS'] == after['FUNDS_STOCKS'], 'Stock archive changed'
    for code in CODES:
        a, b = before['FUNDS_DEEP']['byCode'][code], after['FUNDS_DEEP']['byCode'][code]
        assert {k: v for k, v in a.items() if k not in ('nav', 'dayPct', 'navDate')} == {k: v for k, v in b.items() if k not in ('nav', 'dayPct', 'navDate')}, 'Non-NAV deep profile changed'
    baseline = json.loads((ROOT / '_funds_snapshot_2026-10-15.json').read_text(encoding='utf-8'))
    for expected in baseline['funds']:
        actual = next(x for x in after['FUNDS_HOLD'] if x['code'] == expected['code'])
        assert all(actual[k] == v for k, v in expected.items()), 'Account snapshot mismatch'
        assert actual['amtDate'] == baseline['syncedOn'], 'Account date changed'
    assert baseline['cash'] == after['FUNDS_CASH'], 'Cash snapshot mismatch'
    report['snapshotFixtureComparison'] = '4 fund account records and entire cash array identical to _funds_snapshot_2026-10-15.json; all amtDate retained 2026-10-15'
    report['accountComparison'] = 'All non-NAV holding fields and cash identical; stocks unchanged'
    report['written'] = True
    (ROOT / 'funds.js').write_text(source, encoding='utf-8')
REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
