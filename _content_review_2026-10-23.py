"""Full official-source probes for October 23; preserve all historical identities.

The previous collector supplies only its read/fetch helpers. Its mutation routines
are never called. Exact noon retirement is applied separately after evidence review.
"""
import concurrent.futures
import datetime
import importlib.util
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
TODAY = '2026-10-23'
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
    (ROOT / '_content_review_2026-10-23.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report['summary'], ensure_ascii=False))


def apply_verified():
    """Apply reviewed official excerpts; fail closed on missing source or time proof."""
    path = ROOT / '_content_review_2026-10-23.json'
    report = json.loads(path.read_text(encoding='utf-8'))
    before = prior.datasets()
    assert before['competitions'] == report['nationwideSnapshotsBefore']
    assert before['matches'] == report['curatedSnapshotsBefore']
    assert before['retired'] == report['retiredSnapshotsBefore']
    assert before['notices'] == report['cqutSnapshotsBefore']
    now = datetime.datetime.now(BEIJING)
    assert now.date().isoformat() == TODAY
    cutoff = datetime.datetime.fromisoformat('2026-10-23T12:00:00+08:00')
    assert now > cutoff, 'Do not retire before the independently verified noon cutoff.'
    report['supplementalSources'] = [fetch(url) for url in [INVITATION, MATHOR, 'https://m.saikr.com/vse/LCBCXSX', 'https://m.saikr.com/contest/notice_detail/49373']]
    report['officialExtracts'] = [
        {'url': INVITATION, 'checkedAt': TODAY, 'checkedAtTime': now.isoformat(timespec='seconds'), 'publishedAt': '2026-06-26', 'method': 'Fresh independent web open of the complete organizer invitation; separate current HTTP probes retained.', 'title': '第十二届中国研究生智慧城市技术与创意设计大赛参赛邀请函', 'finding': '报名信息和培养单位资格审核均于2026年10月23日中午12:00截止；已超过该时刻，10月25日中午交作品不构成报名延长。', 'evidenceExcerpt': '提交报名信息：6月27日—10月23日中午12:00；培养单位资格审核：6月27日—10月23日中午12:00；参赛作品提交：6月27日—10月25日中午12:00。', 'verifiedDeadline': '2026-10-23', 'deadlineTime': '12:00', 'timezone': 'Asia/Shanghai'},
        {'url': MATHOR, 'checkedAt': TODAY, 'checkedAtTime': now.isoformat(timespec='seconds'), 'method': 'Fresh independent web open of organizer published competition entry and separate HTTP probe.', 'title': '2026年第七届MathorCup数学应用挑战赛——大数据竞赛', 'finding': '2026年10月23日12:00报名结束，18:00初赛开始；200元/队及官方AI使用规定仍适用已报名团队。', 'evidenceExcerpt': '报名时间：2026.08.13 00:00 - 2026.10.23 12:00；比赛时间：2026.10.23 18:00 - 2026.10.30 20:00。'},
        {'url': 'https://m.saikr.com/vse/LCBCXSX', 'checkedAt': TODAY, 'method': 'Fresh independent web open of publisher competition entry and separate HTTP probe.', 'title': '2026大学生“麟创杯”创新数学竞赛', 'finding': '最新页面为10月24至25日考试，10月25日20:00报名截止；原记录只写10月24日不完整。报名费50元，一人一次参赛。', 'evidenceExcerpt': '报名时间：2026.04.29 00:00 - 2026.10.25 20:00；比赛时间：2026.10.24 10:00 - 2026.10.25 23:00；每位参赛者需缴纳50元资料费，每名选手仅支持一次报名、一次参赛机会。'},
        {'url': 'https://m.saikr.com/contest/notice_detail/49373', 'checkedAt': TODAY, 'publishedAt': '2026-10-21', 'method': 'Fresh independent web open of organizer exam guide and separate HTTP probe.', 'title': '【10月场次考试流程指南】', 'finding': '需本人持证件完成摄像头核验，考试期间不可切屏或翻阅任何资料；AI辅助仅能用于赛前复习，不得暗示考试代答或实时外援。', 'evidenceExcerpt': '考试期间任选一小时参与答题；考试时需使用带有摄像头的设备；考试只支持进入一次，进入后不得切屏，不得翻阅任何资料；本人举着证件面向摄像头展示30S以上。'}
    ]
    smart = next(r for r in before['matches'] if r['n'] == '中国研究生智慧城市技术与创意设计大赛')
    assert smart['dl'] == '2026-10-23' and smart['deadlineTime'] == '12:00'
    retirement = {
        'retiredAt': TODAY, 'retiredAtTime': now.isoformat(timespec='seconds'),
        'reasonCode': 'deadline', 'deadline': '2026-10-23', 'deadlineTime': '12:00',
        'reason': '报名信息提交及培养单位资格审核已于北京时间2026年10月23日中午12:00截止；10月25日中午12:00仅为已报名团队提交作品截止，不能作为新队伍报名期限。',
        'sourceEvidence': [INVITATION], 'evidenceExcerpt': report['officialExtracts'][0]['evidenceExcerpt']
    }
    active = [r for r in before['matches'] if r['n'] != smart['n']]
    retired = before['retired'] + [dict(smart, **retirement)]
    report['removedMatches'] = [dict({'n': smart['n'], 'url': smart['url'], 'dl': smart['dl'], 'snapshot': smart}, **retirement)]
    source_path = ROOT / 'matches.js'
    source = source_path.read_text(encoding='utf-8')
    for key, rows in [('MATCHES', active), ('MATCH_RETIRED', retired)]:
        source, replacements = re.subn(r'window\.' + key + r' = \[[\s\S]*?\n\];', 'window.' + key + ' = ' + json.dumps(rows, ensure_ascii=False, indent=2) + ';', source, count=1)
        assert replacements == 1
    source = re.sub(r'window\.MATCH_UPDATED = "\d{4}-\d{2}-\d{2}";', 'window.MATCH_UPDATED = "' + TODAY + '";', source)
    source = re.sub(r'window\.MATCH_CHECKED = "\d{4}-\d{2}-\d{2}";', 'window.MATCH_CHECKED = "' + TODAY + '";', source)
    source = re.sub(r'window\.MATCH_NOTE = "[^"\n]*";', 'window.MATCH_NOTE = "10月23日重新请求全部精选、退役及官方入口。智慧城市报名与培养单位审核均已于今日中午12:00截止，依据今天重读的官方邀请函退役；保留5项线索、8项有据退役。作品10/25中午截止不等于报名延期。RoboMaster原截止年份仍待核实；受保护、框架页或超时不代表已确认开放。";', source)
    source = source.replace('本次维护：2026-10-20。按官网当届资格和报名日期再清退 2 项，累计 7 项有据退役。', '本次维护：2026-10-23。按今天重读的官方邀请函及精确中午截止退役智慧城市，累计 8 项有据退役。')
    source_path.write_text(source, encoding='utf-8')

    source_path = ROOT / 'competitions.js'; source = source_path.read_text(encoding='utf-8')
    changes = [
        ('中国研究生智慧城市技术与创意设计大赛（第十二届）', {'st': 'closed', 'reg': '报名及培养单位资格审核已于2026/10/23中午12:00截止；10/25交作品仅面向已报名团队'}, [INVITATION]),
        ('MathorCup 数学应用挑战赛·大数据竞赛（第七届）', {'st': 'closed', 'reg': '报名已于2026/10/23 12:00截止（研究生组单独评奖）'}, [MATHOR]),
        ('2026大学生“麟创杯”创新数学竞赛', {'reg': '2026/4/29 – 2026/10/25 20:00（研究生可报；50元资料费）', 'run': '2026/10/24 10:00 – 10/25 23:00；考试期间任选一小时，一人一次机会', 'fit': '适合愿意独立复习与答题的学生；先确认本校竞赛认定、50元费用和摄像头考试要求，不承诺加分或获奖。', 'help': '可协助赛前复习数学知识、讲解练习题。每人50元资料费且仅一次报名和考试机会；正式考试需摄像头与本人证件核验，禁止切屏和翻阅资料，必须独立完成。AI不得用于考试代答或实时外援，考试流程以组委会10/21指南为准。'}, ['https://m.saikr.com/vse/LCBCXSX', 'https://m.saikr.com/contest/notice_detail/49373'])
    ]
    for name, values, evidence in changes:
        start = source.rfind('{scope:', 0, source.index('n:"' + name + '"'))
        end = source.index('\n    {scope:', start)
        block = source[start:end]
        for key, value in values.items():
            block, replacements = re.subn(r'\b' + key + r':"[^"\n]*"', key + ':' + json.dumps(value, ensure_ascii=False), block)
            assert replacements == 1
        if name.startswith('MathorCup'):
            block = block.replace('10/23中午12:00截止。', '10/23中午12:00报名已截止，18:00初赛开始。')
        source = source[:start] + block + source[end:]
    source = re.sub(r'window\.COMP_UPDATED = "\d{4}-\d{2}-\d{2}";', 'window.COMP_UPDATED = "' + TODAY + '";', source)
    source = re.sub(r'window\.COMP_CHECKED = "\d{4}-\d{2}-\d{2}";', 'window.COMP_CHECKED = "' + TODAY + '";', source)
    source = re.sub(r'window\.COMP_CHECK_NOTE = "[^"\n]*";', 'window.COMP_CHECK_NOTE = "10月23日实际请求全部183项原入口与官方备用入口。官方原文确认智慧城市与MathorCup均于今日12:00报名截止，已关闭报名推荐；更新麟创杯10/24–25考试及10/25 20:00报名截止、独立答题规则。部分入口受保护、仅返框架或超时，年度旧赛程不冒充当届开放核验。";', source)
    source_path.write_text(source, encoding='utf-8')

    cqut_results = [r for r in report['sources'] if 'cqut.edu.cn' in r['url']]
    usable = sum(r.get('usableContent', False) for r in cqut_results)
    assert not usable, 'Usable CQUT pages require manual candidate review before a retained-source limitation note.'
    source_path = ROOT / 'cqut.js'; source = source_path.read_text(encoding='utf-8')
    count = len(before['notices'])
    note = f'10月23日实际请求全部{count}条已有通知及学校、部门、学院入口，共{len(cqut_results)}个去重URL；本轮均未取得可核查正文（访问保护、空挑战或超时）。完整保留其他维护者已更新至今日的{count}条通知及原日期；受阻不代表官网没有新通知，具体事务请核对原文。'
    source = re.sub(r'window\.CQUT_CHECKED = "\d{4}-\d{2}-\d{2}";', 'window.CQUT_CHECKED = "' + TODAY + '";', source)
    source = re.sub(r'window\.CQUT_CHECK_NOTE = "[^"\n]*";', 'window.CQUT_CHECK_NOTE = ' + json.dumps(note, ensure_ascii=False) + ';', source)
    source_path.write_text(source, encoding='utf-8')

    after = prior.datasets()
    assert [(r['n'], r['url']) for r in before['competitions']] == [(r['n'], r['url']) for r in after['competitions']]
    identity = lambda rows: sorted((r['n'], r['url'], r['dl'], r['school']) for r in rows)
    assert identity(before['matches'] + before['retired']) == identity(after['matches'] + after['retired'])
    assert after['matches'] == active and after['retired'] == retired
    assert before['notices'] == after['notices'] and before['contentUpdated'] == after['contentUpdated']
    robo_before = next(r for r in before['matches'] if 'RoboMaster' in r['n'])
    assert robo_before == next(r for r in after['matches'] if 'RoboMaster' in r['n'])
    assert robo_before['deadlineUnverified'] and robo_before['verificationNote']
    report['competitionChanges'] = [{'before': next(r for r in before['competitions'] if r['n'] == name), 'after': next(r for r in after['competitions'] if r['n'] == name), 'sourceEvidence': evidence} for name, values, evidence in changes]
    report['curatedDeadlineReview'] = [{'n': r['n'], 'url': r['url'], 'storedDeadline': r['dl'], 'snapshot': r, 'request': next(({'status': s.get('status'), 'usableContent': s.get('usableContent'), 'checkedAtTime': s.get('checkedAtTime'), 'error': s.get('error')} for s in report['sources'] if s['url'] == r['url']), None)} for r in before['matches']]
    report['curatedDeadlineReviewNotes'] = ['All six active and seven previously retired original URLs actually requested.', 'Smart-city registration and unit eligibility review are over at the exact independently verified noon cutoff; submission is separate.', 'RoboMaster complete original object retained with both uncertainty fields.', 'Request failures do not demonstrate expiry or absence of new notices.']
    report['cqut'] = {'beforeCount': count, 'afterCount': len(after['notices']), 'newNoticesByThisReview': 0, 'successfulContentUpdated': after['contentUpdated'], 'checkedAt': TODAY, 'attempts': len(cqut_results), 'usable': usable, 'limitation': 'Other maintainer updated content earlier today; every notice and original date preserved. Current unsuccessful probes cannot prove absence of new notices.'}
    report['identityCountsAfter'] = {'competitions': len(after['competitions']), 'activeMatches': len(after['matches']), 'retiredMatches': len(after['retired']), 'notices': len(after['notices'])}
    report['identityChecks'] = {'nationwideOriginalNamesAndURLsUnchanged': True, 'allThirteenCuratedOriginalNamesURLsDeadlinesSchoolsUnchanged': True, 'retiredObjectsPreviouslyPresentUnchanged': True, 'roboMasterCompleteOriginalObjectAndUncertaintyFieldsUnchanged': True, 'cqutAllNoticesAndContentDateUnchanged': True, 'smartCityBaselineDateUnchangedWithSeparateOfficialTime': True}
    report['contentDates'] = {'nationwide': TODAY, 'curated': TODAY, 'cqut': after['contentUpdated'], 'checkedAt': TODAY}
    report['summary']['supplementalAttempts'] = len(report['supplementalSources'])
    report['summary']['totalAttemptsIncludingSupplement'] = report['summary']['attempts'] + len(report['supplementalSources'])
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'summary': report['summary'], 'counts': report['identityCountsAfter'], 'retiredAtTime': retirement['retiredAtTime']}, ensure_ascii=False))


if __name__ == '__main__':
    if '--apply' in sys.argv:
        apply_verified()
    else:
        collect()
