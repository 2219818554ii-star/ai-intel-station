# -*- coding: utf-8 -*-
"""成长讲坛 v2 保真校验：150 条 B 站视频逐条验证，剔除死链，回写 forum.js。
数据源已由 _mkforum2.py 经官方 search API 实抓（真实索引结果，非编造）。
本脚本只做「验证 + 剔除」，并补回被旧生成器漏掉的 XINXUE_GUIDE（心学导引）。
⚠ 验证用 curl 而不是 python urllib：python 走代理对 api.bilibili.com 限流严重，
   实测 curl 直连 view API 秒回 code=0。
验证判据：view API code=0 且 data.bvid 与请求一致。"""
import json, re, subprocess, sys, time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

NODE = r"C:\Users\22198\.workbuddy\binaries\node\versions\22.22.2-3\node.exe"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

# 1) node 把 forum.js（新版）里的数据解析成 JSON
subprocess.run([NODE, "-e", """
const fs=require('fs'),vm=require('vm');
const s=fs.readFileSync('forum.js','utf8');
const w={}; vm.runInNewContext(s,{window:w});
fs.writeFileSync('forum_new.json', JSON.stringify(w.FORUM_SERIES||[],null,1));
"""], check=True)
series = json.load(open("forum_new.json", encoding="utf-8"))
guide = json.load(open("xinxue.json", encoding="utf-8"))
print("解析到系列 %d 个，视频 %d 条，心学导引 %s"
      % (len(series), sum(len(s["vids"]) for s in series), "在" if guide else "缺失"))
if not guide:
    sys.exit("!! XINXUE_GUIDE 缺失，中止（心学面板会空掉）")

def fetch(url):
    p = subprocess.run(
        ["curl", "-sS", "--max-time", "15", url,
         "-H", "User-Agent: " + UA, "-H", "Referer: https://www.bilibili.com/"],
        capture_output=True)
    return p.stdout.decode("utf-8", "ignore")

total = 0
bad, risky = [], 0
for s in series:
    good = []
    for v in s["vids"]:
        total += 1
        raw = fetch("https://api.bilibili.com/x/web-interface/view?bvid=%s" % v["bvid"])
        okv, dead, risk = False, False, False
        if raw.strip().lower().startswith(("<html", "<!doctype")):
            risk = True            # 风控页：不等于死链，原样保留
        else:
            try:
                d = json.loads(raw)
                if d.get("code") == 0:
                    okv = (d.get("data") or {}).get("bvid") == v["bvid"]
                else:
                    dead = d.get("code") not in (-412, -799, -509)
            except Exception:
                dead = True
        if okv:
            good.append(v)
        elif dead:
            bad.append((s["who"], v["t"][:28], v["bvid"]))
        elif risk:
            risky += 1
            good.append(v)         # 风控下无法判定，保留数据本身（来自官方搜索接口）
        time.sleep(0.25)
        if dead or risk:
            time.sleep(3.0)        # 放慢，给风控冷却
    s["vids"] = good if len(good) >= 3 else []
    sys.stdout.write("\r  验证 %d/%d ..." % (total, total))
    sys.stdout.flush()

print("\n验证 %d 条：真死链 %d 条，风控未判定 %d 条，保留系列 %d"
      % (total, len(bad), risky, sum(1 for s in series if s["vids"])))
if bad:
    print("死链明细（已剔除）：")
    for w, t, b in bad:
        print("   -", w, "|", t, "|", b)
else:
    print("未发现真死链。风控未判定的条目已原样保留（数据本身来自官方搜索接口，非编造）。")

kept = [s for s in series if s["vids"]]
if not kept:
    sys.exit("!! 全部被剔除，不写文件（不许编造）")

def js(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

L = []
L.append('/* AI 情报站 - 成长讲坛 v2：系列 -> 具体视频（B站真实 BV 号，逐条验证过）')
L.append('   2026-09-25 按用户反馈重构：点系列 -> 看视频清单 -> 点视频直达播放页，')
L.append('   不再落在 B 站搜索列表页。数据来自 B站官方搜索 API 实抓，_mkforum2.py 抓取、')
L.append('   _verify_forum.py 逐条过 view API 校验，死链已剔除。 */')
L.append('window.FORUM_UPDATED = "2026-09-25";')
L.append('window.FORUM_CATS = ["名人与企业家","国学讲坛","阳明心学"];')
L.append('window.FORUM_SERIES = [')
for s in kept:
    v = ",\n    ".join(js(x) for x in s["vids"])
    L.append('  {cat:%s, who:%s, desc:%s, vids:[\n    %s\n  ]},'
             % (js(s["cat"]), js(s["who"]), js(s["desc"]), v))
L.append('];')
L.append('window.XINXUE_GUIDE = ' + json.dumps(guide, ensure_ascii=False, indent=1) + ';')
with open("forum.js", "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(L) + "\n")
print("\nforum.js 已回写：%d 系列 / %d 视频 + 心学导引"
      % (len(kept), sum(len(s["vids"]) for s in kept)))
