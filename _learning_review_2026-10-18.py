# -*- coding: utf-8 -*-
"""Read-only official TED metadata audit; apply reviewed results separately.

No date stamp is changed here. HTTP failures are evidence, never invented data.
The Bilibili sample checks document the current access limit without retries
that would turn this into a slow full-library crawl.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import html
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
NODE = r"C:/Users/22198/.workbuddy/binaries/node/versions/22.22.2-6/node.exe"
OUT = ROOT / "_learning_review_2026-10-18.json"


def read_data():
    script = """const fs=require('fs'),vm=require('vm');const c={window:{}};
vm.createContext(c);for(const f of ['ted.js','forum.js'])
vm.runInContext(fs.readFileSync(f,'utf8'),c);
process.stdout.write(JSON.stringify({ted:c.window.TED,forum:c.window.FORUM_SERIES}));"""
    return json.loads(subprocess.check_output([NODE, "-e", script], cwd=ROOT))


def get(url, max_time=22):
    try:
        response = subprocess.run(
            ["curl.exe", "-L", "-sS", "--max-time", str(max_time), "-A", "Mozilla/5.0",
             "-H", "Referer: https://www.bilibili.com" if "bilibili" in url else
             "Referer: https://www.ted.com", "-w", "\n@@HTTP@@%{http_code}", url],
            capture_output=True, timeout=max_time + 5)
        body = response.stdout.decode("utf-8", errors="replace")
        payload, _, status = body.rpartition("\n@@HTTP@@")
        return int(status or 0), payload, response.returncode
    except (subprocess.TimeoutExpired, ValueError):
        return 0, "", -1


def audit_ted(talk):
    status, body, exit_code = get(talk["url"], 40)
    result = {"url": talk["url"], "title": talk["en"], "http": status,
              "curlExit": exit_code, "previousViews": talk.get("views")}
    if status == 200 and exit_code == 0:
        cover = re.search(r'property="og:image"\s+content="([^"]+)"', body)
        plays = re.search(r'([\d,]+)<!--\s*-->\s*plays', body)
        duration = re.search(r'property="og:video:duration"\s+content="(\d+)"', body)
        title = re.search(r'<h1[^>]*>(.*?)</h1>', body, re.S)
        result.update({
            "officialTitle": html.unescape(re.sub(r"<[^>]+>", "", title[1])).strip() if title else None,
            "cover": html.unescape(cover[1]).split("?")[0] if cover else None,
            "views": int(plays[1].replace(",", "")) if plays else None,
            "durationSeconds": int(duration[1]) if duration else None,
        })
    print(f"TED {status} {talk['en'][:55]}", flush=True)
    return result


def main():
    data = read_data()
    with ThreadPoolExecutor(max_workers=4) as pool:
        ted = list(pool.map(audit_ted, data["ted"]))
    # One official API request and one normal playback-page request are enough
    # to document a shared 412 response. Do not mark individual videos dead.
    sample_bvid = data["forum"][0]["vids"][0]["bvid"]
    bili_urls = ["https://api.bilibili.com/x/web-interface/view?bvid=" + sample_bvid,
                 "https://www.bilibili.com/video/" + sample_bvid]
    bili = []
    for url in bili_urls:
        status, body, exit_code = get(url)
        bili.append({"url": url, "http": status, "curlExit": exit_code,
                     "securityRejection": "412" in body and ("风控" in body or "security control" in body)})
    result = {"reviewDate": "2026-10-18", "checkedAtUTC": datetime.now(timezone.utc).isoformat(),
              "ted": ted, "forumAccessChecks": bili,
              "forumAccessLimit": "Bilibili returned HTTP 412. Playback counts and current availability are not refreshed or inferred from this response.",
              "forumContentCorrections": []}
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ted200": sum(x["http"] == 200 and x["curlExit"] == 0 for x in ted),
                      "tedViewsExposed": sum(x.get("views") is not None for x in ted),
                      "bilibili": bili}, ensure_ascii=False), flush=True)


def apply_reviewed():
    review = json.loads(OUT.read_text(encoding="utf-8"))
    ted_results = {x["url"]: x for x in review["ted"]}
    if len(ted_results) != 40 or any(x["http"] != 200 or x["curlExit"] != 0 for x in ted_results.values()):
        raise RuntimeError("All 40 TED official pages must succeed before applying this full refresh")
    source = (ROOT / "ted.js").read_text(encoding="utf-8")
    changes = []

    def replace_ted(match):
        url = match[1]
        old = match[0]
        current = ted_results[url]
        cover = json.dumps(current.get("cover"), ensure_ascii=False)
        views = json.dumps(current.get("views"))
        changed = 'url:' + json.dumps(url) + ', cover:' + cover + ', views:' + views + '}' + match[2]
        if old != changed:
            changes.append({"url": url, "previousViews": current.get("previousViews"),
                            "views": current.get("views")})
        return changed

    source, replaced = re.subn(r'url:"([^"]+)",\s*cover:(?:"[^"]*"|null),\s*views:(?:\d+|null)\}(,?)', replace_ted, source)
    if replaced != 40:
        raise RuntimeError(f"Expected 40 existing TED rows, got {replaced}")
    source = source.replace('window.TED_UPDATED = "2026-10-14";', 'window.TED_UPDATED = "2026-10-18";')
    source = source.replace("2026-10-14 全量复核存在性 + 抓取封面图/官网播放量", "2026-10-18 全量复核40个官网页面并刷新封面图/官网播放量")
    source = source.replace("2026-10-14 已逐条验活，全部 200 可访问", "2026-10-18 已逐条请求，40个页面均返回200")
    source = source.replace("2026-10-14 抓取；null=该条页面未暴露播放数", "2026-10-18 抓取；null=该条页面未暴露播放数")
    source = source.replace("   渲染策略（2026-09-22 修订）：弃用易 404 的 ted.com/talks/<slug> 直链，\n        改为「TED 官方搜索(免费) + YouTube + B站(中英字幕)」三入口，\n        哪个通点哪个，彻底解决视频打不开的问题。", "   渲染策略：TED 官网直达为主入口，另备 YouTube / B站搜索；搜索结果不保证字幕或上传授权。\n   复核范围：官网页面与公开元数据；HTTP 200 不等于已在本机完整播放视频。")
    (ROOT / "ted.js").write_text(source, encoding="utf-8")

    # These exclusions use the already stored titles, not fabricated current API
    # results. Preserve the speaker/series keys and every retained BV identifier.
    exclusions = {
        "BV1zW411b753": "舞蹈表演，不是演讲或学习课程",
        "BV1Fs411e7Sb": "富豪互怼剪辑，偏离演讲学习用途",
        "BV1yb411k7KG": "饭桌八卦剪辑，偏离演讲学习用途",
        "BV1EeYN6cEKW": "标题为特朗普演讲，误归入马斯克系列",
        "BV1U5RNYgEfp": "斯坦福CS224N课程，不是乔布斯演讲",
        "BV1kP4y1Y7tV": "人物对立与野心指控的剪辑，偏离访谈学习用途",
        "BV187qQBpECc": "馆长个人直播，不是曹德旺演讲或专访",
        "BV1aF411Q7Je": "哈佛幸福研究TED，不是稻盛和夫演讲",
        "BV1oG4y1D7DW": "车主电池衰减测试，不是曾毓群本人演讲或访谈",
        "BV1NG4y1i7Cb": "面相分析，不是电池技术或经营内容",
        "BV1FweJ6VEJB": "个人八卦事件，偏离动力电池学习用途",
        "BV12j416VEvM": "标题明确为AI虚构三国内容，不是易中天本人讲坛",
        "BV1KvmcBNEoX": "粉丝脱粉评论，偏离本系列历史课程用途",
        "BV1PMDvBYE2U": "围绕讲者的小故事争议评论，偏离历史课程用途",
        "BV1Z8411c7t7": "史记原文朗读，标题没有王立群讲解，不应归为其讲坛",
        "BV1e64y1Q7D5": "讲者个人现状八卦，偏离国学课程用途",
        "BV1Dw4m1m7pm": "标题明确为女主播年鉴，同名人物误命中",
        "BV1Ui421D7Dq": "标题明确为女主播年鉴，同名人物误命中",
        "BV1Typ4eME4g": "武则天八字分析，不是蒙曼历史讲座",
        "BV1dMyhBWEA4": "游戏角色武则天教学，与蒙曼历史讲座无关",
        "BV1E94y1E7mx": "知识放映室第三方王阳明概述，标题未署郦波；避免误作其讲座",
        "BV1ZvpCzoELp": "唐宋主题电视节目，标题未署康震，避免误作其讲座",
        "BV15W4y1d7Jk": "掌掴事件报道，偏离清史课程用途",
        "BV1M5Et6GEWe": "掌掴事件当事人评论，偏离清史课程用途",
        "BV12b411S7FW": "掌掴风波回应，偏离清史课程用途",
        "BV1ciKQ6wEuo": "掌掴事件当事人评论，偏离清史课程用途",
        "BV11Z3NzMEk8": "标题仅为如图，无法从现有元数据确认课程主题与讲者",
        "BV1oU4y1a7dc": "欧丽娟中国文学史课程，不是央视典籍里的中国",
        "BV151JLziEeJ": "王德峰传习录公开课，不是央视典籍里的中国节目",
        "BV1QY411J7jv": "杨立华中国哲学史通论，不是传习录精读课程",
        "BV1pj421o7UX": "战争雷霆游戏，与作者度阴山或阳明心学无关",
        "BV1SA4m1F7PS": "MC游戏动画，因诗句度阴山误命中作者名",
        "BV1oL411N763": "成人游戏实况，与作者度阴山或阳明心学无关",
    }
    series_exclusions = {
        ("董平 · 浙大公开课", "BV15Z4y1R76Z"): "王德峰讲座误归董平，已保留在王德峰及心学实践系列",
        ("度阴山 · 通俗解读", "BV1xo4y1T7cU"): "作者为熊逸，不是度阴山；保留在心学实践主题系列",
    }
    priority = {
        "马云": ["BV1Az4y1v7Z8"], "任正非": ["BV1ea411R7Uc", "BV1Wx411o7BF"],
        "曹德旺": ["BV1uV411q7Yf", "BV1oU4y1h7J4"], "稻盛和夫": ["BV1Yz421X7ad"],
        "曾毓群": ["BV13M4y1V7Vw", "BV1fh4y1B7cU", "BV19Ptpe2EaF", "BV12UsremEVm"],
        "于丹": ["BV1g9H6e1ED4", "BV1jb411h7q2"], "郦波": ["BV1h44y1D7mU"],
        "郦波 · 心学入门": ["BV1h44y1D7mU"], "董平 · 浙大公开课": ["BV1wX4y1L7Rw"],
        "典籍里的中国": ["BV1B121BGEAf", "BV15xJzzqE2d", "BV1Mr4y1P7ua"],
        "度阴山 · 通俗解读": ["BV1494y1f7TX"], "心学实践": ["BV11u4y1h7Ry"],
    }
    descriptions = {
        "马云": "创业经历、教育与经营主题的演讲和访谈。优先从完整演讲入手，再看短剪辑。",
        "马斯克": "科技创业、第一性原理与人工智能等话题的访谈，另含传记和第三方评论；字幕以视频页为准。",
        "任正非": "访谈、经营观点与华为相关人物观察。先听本人完整回答，再对照第三方评论。",
        "曹德旺": "制造业经营与创业经历的专访，另收录相关纪录片、人物观察。",
        "稻盛和夫": "经营哲学、六项精进与人生主题的演讲和解读，区分本人讲话、讲解与有声读物。",
        "曾毓群": "动力电池与产业经营的本人访谈、主旨演讲，另含相关产业观察；第三方观点不代表讲者本人。",
        "于丹": "论语、庄子与人生主题的讲座和读书内容，已剔除同名新闻主播与人物八卦。",
        "郦波": "从五百年来王阳明等讲座入手，兼看诗词、历史与人物主题的演讲。",
        "董平 · 浙大公开课": "从董平的王阳明心学公开课搭建框架，理解心即理、知行合一与致良知。",
        "典籍里的中国": "央视节目合集与相关片段。学习传习录时可先找对应一期，再结合原典阅读。",
        "度阴山 · 通俗解读": "度阴山相关的王阳明讲解、有声读物与历史内容。课程、原著与配音解读以视频页标注为准。",
        "心学实践": "原典诵读、心学课程与不同作者的主题解读。读完后选一件真实小事练习，避免只收藏。",
    }
    path = ROOT / "forum.js"
    original = path.read_text(encoding="utf-8")
    data = read_data()["forum"]
    removed = []
    duration_normalized = 0
    for series in data:
        kept = []
        for video in series["vids"]:
            reason = series_exclusions.get((series["who"], video["bvid"])) or exclusions.get(video["bvid"])
            if reason:
                removed.append({"series": series["who"], "bvid": video["bvid"], "title": video["t"],
                                "reason": reason, "basis": "Previously stored Bilibili title/uploader; no claim of fresh video-page verification"})
                continue
            video["t"] = html.unescape(video["t"])
            parts = video["dur"].split(":")
            if len(parts) == 2 and all(part.isdigit() for part in parts):
                normalized = str(int(parts[0])) + ":" + parts[1].zfill(2)
                duration_normalized += normalized != video["dur"]
                video["dur"] = normalized
            kept.append(video)
        preferred = priority.get(series["who"], [])
        kept.sort(key=lambda video: preferred.index(video["bvid"]) if video["bvid"] in preferred else len(preferred))
        series["vids"] = kept
        series["desc"] = descriptions.get(series["who"], series["desc"])
    assert len(data) == 25 and all(len(s["vids"]) >= 3 for s in data)
    assert sum(len(s["vids"]) for s in data) >= 100
    q = lambda value: json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    header = """/* AI 情报站 - 成长讲坛：系列 -> 视频；保留既有BV直达链接。
   2026-10-14：上次B站view API全量抓取播放量（历史快照）。
   2026-10-18：按已有标题/UP主整理分组，剔除错讲者、同名误命中、游戏与八卦，完整课程/本人访谈优先。
   本次B站官方API和播放页均返回HTTP 412，未重新确认视频存活或播放量；风控不等于死链。
   明细与联网限制见 _learning_review_2026-10-18.json；没有为了凑数补入未经核实的视频。 */
