"""2026-10-20 official-source collection; no guessed dates or automatic retirements."""
import concurrent.futures
import datetime
import html
import json
import pathlib
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
NODE = r'C:/Users/22198/.workbuddy/binaries/node/versions/22.22.2-6/node.exe'
TODAY = '2026-10-20'

def datasets():
    code = "const fs=require('fs'),vm=require('vm'),w={};let c={window:w};vm.createContext(c);['cqut.js','matches.js','competitions.js'].forEach(f=>vm.runInContext(fs.readFileSync(f,'utf8'),c));console.log(JSON.stringify({notices:w.CQUT_NOTICES,sources:w.CQUT_SOURCES,matches:w.MATCHES,retired:w.MATCH_RETIRED,competitions:w.COMP,contentUpdated:w.CQUT_UPDATED}));"
    return json.loads(subprocess.check_output([NODE, '-e', code], cwd=ROOT).decode('utf-8'))

def strip(text):
    text = re.sub(r'<(script|style)\b[^>]*>[\s\S]*?</\1>', '', text, flags=re.I)
    return re.sub(r'\s+', ' ', html.unescape(re.sub('<[^>]+>', ' ', text))).strip()

def fetch(url):
    result = {'url': url, 'checkedAt': TODAY}
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Accept-Encoding': 'identity'})
        with urllib.request.urlopen(req, timeout=8) as response:
            raw = response.read(2_000_000)
            charset = response.headers.get_content_charset() or 'utf-8'
            candidates = [raw.decode(c, errors='replace') for c in dict.fromkeys([charset, 'utf-8', 'gb18030'])]
            source = min(candidates, key=lambda s: s.count('\ufffd'))
            text = strip(source)
            title_match = re.search(r'<title[^>]*>([\s\S]*?)</title>', source, re.I)
            usable = response.status == 200 and len(text) > 300 and not re.search(r'just a moment|verify you are human|checking your browser|访问验证|人机验证', text[:1500], re.I)
            result.update(status=response.status, finalUrl=response.url, title=strip(title_match.group(1)) if title_match else '', usableContent=bool(usable), text=text[:12000])
            if not usable:
                result['limitation'] = 'Empty, short, JavaScript-only, or access-protected response; not evidence of a dead link or no new content.'
            result['links'] = [{'url': urllib.parse.urljoin(response.url, m.group(1)), 'title': strip(m.group(2))} for m in re.finditer(r'<a\b[^>]*href=[\"\']([^\"\']+)[\"\'][^>]*>([\s\S]*?)</a>', source, re.I) if '/info/' in m.group(1) or 'wbnewsid=' in m.group(1)]
            result['datedLinks'] = [strip(m.group(0)) for m in re.finditer(r'<li\b[^>]*>[\s\S]*?</li>', source, re.I) if '/info/' in m.group(0) or 'wbnewsid=' in m.group(0)]
    except urllib.error.HTTPError as error:
        result.update(status=error.code, error=str(error), usableContent=False, limitation='HTTP error alone is not a verified dead-link verdict; retained existing data.')
    except Exception as error:
        result.update(error=str(error), usableContent=False, limitation='Request failed; retained existing data.')
    return result

