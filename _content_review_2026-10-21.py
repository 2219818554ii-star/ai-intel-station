"""2026-10-21 official-source collection; no guessed dates or automatic retirements."""
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
TODAY = '2026-10-21'

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
            if 'tianchi.aliyun.com/competition/entrance/' in url and not re.search(r'赛题|比赛时间|赛程|报名时间|评审|作品提交', text):
                usable = False
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
    urls = [source['u'] for group in data['sources'].values() for source in group]
    urls += ['https://www.cqut.edu.cn/tzgg.htm', 'https://www.cqut.edu.cn/tzgg/xygtz.htm', 'https://yjsy.cqut.edu.cn/']
    urls += [row['url'] for row in data['competitions'] + data['matches'] + data['retired'] + data['notices']]
    urls += [row['alt'] for row in data['competitions'] + data['matches'] if row.get('alt')]
    urls = list(dict.fromkeys(urls))
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as pool:
        results = list(pool.map(fetch, urls))
    known = {row['url'] for row in data['notices']}
    candidates = [{'source':row['url'],'link':link} for row in results if row.get('usableContent') for link in row.get('links',[]) if 'cqut.edu.cn' in link['url'] and link['url'] not in known]
    cqut = [r for r in results if 'cqut.edu.cn' in r['url']]
    summary = {'attempts':len(results),'usable':sum(r.get('usableContent',False) for r in results),'cqutAttempts':len(cqut),'cqutUsable':sum(r.get('usableContent',False) for r in cqut),'newNoticeCandidates':len(candidates),'statusCounts':{str(s):sum(r.get('status')==s for r in results) for s in {r.get('status') for r in results}}}
    report = {'reviewedAt':TODAY,'attemptedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Every retained nationwide competition identity, all active and retired curated originals, all configured CQUT source portals, every retained notice URL and official alternates. A failed request does not certify expiry or no new notice.','sources':results,'noticeCandidates':candidates,'identityCountsBefore':{'competitions':len(data['competitions']),'activeMatches':len(data['matches']),'retiredMatches':len(data['retired']),'notices':len(data['notices'])},'cqutContentUpdatedBefore':data['contentUpdated'],'summary':summary}
    (ROOT/'_content_review_2026-10-21.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False))

def annotate_and_apply():
    report_path = ROOT/'_content_review_2026-10-21.json'
    report = json.loads(report_path.read_text(encoding='utf-8'))
    before = datasets()
    notice_url = 'https://www.simcm.org.cn/article_detail.php?id=200'
    supplemental = fetch(notice_url)
    report['supplementalSources'] = [supplemental]
    # The complete official notice was independently read with the web tool as well.
    # Preserve that independent extraction even if this second HTTP request fails.
    report['officialExtracts'] = [{
        'url':notice_url,'checkedAt':TODAY,'publishedAt':'2026-10-15',
        'method':'web open of organizer official HTML, followed by independent local HTTP request',
        'title':'2026“科创杯”大学生数学建模竞赛 分赛区非企业命题赛前通知',
        'finding':'该当届非企业命题分赛区报名及提交答卷均于北京时间2026年10月20日24时截止，截止后不能再提交报名；后续晋级国赛需填写分赛区队号。',
        'evidenceExcerpt':'报名及提交答卷的截止时间为北京时间2026年10月20日24时，截止时间后不能再提交报名；后续晋级国赛需填写分赛区队号。'
    }]
    name = '“科创杯”大学生数学建模竞赛（2026 非企业命题赛道）'
    target = next(row for row in before['competitions'] if row['n']==name)
    comp_path = ROOT/'competitions.js'
    comp = comp_path.read_text(encoding='utf-8')
    start = comp.index('{scope:', comp.index('url:"https://m.saikr.com/MW26MM"'))
    end = comp.index('\n    {scope:',start)
    block = comp[start:end]
    if name not in block:
        raise RuntimeError('Refuse to change unexpected competition block')
    block = block.replace('st:"soon"','st:"closed"',1)
    block = re.sub(r'\breg:"[^"\n]*"','reg:"2026/10/20 24:00 分赛区非企业命题赛道报名与交卷均已截止；官网10/15赛前通知明确截止后不能再报名。国赛11/25启动仅供已晋级队伍，不能当作新报名入口。"',block)
    block = re.sub(r'\brun:"[^"\n]*"','run:"分赛区赛10/15 12:00–10/20 24:00（已结束）；国赛11/25–11/30，按官网晋级通知参加。"',block)
    block = re.sub(r'\bfit:"[^"\n]*"','fit:"分赛区当前已无法新报名；可作为建模练习资料。已参赛队伍按官网核对晋级资格，研究生按最高学历分组。"',block)
    block = re.sub(r'\bhelp:"[^"\n]*"','help:"可以协助复盘已公布赛题、核查推导与代码；已晋级队伍按官方通知准备国赛，保留独立推导、实验记录和原创性，不承诺证书或奖项。"',block)
    block = block.replace('url:"https://www.simcm.org.cn/"','url:"https://www.simcm.org.cn/", alt:"'+notice_url+'"')
    comp = comp[:start]+block+comp[end:]
    comp = re.sub(r'window\.COMP_UPDATED = "\d{4}-\d{2}-\d{2}";','window.COMP_UPDATED = "2026-10-21";',comp)
    comp = re.sub(r'window\.COMP_CHECKED = "\d{4}-\d{2}-\d{2}";','window.COMP_CHECKED = "2026-10-21";',comp)
    comp = re.sub(r'window\.COMP_CHECK_NOTE = "[^"\n]*";','window.COMP_CHECK_NOTE = "已实际请求全部183项原入口及官方备用入口；科创杯非企业命题分赛区10/20 24:00已截止，退出可报名推荐。其他部分官网受保护、仅返回页面框架或超时；旧赛程不冒充本次全部报名核验。";',comp)
    comp_path.write_text(comp,encoding='utf-8')
    match_path = ROOT/'matches.js'
    matches = match_path.read_text(encoding='utf-8')
    matches = re.sub(r'window\.MATCH_NOTE = "[^"\n]*";','window.MATCH_NOTE = "10月21日重新请求全部精选及退役来源，仍保留6项精选、7项有据退役；智慧城市官网报名截止10/23、交作品10/25。RoboMaster校内原文受保护，原填2026-12-20尚未从当前原文复核；部分来源仅页面框架或超时，不代表已确认开放。具体资格、费用及截止须以当届原文为准。";',matches)
    if 'window.MATCH_CHECKED' not in matches:
        matches = matches.replace('window.MATCH_UPDATED = "2026-10-20";','window.MATCH_UPDATED = "2026-10-20";\nwindow.MATCH_CHECKED = "2026-10-21";')
    match_path.write_text(matches,encoding='utf-8')
    cqut_path = ROOT/'cqut.js'
    cqut = cqut_path.read_text(encoding='utf-8')
    cqut = re.sub(r'window\.CQUT_CHECKED = "\d{4}-\d{2}-\d{2}";','window.CQUT_CHECKED = "2026-10-21";',cqut)
    cqut = re.sub(r'window\.CQUT_CHECK_NOTE = "[^"\n]*";','window.CQUT_CHECK_NOTE = "10月21日实际请求全部308条已有通知及配置的学校、部门与学院入口，共334个去重URL；本轮均未取得可核查正文（访问保护、空挑战或超时），保留308条通知和10月20日内容更新日。受阻不代表官网没有新通知，具体事务请核对原文。";',cqut)
    cqut_path.write_text(cqut,encoding='utf-8')
    after = datasets()
    assert before['notices']==after['notices'] and before['contentUpdated']==after['contentUpdated']
    assert before['matches']==after['matches'] and before['retired']==after['retired']
    assert [(r['n'],r['url']) for r in before['competitions']]==[(r['n'],r['url']) for r in after['competitions']]
    report['competitionChanges'] = [{'identity':{'n':target['n'],'url':target['url']},'before':target,'after':next(r for r in after['competitions'] if r['n']==name),'reasonCode':'verified_deadline','deadline':'2026-10-21T00:00:00+08:00','officialDeadlineText':'2026年10月20日24:00','sourceEvidence':[notice_url],'evidenceExcerpt':report['officialExtracts'][0]['evidenceExcerpt']}]
    report['curatedDeadlineReview'] = [{'n':r['n'],'url':r['url'],'storedDeadline':r['dl'],'snapshot':r,'request':next(({'status':s.get('status'),'usableContent':s.get('usableContent'),'error':s.get('error')} for s in report['sources'] if s['url']==r['url']),None)} for r in before['matches']]
    report['roboMasterOriginalEvidenceAudit'] = {'firstRepositoryCommit':'c179287','firstStoredDataDate':'2026-09-26','baselineFile':'_match_baseline_2026-10-17.json','baselineSourceCommit':'04988e0','originalURL':'https://www.cqut.edu.cn/info/1103/68024.htm','storedDeadline':'2026-12-20','independentDeadlineProofLocated':False,'previousReviewFiles':['_content_review_2026-10-19.json','_content_review_2026-10-20.json'],'finding':'Original first stored dataset and later baseline retain this date, but neither is independent proof of source text. October19,20,21 original-source probes return access protection. Do not alter the deadline or infer closure without original evidence.'}
    report['curatedDeadlineReviewNotes'] = ['No retained active curated entry has an explicitly stored October21 deadline.','Smart-city annual schedule and current event portal explicitly confirm October23 registration and October25 submission; no inferred deadline extension.','RoboMaster school selection original is access-protected; season2026 combined with stored December20 requires original-year verification. Do not infer closure from season or failed request.','Tianchi532503 can return only shared navigation, not competition rules. Existing stored October27 track1 extension note is retained, currently unconfirmed, rather than closing from the old aggregate October20 date.','Local readable page does not by itself prove current registration eligibility; all missing, protected or shell-only responses remain unverified.']
    report['cqut'] = {'beforeCount':308,'afterCount':308,'newNotices':0,'successfulContentUpdated':after['contentUpdated'],'checkedAt':TODAY,'attempts':report['summary']['cqutAttempts'],'usable':report['summary']['cqutUsable'],'limitation':'All configured sources plus all retained notice URLs actually requested; no usable new notice evidence. Access failures do not prove that no notices were published.'}
    report['identityCountsAfter'] = {'competitions':len(after['competitions']),'activeMatches':len(after['matches']),'retiredMatches':len(after['retired']),'notices':len(after['notices'])}
    report['removedMatches'] = []
    report['contentDates'] = {'nationwide':'2026-10-21','curated':'2026-10-20','cqut':after['contentUpdated'],'checkedAt':TODAY}
    report['summary']['supplementalAttempts'] = len(report['supplementalSources'])
    report['summary']['totalAttemptsIncludingSupplement'] = report['summary']['attempts'] + report['summary']['supplementalAttempts']
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'summary':report['summary'],'after':report['identityCountsAfter'],'changes':1},ensure_ascii=False))

