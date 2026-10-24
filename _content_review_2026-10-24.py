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
TODAY = '2026-10-24'
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
    (ROOT / '_content_review_2026-10-24.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report['summary'], ensure_ascii=False))


if __name__ == "__main__":
    collect()
