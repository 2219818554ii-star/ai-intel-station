"""One-off, dated release verification requested by the owner on November 5.

Collects public primary sources into an explicit external evidence directory.
No dataset is modified by this collector. No login, secrets, proxy changes,
model inference, retirement decisions or private cloud access are involved.
"""
import concurrent.futures as cf
import datetime as dt
import hashlib
import html
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parent
DAY = '2026-11-05'
TZ = dt.timezone(dt.timedelta(hours=8))
MODE, OUTPUT = sys.argv[1], Path(sys.argv[2])
OUTPUT.mkdir(parents=True, exist_ok=True)
assert dt.datetime.now(TZ).date().isoformat() == DAY

def now():
    return dt.datetime.now(TZ).isoformat(timespec='seconds')

def data():
    code = "const fs=require('fs'),vm=require('vm');let s={window:{}};for(const f of ['cqut.js','competitions.js','matches.js','ted.js','forum.js','funds.js','rank.js'])vm.runInNewContext(fs.readFileSync(f,'utf8'),s);process.stdout.write(JSON.stringify(s.window));"
    return json.loads(subprocess.check_output(['node','-e',code],cwd=ROOT))

def plain(text):
    text = re.sub(r'<(script|style)\b[^>]*>[\s\S]*?</\1>', '', text, flags=re.I)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', text))).strip()