def correct_smart_city():
    """Use the actual current event rules rather than a contradictory comparison."""
    before = datasets()
    old = next(x for x in before['matches'] if x['n']=='中国研究生智慧城市技术与创意设计大赛')
    updated = dict(old)
    updated['rego'] = '研究生等；1–4名学生，研究生任队长，本科生可作队员'
    updated['intro'] = '中国研究生创新实践系列大赛主题赛事之一，本届官网报名截止10月23日、作品提交截止10月25日，决赛12月26–27日。每队由1–4名学生和1–2名指导教师组成；队伍中若有本科生，须由研究生作为队长注册。同一作品只能参加本届大赛一个赛题，具体命题要求以当届通知为准。'
    updated['alt'] = 'https://cpipc.acge.org.cn/cw/hp/1'
    path = ROOT/'matches.js';source = path.read_text(encoding='utf-8')
    old_json = json.dumps(old,ensure_ascii=False,indent=2)
    # Objects in matches.js are indented by two spaces within the array.
    original_block = '\n'.join('  '+line for line in old_json.splitlines())
    new_block = '\n'.join('  '+line for line in json.dumps(updated,ensure_ascii=False,indent=2).splitlines())
    if original_block not in source:
        raise RuntimeError('Exact original smart-city object not found; do not rewrite unrelated data')
    source = source.replace(original_block,new_block,1).replace('window.MATCH_UPDATED = "2026-10-20";','window.MATCH_UPDATED = "2026-10-21";')
    path.write_text(source,encoding='utf-8')
    after = datasets()
    assert [(x['n'],x['url'],x['dl']) for x in before['matches']]==[(x['n'],x['url'],x['dl']) for x in after['matches']]
    rp=ROOT/'_content_review_2026-10-21.json';report=json.loads(rp.read_text(encoding='utf-8'))
    report['curatedContentChanges']=[{'before':old,'after':updated,'reason':'Remove internally false latest-registration-deadline comparison; include current official team-size and undergraduate captain rules.','sourceEvidence':[updated['alt']],'evidenceExcerpt':'每支参赛队伍由1-4名学生和1-2名指导教师组成；队伍中若有本科生参加，须由研究生作为队长注册。'}]
    report['contentDates']['curated']=TODAY
    rp.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Smart-city description and team rules corrected; original name, URL and deadline unchanged.')

if __name__ == '__main__':
    if '--apply' in sys.argv:
        annotate_and_apply()
        correct_smart_city()
    else:
        main()
