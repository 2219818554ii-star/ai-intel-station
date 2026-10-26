"""Bounded, official-source metadata audit. Never infers video availability from WAF responses."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import html
import json
import re
import subprocess
import sys
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parent
NODE = r"C:/Users/22198/.workbuddy/binaries/node/versions/22.22.2-6/node.exe"
DATE = "2026-10-26"
OUT = ROOT / ("_learning_review_" + DATE + ".json")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"


def get(url, seconds=18):
    try:
        p = subprocess.run(["curl.exe", "-L", "-sS", "--compressed", "--max-time", str(seconds), "-A", UA,
                            "-H", "Referer: " + ("https://www.bilibili.com/" if "bilibili" in url else url),
                            "-w", '\n@@RESULT@@%{json}', url], capture_output=True, timeout=seconds + 4)
        body, _, tail = p.stdout.decode("utf-8", "replace").rpartition("\n@@RESULT@@")
        result = json.loads(tail) if tail else {}
        effective = result.get("url_effective", url)
        parsed = urlsplit(effective)
        if parsed.hostname == "accounts.google.com":
            effective = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))
        return body, {"url": url, "http": result.get("http_code", 0), "finalURL": effective,
                      "curlExit": p.returncode, "bytes": result.get("size_download", 0),
                      "error": p.stderr.decode("utf-8", "replace").strip()[:300]}
    except (subprocess.TimeoutExpired, ValueError) as exc:
        return "", {"url": url, "http": 0, "curlExit": -1, "error": str(exc)[:300]}


def read_data():
    script = "const fs=require('fs'),vm=require('vm');let c={window:{}};vm.createContext(c);for(let f of ['ted.js','forum.js'])vm.runInContext(fs.readFileSync(f,'utf8'),c);process.stdout.write(JSON.stringify({ted:c.window.TED,forum:c.window.FORUM_SERIES}));"
    return json.loads(subprocess.check_output([NODE, "-e", script], cwd=ROOT))


def audit_ted(talk):
    body, result = get(talk["url"])
    result.update(title=talk["en"], previousViews=talk.get("views"))
    if result["http"] == 200 and result["curlExit"] == 0:
        title = re.search(r'<h1[^>]*>(.*?)</h1>', body, re.S)
        cover = re.search(r'property="og:image"\s+content="([^"]+)"', body)
        # TED now also emits plain "39,157,124 plays" text. React's empty
        # comment separator is optional; require the visible plays label.
        plays = re.search(r'([\d,]+)(?:<!--\s*-->\s*|\s+)plays\b', body)
        result.update(officialTitle=html.unescape(re.sub(r"<[^>]+>", "", title[1])).strip() if title else None,
                      cover=html.unescape(cover[1]).split("?")[0] if cover else None,
                      views=int(plays[1].replace(",", "")) if plays else None,
                      viewsEvidence=plays[0] if plays else None)
    print("TED", result["http"], talk["en"][:45], flush=True)
    return result


def audit_link(row):
    body, result = get(row["url"], 12)
    title = re.search(r'<title[^>]*>(.*?)</title>', body, re.S | re.I)
    result.update(title=row["title"], pageTitle=html.unescape(re.sub(r"<[^>]+>", "", title[1])).strip()[:240] if title else None)
    # WAF/login/network failures are not dead links, even if the numeric response is 200.
    result["classification"] = "http-accessible" if result["http"] == 200 and result["curlExit"] == 0 else "unverified-access"
    if result["classification"] == "http-accessible":
        if urlsplit(result.get("finalURL", "")).hostname == "accounts.google.com":
            result["classification"] = "login-required"
        elif re.search(r"just a moment|access denied|verify you are human|security verification|验证码|安全验证|访问受限", result.get("pageTitle") or "", re.I):
            result["classification"] = "access-protected"
    print("LEARN", result["http"], row["title"][:38], flush=True)
    return result


def main():
    data = read_data()
    with ThreadPoolExecutor(max_workers=4) as pool:
        ted = list(pool.map(audit_ted, data["ted"]))
    bili = []
    samples = [next(s for s in data["forum"] if s["cat"] == cat)["vids"][0] for cat in dict.fromkeys(s["cat"] for s in data["forum"])]
    for video in samples:
        url = "https://api.bilibili.com/x/web-interface/view?bvid=" + video["bvid"]
        body, result = get(url, 12)
        result.update(bvid=video["bvid"], title=video["t"], previousPlay=video.get("play"))
        try:
            response = json.loads(body)
            result.update(apiCode=response.get("code"), apiMessage=response.get("message"))
            if response.get("code") == 0:
                result.update(officialTitle=response["data"].get("title"), play=response["data"].get("stat", {}).get("view"))
        except ValueError:
            pass
        bili.append(result)
    body, playback = get("https://www.bilibili.com/video/" + samples[0]["bvid"], 12)
    bili.append(playback)
    src = (ROOT / "index.src.html").read_text(encoding="utf-8")
    learn = src[src.index('id="view-learn"'):src.index('id="view-ted"')]
    links = [{"url": html.unescape(url), "title": html.unescape(re.sub(r'<[^>]+>', '', title)).strip()}
             for url, title in re.findall(r'<a class="rsrc" href="([^"]+)"[^>]*>(.*?)</a>', learn, re.S)]
    unique = list({r["url"]: r for r in links}.values())
    with ThreadPoolExecutor(max_workers=4) as pool:
        learning = list(pool.map(audit_link, unique))
    result = {"reviewDate": DATE, "checkedAtUTC": datetime.now(timezone.utc).isoformat(),
              "ted": ted, "forumAccessChecks": bili,
              "forumSeries": len(data["forum"]), "forumVideos": sum(len(s["vids"]) for s in data["forum"]),
              "learningResourceChecks": learning,
              "scope": "TED: all 40 official talk pages. Forum: one API sample from each of the three categories and one ordinary playback page; failures do not imply other videos are dead. Learning: every distinct existing resource link; HTTP success is not a full course or pricing validation.",
              "applied": False}
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ted200": sum(r["http"] == 200 and r["curlExit"] == 0 for r in ted),
                      "tedViews": sum(r.get("views") is not None for r in ted),
                      "forum": bili, "learningLinks": len(learning)}, ensure_ascii=False), flush=True)


def retry_incomplete():
    review = json.loads(OUT.read_text(encoding="utf-8"))
    previous = {r["url"]: r for r in review["ted"]}
    failed = [t for t in read_data()["ted"] if previous[t["url"]]["http"] != 200 or previous[t["url"]]["curlExit"] != 0
              or previous[t["url"]].get("officialTitle") != t["en"]
              or (t.get("views") is not None and previous[t["url"]].get("views") is None)]
    with ThreadPoolExecutor(max_workers=3) as pool:
        retried = {r["url"]: r for r in pool.map(audit_ted, failed)}
    review["initialTedAttempt"] = review["ted"]
    review["ted"] = [retried.get(r["url"], r) for r in review["ted"]]
    review["retryCount"] = len(failed)
    review["tedRetryReason"] = "One bounded retry of incomplete HTTP/curl, title, or previously disclosed-play responses. Both known official markup variants remain supported; never replace a known count with an incomplete response."
    review["retryCheckedAtUTC"] = datetime.now(timezone.utc).isoformat()
    OUT.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"completeTedResponses": sum(r["http"] == 200 and r["curlExit"] == 0 for r in review["ted"]),
                      "viewsExposed": sum(r.get("views") is not None for r in review["ted"])}), flush=True)


def retry_resources():
    """One bounded retry for network-incomplete entries; do not hammer known WAFs."""
    review = json.loads(OUT.read_text(encoding="utf-8"))
    retry = [r for r in review["learningResourceChecks"] if r.get("http") == 0 or r.get("curlExit") not in (0, None)]
    with ThreadPoolExecutor(max_workers=3) as pool:
        review["learningResourceRetries"] = list(pool.map(audit_link, retry))
    review["resourceRetryCheckedAtUTC"] = datetime.now(timezone.utc).isoformat()
    OUT.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"resourceRetries": len(retry), "completeRetries": sum(r["http"] == 200 and r["curlExit"] == 0 for r in review["learningResourceRetries"])}), flush=True)


def apply_reviewed():
    """Apply exact TED responses and individually proved public video counters.

    This daily review independently attempts all 194 official BV statistics.
    Only complete responses with returned BV and title matches may update plays.
    Those records get their own capture date; unverified records keep the old
    per-video or global snapshot date and all other content/metadata intact.
    """
    review=json.loads(OUT.read_text(encoding="utf-8"))
    before=read_data()
    fetched={r["url"]:r for r in review["ted"]}
    assert len(fetched)==len(before["ted"])==40
    assert all(r["http"]==200 and r["curlExit"]==0 and r.get("officialTitle")==r["title"] for r in fetched.values())
    assert all(fetched[t["url"]].get("views") is not None for t in before["ted"] if t.get("views") is not None)
    assert all(isinstance(r.get("cover"),str) and r["cover"].startswith("https://pi.tedcdn.com/") for r in fetched.values())
    metadata_path=ROOT/("_forum_metadata_"+DATE+".json")
    metadata=json.loads(metadata_path.read_text(encoding="utf8"))
    assert metadata["reviewDate"]==DATE and not metadata["comparison"]["metadataChanges"]
    plays_path=ROOT/("_forum_plays_"+DATE+".json")
    plays=json.loads(plays_path.read_text(encoding="utf8"))
    assert plays["reviewDate"]==DATE and not plays.get("applied")
    videos=[v for series in before["forum"] for v in series["vids"]]
    unique={v["bvid"]:v for v in videos}
    assert len(unique)==194 and len(plays["attempts"])==194
    assert set(unique)=={r["bvid"] for r in plays["attempts"]}
    accepted={}
    for row in plays["attempts"]:
        if not row.get("verified"):continue
        official=row.get("officialData") or {}
        assert row["http"]==200 and row["curlExit"]==0 and row["apiCode"]==0
        assert official.get("bvid")==row["bvid"] and official.get("title")==row["storedTitle"]==unique[row["bvid"]]["t"]
        assert isinstance(official.get("view"),int) and official["view"]>=0
        accepted[row["bvid"]]=row
    assert len(accepted)==plays["summary"]["verified"]
    changed_bv={bv:r for bv,r in accepted.items() if r["officialData"]["view"]!=unique[bv]["play"]}
    ted_source=(ROOT/"ted.js").read_text(encoding="utf8")
    def ted_row(match):
        current=fetched[match[1]]
        return 'url:'+json.dumps(match[1])+', cover:'+json.dumps(current["cover"])+', views:'+json.dumps(current.get("views"))+'}'+match[2]
    ted_source,count=re.subn(r'url:"([^"]+)",\s*cover:(?:"[^"]*"|null),\s*views:(?:\d+|null)\}(,?)',ted_row,ted_source)
    assert count==40
    ted_changes=[{"url":t["url"],"beforeViews":t.get("views"),"views":fetched[t["url"]].get("views"),"coverChanged":t.get("cover")!=fetched[t["url"]].get("cover")} for t in before["ted"] if t.get("views")!=fetched[t["url"]].get("views") or t.get("cover")!=fetched[t["url"]].get("cover")]
    if ted_changes:ted_source=re.sub(r'window.TED_UPDATED = "[\d-]+";', 'window.TED_UPDATED = "'+DATE+'";',ted_source)
    for key in ["TED_VIEWS_CAPTURED_AT","TED_CHECKED"]:
        ted_source=re.sub(r'window\.'+key+r' = "[\d-]+";', 'window.'+key+' = "'+DATE+'";',ted_source)
    ted_source=re.sub(r'\d{4}-\d{2}-\d{2} 全量复核40个官网页面并刷新封面图/官网播放量',DATE+' 全量复核40个官网页面并刷新封面图/官网播放量',ted_source)
    ted_source=re.sub(r'\d{4}-\d{2}-\d{2} 已逐条完整获取，40个页面均返回200',DATE+' 已逐条完整获取，40个页面均返回200',ted_source)
    ted_source=re.sub(r'\d{4}-\d{2}-\d{2} 抓取；null=该条页面未暴露播放数',DATE+' 抓取；null=该条页面未暴露播放数',ted_source)
    forum_source=(ROOT/"forum.js").read_text(encoding="utf8")
    rows_changed=[]
    def forum_row(match):
        row=json.loads(match[0]);proof=changed_bv.get(row["bvid"])
        if not proof:return match[0]
        before_play=row["play"];row["play"]=proof["officialData"]["view"];row["playCapturedAt"]=DATE
        rows_changed.append({"bvid":row["bvid"],"title":row["t"],"beforePlay":before_play,"play":row["play"],"playCapturedAt":DATE})
        return json.dumps(row,ensure_ascii=False,separators=(',',':'))
    forum_source,count=re.subn(r'\{[^\n{}]*"bvid"[^\n{}]*\}',forum_row,forum_source)
    assert count==len(videos)==205
    assert {r["bvid"] for r in rows_changed}==set(changed_bv)
    assert all(next(iter(set(v["play"] for v in videos if v["bvid"]==bv)))==proof["storedPlay"] for bv,proof in changed_bv.items())
    for key in (["FORUM_UPDATED","FORUM_CHECKED"] if changed_bv else ["FORUM_CHECKED"]):
        forum_source=re.sub(r'window\.'+key+r' = "[\d-]+";', 'window.'+key+' = "'+DATE+'";',forum_source)
    dated_label=str(int(DATE[5:7]))+'月'+str(int(DATE[8:10]))+'日'
    retained_dates=sorted({v.get('playCapturedAt','2026-10-14') for v in videos if v['bvid'] not in changed_bv})
    note=dated_label+'实际尝试全部194个独立BV的官方view统计，'+str(len(accepted))+'个取得完整且BV/标题一致的计数，其中'+str(len(changed_bv))+'个发生变化（涉及'+str(len(rows_changed))+'条收录），变化项逐条标注采集'+dated_label+'；其余保留原逐条日期或历史快照（'+ '、'.join(retained_dates)+'），不能当作全量已刷新。另pagelist完整核实'+str(metadata["comparison"]["completeResponses"])+'个，分P与总时长未发现变化，元数据日期仍10月22日。分P核验不等于全片可播。'
    forum_source=re.sub(r'window.FORUM_REVIEW_NOTE = "[^"\n]*";',lambda _:'window.FORUM_REVIEW_NOTE = '+json.dumps(note,ensure_ascii=False)+';',forum_source)
    forum_source=re.sub(r'本次联网记录见 _learning_review_\d{4}-\d{2}-\d{2}\.json','本次联网记录见 _learning_review_'+DATE+'.json',forum_source)
    forum_source=forum_source.replace('   整理证据见','   '+DATE+'：全量尝试194个BV；'+str(len(changed_bv))+'个已核实播放变化单列采集日期，其他项保留原逐条日期，元数据日期不变。\n   整理证据见',1)
    assert 'window.FORUM_PLAY_CAPTURED_AT = "2026-10-14";' in forum_source
    # Commit the two scoped data sources only after all independent evidence guards.
    (ROOT/"ted.js").write_text(ted_source,encoding="utf8")
    (ROOT/"forum.js").write_text(forum_source,encoding="utf8")
    after=read_data()
    assert len(after["ted"])==len(before["ted"])==40
    for a,b in zip(before["ted"],after["ted"]):
        assert {k:v for k,v in a.items() if k not in ['views','cover']}=={k:v for k,v in b.items() if k not in ['views','cover']}
        assert b["views"]==fetched[b["url"]]["views"] and b["cover"]==fetched[b["url"]]["cover"]
    for a_series,b_series in zip(before["forum"],after["forum"]):
        assert {k:v for k,v in a_series.items() if k!='vids'}=={k:v for k,v in b_series.items() if k!='vids'}
        for a,b in zip(a_series['vids'],b_series['vids']):
            if a['bvid'] not in changed_bv:assert a==b
            else:
                assert b['play']==changed_bv[a['bvid']]['officialData']['view'] and b['playCapturedAt']==DATE
                assert {k:v for k,v in a.items() if k not in ['play','playCapturedAt']}=={k:v for k,v in b.items() if k not in ['play','playCapturedAt']}
    plays.update(applied=True,appliedChanges=rows_changed,globalFallbackCaptureDatePreserved='2026-10-14',policy='Verified changed rows carry individual playCapturedAt dates; unverified records retain their original per-video or global historical capture dates. No new full-snapshot capture date is inferred.')
    plays_path.write_text(json.dumps(plays,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    resources={r['url']:r for r in review['learningResourceChecks']}
    resources.update({r['url']:r for r in review.get('learningResourceRetries',[])})
    forum_content_date=re.search(r'window.FORUM_UPDATED = "([\d-]+)";',forum_source)[1]
    review.update(applied=True,tedAppliedChanges=ted_changes,tedViewsCapturedAt=DATE,forumMetadataReview=metadata['comparison'],forumMetadataEvidence=metadata_path.name,forumPlayReview=plays['summary'],forumPlayEvidence=plays_path.name,forumPlayRowsChanged=len(rows_changed),forumPlayFallbackCapturedAt='2026-10-14',forumContentUpdatedAt=forum_content_date,forumRetainedPlayDates=retained_dates,forumMetadataLastVerified='2026-10-22',learningLatestEntryChecks=list(resources.values()))
    review['learningEntrySummary']={'distinctURLsAttempted':len(resources),'completeHTTP200':sum(r['http']==200 and r['curlExit']==0 for r in resources.values()),'limitedOrIncomplete':sum(r['http']!=200 or r['curlExit']!=0 for r in resources.values()),'confirmed404or410':sum(r['http'] in (404,410) and r['curlExit']==0 for r in resources.values()),'classificationCounts':{k:sum(r['classification']==k for r in resources.values()) for k in {r['classification'] for r in resources.values()}},'scope':'Official/search/video entry-page checks only; HTTP success is not full playback or pricing verification. Access protection/login/timeouts do not mean dead links.'}
    OUT.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'tedRows':40,'tedChanges':len(ted_changes),'forumBVChanged':len(changed_bv),'forumRowsChanged':len(rows_changed),'forumMetadataUnchanged':True,'learning':review['learningEntrySummary']},ensure_ascii=False),flush=True)


def check_covers():
    """Actually request every stored official CDN image header, not just its URL."""
    urls=list(dict.fromkeys(t['cover'] for t in read_data()['ted']))
    def probe(url):
        try:
            result=subprocess.run(['curl.exe','-I','-L','-sS','--max-time','12','-A',UA,'-w','\n@@RESULT@@%{json}',url],capture_output=True,timeout=16)
            head,_,tail=result.stdout.decode('utf8','replace').rpartition('\n@@RESULT@@')
            observed=json.loads(tail) if tail else {}
            row={'url':url,'http':observed.get('http_code',0),'curlExit':result.returncode,'contentType':observed.get('content_type'),'finalURL':observed.get('url_effective',url),'error':result.stderr.decode('utf8','replace').strip()[:250]}
            row['verifiedImage']=bool(row['http']==200 and row['curlExit']==0 and str(row['contentType']).startswith('image/'))
            return row
        except (subprocess.TimeoutExpired,ValueError) as error:
            return {'url':url,'http':0,'curlExit':-1,'verifiedImage':False,'error':str(error)[:250]}
    with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(probe,urls))
    retry=[]
    for row in rows:
        if not row['verifiedImage'] and row.get('curlExit') not in (0,None):
            retry.append(probe(row['url']))
    latest={r['url']:r for r in rows};latest.update({r['url']:r for r in retry})
    review=json.loads(OUT.read_text(encoding='utf8'));review['tedCoverChecks']=rows;review['tedCoverRetries']=retry
    review['tedCoverCheckSummary']={'talks':len(read_data()['ted']),'distinctImages':len(urls),'completeHTTP200Images':sum(r['verifiedImage'] for r in latest.values()),'unverifiedImages':sum(not r['verifiedImage'] for r in latest.values()),'method':'Normal official CDN HTTP HEAD; failed network checks are not dead-image proof.'}
    OUT.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(review['tedCoverCheckSummary']),flush=True)


if __name__=="__main__":
    if "--check-covers" in sys.argv: check_covers()
    elif "--apply-reviewed" in sys.argv: apply_reviewed()
    elif "--retry-incomplete" in sys.argv: retry_incomplete()
    elif "--retry-resource-incomplete" in sys.argv: retry_resources()
    else: main()