def main():
    data = datasets()
    urls = []
    for group in data['sources'].values():
        urls += [source['u'] for source in group]
    urls += ['https://www.cqut.edu.cn/tzgg.htm', 'https://www.cqut.edu.cn/tzgg/xygtz.htm', 'https://yjsy.cqut.edu.cn/']
    urls += [row['url'] for row in data['competitions'] + data['matches']]
    urls += [row['url'] for row in data['notices'][:15]]
    urls += ['https://news.cqjtu.edu.cn/info/1024/67939.htm', 'https://math.nankai.edu.cn/2026/0918/c33101a602957/page.htm', 'https://jwc.ynu.edu.cn/info/1009/4371.htm']
    urls = list(dict.fromkeys(urls))
    with concurrent.futures.ThreadPoolExecutor(max_workers=14) as pool:
        results = list(pool.map(fetch, urls))
    known = {row['url'] for row in data['notices']}
    candidates = [{'source': row['url'], 'link': link} for row in results if row.get('usableContent') for link in row.get('links', []) if 'cqut.edu.cn' in link['url'] and link['url'] not in known]
    report = {'reviewedAt': TODAY, 'attemptedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'scope': 'All configured CQUT source portals, all nationwide competition entry URLs, active curated competition originals, and newest existing CQUT notices; official eligibility/deadline review. Source failure never certifies closure or no new content.', 'sources': results, 'noticeCandidates': candidates, 'identityCountsBefore': {'competitions':len(data['competitions']), 'activeMatches':len(data['matches']), 'retiredMatches':len(data['retired']), 'notices':len(data['notices'])}, 'cqutContentUpdatedBefore':data['contentUpdated']}
    (ROOT / '_content_review_2026-10-20.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'attempts':len(results), 'usable':sum(row.get('usableContent', False) for row in results), 'newNoticeCandidates':len(candidates), 'statusCounts':{str(status):sum(row.get('status')==status for row in results) for status in {row.get('status') for row in results}}},ensure_ascii=False))

def apply_review():
    report_path = ROOT / '_content_review_2026-10-20.json'
    report = json.loads(report_path.read_text(encoding='utf-8'))
    data = datasets()
    retirements = {
        '第十八届全国大学生数学竞赛 · 重庆赛区': {
            'reasonCode': 'eligibility',
            'deadline': None,
            'reason': '当届高校正式通知明确面向全日制本科在校生，研究生不符合资格；不能把本科个人笔试误当成研究生三人数学建模赛推荐。',
            'sourceEvidence': ['https://math.nankai.edu.cn/2026/0918/c33101a602957/page.htm', 'https://jwc.ynu.edu.cn/info/1009/4371.htm'],
            'evidenceExcerpt': '南开大学当届通知：参赛对象为所有全日制在校本科生；云南大学当届通知：参赛选手须为全日制在籍本科生。'
        },
        '重庆交通大学首届低空经济创新大赛': {
            'reasonCode': 'deadline_and_eligibility',
            'deadline': '2026-09-24',
            'reason': '主办高校正式通知明确仅限重庆交通大学全日制本科在校生，且9月24日报名已截止；10月20日是已报名队伍交作品截止，不是新报名截止。',
            'sourceEvidence': ['https://news.cqjtu.edu.cn/info/1024/67939.htm'],
            'evidenceExcerpt': '参赛对象为重庆交通大学正式录取的全日制本科在校生；报名2026年8月31日—9月24日；提交作品10月20日24:00之前。'
        }
    }
    if len(data['matches']) != 8 or len(data['retired']) != 5:
        raise RuntimeError('Expected untouched 8 active / 5 retired identities; refuse repeat or conflicting apply.')
    removed = []
    active = []
    for item in data['matches']:
        if item['n'] not in retirements:
            active.append(item)
            continue
        info = retirements[item['n']]
        removed.append(dict(n=item['n'], url=item['url'], dl=item['dl'], retiredAt=TODAY, snapshot=item, **info))
    if len(removed) != 2:
        raise RuntimeError('Expected both reviewed original identities.')
    retired = data['retired'] + [dict(item['snapshot'], retiredAt=TODAY, **retirements[item['n']]) for item in removed]
    source = (ROOT/'matches.js').read_text(encoding='utf-8')
    # Preserve every historical object exactly in the audit list; no silent deletion.
    start = source.index('window.MATCHES = ')
    after_active = source.index('/* ---------------- 各学校信源直达 ---------------- */')
    source = source[:start] + 'window.MATCHES = ' + json.dumps(active, ensure_ascii=False, indent=2) + ';\n\n' + source[after_active:]
    source = re.sub(r'window\.MATCH_RETIRED\s*=\s*[\s\S]*?;\s*$', 'window.MATCH_RETIRED = '+json.dumps(retired,ensure_ascii=False,indent=2)+';\n',source)
    source = source.replace('window.MATCH_UPDATED = "2026-10-19";', 'window.MATCH_UPDATED = "2026-10-20";')
    source = re.sub(r'window\.MATCH_NOTE\s*=\s*[^\n]+', 'window.MATCH_NOTE = "10月20日另清理2项限本科或已截止赛事（数学竞赛、重交低空大赛），历史13项完整保留为6项精选、7项有据退役。部分校内来源访问受限；仍需确认本校资格、费用和截止。";', source)
    source = source.replace('本次维护：2026-10-19。按官方报名日期与学籍要求清退 5 项过期或不符合身份的赛事。', '本次维护：2026-10-20。按官网当届资格和报名日期再清退 2 项，累计 7 项有据退役。')
    source = source.replace('完整旧条目和退役依据保存在 MATCH_RETIRED 与 _content_review_2026-10-19.json。', '完整旧条目和退役依据保存在 MATCH_RETIRED 与各退役日的 _content_review_YYYY-MM-DD.json。')
    for school in ['cqupt', 'cqjtu']:
        source = re.sub(r'\n  \{k:"'+school+r'",[^\n]*\},?', '', source)
    (ROOT/'matches.js').write_text(source, encoding='utf-8')
    comp = (ROOT/'competitions.js').read_text(encoding='utf-8')
    start = comp.index('n:"全国大学生数学竞赛"')
    block_start = comp.rfind('{scope:',0,start)
    block_end = comp.index('\n    {scope:',start)
    block = comp[block_start:block_end]
    block = block.replace('scope:"me"', 'scope:"world"',1).replace('st:"soon"','st:"closed"',1).replace('team:"组队（专业相关）"','team:"个人笔试（本科生）"',1)
    block = re.sub(r'\breg:"[^"\n]*"', 'reg:"第十八届由各省数学会与学校组织报名；本站原收录截止10/19已过。研究生不符合已核实的本科生参赛要求，各校已报名考生按校内通知参加初赛。"', block)
    block = re.sub(r'\bdesc:"[^"\n]*"', 'desc:"中国数学会主办的个人数学笔试，分数学专业与非数学专业等类别；不是三人组队的数学建模论文竞赛。"', block)
    block = re.sub(r'\bfit:"[^"\n]*"', 'fit:"当届南开、云南大学正式通知均明确本科生资格，不适配本站研究生用户；保留资源身份供查阅。"', block)
    block = re.sub(r'\bhelp:"[^"\n]*"', 'help:"可用历届试题复习高等数学与线性代数；不要按研究生数学建模赛准备组队、论文或报名材料。"', block)
    comp = comp[:block_start] + block + comp[block_end:]
    comp = comp.replace('window.COMP_UPDATED = "2026-10-19";', 'window.COMP_UPDATED = "2026-10-20";')
    comp += '\n/* 本次实际请求全部已收录入口；访问受限不是来源已失效。 */\nwindow.COMP_CHECKED = "2026-10-20";\nwindow.COMP_CHECK_NOTE = "已实际核查全部已收录入口，纠正数学竞赛截止、个人笔试与本科资格；部分官网访问受限，其他旧赛程不冒充今日全部重新确认。";\n'
    (ROOT/'competitions.js').write_text(comp,encoding='utf-8')
    cqut_path = ROOT/'cqut.js'
    cqut = cqut_path.read_text(encoding='utf-8')
    cqut = re.sub(r'window\.CQUT_CHECKED = "\d{4}-\d{2}-\d{2}";', 'window.CQUT_CHECKED = "2026-10-20";', cqut)
    cqut = re.sub(r'window\.CQUT_CHECK_NOTE = "[^"\n]*";', 'window.CQUT_CHECK_NOTE = "本次重新核查学校及各部门、学院官网入口；多数来源返回访问保护、空挑战或超时，保留当前308条通知和已有内容更新日，受阻不代表官网没有新通知。具体事务请以原文为准。";', cqut)
    cqut_path.write_text(cqut,encoding='utf-8')
    after = datasets()
    assert data['notices'] == after['notices'] and data['contentUpdated'] == after['contentUpdated']
    assert [(row['n'],row['url']) for row in data['competitions']] == [(row['n'],row['url']) for row in after['competitions']]
    assert len(after['matches']) == 6 and len(after['retired']) == 7
    report.update(removedMatches=removed, retirementAllowedHosts=['news.cqjtu.edu.cn', 'math.nankai.edu.cn', 'jwc.ynu.edu.cn'], competitionChanges={'mathematics': 'Moved to reference-only world scope, closed expired entry, corrected undergraduate-only individual written test rather than three-person graduate mathematical modelling.', 'preservedIdentities':len(after['competitions'])}, cqut={'beforeCount':len(data['notices']), 'afterCount':len(after['notices']), 'newNotices':0,'successfulContentUpdated':after['contentUpdated'], 'checkedAt':TODAY,'limitation':'Preserved other maintainer\'s full 308-notice source unchanged. Protected and failed pages do not prove no new notices.'}, identityCountsAfter={'competitions':len(after['competitions']),'activeMatches':len(after['matches']),'retiredMatches':len(after['retired']),'notices':len(after['notices'])})
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report['identityCountsAfter']))

