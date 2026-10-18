"""Dated, evidence-bounded content review.

Default: fetch known official source pages to the dated JSON without changing JS.
--apply: apply the explicit, manually reviewed 2026-10-19 retirements and wording
changes after collection; refuse if the expected original identities differ.
This script is a review artifact, not a claim that blocked sources were refreshed.
"""
import concurrent.futures, urllib.request, urllib.error, subprocess, json, re, html, pathlib, datetime, sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).resolve().parent
NODE=r'C:/Users/22198/.workbuddy/binaries/node/versions/22.22.2-6/node.exe'
TODAY='2026-10-19'
def datasets():
    code="const fs=require('fs'),vm=require('vm'),w={};let c={window:w};vm.createContext(c);['cqut.js','matches.js','competitions.js'].forEach(f=>vm.runInContext(fs.readFileSync(f,'utf8'),c));console.log(JSON.stringify({notices:w.CQUT_NOTICES,sources:w.CQUT_SOURCES,matches:w.MATCHES,competitions:w.COMP}));"
    return json.loads(subprocess.check_output([NODE,'-e',code],cwd=ROOT).decode('utf-8'))
def strip(x):
    x=re.sub(r'<(script|style)\b[^>]*>[\s\S]*?</\1>', '', x,flags=re.I)
    return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>',' ',x))).strip()
def fetch(url):
    result={'url':url}
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req,timeout=18) as r:
            raw=r.read()
            enc=r.headers.get_content_charset()
            meta=re.search(br'(?:charset\s*=\s*[\"\']?)([\w-]+)',raw[:4096],re.I)
            enc=(meta.group(1).decode('ascii') if meta else enc) or 'utf-8'
            s=raw.decode(enc,errors='replace')
            if '\ufffd' in s:
                candidates=[raw.decode(c,errors='replace') for c in ['utf-8','gb18030']]
                s=min([s]+candidates,key=lambda x:x.count('\ufffd'))
            result.update(status=r.status,finalUrl=r.url,title=strip(re.search(r'<title[^>]*>([\s\S]*?)</title>',s,re.I).group(1)) if re.search(r'<title[^>]*>([\s\S]*?)</title>',s,re.I) else '',text=strip(s))
            result['usableContent']=r.status==200 and len(result['text'])>300
            if r.status==202: result['limitation']='HTTP 202 empty anti-bot challenge, not a usable notice page'
            result['links']=[{'url':urllib.parse.urljoin(r.url,m.group(1)),'title':strip(m.group(2))} for m in re.finditer(r'<a\b[^>]*href=[\"\']([^\"\']+)[\"\'][^>]*>([\s\S]*?)</a>',s,re.I) if '/info/' in m.group(1)]
            # preserve surrounding publication dates for list records
            result['datedLinks']=[strip(m.group(0)) for m in re.finditer(r'<li\b[^>]*>[\s\S]*?</li>',s,re.I) if '/info/' in m.group(0)]
    except Exception as e: result.update(error=str(e))
    return result

