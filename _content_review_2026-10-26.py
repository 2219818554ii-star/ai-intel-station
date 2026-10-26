"""Full official-source probes for October 25; preserve all historical identities.

The previous collector supplies only its read/fetch helpers. Its mutation routines
are never called. No automatic retirement or content-date changes are permitted without new official evidence.
"""
import concurrent.futures
import datetime
import importlib.util
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
TODAY = '2026-10-26'
spec = importlib.util.spec_from_file_location('prior_content_probe', ROOT / '_content_review_2026-10-22.py')
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
prior.TODAY = TODAY
BEIJING = datetime.timezone(datetime.timedelta(hours=8))
INVITATION = 'https://cpipc.acge.org.cn/cw/contestNews/detail/1/2c9080189ef4ecee019f036d22cf5bcb?page=0'
MATHOR = 'https://m.saikr.com/vse/bigdata2026'


def fetch(url):
    result = prior.fetch(url)
    result['checkedAtTime'] = datetime.datetime.now(BEIJING).isoformat(timespec='seconds')
    return result


def collect():
    before = prior.datasets()
    urls = [source['u'] for group in before['sources'].values() for source in group]
    urls += ['https://www.cqut.edu.cn/tzgg.htm', 'https://www.cqut.edu.cn/tzgg/xygtz.htm', 'https://yjsy.cqut.edu.cn/']
    urls += [row['url'] for row in before['competitions'] + before['matches'] + before['retired'] + before['notices']]
    urls += [row['alt'] for row in before['competitions'] + before['matches'] if row.get('alt')]
    urls += [source['u'] for source in before['matchSources']]
    urls += [INVITATION, MATHOR, 'https://m.saikr.com/contest/notice_detail/49194']
    urls = list(dict.fromkeys(urls))
    started = datetime.datetime.now(BEIJING).isoformat(timespec='seconds')
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as pool:
        sources = list(pool.map(fetch, urls))
    cqut = [r for r in sources if 'cqut.edu.cn' in r['url']]
    known = {row['url'] for row in before['notices']}
    candidates = [{'source': row['url'], 'link': link} for row in cqut if row.get('usableContent') for link in row.get('links', []) if 'cqut.edu.cn' in link['url'] and link['url'] not in known]
    report = {
        'reviewedAt': TODAY, 'attemptedAt': started,
        'completedAt': datetime.datetime.now(BEIJING).isoformat(timespec='seconds'),
        'scope': 'All 183 retained nationwide identities, active/retired curated originals, every retained CQUT notice, configured source portals and official alternates. Errors and access challenges do not prove expiry, a dead link or no new content.',
        'sources': sources, 'noticeCandidates': candidates,
        'identityCountsBefore': {'competitions': len(before['competitions']), 'activeMatches': len(before['matches']), 'retiredMatches': len(before['retired']), 'notices': len(before['notices'])},
        'curatedSnapshotsBefore': before['matches'], 'retiredSnapshotsBefore': before['retired'],
        'nationwideSnapshotsBefore': before['competitions'], 'cqutSnapshotsBefore': before['notices'],
        'cqutContentUpdatedBefore': before['contentUpdated'],
        'summary': {'attempts': len(sources), 'usable': sum(r.get('usableContent', False) for r in sources), 'cqutAttempts': len(cqut), 'cqutUsable': sum(r.get('usableContent', False) for r in cqut), 'newNoticeCandidates': len(candidates), 'statusCounts': {str(s): sum(r.get('status') == s for r in sources) for s in {r.get('status') for r in sources}}}
    }
    (ROOT / '_content_review_2026-10-26.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report['summary'], ensure_ascii=False))



def apply_verified_changes():
    """Apply newly documented fees/rules and a genuinely passed official cutoff.

    School source checks are incomplete: preserve content and CQUT_UPDATED.
    This does not pretend the organizer published these existing rules today.
    """
    path=ROOT/'_content_review_2026-10-26.json';report=json.loads(path.read_text(encoding='utf8'))
    before=prior.datasets()
    assert before['matches']==report['curatedSnapshotsBefore']
    assert before['retired']==report['retiredSnapshotsBefore']
    assert before['competitions']==report['nationwideSnapshotsBefore']
    assert before['notices']==report['cqutSnapshotsBefore']
    assert datetime.datetime.now(BEIJING).date().isoformat()==TODAY
    assert datetime.datetime.now(BEIJING)>datetime.datetime.fromisoformat('2026-10-25T20:00:00+08:00')
    ai_url='https://www.ncccu.org.cn/index/Paper/case1.html'
    big_url='https://www.ncccu.org.cn/index/Paper/case2.html'
    sources={x['url']:x for x in report['sources']}
    for url in [ai_url,big_url]:
        proof=sources[url];text=proof.get('text','')
        assert proof.get('status')==200 and proof.get('usableContent') and '200元/队' in text and '国赛不再另行收费' in text
        assert 'submission.csv' in text and '每日最多 2 次提交' in text
    assert 'Macro-averaged AUC' in sources[ai_url]['text']
    assert 'AUROC' in sources[big_url]['text'] and 'AUPRC' in sources[big_url]['text']
    report['supplementalSources']=[fetch('https://m.saikr.com/vse/LCBCXSX')]
    report['officialExtracts']=[
      {'url':ai_url,'checkedAt':TODAY,'method':'Complete independent HTTP200 official rules and separately opened official web page.',
       'newlyDocumentedFacts':{'regionalTeamFeeRMB':200,'nationalAdditionalFeeRMB':0,'teamSize':'1–3 including captain; cross-school permitted; optional one instructor','dailySubmissionLimit':2,'regionalSubmission':'UTF-8 submission.csv','nationalSubmission':'CSV and model','primaryMetric':'Macro-averaged AUC','tieBreaker':'Macro-F1','regionalDeadline':'2026-11-13T23:59:00+08:00','nationalPeriod':'2026-11-19 17:00 – 2026-11-24'},
       'boundary':'These existing official rules are newly documented by this site, not claimed to have changed at the organizer today.'},
      {'url':big_url,'checkedAt':TODAY,'method':'Complete independent HTTP200 official rules and separately opened official web page.',
       'newlyDocumentedFacts':{'regionalTeamFeeRMB':200,'nationalAdditionalFeeRMB':0,'teamSize':'1–3 including captain; cross-school permitted; optional one instructor','dailySubmissionLimit':2,'regionalSubmission':'UTF-8 submission.csv','nationalSubmission':'CSV and model','primaryMetric':'AUROC','tieBreaker':'AUPRC','regionalDeadline':'2026-11-06T23:59:00+08:00','nationalPeriod':'2026-11-13 17:00 – 2026-11-18'},
       'boundary':'No assumption of a newly changed organizer rule or student eligibility beyond the official stated groups.'},
      {'url':'https://m.saikr.com/vse/LCBCXSX','checkedAt':TODAY,'method':'Fresh independent official publisher web open; normal HTTP attempt retained separately.',
       'title':'2026大学生“麟创杯”创新数学竞赛','finding':'Registration ended October25 at20:00 and the exam ended at23:00. October26 is after both actual cutoffs.',
       'registrationDeadline':'2026-10-25T20:00:00+08:00','examEnd':'2026-10-25T23:00:00+08:00'},
      {'url':'https://m.saikr.com/vse/AIPC26','checkedAt':TODAY,'method':'Fresh official publisher web open plus independently collected complete HTTP200 text.',
       'finding':'Only round1 ended October25. Round2 is October26–November29; round3 is November30–December27. Body explicitly allows total registration through December27; each round ends at23:59. The list header now refers to the next round, not the entire event.',
       'feeRMBPerPerson':29}
    ]
    active=[dict(m) for m in before['matches']]
    changes=[]
    for m in active:
        old=dict(m)
        if m['url']==ai_url:
            m['rego']='高校所有专业在校生；本研组与高职组分别评奖；1–3人含队长，可跨校，可设1名指导教师'
            m['help']='协助理解规则、设计基线和核对提交文件。官方主指标为Macro-AUC，辅指标Macro-F1；每个Study_id须输出10类概率，初赛交UTF-8的submission.csv，复赛还需模型。最终结果由队伍独立验证，遵守原创性和数据使用限制。'
            m['need']='先确认本校竞赛认定与训练条件。区域赛报名、考试和评审费200元/队，由队长缴费，其他队员不重复缴费；国赛不另收费。11月13日23:59前交预测CSV，每天最多2次提交；11月18日晋级公示，国赛11月19日17:00至24日。仅使用主办方允许的数据，不擅自传播赛题数据。'
        elif m['url']==big_url:
            m['rego']='高校所有专业在校生；本研组与高职组分别评奖；1–3人含队长，可跨校，可设1名指导教师'
            m['help']='协助理解眼底图像二分类与不平衡数据评价。官方主指标为AUROC，辅指标AUPRC；初赛提交UTF-8的submission.csv，复赛还需模型，不把辅助指标误作主排名。最终由队伍核验模型、结果与原创性。'
            m['need']='先确认本校认定与训练资源。区域赛报名、考试和评审费200元/队，由队长缴费，其他队员不重复缴费；国赛不另收费。11月6日23:59前提交预测CSV，每天最多2次；11月12日晋级公示，国赛11月13日17:00至18日。核对字段与数据使用限制后再投入训练。'
        if m!=old:changes.append({'before':old,'after':m,'sourceEvidence':[m['url']],'reason':'Newly documented concrete official cost, team and submission rules, not a date-only refresh.'})
    assert len(changes)==2
    source=(ROOT/'matches.js').read_text(encoding='utf8')
    source,n=re.subn(r'window\.MATCHES = \[[\s\S]*?\n\];',lambda _:'window.MATCHES = '+json.dumps(active,ensure_ascii=False,indent=2)+';',source,count=1);assert n==1
    def stamp(source,key,value):
        source,n=re.subn(r'window\.'+key+r' = "[^"\n]*";',lambda _:'window.'+key+' = '+json.dumps(value,ensure_ascii=False)+';',source,count=1);assert n==1;return source
    source=stamp(source,'MATCH_UPDATED',TODAY);source=stamp(source,'MATCH_CHECKED',TODAY)
    source=stamp(source,'MATCH_NOTE','10月26日实际复核全部精选及官方入口；新增两项计挑赛已核实的200元/队费用、1–3人组队、每天2次提交和CSV/模型要求，区分两赛评测指标。是站内补齐已有规则，不声称官网今天变更。5项线索/8项退役身份完整；RoboMaster当届截止年份仍待核实，化工技能赛的具体报名时刻仍须向组织方确认。')
    (ROOT/'matches.js').write_text(source,encoding='utf8')
    source=(ROOT/'competitions.js').read_text(encoding='utf8')
    plans=[
      ('2026大学生“麟创杯”创新数学竞赛',{'st':'closed','reg':'2026/4/29 – 2026/10/25 20:00（报名已截止；原50元资料费）','run':'2026/10/24 10:00 – 10/25 23:00（本场考试已结束）'},['https://m.saikr.com/vse/LCBCXSX']),
      ('2026 全国大学生人工智能应用实践大赛',{'reg':'正文总报名至2026/12/27；列表当前对应11/29场次，报名时再核对所选场次','run':'第一场10/25已结束；第二场10/26至11/29；第三场11/30至12/27，各场截止当日23:59、独立评审','help':'可协助理解赛题、制作原型、核对HTML导出；成果须本人审核。官网公示29元/人，第二场现为10月26日至11月29日，第三场11月30日至12月27日；第一场结束不代表整个赛事结束。按所选场次交作品并核对当场报名状态。'},['https://m.saikr.com/vse/AIPC26'])
    ]
    national_changes=[]
    for name,values,evidence in plans:
        start=source.rfind('{scope:',0,source.index('n:"'+name+'"'));end=source.index('\n    {scope:',start)
        block=source[start:end];old=next(m for m in before['competitions'] if m['n']==name)
        for k,v in values.items():block,n=re.subn(r'\b'+k+r':"[^"\n]*"',lambda _,k=k,v=v:k+':'+json.dumps(v,ensure_ascii=False),block,count=1);assert n==1
        source=source[:start]+block+source[end:];national_changes.append({'before':old,'changedFields':values,'sourceEvidence':evidence})
    source=stamp(source,'COMP_UPDATED',TODAY);source=stamp(source,'COMP_CHECKED',TODAY)
    source=stamp(source,'COMP_CHECK_NOTE','10月26日实际请求全部183项全国赛事、精选、退役及学校通知/备用源，共554个去重入口，119份可核查正文。发布者原页确认麟创杯10/25 20:00报名、23:00考试均已截止，已关闭；AIPC仅第一场结束，第二场10/26开始、第三场仍开放计划，未误退整赛。受保护或超时不作死链结论。')
    (ROOT/'competitions.js').write_text(source,encoding='utf8')
    source=(ROOT/'cqut.js').read_text(encoding='utf8')
    source=stamp(source,'CQUT_CHECKED',TODAY)
    source=stamp(source,'CQUT_CHECK_NOTE','10月26日实际请求全部322条已有通知与学校、学院、部门共349个去重入口，本轮均未取得可核查正文。普通Edge另查主站通知/部门通知、研究生院、化学化工和材料学院，仍超时；保留322条与原日期、最近内容更新10/23，不声称没有新通知。暂无法以真实新内容消除内容新鲜度告警。')
    (ROOT/'cqut.js').write_text(source,encoding='utf8')
    after=prior.datasets()
    identity=lambda rows:sorted((r['n'],r['url'],r['dl'],r['school']) for r in rows)
    assert identity(before['matches']+before['retired'])==identity(after['matches']+after['retired'])
    assert before['retired']==after['retired']
    assert next(m for m in before['matches'] if 'RoboMaster' in m['n'])==next(m for m in after['matches'] if 'RoboMaster' in m['n'])
    assert [(m['n'],m['url']) for m in before['competitions']]==[(m['n'],m['url']) for m in after['competitions']]
    assert before['notices']==after['notices'] and before['contentUpdated']==after['contentUpdated']=='2026-10-23'
    browser_path=pathlib.Path('C:/Users/22198/Documents/ChatGPT/学习/site-redesign-2026-10-26/official-cqut-browser.json')
    report.update(curatedContentChanges=changes,competitionChanges=national_changes,newNotices=[],additionalRetirements=[],allHistoricalIdentitiesPreserved=True,cqutAllContentAndContentDatePreserved=True,unresolvedFreshness={'CQUT_UPDATED':'2026-10-23','reason':'No readable current official notice/list/API was acquired; no date-only refresh or weakened guard.'})
    if browser_path.exists():report['cqutNormalBrowserAttempts']=json.loads(browser_path.read_text(encoding='utf8'))
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'curatedChanges':len(changes),'nationwideChanges':len(national_changes),'notices':len(after['notices']),'cqutContentUpdated':after['contentUpdated'],'unresolved':report['unresolvedFreshness']},ensure_ascii=False))

if __name__ == "__main__":
    if "--apply-verified" in sys.argv: apply_verified_changes()
    else: collect()