def annotate_independent_evidence():
    """Retain the independent browser extraction when the local probe was blocked."""
    path = ROOT / '_content_review_2026-10-20.json'
    report = json.loads(path.read_text(encoding='utf-8'))
    report['officialExtracts'] = [
        {'url':'https://news.cqjtu.edu.cn/info/1024/67939.htm','checkedAt':TODAY,
         'method':'web search then open official HTML; independent retrieval succeeded after local HTTP probe timed out',
         'title':'关于举办“重庆交通大学首届低空经济创新大赛”的通知',
         'finding':'参赛对象为重庆交通大学正式录取的全日制本科在校生；报名2026年8月31日—9月24日；10月20日为已报名队伍提交作品截止。'},
        {'url':'https://math.nankai.edu.cn/2026/0918/c33101a602957/page.htm','checkedAt':TODAY,
         'method':'official HTML via local HTTP200 and web open',
         'title':'南开大学第十八届全国大学生数学竞赛报名通知',
         'finding':'参赛对象为所有全日制在校本科生。'},
        {'url':'https://jwc.ynu.edu.cn/info/1009/4371.htm','checkedAt':TODAY,
         'method':'official HTML via local HTTP200 and web open',
         'title':'关于组织参加2026年第十八届全国大学生数学竞赛的通知',
         'finding':'参赛选手须为全日制在籍本科生，非三人组队研究生数学建模。'}
    ]
    for source in report['sources']:
        if 'text' in source:
            source['text'] = source['text'][:12000]
    cqut = [source for source in report['sources'] if 'cqut.edu.cn' in source['url']]
    report['summary'] = {'attempts':len(report['sources']),'usable':sum(source.get('usableContent',False) for source in report['sources']), 'cqutAttempts':len(cqut), 'cqutUsable':sum(source.get('usableContent',False) for source in cqut)}
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report['summary']))

if __name__ == '__main__':
    if '--annotate' in sys.argv:
        annotate_independent_evidence()
    elif '--apply' in sys.argv:
        apply_review()
        annotate_independent_evidence()
    else:
        main()