def collect():
    data=datasets(); sources=[]
    for group in data['sources'].values(): sources.extend(x['u'] for x in group)
    sources += ['https://www.cqut.edu.cn/tzgg.htm','https://www.cqut.edu.cn/tzgg/xygtz.htm','https://yjsy.cqut.edu.cn/']
    urgent=[x['url'] for x in data['competitions'] if x['n'] in ['中国研究生网络安全创新大赛（第五届）','2026华智·高校大学生人工智能大赛','第七届中国人工智能大赛','天池·Agent / 数据共情者算法大赛','全国大学生数学竞赛']]
    sources += urgent + [x['url'] for x in data['matches']]
    sources=list(dict.fromkeys(sources))
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool: results=list(pool.map(fetch,sources))
    evidence_path=ROOT/'_content_review_2026-10-19.json'
    out=json.loads(evidence_path.read_text(encoding='utf-8')) if evidence_path.exists() else {}
    out.update(reviewedAt=TODAY,scope='CQUT source discovery and urgent competition deadline review. Existing identities are preserved; HTTP blocking is not a dead-link verdict.',sources=results)
    (ROOT/'_content_review_2026-10-19.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    for r in results:
        print(json.dumps({'url':r['url'],'status':r.get('status'),'error':r.get('error'),'title':r.get('title'),'newLinks': [x for x in r.get('links',[]) if x['url'] not in {n['url'] for n in data['notices']}]},ensure_ascii=False))
def apply_review():
    evidence_path=ROOT/'_content_review_2026-10-19.json'
    review=json.loads(evidence_path.read_text(encoding='utf-8'))
    for r in review['sources']:
        r['usableContent']=r.get('status')==200 and len(r.get('text',''))>300
        if r.get('status')==202: r['limitation']='HTTP 202 empty anti-bot challenge, not a usable notice page'
        if '\ufffd' in r.get('text',''): r['decodingWarning']='Contains replacement characters; not used as evidence for an edit.'
    data=datasets()
    retired={
      '第五届中国研究生网络安全创新大赛':('deadline','2026-10-18','报名已于北京时间2026年10月18日结束；作品提交期不等于新队伍报名期。',['https://cpipc.acge.org.cn/cw/hp/2c90800c8093eef401809d33b36f0652'],'官网赛程：报名2026年06月18日—2026年10月18日。'),
      '第七届中国人工智能大赛':('deadline','2026-10-18','官方启动通知规定10月18日报名截止，现已过期。',['https://ai.xm.gov.cn/detail/article-detail.html?id=2026c40news0001'],'报名阶段即日起—10月18日，报名和资格审核。'),
      '2026 年第十三届「学创杯」全国大学生创业综合模拟大赛（校内赛）':('deadline','2026-04-07','该校内赛报名与比赛均早已结束，原“以校内通知为准”掩盖了明确的过期信息。',['https://news.ctbu.edu.cn/info/1047/1053911.htm'],'报名3月25日—4月7日；决赛4月26日。'),
      '第六届全国大学生化学实验创新设计大赛 · 云南大学预选赛':('eligibility',None,'官网明确仅限云南大学普通全日制本科在校学生；本站用户为重庆理工研究生，不符合参赛身份。',['http://www.eccce.ynu.edu.cn/info/1010/1195.htm'],'参赛对象：云南大学普通全日制本科在校学生。'),
      '第七届国际大学生工程力学竞赛（全英文）· 重庆交通大学选拔赛':('deadline_and_eligibility','2026-10-14','10月14日已截止、10月16日已举办，且仅限该校本科生。',['http://civil.cqjtu.edu.cn/info/1004/13318.htm'],'参赛对象：全体在校本科生；2026年10月14日前加入竞赛群；10月16日选拔赛。')
    }
    removed=[]
    for m in data['matches']:
        if m['n'] in retired:
            kind,deadline,reason,sources,excerpt=retired[m['n']]
            removed.append(dict(n=m['n'],url=m['url'],dl=m['dl'],deadline=deadline,reasonCode=kind,reason=reason,sourceEvidence=sources,evidenceExcerpt=excerpt,retiredAt=TODAY,snapshot=m))
    if len(removed)!=5:
        raise RuntimeError('Expected exactly five independently evidenced retirements; refuse a partial rewrite.')
    p=ROOT/'matches.js'; src=p.read_text(encoding='utf-8')
    for item in removed:
        matches=list(re.finditer(r'\n  \{\n[\s\S]*?\n  \},',src))
        target=[m for m in matches if 'n:'+json.dumps(item['n'],ensure_ascii=False) in m.group(0)]
        if len(target)!=1: raise RuntimeError('Cannot locate unique match block: '+item['n'])
        src=src[:target[0].start()]+src[target[0].end():]
    src=src.replace('window.MATCH_UPDATED = "2026-10-17"','window.MATCH_UPDATED = "'+TODAY+'"')
    src=src.replace('本次维护：2026-10-17。清退 3 项已过报名截止的赛事和 1 项限本科生的赛事；\n * 补入数维杯、中国人工智能大赛和计算机能力挑战赛两个独立赛项。\n * 新增项的来源与截止证据见 _matches_review_2026-10-17.json；旧条目不冒充本次全量核验。','本次维护：2026-10-19。按官方报名日期与学籍要求清退 5 项过期或不符合身份的赛事。\n * 完整旧条目和退役依据保存在 MATCH_RETIRED 与 _content_review_2026-10-19.json。\n * 部分来源受反爬限制；保留条目不冒充本次全量可报名核验。')
    src=re.sub(r'window\.MATCH_NOTE\s*=\s*[\s\S]*?;\n','window.MATCH_NOTE = '+json.dumps('10月19日已清理5项过期或不符合参赛身份的赛事。部分校内来源本次访问受限，报名之前仍需核对本校资格、截止时间和费用；列表不代表保证仍可报名。',ensure_ascii=False)+';\n',src,count=1)
    for school in ['ctbu','ynu']:
        src=re.sub(r'\n  \{k:"'+school+r'",[^\n]*\},?','',src)
    retired_data=[dict(x['snapshot'],retiredAt=TODAY,reasonCode=x['reasonCode'],reason=x['reason'],sourceEvidence=x['sourceEvidence'],evidenceExcerpt=x['evidenceExcerpt'],deadline=x['deadline']) for x in removed]
    src+='\n/* 已退役精选：仅供审计，不进入可报名列表。原始字段完整保留，禁止无依据回流。 */\nwindow.MATCH_RETIRED = '+json.dumps(retired_data,ensure_ascii=False,indent=2)+';\n'
    p.write_text(src,encoding='utf-8')
    comp=ROOT/'competitions.js'; old=comp.read_text(encoding='utf-8'); new=old
    replacements={
      '6/18 – 10/18 23:59（距今 1 天，明天截止，尽快组队）':'6/18 – 10/18 23:59（报名已截止；已报名队伍按官网要求提交作品）',
      '报名 2026.07.01 – 10/18（第三场考试 10/18，距今 1 天，明天截止，尽快报名）':'原公告报名至2026/10/18（已截止）；是否另开11/15场次报名须查官网，不能凭考试日期视为可报名',
      '报名 即日起 – 2026/10/18（距今 1 天，明天截止，尽快通过官网注册组队）':'报名 即日起 – 2026/10/18（官网启动通知规定的报名截止已过）',
      '6/27 – 10/23 12:00（距今 6 天，尽快组队）':'6/27 – 10/23 12:00（截止时刻以当届赛事细则为准）',
      '即日起 – 10/23 12:00（距今 6 天，研究生组单独评奖）':'即日起 – 10/23 12:00（研究生组单独评奖）',
      '（赛题1 延至 10/27，以官网为准；距今 3 天）':'（赛题1 延至 10/27，以赛题官方最新通知为准）',
      '（缴费 10/20；报名费 60–100 元/人以学校为准，距今 2 天）':'（缴费 10/20；各校可能更早截止，资格与费用以本校通知为准）',
      '（约 10/20 截止，距今 3 天）':'（约 10/20 截止，精确时刻须查赛题通知）',
      '省赛 10/17–11/2（明天开赛）':'省赛 10/17–11/2（仅面向已获参赛资格的选手）'
    }
    for a,b in replacements.items():
        if a not in new: raise RuntimeError('Missing expected dated wording: '+a)
        new=new.replace(a,b)
    for name in ['中国研究生网络安全创新大赛（第五届）','2026华智·高校大学生人工智能大赛','第七届中国人工智能大赛']:
        start=new.index('n:'+json.dumps(name,ensure_ascii=False))
        end=new.find('\n    {scope:',start)
        if end<0: end=new.index('\n  ];',start)
        block=new[start:end]
        if 'st:"soon"' not in block: raise RuntimeError('Expected soon state for '+name)
        new=new[:start]+block.replace('st:"soon"','st:"closed"',1)+new[end:]
    new=new.replace('window.COMP_UPDATED = "2026-10-17"','window.COMP_UPDATED = "'+TODAY+'"').replace('(snapshot 2026-10-17)','(deadline review 2026-10-19; identities preserved)')
    new=new.replace('请于 10/18 截止前提交完整材料，AI 使用范围以赛题规则为准。','原报名截止为10/18；已报名团队请核对后续赛程，AI 使用范围以赛题规则为准。')
    comp.write_text(new,encoding='utf-8')
    cqut=ROOT/'cqut.js'; cqsrc=cqut.read_text(encoding='utf-8')
    cqsrc+='\n/* 核查尝试与内容成功更新分开记录；反爬挑战不能冒充新通知。 */\nwindow.CQUT_CHECKED = "'+TODAY+'";\nwindow.CQUT_CHECK_NOTE = "10月19日已尝试核查官网；部分通知列表返回反爬挑战或超时，暂保留10月17日成功更新的294条。具体事务请以官网原文为准。";\n'
    cqut.write_text(cqsrc,encoding='utf-8')
    result=datasets()
    assert len(result['notices'])==294 and result['notices']==data['notices']
    assert len(result['matches'])==8
    assert [(x['n'],x['url']) for x in result['competitions']]==[(x['n'],x['url']) for x in data['competitions']]
    review.update(removedMatches=removed,cqut={'beforeCount':294,'afterCount':294,'newNotices':0,'successfulContentUpdated':'2026-10-17','attemptedAt':TODAY,'limitation':'Core lists returned HTTP 412, HTTP 202 empty challenge pages, or network timeouts. No notices or success timestamp were fabricated.'},competitionChanges={'closed':[x for x in ['中国研究生网络安全创新大赛（第五届）','2026华智·高校大学生人工智能大赛','第七届中国人工智能大赛']],'relativeTextRemoved':list(replacements.keys()),'preservedIdentities':183,'note':'华智官网为JS页面，本次未取得新的报名细则，按已收录10/18明确截止保守关闭；不推断11/15考试仍可新报名。'},officialExtracts=[{'url':'https://ai.xm.gov.cn/detail/article-detail.html?id=2026c40news0001','method':'web search/open official extracted content, 2026-10-19','finding':'第七届中国人工智能大赛：报名与资格审核截止10月18日。'}])
    evidence_path.write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'activeMatches':len(result['matches']),'retiredMatches':len(removed),'CQUT':len(result['notices']),'competitionIdentities':len(result['competitions'])},ensure_ascii=False))

if __name__=='__main__':
    if '--apply' in sys.argv: apply_review()
    else: collect()
