"""2026-10-22 official-source collection; no guessed dates or automatic retirements."""
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
TODAY = '2026-10-22'

def datasets():
    code = "const fs=require('fs'),vm=require('vm'),w={};let c={window:w};vm.createContext(c);['cqut.js','matches.js','competitions.js'].forEach(f=>vm.runInContext(fs.readFileSync(f,'utf8'),c));console.log(JSON.stringify({notices:w.CQUT_NOTICES,sources:w.CQUT_SOURCES,matches:w.MATCHES,retired:w.MATCH_RETIRED,matchSources:w.MATCH_SOURCES,competitions:w.COMP,contentUpdated:w.CQUT_UPDATED}));"
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
    urls += [row['u'] for row in data['matchSources']]
    urls = list(dict.fromkeys(urls))
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as pool:
        results = list(pool.map(fetch, urls))
    known = {row['url'] for row in data['notices']}
    candidates = [{'source':row['url'],'link':link} for row in results if row.get('usableContent') for link in row.get('links',[]) if 'cqut.edu.cn' in link['url'] and link['url'] not in known]
    cqut = [r for r in results if 'cqut.edu.cn' in r['url']]
    summary = {'attempts':len(results),'usable':sum(r.get('usableContent',False) for r in results),'cqutAttempts':len(cqut),'cqutUsable':sum(r.get('usableContent',False) for r in cqut),'newNoticeCandidates':len(candidates),'statusCounts':{str(s):sum(r.get('status')==s for r in results) for s in {r.get('status') for r in results}}}
    report = {'reviewedAt':TODAY,'attemptedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Every retained nationwide competition identity, all active and retired curated originals, all configured CQUT source portals, every retained notice URL and official alternates. A failed request does not certify expiry or no new notice.','sources':results,'noticeCandidates':candidates,'identityCountsBefore':{'competitions':len(data['competitions']),'activeMatches':len(data['matches']),'retiredMatches':len(data['retired']),'notices':len(data['notices'])},'cqutContentUpdatedBefore':data['contentUpdated'],'curatedSnapshotsBefore':data['matches'],'retiredSnapshotsBefore':data['retired'],'nationwideIdentityBefore':[{'n':r['n'],'url':r['url']} for r in data['competitions']],'summary':summary}
    (ROOT/'_content_review_2026-10-22.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False))


def apply_verified_notes():
    """Apply only explicitly evidenced dates/rules; keep protected identities."""
    report_path = ROOT/'_content_review_2026-10-22.json'
    report = json.loads(report_path.read_text(encoding='utf-8'))
    before = datasets()
    invitation = 'https://cpipc.acge.org.cn/cw/contestNews/detail/1/2c9080189ef4ecee019f036d22cf5bcb?page=0'
    ai_rules = 'https://m.saikr.com/contest/notice_detail/49194'
    organizer_page = 'https://m.saikr.com/vse/bigdata2026'
    report['supplementalSources'] = [fetch(url) for url in [invitation,ai_rules,organizer_page]]
    report['officialExtracts'] = [
        {'url':invitation,'checkedAt':TODAY,'publishedAt':'2026-06-26','method':'Independent web open of current organizer invitation, with separate local HTTP probe in supplementalSources.','title':'第十二届中国研究生智慧城市技术与创意设计大赛参赛邀请函','finding':'报名与培养单位资格审核均于10月23日中午12:00截止；作品提交于10月25日中午12:00截止；不能将作品截止理解为报名期限。','evidenceExcerpt':'提交报名信息：6月27日—10月23日中午12:00；培养单位资格审核：6月27日—10月23日中午12:00；参赛作品提交：6月27日—10月25日中午12:00'},
        {'url':ai_rules,'checkedAt':TODAY,'publishedAt':'2026-10-16','method':'Independent web open of organizer published notice and separate local HTTP probe.','title':'【人工智能工具使用规定】2026年第七届MathorCup数学应用挑战赛——大数据竞赛','finding':'核心建模、算法、求解与分析必须独立完成；论文参考文献后声明使用/未使用AI；使用者必须提供AI工具使用详情说明PDF，保留关键交互与人工修改，代码注释注明AI辅助。','evidenceExcerpt':'使用AI工具的参赛作品必须在支撑材料中提供“AI工具使用详情说明”（PDF格式，以此命名）；不符合上述要求的参赛作品，视为违反竞赛规则，取消其评奖资格。'},
        {'url':organizer_page,'checkedAt':TODAY,'method':'Independent web open of competition organizer page, with separate HTTP probe.','title':'2026年第七届MathorCup数学应用挑战赛——大数据竞赛','finding':'报名10/23 12:00截止，初赛10/23 18:00—10/30 20:00；每队200元，报名和收费不能误作零成本拿奖。','evidenceExcerpt':'报名时间2026.08.13 00:00 - 2026.10.23 12:00；比赛时间2026.10.23 18:00 - 2026.10.30 20:00；每队需缴纳报名及评审费用200元。'}
    ]
    old = next(r for r in before['matches'] if r['n']=='中国研究生智慧城市技术与创意设计大赛')
    new = dict(old)
    new['deadlineTime'] = '12:00'
    new['intro'] = '中国研究生创新实践系列大赛主题赛事之一。本届报名与培养单位资格审核均于10月23日中午12:00截止，作品提交于10月25日中午12:00截止；提交作品期限不能代替报名期限。每队1–4名学生、1–2名指导教师；研究生任队长，本科生资格按当届原文核对。允许跨校、跨单位组队，同一作品不得重复申报。'
    new['need'] = '10月23日中午12:00前完成官网报名，并留出培养单位资格审核时间；10月25日中午12:00前交作品。先与队友和导师确认题目、材料及真实数据，具体命题要求以当届邀请函和赛题指南为准。'
    new['help'] = '协助对照赛题判断已有研究能否支持智慧城市实际场景，整理证据、检查方案和答辩材料。核心创新、实验数据与结果须由参赛者核验；不以更换叙事替代实际功能，也不承诺获奖。'
    new['alt'] = invitation
    path = ROOT/'matches.js';source = path.read_text(encoding='utf-8')
    render = lambda row: '\n'.join('  '+line for line in json.dumps(row,ensure_ascii=False,indent=2).splitlines())
    if render(old) not in source:
        raise RuntimeError('Exact curated object changed since read; refuse overwrite.')
    source = source.replace(render(old),render(new),1)
    source = re.sub(r'window\.MATCH_UPDATED = "\d{4}-\d{2}-\d{2}";',f'window.MATCH_UPDATED = "{TODAY}";',source)
    source = re.sub(r'window\.MATCH_CHECKED = "\d{4}-\d{2}-\d{2}";',f'window.MATCH_CHECKED = "{TODAY}";',source)
    source = re.sub(r'window\.MATCH_NOTE = "[^"\n]*";','window.MATCH_NOTE = "10月22日重新请求全部精选、退役及官方入口；保留6项线索、7项有据退役。智慧城市当届邀请函确认：10/23中午12:00报名与培养单位审核截止，10/25中午12:00交作品。RoboMaster原填截止年份仍待原文复核；访问保护、框架页或超时不代表已确认开放。";',source)
    path.write_text(source,encoding='utf-8')
    path = ROOT/'competitions.js';source = path.read_text(encoding='utf-8')
    name = 'MathorCup 数学应用挑战赛·大数据竞赛（第七届）'
    begin = source.rfind('{scope:',0,source.index('n:"'+name+'"'))
    end = source.index('\n    {scope:',begin)
    block = source[begin:end]
    old_comp = next(r for r in before['competitions'] if r['n']==name)
    block = re.sub(r'\bhelp:"[^"\n]*"','help:"每队报名及评审费200元；10/23中午12:00截止。官网10/16发布AI使用规定：核心建模、算法、求解与分析由队员独立完成；论文参考文献后声明AI使用情况（未使用也须声明）。使用者须附《AI工具使用详情说明》PDF，列工具版本、用途、关键交互与人工修改，代码注释同步标注。可协助理解规则、检查数据与代码；不以代写代赛替代独立完成。"',block)
    block = re.sub(r'\bfit:"[^"\n]*"','fit:"适合愿意独立完成数据分析与建模的1–3人队；先评估赛期投入与200元/队费用，AI仅按官方规定辅助。"',block)
    block = block.replace('url:"https://new.saikr.com/vse/bigdata2026"','url:"https://new.saikr.com/vse/bigdata2026", alt:"'+ai_rules+'"')
    source = source[:begin]+block+source[end:]
    # The same smart-city identity in the nationwide library uses the precise organizer invitation.
    name_smart = '中国研究生智慧城市技术与创意设计大赛（第十二届）'
    begin = source.rfind('{scope:',0,source.index('n:"'+name_smart+'"'))
    end = source.index('\n    {scope:',begin)
    block = source[begin:end]
    block = re.sub(r'\bteam:"[^"\n]*"','team:"1–4名学生、1–2名指导教师；可跨校"',block)
    block = re.sub(r'\breg:"[^"\n]*"','reg:"报名及培养单位资格审核均为6/27–10/23中午12:00；勿等作品截止才报名"',block)
    block = re.sub(r'\bdesc:"[^"\n]*"','desc:"围绕智慧城市实际需求提交创新方案或作品，设定向、自由、企业揭榜和地方主题赛道；研究生任队长，作品需体现原创性、完成程度、性能和应用价值。"',block)
    block = re.sub(r'\bfit:"[^"\n]*"','fit:"已有研究须与真实城市应用需求相符；先核对赛题、数据和原型成熟度，避免临近截止仅改写材料。"',block)
    block = re.sub(r'\bhelp:"[^"\n]*"','help:"协助核对赛题、整理真实证据、检查作品及答辩材料；报名与培养单位资格审核均须10/23中午12:00前完成，作品10/25中午12:00前提交。"',block)
    block = block.replace('url:"https://cpipc.acge.org.cn/cw/hp/1"','url:"https://cpipc.acge.org.cn/cw/hp/1", alt:"'+invitation+'"')
    source = source[:begin]+block+source[end:]
    source = re.sub(r'window\.COMP_UPDATED = "\d{4}-\d{2}-\d{2}";',f'window.COMP_UPDATED = "{TODAY}";',source)
    source = re.sub(r'window\.COMP_CHECKED = "\d{4}-\d{2}-\d{2}";',f'window.COMP_CHECKED = "{TODAY}";',source)
    source = re.sub(r'window\.COMP_CHECK_NOTE = "[^"\n]*";','window.COMP_CHECK_NOTE = "10月22日实际请求全部183项原入口及官方备用入口；补齐智慧城市10/23中午12:00报名与单位审核要求、MathorCup官方AI使用规定。本轮未取得需新增清退的可靠证据；部分官网受保护、仅返回框架或超时，旧赛程不冒充全部报名核验。";',source)
    path.write_text(source,encoding='utf-8')
    cqut_count = sum('cqut.edu.cn' in r['url'] for r in report['sources'])
    cqut_usable = sum(r.get('usableContent',False) for r in report['sources'] if 'cqut.edu.cn' in r['url'])
    if cqut_usable:
        raise RuntimeError('Usable CQUT responses need manual notice review before applying no-new-content note.')
    path = ROOT/'cqut.js';source = path.read_text(encoding='utf-8')
    source = re.sub(r'window\.CQUT_CHECKED = "\d{4}-\d{2}-\d{2}";',f'window.CQUT_CHECKED = "{TODAY}";',source)
    note = f'10月22日实际请求全部308条已有通知及学校、部门、学院入口，共{cqut_count}个去重URL；本轮均未取得可核查正文（访问保护、空挑战或超时）。保留308条通知和10月20日内容更新日；受阻不代表官网没有新通知，具体事务请核对原文。'
    source = re.sub(r'window\.CQUT_CHECK_NOTE = "[^"\n]*";','window.CQUT_CHECK_NOTE = "'+note+'";',source)
    path.write_text(source,encoding='utf-8')
    after = datasets()
    identity = lambda rows,keys: [tuple(r[k] for k in keys) for r in rows]
    assert identity(before['competitions'],['n','url']) == identity(after['competitions'],['n','url'])
    assert identity(before['matches'],['n','url','dl','school']) == identity(after['matches'],['n','url','dl','school'])
    assert before['retired']==after['retired']
    assert before['notices']==after['notices'] and before['contentUpdated']==after['contentUpdated']
    robo_before = next(r for r in before['matches'] if 'RoboMaster' in r['n'])
    robo_after = next(r for r in after['matches'] if 'RoboMaster' in r['n'])
    assert robo_before==robo_after and robo_after['deadlineUnverified'] and robo_after['verificationNote']
    report['competitionChanges'] = [{'before':r,'after':next(a for a in after['competitions'] if a['n']==r['n']),'reasonCode':'verified_rules_and_exact_cutoff','sourceEvidence':[invitation] if '智慧城市' in r['n'] else [ai_rules,organizer_page]} for r in before['competitions'] if r != next(a for a in after['competitions'] if a['n']==r['n'])]
    report['curatedContentChanges'] = [{'before':old,'after':new,'reason':'Replace vague dates and unsubstantiated award-oriented research packaging with exact official cutoff and required unit review.','sourceEvidence':[invitation]}]
    report['curatedDeadlineReview'] = [{'n':r['n'],'url':r['url'],'storedDeadline':r['dl'],'snapshot':r,'request':next(({'status':s.get('status'),'usableContent':s.get('usableContent'),'error':s.get('error')} for s in report['sources'] if s['url']==r['url']),None)} for r in before['matches']]
    report['curatedDeadlineReviewNotes'] = ['Smart-city registration and unit eligibility review both end at12:00 Beijing time October23; submission12:00 October25 is separate.','All6active and7retired curated source URLs actually requested; no newly verified expired eligible entry as ofOctober22.','RoboMaster exact original object retained, including deadlineUnverified and verificationNote.','Tianchi532503 still only returns navigation/login shell; do not interpret aggregate oldOctober20 or one track extension as universal deadline.','No automatic retirement based on request errors or vague annual calendars.']
    report['cqut'] = {'beforeCount':308,'afterCount':308,'newNotices':0,'successfulContentUpdated':after['contentUpdated'],'checkedAt':TODAY,'attempts':cqut_count,'usable':cqut_usable,'limitation':'No usable text; retained content, source dates and URLs. The failed source checks do not prove no new notices exist.'}
    report['identityCountsAfter'] = {'competitions':len(after['competitions']),'activeMatches':len(after['matches']),'retiredMatches':len(after['retired']),'notices':len(after['notices'])}
    report['removedMatches'] = []
    report['identityChecks'] = {'nationwideOriginalNamesAndURLsUnchanged':True,'curatedOriginalNamesURLsDeadlinesSchoolsUnchanged':True,'retiredObjectsUnchanged':True,'roboMasterOriginalObjectIncludingUncertaintyUnchanged':True,'cqutContentAndSourceDateUnchanged':True}
    report['contentDates'] = {'nationwide':TODAY,'curated':TODAY,'cqut':after['contentUpdated'],'checkedAt':TODAY}
    report['summary']['supplementalAttempts'] = len(report['supplementalSources'])
    report['summary']['totalAttemptsIncludingSupplement'] = report['summary']['attempts'] + len(report['supplementalSources'])
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'summary':report['summary'],'after':report['identityCountsAfter'],'changes':len(report['competitionChanges'])+1},ensure_ascii=False))


