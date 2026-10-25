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
TODAY = '2026-10-25'
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
    (ROOT / '_content_review_2026-10-25.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report['summary'], ensure_ascii=False))


def apply_checked_notes():
    """Apply only check metadata after reviewing complete source attempts.

    Existing registration content and all identities stay byte-for-value equal.
    Nothing here treats a network failure or a future cutoff as retirement.
    """
    assert datetime.datetime.now(BEIJING).date().isoformat() == TODAY
    path = ROOT / '_content_review_2026-10-25.json'
    report = json.loads(path.read_text(encoding='utf-8'))
    before = prior.datasets()
    assert before['competitions'] == report['nationwideSnapshotsBefore']
    assert before['matches'] == report['curatedSnapshotsBefore']
    assert before['retired'] == report['retiredSnapshotsBefore']
    assert before['notices'] == report['cqutSnapshotsBefore']
    assert not report['noticeCandidates'], 'Read and verify possible new notices before applying a retained-content note.'
    assert len(before['competitions']) == 183
    assert len(before['matches']) == 5 and len(before['retired']) == 8
    assert len(before['notices']) == 322
    robo = next(m for m in before['matches'] if 'RoboMaster' in m['n'])
    assert robo['deadlineUnverified'] and robo['verificationNote']
    summary = report['summary']
    content_dates = {}
    for file, prefix in [('competitions.js', 'COMP'), ('matches.js', 'MATCH'), ('cqut.js', 'CQUT')]:
        source = (ROOT/file).read_text(encoding='utf-8')
        match = re.search(r'window\.'+prefix+r'_UPDATED = "([^"]+)";', source)
        content_dates[prefix] = match[1]
    notes = {
        'competitions.js': ('COMP_CHECKED', 'COMP_CHECK_NOTE',
            f'10月25日实际请求全部183项全国赛事、精选及退役原入口和官方备用源，共{summary["attempts"]}个去重URL、{summary["usable"]}份可核查正文。另读发布者原页确认麟创杯10/25 20:00报名截止、23:00考试结束，未提前关闭；AIPC今天仅第一场交作品，后两场仍按原文区分。未发现足以新增退役的官方证据，保留原内容日期；受阻和404不等于整项赛事停办。'),
        'matches.js': ('MATCH_CHECKED', 'MATCH_NOTE',
            '10月25日实际重新核查全部精选、退役及官方入口；保留5项线索、8项有据退役。智慧城市报名已于10/23 12:00截止，不因10/25交作品回流。RoboMaster旧截止年份仍待核实；网络失败不代表已确认开放。'),
        'cqut.js': ('CQUT_CHECKED', 'CQUT_CHECK_NOTE',
            f'10月25日实际请求全部322条已有通知与学校、部门、学院入口，共{summary["cqutAttempts"]}个去重URL。'+
            (f'取得{summary["cqutUsable"]}份可核查正文，其余受访问保护、空响应或超时；' if summary['cqutUsable'] else '本轮受访问保护、空响应或超时，未取得可核查正文；')+
            '保留既有322条通知和原单篇日期，最新仍为10/23。受阻不代表官网没有新通知，办理事项及截止安排请以官网原文为准。')
    }
    for file, (checked, key, note) in notes.items():
        path_source = ROOT/file
        source = path_source.read_text(encoding='utf-8')
        for field, value in [(checked, TODAY), (key, note)]:
            source, n = re.subn(r'window\.'+field+r' = "[^"\n]*";',
                lambda _: 'window.'+field+' = '+json.dumps(value, ensure_ascii=False)+';', source, count=1)
            assert n == 1, field
        path_source.write_text(source, encoding='utf-8')
    after = prior.datasets()
    assert after == before, 'All source records, identities, eligibility flags and original dates must remain identical.'
    for file, prefix in [('competitions.js', 'COMP'), ('matches.js', 'MATCH'), ('cqut.js', 'CQUT')]:
        assert re.search(r'window\.'+prefix+r'_UPDATED = "([^"]+)";', (ROOT/file).read_text(encoding='utf-8'))[1] == content_dates[prefix]
    report['supplementalOfficialReview'] = [
        {'url': 'https://m.saikr.com/vse/LCBCXSX', 'checkedAt': TODAY,
         'method': 'Independent current organizer-published web page read; current HTTP collection retained separately.',
         'finding': 'Official registration closes October25 at20:00; the October24–25 exam ends at23:00. Checked before the registration cutoff; no early closed status applied.',
         'registrationDeadline': '2026-10-25T20:00:00+08:00', 'examEnd': '2026-10-25T23:00:00+08:00'},
        {'url': 'https://m.saikr.com/vse/AIPC26', 'checkedAt': TODAY,
         'method': 'Independent current organizer-published web page read; list/header and full stage descriptions compared.',
         'finding': 'The October25 header describes round1; body explicitly permits registration through December27 and separately lists October25, November29 and December27 submissions, each at23:59. No total-event retirement.'},
        {'url': 'https://www.cqut.edu.cn/tzgg.htm', 'checkedAt': TODAY,
         'method': 'Independent official web open', 'status': 'unavailable',
         'finding': 'Web tool could not access the page; failure does not show absence of new notices.'},
        {'url': 'https://yjsy.cqut.edu.cn/', 'checkedAt': TODAY,
         'method': 'Independent official web open', 'status': 'empty',
         'finding': 'No article text was returned; retained current data and dates.'}
    ]
    report['appliedCheckNotes'] = True
    report['additionalRetirements'] = []
    report['newNotices'] = []
    report['contentDatesPreserved'] = content_dates
    report['identityChecks'] = {'all183NationwideCompleteObjectsUnchanged': True,
        'all5ActiveCompleteObjectsUnchanged': True, 'all8RetiredCompleteObjectsUnchanged': True,
        'roboMasterUncertaintyFieldsUnchanged': True, 'all322NoticesAndDatesUnchanged': True}
    report['scopeLimitations'] = ['Failed or empty requests cannot certify that no new notices or revised deadlines exist.',
        'Supplemental search results without a current readable official article were not accepted as new notices.',
        'No automatic retirement routines from earlier dated collectors were called.']
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'sourceSummary': summary, 'contentDatesPreserved': content_dates,
        'active': len(after['matches']), 'retired': len(after['retired']), 'notices': len(after['notices'])}, ensure_ascii=False))


if __name__ == "__main__":
    if '--apply-checked' in sys.argv:
        apply_checked_notes()
    else:
        collect()
