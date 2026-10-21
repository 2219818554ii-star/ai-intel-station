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
DATE = "2026-10-21"
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
    review["tedRetryReason"] = "TED changed its visible plays markup to plain text without a React comment. Retry previously disclosed counts with both official markup variants supported; never replace a known count with a parser failure."
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
    review = json.loads(OUT.read_text(encoding="utf-8"))
    data = read_data()
    fetched = {r["url"]: r for r in review["ted"]}
    assert len(fetched) == len(data["ted"]) == 40
    assert all(r["http"] == 200 and r["curlExit"] == 0 and r.get("officialTitle") == r["title"] for r in fetched.values())
    assert all(fetched[t["url"]].get("views") is not None for t in data["ted"] if t.get("views") is not None)
    assert all(isinstance(r.get("cover"), str) and r["cover"].startswith("https://pi.tedcdn.com/") for r in fetched.values())
    changed = []
    source = (ROOT / "ted.js").read_text(encoding="utf-8")

    def replace_row(match):
        current = fetched[match[1]]
        row = 'url:' + json.dumps(match[1]) + ', cover:' + json.dumps(current["cover"]) + ', views:' + json.dumps(current.get("views")) + '}' + match[2]
        if row != match[0]:
            changed.append({"url": match[1], "previousViews": current.get("previousViews"), "views": current.get("views")})
        return row

    source, count = re.subn(r'url:"([^"]+)",\s*cover:(?:"[^"]*"|null),\s*views:(?:\d+|null)\}(,?)', replace_row, source)
    assert count == 40
    if changed:
        source = re.sub(r'window.TED_UPDATED = "[\d-]+";', 'window.TED_UPDATED = "' + DATE + '";', source)
    source = re.sub(r'window.TED_VIEWS_CAPTURED_AT = "[\d-]+";', 'window.TED_VIEWS_CAPTURED_AT = "' + DATE + '";', source)
    if "window.TED_CHECKED" not in source:
        source = source.replace('window.TED_UPDATED', 'window.TED_CHECKED = "' + DATE + '";\nwindow.TED_UPDATED', 1)
    else:
        source = re.sub(r'window.TED_CHECKED = "[\d-]+";', 'window.TED_CHECKED = "' + DATE + '";', source)
    source = source.replace("2026-10-20 全量复核40个官网页面并刷新封面图/官网播放量", DATE + " 全量复核40个官网页面并刷新封面图/官网播放量")
    source = source.replace("2026-10-20 已逐条完整获取，40个页面均返回200", DATE + " 已逐条完整获取，40个页面均返回200")
    source = source.replace("2026-10-20 抓取；null=该条页面未暴露播放数", DATE + " 抓取；null=该条页面未暴露播放数")
    (ROOT / "ted.js").write_text(source, encoding="utf-8")

    path = ROOT / "forum.js"
    forum_source = path.read_text(encoding="utf-8")
    assert all(r.get("play") is None for r in review["forumAccessChecks"]), "Accessible API sample requires a complete collection before declaring the old access limit."
    note = "10月21日核查：三个分类的B站官方API样本与播放页仍有访问保护或网络异常，未刷新视频状态；累计播放量保留10月14日历史采集值。"
    forum_source = re.sub(r'window.FORUM_REVIEW_NOTE = "[^"\n]*";', 'window.FORUM_REVIEW_NOTE = ' + json.dumps(note, ensure_ascii=False) + ';', forum_source)
    if "window.FORUM_CHECKED" not in forum_source:
        forum_source = forum_source.replace('window.FORUM_UPDATED', 'window.FORUM_CHECKED = "' + DATE + '";\nwindow.FORUM_UPDATED', 1)
    else:
        forum_source = re.sub(r'window.FORUM_CHECKED = "[\d-]+";', 'window.FORUM_CHECKED = "' + DATE + '";', forum_source)
    forum_source = forum_source.replace("   2026-10-20：三个分类的API样本及正常播放页出现HTTP 412或网络异常；未重新确认视频状态或播放量。", "   2026-10-21：三个分类的API样本及正常播放页出现HTTP 412或网络异常；未重新确认视频状态或播放量。")
    forum_source = forum_source.replace("本次联网记录见 _learning_review_2026-10-20.json", "本次联网记录见 _learning_review_2026-10-21.json")
    path.write_text(forum_source, encoding="utf-8")
    after = read_data()
    assert after["forum"] == data["forum"], "Existing 25 series and 205 video snapshots must remain identical."
    assert [t["url"] for t in after["ted"]] == [t["url"] for t in data["ted"]]
    review.update(applied=True, tedAppliedChanges=changed, tedViewsCapturedAt=DATE,
                  forumSeriesAndVideosUnchanged=True, forumPlayCapturedAt="2026-10-14",
                  forumContentUpdatedAt="2026-10-18", forumPlaybackValuesChanged=0)
    latest_resources = {r["url"]: r for r in review["learningResourceChecks"]}
    latest_resources.update({r["url"]: r for r in review.get("learningResourceRetries", [])})
    review["learningLatestEntryChecks"] = list(latest_resources.values())
    review["learningEntrySummary"] = {
        "distinctURLsAttempted": len(latest_resources),
        "completeHTTP200": sum(r["http"] == 200 and r["curlExit"] == 0 for r in latest_resources.values()),
        "limitedOrIncomplete": sum(r["http"] != 200 or r["curlExit"] != 0 for r in latest_resources.values()),
        "confirmed404or410": sum(r["http"] in (404, 410) and r["curlExit"] == 0 for r in latest_resources.values()),
        "scope": "Public entry-page checks only; search pages are not verified individual courses, HTTP 200 is not complete video playback, and WAF/login/timeout responses are not dead-link evidence. Existing three materials and battery modelling resources have complete official-homepage responses after one network retry."
    }
    OUT.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"tedRows": 40, "tedChanged": len(changed), "forumSeriesUnchanged": len(after["forum"]),
                      "forumVideosUnchanged": sum(len(s["vids"]) for s in after["forum"])}), flush=True)


if __name__ == "__main__":
    if "--apply-reviewed" in sys.argv:
        apply_reviewed()
    elif "--retry-incomplete" in sys.argv:
        retry_incomplete()
    elif "--retry-resource-incomplete" in sys.argv:
        retry_resources()
    else:
        main()
