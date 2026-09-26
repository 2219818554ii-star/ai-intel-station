# -*- coding: utf-8 -*-
"""T51b-2: 校验新增 bvid 并写入 forum.js（读取 _forum_adds.json）。"""
import io
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

sys.stdout.reconfigure(encoding="cp936", errors="replace")

adds = json.loads(io.open("_forum_adds.json", encoding="utf-8").read())
new_bvs = [p["bvid"] for v in adds.values() for p in v]
print("待校验:", len(new_bvs))


def bv_code(bv):
    try:
        p = subprocess.run(["curl", "-sS", "--noproxy", "*", "-o", "/dev/null",
                            "-w", "%{http_code}", "--max-time", "15",
                            "https://www.bilibili.com/video/" + bv],
                           capture_output=True, timeout=25)
        return p.stdout.decode("ascii", "replace").strip()
    except Exception:
        return "ERR"


with ThreadPoolExecutor(max_workers=6) as ex:
    codes = list(ex.map(bv_code, ["BV1va4y1s7k8", "BV0000000000"] + new_bvs))

ctrl_ok, ctrl_bad = codes[0], codes[1]
print("对照：真视频=%s 假视频=%s" % (ctrl_ok, ctrl_bad))
if ctrl_ok not in ("200", "301") or ctrl_bad != "404":
    print("判据不成立，终止不写入")
    sys.exit(1)

bad = [bv for bv, c in zip(new_bvs, codes[2:]) if c not in ("200", "301")]
print("校验失败:", len(bad))
if bad:
    print(bad)
    sys.exit(1)

# ---- 写入 forum.js：每个系列的 vids 数组尾部追加 ----
s = io.open("forum.js", encoding="utf-8").read()
n_ins = 0
for who, picks in adds.items():
    if not picks:
        continue
    i = s.find('who:"%s"' % who)
    if i < 0:
        print("找不到系列:", who)
        continue
    j = s.index("vids:[", i)
    k = s.index("]},", j)              # 该系列 vids 数组结尾
    block = "".join(
        ',\n    {"t":%s,"bvid":"%s","up":"%s","dur":"%s","play":%d}' % (
            json.dumps(p["t"], ensure_ascii=False), p["bvid"], p["up"], p["dur"], p["play"])
        for p in picks)
    s = s[:k] + block + s[k:]
    n_ins += len(picks)

s = s.replace('window.FORUM_UPDATED = "2026-09-25";', 'window.FORUM_UPDATED = "2026-09-26";')
io.open("forum.js", "w", encoding="utf-8").write(s)
print("已写入 forum.js：新增 %d 条" % n_ins)
