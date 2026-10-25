"""Probe every existing BV after one public view sample actually became readable.

Never applies a partial new count to a uniformly dated historical snapshot.
Only minimal public model/title/view evidence is retained, not owner profile data.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import importlib.util
import json

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('learning25',ROOT/'_learning_review_2026-10-25.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
data=m.read_data()
videos={v['bvid']:v for s in data['forum'] for v in s['vids']}

def check(v):
    url='https://api.bilibili.com/x/web-interface/view?bvid='+v['bvid']
    body,result=m.get(url,12)
    result.update(bvid=v['bvid'],storedTitle=v['t'],storedPlay=v['play'])
    try:
        doc=json.loads(body);result.update(apiCode=doc.get('code'),apiMessage=doc.get('message'))
        record=doc.get('data') or {}
        if doc.get('code')==0 and isinstance(record,dict):
            result['officialData']={k:record.get(k) for k in ['bvid','title','duration']}
            result['officialData']['view']=(record.get('stat') or {}).get('view')
    except ValueError:
        pass
    official=result.get('officialData') or {}
    result['verified']=bool(result.get('http')==200 and result.get('curlExit')==0 and result.get('apiCode')==0
        and official.get('bvid')==v['bvid'] and isinstance(official.get('view'),int) and official['view']>=0)
    print(v['bvid'],result.get('http'),result['verified'],flush=True)
    return result

with ThreadPoolExecutor(max_workers=6) as pool: rows=list(pool.map(check,videos.values()))
initial=json.loads((ROOT/'_learning_review_2026-10-25.json').read_text(encoding='utf8'))
# One limited recheck only for a genuinely complete initial category sample that
# became unreadable in the full pass. Do not retry the remaining known WAFs.
initial_readable={x['bvid'] for x in initial['forumAccessChecks'] if x.get('http')==200 and x.get('curlExit')==0 and x.get('apiCode')==0 and isinstance(x.get('play'),int)}
retries=[]
for i,row in enumerate(rows):
    if row['bvid'] in initial_readable and not row['verified']:
        retry=check(videos[row['bvid']]);retries.append({'initialFullAttempt':row,'retry':retry})
        if retry['verified']:rows[i]=retry
verified=[r for r in rows if r['verified']]
report={'reviewDate':'2026-10-25','checkedAtUTC':datetime.now(timezone.utc).isoformat(),
        'scope':'Every retained unique BV; ordinary public official view API, no login/CAPTCHA/private cookies/proxy bypass.',
        'trigger':'Initial category sample BV1Az4y1v7Z8 returned a complete official API response with a changed view count.',
        'attempts':rows,'retryEvidence':retries,'summary':{'uniqueVideos':len(videos),'verified':len(verified),'unverified':len(videos)-len(verified),
                'completeAll':len(verified)==len(videos),'changedAmongVerified':sum(r['officialData']['view']!=r['storedPlay'] for r in verified)},
        'applied':False,'policy':'Incomplete source coverage does not certify a new full-snapshot capture date. An API 404/412 is not a dead-video verdict.'}
(ROOT/'_forum_plays_2026-10-25.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(report['summary']),flush=True)
