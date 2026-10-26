from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import importlib.util
import json
import re
import sys
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("learning",ROOT/"_learning_review_2026-10-26.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
data=m.read_data()
samples=[next(s for s in data["forum"] if s["cat"]==cat)["vids"][0] for cat in dict.fromkeys(s["cat"] for s in data["forum"])]
urls=[]
for v in samples:
    urls.extend([("official-public-stat-api",v,"https://api.bilibili.com/x/web-interface/archive/stat?bvid="+v["bvid"]),("official-mobile-playback",v,"https://m.bilibili.com/video/"+v["bvid"])])
v=samples[0]
urls.extend([("official-public-pages-api",v,"https://api.bilibili.com/x/player/pagelist?bvid="+v["bvid"]),("official-public-detail-api",v,"https://api.bilibili.com/x/web-interface/view/detail?bvid="+v["bvid"])])
def check(row):
    kind,v,url=row
    body,result=m.get(url,15)
    result.update(kind=kind,bvid=v["bvid"],storedTitle=v["t"],storedPlay=v["play"])
    try:
        d=json.loads(body)
        result.update(apiCode=d.get("code"),apiMessage=d.get("message"))
        if d.get("code")==0:
            result["officialData"]=[{k:p[k] for k in ["cid","page","part","duration"] if k in p} for p in d["data"]] if isinstance(d.get("data"),list) else d.get("data")
    except ValueError:pass
    title=re.search(r"<title[^>]*>(.*?)</title>",body,re.S|re.I)
    result["pageTitle"]=title[1] if title else None
    result["responseExcerpt"]=re.sub(r"<[^>]+>"," ",body)[:600]
    print(kind,result["http"],v["bvid"],flush=True)
    return result
if "--all-pages" in sys.argv:
    unique={v["bvid"]:v for s in data["forum"] for v in s["vids"]}
    urls=[("official-public-pages-api",v,"https://api.bilibili.com/x/player/pagelist?bvid="+v["bvid"]) for v in unique.values()]
with ThreadPoolExecutor(max_workers=6) as pool:rows=list(pool.map(check,urls))
report={"reviewDate":m.DATE,"checkedAtUTC":datetime.now(timezone.utc).isoformat(),"scope":"Ordinary public official stat, mobile playback, page-list, and detail endpoints. No login, CAPTCHA solving, private cookies, or alternate-domain proxies.","attempts":rows}
(ROOT/("_forum_metadata_2026-10-26.json" if "--all-pages" in sys.argv else "_forum_review_2026-10-26.json")).write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

if "--all-pages" in sys.argv:
    existing={v["bvid"]:v for s in data["forum"] for v in s["vids"]}
    changes=[]
    accepted=[]
    for row in rows:
        pages=row.get("officialData")
        if row.get("http")!=200 or row.get("curlExit")!=0 or row.get("apiCode")!=0 or not isinstance(pages,list) or not pages: continue
        assert [p.get("page") for p in pages]==list(range(1,len(pages)+1))
        assert len({p.get("cid") for p in pages})==len(pages)
        assert all(isinstance(p.get("duration"),int) and p["duration"]>0 for p in pages)
        seconds=sum(p["duration"] for p in pages)
        new={"pageCount":len(pages),"durationSeconds":seconds,"dur":str(seconds//60)+":"+str(seconds%60).zfill(2)}
        old={k:existing[row["bvid"]].get(k) for k in new}
        accepted.append(row["bvid"])
        if new!=old: changes.append({"bvid":row["bvid"],"old":old,"new":new})
    report["comparison"]={"uniqueVideos":len(existing),"completeResponses":len(accepted),"unverified":len(existing)-len(accepted),"metadataChanges":changes,"playbackCountsUnchanged":True,"applied":False,"policy":"Independent check report only when metadata unchanged; retain previous content update and per-video metadata check dates. Never treat page-list success as cumulative-play or full-playback proof."}
    (ROOT/"_forum_metadata_2026-10-26.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report["comparison"],ensure_ascii=False),flush=True)