window.FORUM_UPDATED = "2026-10-18";
window.FORUM_PLAY_CAPTURED_AT = "2026-10-14";
window.FORUM_REVIEW_NOTE = "本次按已有标题整理内容；B站访问受限，未实时验活，播放量为历史采集值。";
window.FORUM_CATS = ["名人与企业家","国学讲坛","阳明心学"];
window.FORUM_SERIES = [
"""
    blocks = []
    for series in data:
        lines = ['  {cat:' + q(series["cat"]) + ', who:' + q(series["who"]) + ', desc:' + q(series["desc"]) + ', vids:[']
        lines.append(",\n".join("    " + q(video) for video in series["vids"]))
        lines.append("  ]}")
        blocks.append("\n".join(lines))
    guide = original[original.index("window.XINXUE_GUIDE ="):]
    path.write_text(header + ",\n".join(blocks) + "\n];\n" + guide, encoding="utf-8")
    review.update({"tedAppliedChanges": changes, "forumContentCorrections": removed,
                   "forumVideoCountBefore": sum(len(s["vids"]) for s in read_data()["forum"]) + len(removed),
                   "forumVideoCountAfter": sum(len(s["vids"]) for s in data),
                   "forumSeriesAfter": [{"who": s["who"], "count": len(s["vids"])} for s in data],
                   "forumDurationFormattingNormalized": duration_normalized,
                   "forumPlaybackValuesChanged": 0, "forumPlaybackCapturedAt": "2026-10-14",
                   "forumCountSafeguards": "Unchanged: exactly 25 series; each >=3 videos; total >=100."})
    OUT.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"tedChanged": len(changes), "forumRemovedRows": len(removed),
                      "forumRemaining": sum(len(s["vids"]) for s in data)}, ensure_ascii=False))


def retry_incomplete():
    review = json.loads(OUT.read_text(encoding="utf-8"))
    current = {t["url"]: t for t in read_data()["ted"]}
    failed = [current[x["url"]] for x in review["ted"] if x["http"] != 200 or x["curlExit"] != 0]
    with ThreadPoolExecutor(max_workers=3) as pool:
        retried = {x["url"]: x for x in pool.map(audit_ted, failed)}
    review["ted"] = [retried.get(x["url"], x) for x in review["ted"]]
    review["tedRetriedCount"] = len(failed)
    OUT.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("TED complete responses:", sum(x["http"] == 200 and x["curlExit"] == 0 for x in review["ted"]))


if __name__ == "__main__":
    if "--apply-reviewed" in sys.argv:
        apply_reviewed()
    elif "--retry-incomplete" in sys.argv:
        retry_incomplete()
    else:
        main()