def get(url, seconds=12):
    started = now()
    args = ['curl.exe','-L','-sS','--compressed','--connect-timeout',str(min(15,max(6,seconds//3))),'--max-time',str(seconds),
            '-A','Mozilla/5.0','-H','Referer: '+('https://www.bilibili.com/' if 'bilibili.com' in url else url),
            '-w','\n@@RESULT@@%{json}',url]
    row = {'url':url,'checkedAt':DAY,'checkedAtTime':started}
    raw = b''
    try:
        proc = subprocess.run(args,capture_output=True,timeout=seconds+5)
        raw, separator, tail = proc.stdout.rpartition(b'\n@@RESULT@@')
        meta = json.loads(tail) if separator else {}
        status = meta.get('http_code') or None
        row.update(status=status,http=status,curlExit=proc.returncode,finalURL=meta.get('url_effective',url),
                   complete=proc.returncode==0 and status==200,error=proc.stderr.decode('utf8','replace').strip()[:350] or None)
    except (subprocess.TimeoutExpired,ValueError) as error:
        row.update(status=None,http=None,curlExit=-1,complete=False,error=str(error)[:350])
    row.update(completedAt=now(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
    cache = OUTPUT / (hashlib.sha256(url.encode()).hexdigest()+'.'+row['sha256']+'.raw')
    cache.write_bytes(raw)
    text = raw.decode('utf-8','replace')
    if text.count('\ufffd') > 5:
        alt = raw.decode('gb18030','replace')
        if alt.count('\ufffd') < text.count('\ufffd'): text=alt
    title = re.search(r'<title[^>]*>([\s\S]*?)</title>',text,re.I)
    clean = plain(text)
    row['title'] = plain(title[1]) if title else None
    row['usableContent'] = bool(row['complete'] and len(clean)>300 and not re.search(r'just a moment|verify you are human|checking your browser|访问验证|人机验证',clean[:1500],re.I))
    if not row['usableContent']:
        row['limitation']='Incomplete, protected, empty or non-content response; no dead-link or expiry conclusion.'
    return text,row

def save(name, value):
    (OUTPUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def probes(w):
    urls=['https://artificialanalysis.ai/leaderboards/models','https://artificialanalysis.ai/changelog',
          'https://yjsy.cqut.edu.cn/info/1041/5405.htm',
          'https://api.bilibili.com/x/web-interface/view?bvid=BV1Az4y1v7Z8',
          w['TED'][0]['url']]
    urls += ['https://fund.eastmoney.com/pingzhongdata/'+f['code']+'.js' for f in w['FUNDS_HOLD']]
    urls += [m['url'] for m in w['MATCHES']]
    with cf.ThreadPoolExecutor(max_workers=6) as pool:
        rows=list(pool.map(lambda u:get(u,22)[1],urls))
    save('probes.json',rows)
    print(json.dumps(rows,ensure_ascii=True),flush=True)

def forum(w):
    videos={v['bvid']:v for s in w['FORUM_SERIES'] for v in s['vids']}
    def one(v):
        body,row=get('https://api.bilibili.com/x/web-interface/view?bvid='+v['bvid'])
        row.update(bvid=v['bvid'],storedTitle=v['t'],storedPlay=v['play'])
        try:
            doc=json.loads(body);row.update(apiCode=doc.get('code'),apiMessage=doc.get('message'))
            d=doc.get('data') or {}
            if doc.get('code')==0:
                row['officialData']={k:d.get(k) for k in ('bvid','title','duration')}
                row['officialData']['view']=(d.get('stat') or {}).get('view')
        except (ValueError,AttributeError):pass
        d=row.get('officialData') or {}
        row['verified']=bool(row['complete'] and row.get('apiCode')==0 and d.get('bvid')==v['bvid'] and d.get('title')==v['t'] and isinstance(d.get('view'),int) and d['view']>=0)
        print('BV',v['bvid'],row['http'],row['verified'],flush=True)
        return row
    started=now()
    with cf.ThreadPoolExecutor(max_workers=6) as pool:rows=list(pool.map(one,videos.values()))
    report={'reviewDate':DAY,'attemptedAt':started,'completedAt':now(),'scope':'All 194 retained unique BVs; full ordinary official view responses, relevant returned identity/title/count fields retained with raw-body SHA256. No playback or simultaneous-full-snapshot claim.','attempts':rows,'summary':{'uniqueVideos':len(videos),'verified':sum(r['verified'] for r in rows),'unverified':sum(not r['verified'] for r in rows)},'applied':False}
    save('_forum_plays_'+DAY+'.json',report)
    print(json.dumps(report['summary']),flush=True)

def ted_one(t,seconds=18):
    body,row=get(t['url'],seconds)
    row.update(title=t['en'],previousViews=t.get('views'))
    if row['complete']:
        title=re.search(r'<h1[^>]*>(.*?)</h1>',body,re.S)
        cover=re.search(r'property="og:image"\s+content="([^"]+)"',body)
        plays=re.search(r'([\d,]+)(?:<!--\s*-->\s*|\s+)plays\b',body)
        row.update(officialTitle=plain(title[1]) if title else None,
                   cover=html.unescape(cover[1]).split('?')[0] if cover else None,
                   views=int(plays[1].replace(',','')) if plays else None,
                   viewsEvidence=plays[0] if plays else None)
    print('TED',row['http'],row.get('officialTitle')==t['en'],flush=True)
    return row

def ted(w):
    started=now()
    with cf.ThreadPoolExecutor(max_workers=5) as pool:rows=list(pool.map(ted_one,w['TED']))
    report={'reviewDate':DAY,'attemptedAt':started,'completedAt':now(),'ted':rows,'scope':'All 40 official TED talk pages. Returned title and publicly displayed cumulative plays only; no inferred publication date or exact viewing progress.','applied':False}
    save('_learning_review_'+DAY+'.json',report)
    print(json.dumps({'talks':len(rows),'complete':sum(r['complete'] for r in rows),'knownPlays':sum(r.get('views') is not None for r in rows)}),flush=True)

def retry(w):
    report=json.loads((OUTPUT/('_learning_review_'+DAY+'.json')).read_text(encoding='utf8'))
    previous={r['url']:r for r in report['ted']}
    needed=[t for t in w['TED'] if not previous[t['url']]['complete'] or previous[t['url']].get('officialTitle')!=t['en'] or (t.get('views') is not None and previous[t['url']].get('views') is None)]
    with cf.ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(lambda t:ted_one(t,45),needed))
    replacement={r['url']:r for r in rows}
    report.setdefault('initialTedAttempts',report['ted'])
    report.setdefault('retryRounds',[]).append({'completedAt':now(),'attempts':rows})
    report['ted']=[replacement.get(r['url'],r) for r in report['ted']]
    report['retryCompletedAt']=now()
    report['retryCount']=len(rows)
    save('_learning_review_'+DAY+'.json',report)
    print(json.dumps({'retried':len(rows),'complete':sum(r['complete'] for r in report['ted']),'knownPlays':sum(r.get('views') is not None for r in report['ted'])}),flush=True)

def supplemental(w):
    urls=['https://artificialanalysis.ai/leaderboards/models','https://artificialanalysis.ai/changelog',
          'https://fund.eastmoney.com/pingzhongdata/016452.js','https://yjsy.cqut.edu.cn/info/1041/5405.htm']
    with cf.ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(lambda u:get(u,85)[1],urls))
    save('supplemental.json',rows)
    print(json.dumps(rows,ensure_ascii=True),flush=True)

def learning(w):
    source=(ROOT/'index.src.html').read_text(encoding='utf8')
    section=source[source.index('id="view-learn"'):source.index('id="view-ted"')]
    urls=list(dict.fromkeys(html.unescape(u) for u in re.findall(r'<a class="rsrc" href="([^"]+)"',section)))
    with cf.ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(lambda u:get(u,25)[1],urls))
    save('learning-entries.json',{'reviewDate':DAY,'attempts':rows,'scope':'Every existing official AI learning entry; response access only, no course, price or playback certification.'})
    print(json.dumps({'entries':len(rows),'complete':sum(r['complete'] for r in rows)}),flush=True)

def campus(w):
    urls=list(dict.fromkeys([r['url'] for r in w['CQUT_NOTICES']]+[s['u'] for group in w['CQUT_SOURCES'].values() for s in group]))
    report={'reviewedAt':DAY,'attemptedAt':now(),'cqutSnapshotsBefore':w['CQUT_NOTICES'],
            'cqutContentUpdatedBefore':w['CQUT_UPDATED'],'sourcesConfiguredBefore':w['CQUT_SOURCES']}
    save('campus-recheck-before.json',report)
    with cf.ThreadPoolExecutor(max_workers=12) as pool:rows=list(pool.map(lambda u:get(u,10)[1],urls))
    report.update(completedAt=now(),sources=rows)
    save('campus-recheck.json',report)
    print(json.dumps({'requiredURLs':len(urls),'attempts':len(rows),'usable':sum(r['usableContent'] for r in rows)}),flush=True)

def content(w):
    urls=[s['u'] for group in w['CQUT_SOURCES'].values() for s in group]
    urls += [r['url'] for r in w['COMP']+w['MATCHES']+w['MATCH_RETIRED']+w['CQUT_NOTICES']]
    urls += [r['alt'] for r in w['COMP']+w['MATCHES'] if r.get('alt')]
    urls += [s['u'] for s in w['MATCH_SOURCES']]
    urls += ['https://www.cqut.edu.cn/tzgg.htm','https://www.cqut.edu.cn/tzgg/xygtz.htm','https://yjsy.cqut.edu.cn/']
    urls=list(dict.fromkeys(urls))
    def one(url):
        body,row=get(url,8)
        if row['usableContent']:
            row['links']=[{'url':urljoin(row.get('finalURL',url),m[0]),'title':plain(m[1])[:160]} for m in re.findall(r'<a\b[^>]*href=[\"\']([^\"\']+)[\"\'][^>]*>([\s\S]*?)</a>',body,re.I) if '/info/' in m[0] or 'wbnewsid=' in m[0]]
        return row
    started=now()
    with cf.ThreadPoolExecutor(max_workers=16) as pool:rows=list(pool.map(one,urls))
    school=[r for r in rows if urlsplit(r['url']).hostname=='cqut.edu.cn' or str(urlsplit(r['url']).hostname).endswith('.cqut.edu.cn')]
    counts={}
    for r in rows:
        key='None' if r['status'] is None else str(r['status']);counts[key]=counts.get(key,0)+1
    report={'reviewedAt':DAY,'attemptedAt':started,'completedAt':now(),'scope':'Every retained nationwide identity, active/retired curated original, every existing campus notice and all configured official source portals/alternates. Full responses cached outside the website; no automatic changes or retirements.','sources':rows,'identityCountsBefore':{'competitions':len(w['COMP']),'activeMatches':len(w['MATCHES']),'retiredMatches':len(w['MATCH_RETIRED']),'notices':len(w['CQUT_NOTICES'])},'summary':{'attempts':len(rows),'usable':sum(r['usableContent'] for r in rows),'cqutAttempts':len(school),'cqutUsable':sum(r['usableContent'] for r in school),'statusCounts':counts},'applied':False}
    save('_content_review_'+DAY+'.json',report)
    print(json.dumps(report['summary']),flush=True)

if __name__=='__main__':
    funcs={'probes':probes,'forum':forum,'ted':ted,'content':content,'retry':retry,'supplemental':supplemental,'learning':learning,'campus':campus}
    funcs[MODE](data())
