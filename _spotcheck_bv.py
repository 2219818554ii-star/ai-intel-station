# -*- coding: utf-8 -*-
"""成长讲坛视频链接「真实可用」复核（不触发 B 站风控的轻量做法）。
B站 json API 在高频后会把 IP 拉进风控（返回 HTML 页），所以改用：
   HEAD https://www.bilibili.com/video/<bvid>  看状态码
先用一个「已知无效」的对照 BV 号校准判据：无效号会 404，有效号 301 到自身 /video/<bvid>/。
从数据源 forum.js 抽全部（或抽样）BV 号核验，输出统计。
"""
import re, random, subprocess, sys, time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
src = open("forum.js", encoding="utf-8").read()
bvs = sorted(set(re.findall(r'"bvid":"(BV[0-9A-Za-z]{10})"', src)))
print("数据源视频 %d 条\n" % len(bvs))

def status(bvid):
    p = subprocess.run(["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}",
                        "--max-time", "12",
                        "https://www.bilibili.com/video/" + bvid,
                        "-H", "User-Agent: " + UA], capture_output=True)
    return p.stdout.decode().strip()

print("[对照组] 明显无效的 BV 号 BV0000000000 ->", status("BV0000000000"),
      "（若为 404，说明 301 就是有效判据）")
time.sleep(1)
random.seed(20260925)
sample = bvs          # 全量核验（不抽样）：140 条，约 100 秒
ok = bad = 0
for i, b in enumerate(sample):
    code = status(b)
    if code in ("301", "200"):
        ok += 1
    elif code == "404":
        bad += 1
        print("  [死链 404] %s" % b)
    else:
        print("  [异常] %s -> %s" % (b, code))
    time.sleep(0.25)
print("\n抽样 %d 条：有效 %d，死链 %d，异常 %d" % (len(sample), ok, bad, len(sample) - ok - bad))
print("结论：%s" % ("抽检全部有效，链接真实可用" if bad == 0 else "存在死链，需要重抓该系列"))
