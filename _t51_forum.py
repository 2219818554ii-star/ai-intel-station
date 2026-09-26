# -*- coding: utf-8 -*-
"""T51b: 讲坛扩容——python urllib 直连 B站搜索 API，每系列 +4，去重后写入 forum.js。"""
import io
import json
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="cp936", errors="replace")

op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
op.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126"),
                 ("Referer", "https://www.bilibili.com/")]
r = op.open("https://www.bilibili.com", timeout=15)
m = re.search(r"buvid3=([^;]+)", r.headers.get("Set-Cookie", ""))
op.addheaders.append(("Cookie", "buvid3=" + (m.group(1) if m else "")))


def search(kw):
    q = urllib.parse.quote(kw)
    u = ("https://api.bilibili.com/x/web-interface/search/type?search_type=video"
         "&order=click&keyword=%s&page=1" % q)
    t = op.open(u, timeout=15).read().decode("utf-8", "replace")
    d = json.loads(t)
    if d.get("code") != 0:
        return []
    out = []
    for it in d["data"]["result"][:24]:
        if it.get("type") != "video":
            continue
        title = re.sub(r"<em[^>]*>|</em>", "", it.get("title", ""))
        out.append({"t": title, "bvid": it["bvid"], "up": it.get("author", ""),
                    "dur": it.get("duration", ""), "play": int(it.get("play", 0) or 0)})
    return out


def dsec(d):
    p = [int(x) for x in d.split(":") if x.isdigit()]
    while len(p) < 3:
        p.insert(0, 0)
    return p[0] * 3600 + p[1] * 60 + p[2]


s = io.open("forum.js", encoding="utf-8").read()
series = re.findall(r'\{cat:"([^"]+)",\s*who:"([^"]+)"', s)
existing = set(re.findall(r'bvid":"(BV[0-9A-Za-z]{10})"', s))
print("系列 %d，已有视频 %d" % (len(series), len(existing)))

adds = {}
for cat, who in series:
    key = who.split("（")[0].split(" ·")[0].strip()
    kw = key + " 演讲"
    try:
        items = search(kw)
    except Exception as e:
        print("%-12s 搜索失败 %s" % (who, str(e)[:50]))
        items = []
    pick = []
    for it in items:
        if it["bvid"] in existing or any(p["bvid"] == it["bvid"] for p in pick):
            continue
        if key not in it["t"]:
            continue
        if dsec(it["dur"]) < 180:
            continue
        pick.append(it)
        if len(pick) >= 4:
            break
    adds[who] = pick
    print("%-14s 新增 %d" % (who, len(pick)))
    time.sleep(1.5)

total = sum(len(v) for v in adds.values())
print("合计新增:", total)
io.open("_forum_adds.json", "w", encoding="utf-8").write(
    json.dumps(adds, ensure_ascii=False, indent=1))
if total == 0:
    sys.exit(1)

# ---- 校验新 bvid 可打开（301/200 有效，404 无效；对照组校准）----
new_bvs = [p["bvid"] for v in adds.values() for p in v]


def bv_ok(bv):
    try:
        p = subprocess.run(["curl", "-sS", "--noproxy", "*", "-o", "/dev/null",
                            "-w", "%{http_code}", "--max-time", "15",
                            "https://www.bilibili.com/video/" + bv],
                           capture_output=True, timeout=25)
        return p.stdout.decode("ascii", "replace").strip() in ("200", "301")
    except Exception:
        return False


ctrl_ok = bv_ok("BV1va4y1s7k8")
ctrl_bad = "BV0000000000"
try:
    p = subprocess.run(["curl", "-sS", "--noproxy", "*", "-o", "/dev/null",
                        "-w", "%{http_code}", "--max-time", "15",
                        "https://www.bilibili.com/video/" + ctrl_bad],
                       capture_output=True, timeout=25)
    ctrl_bad_code = p.stdout.decode("ascii", "replace").strip()
except Exception:
    ctrl_bad_code = "?"
print("对照：真视频=%s 假视频=%s" % ("OK" if ctrl_ok else "FAIL", ctrl_bad_code))
if not ctrl_ok or ctrl_bad_code != "404":
    print("判据不成立，终止不写入")
    sys.exit(1)

with open("_bv_check.txt", "w", encoding="utf-8") as f:
    pass
bad = []
with ThreadPoolExecutorMP() if False else io.open("_bv_check.txt", "w", encoding="utf-8") as f:
    pass