def finalize_precise_cutoff_and_stages():
    """Keep original date identity and separate registration from per-stage submissions."""
    before = datasets()
    path = ROOT/'matches.js';source = path.read_text(encoding='utf-8')
    old = next(r for r in before['matches'] if r['n']=='中国研究生智慧城市技术与创意设计大赛')
    new = dict(old);new['deadlineTime']='12:00'
    render = lambda row: '\n'.join('  '+line for line in json.dumps(row,ensure_ascii=False,indent=2).splitlines())
    assert render(old) in source
    path.write_text(source.replace(render(old),render(new),1),encoding='utf-8')
    name = '2026 全国大学生人工智能应用实践大赛'
    path = ROOT/'competitions.js';source = path.read_text(encoding='utf-8')
    begin = source.rfind('{scope:',0,source.index('n:"'+name+'"'));end = source.index('\n    {scope:',begin)
    block = source[begin:end]
    values = {
      'org':'四川汇鑫创融大数据研究院主办；腾讯WorkBuddy为指定创作工具',
      'reg':'正文说明总报名至2026/12/27；列表显示10/25为第一场，三场任选，报名前再核对当场报名状态',
      'run':'三场作品分别截至10/25、11/29、12/27当日23:59；按提交时间归入当场，各场独立评审，只需参加一场',
      'desc':'依托指定WorkBuddy工具制作并提交HTML作品，面向在校生（含研究生）及年满18周岁的其他人士。正文为三场任选，列表“周日截止”不等于全部赛事结束。',
      'fit':'适合已有可演示AI工具作品的学生练习交付；先核对题目、费用和学院认定，不保证综测或评奖加分。',
      'help':'可协助读题、制作原型、检查HTML导出和演示；成果须由本人审核。官网公示29元/人；报名列表与正文的截止范围有差异，第一场10/25 23:59前提交，后两场按原文安排核对，选定场次后以该场截止为准。'
    }
    for key,value in values.items():
      block = re.sub(r'\b'+key+r':"[^"\n]*"',key+':"'+value+'"',block)
    source = source[:begin]+block+source[end:];path.write_text(source,encoding='utf-8')
    after = datasets()
    assert [(r['n'],r['url']) for r in before['competitions']]==[(r['n'],r['url']) for r in after['competitions']]
    assert [(r['n'],r['url'],r['dl'],r['school']) for r in before['matches']]==[(r['n'],r['url'],r['dl'],r['school']) for r in after['matches']]
    assert before['notices']==after['notices'] and before['retired']==after['retired']
    rp = ROOT/'_content_review_2026-10-22.json';report=json.loads(rp.read_text(encoding='utf-8'))
    report['curatedContentChanges'][0]['after'] = next(r for r in after['matches'] if r['n']=='中国研究生智慧城市技术与创意设计大赛')
    report['curatedContentChanges'][0]['deadlinePrecision'] = {'baselineDateUnchanged':'2026-10-23','separateVerifiedTime':'12:00','timezone':'Asia/Shanghai','source':new['alt']}
    report['competitionChanges'].append({'before':next(r for r in before['competitions'] if r['n']==name),'after':next(r for r in after['competitions'] if r['n']==name),'reasonCode':'verified_stage_schedule_and_cost','sourceEvidence':['https://m.saikr.com/vse/AIPC26'],'evidenceExcerpt':'主办单位：四川汇鑫创融大数据研究院；报名即日起至2026年12月27日，作品三场分别截止10月25日、11月29日、12月27日当日23:59，每场独立评审；29元/位。','sourceConflict':'列表报名及比赛结束标10月25日，正文安排总报名12月27日和三场任选；仅展示已明确区分，不假定任意场次都延长。'})
    report['officialExtracts'].append({'url':'https://m.saikr.com/vse/AIPC26','checkedAt':TODAY,'method':'Complete independent HTTP200 organizer listing returned in sources, including stage schedule, cost and publisher.','title':'2026年全国大学生人工智能应用实践大赛','finding':'October25 is the first submission round, not total event cutoff. December27 total registration and three independently judged rounds explicitly stated.','evidenceExcerpt':report['competitionChanges'][-1]['evidenceExcerpt']})
    report['identityChecks']['smartCityBaselineDateUnchangedWithSeparateOfficialTime'] = True
    rp.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Verified noon cutoff and AIPC separate rounds/cost applied; identities preserved.')


if __name__ == '__main__':
    if '--finalize' in sys.argv:
        finalize_precise_cutoff_and_stages()
    elif '--apply' in sys.argv:
        apply_verified_notes()
        finalize_precise_cutoff_and_stages()
    else:
        main()
