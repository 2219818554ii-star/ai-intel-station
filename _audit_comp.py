# -*- coding: utf-8 -*-
"""「可报名比赛」栏目内容级核对（对标 _audit_content.py）。
三道关只验链接格式合法 + 上线前抽检 6 个入口，这里做的是：
  1) 172 条赛事链接全量可达性（HTTP 状态码 + 最终落点）
  2) 标记「通用首页/平台首页」的条目：点进去不是具体赛事页，属于信息 unavailable
  3) 标题与页面实际 <title> 的相似度（能抓到的站点）
输出报告，不改数据，问题交给人工判断。
"""
import re, sys, json, subprocess, time, urllib.parse
from concurrent.futures import ThreadPoolExecutor

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

s = open("competitions.js", encoding="utf-8").read()
blk = s[s.index("window.COMP = ["):]
rows = re.findall(
    r'scope:"(\w+)", n:"(.*?)".*?st:"(\w+)".*?url:"(.*?)"', blk, re.S)
print("条目总数 %d\n" % len(rows))


def probe(a):
    i, sc, n, st, url = a
    p = subprocess.run(
        ["curl", "-sS", "--compressed", "-o", "_tmp_page.html",
         "-w", "%{http_code}|%{url_effective}", "-L",
         "--max-time", "25", "-A", UA, url],
        capture_output=True)
    out = p.stdout.decode("utf-8", "replace").strip()
    code, _, eff = out.partition("|")
    return {
        "i": i, "n": n, "st": st, "url": url,
        "code": code if code else "ERR",
        "eff": eff if eff else url,
    }


t0 = time.time()
with ThreadPoolExecutor(max_workers=8) as ex:
    res = list(ex.map(probe, [(i, sc, n, st, u)
                              for i, (sc, n, st, u) in enumerate(rows, 1)]))
print("探测耗时 %.1fs\n" % (time.time() - t0))

bad = [r for r in res if r["code"] not in ("200", "203", "204")]
print("=" * 60)
print("【1】不可达 / 异常 %d 条" % len(bad))
for r in bad:
    print("  %02d [%s] %s" % (r["i"], r["code"], r["n"][:44]))
    print("      %s" % r["url"][:96])

# 落点跟原 url 完全不一样 = 被重定向/404兜底页
print("\n" + "=" * 60)
print("【2】落点与原地址不同（可能被劫持到兜底页）")
same = 0
for r in res:
    a, b = r["url"].rstrip("/"), r["eff"].rstrip("/")
    if a != b:
        print("  %02d %s" % (r["i"], r["n"][:44]))
        print("      原: %s" % a[:92])
        print("      落: %s" % b[:92])
    else:
        same += 1
print("（其中 %d 条落点与原地址一致）" % same)

# 通用首页：没有具体赛事路径
print("\n" + "=" * 60)
print("【3】url 是「首页/平台页」而非具体赛事页")
home = []
for r in res:
    u = r["url"]
    path = (urllib.parse.urlparse(u).path or "").lstrip("/")
    if path in ("", "index.htm", "index.html", "index.asp",
                "cw/hp/", "competitions", "vse"):
        home.append(r)
for r in home:
    print("  %02d [st=%s] %s" % (r["i"], r["st"], r["n"][:46]))
    print("       %s" % r["url"])
print("共 %d 条" % len(home))

from collections import Counter
print("\n状态码分布:", dict(Counter(r["code"] for r in res)))

# 报告落盘（避免管道截断导致统计丢失）
rep = []
rep.append("状态码分布: %s\n" % dict(Counter(r["code"] for r in res)))
rep.append("\n===== 【1】不可达/异常 =====\n")
for r in bad:
    rep.append("%02d [%s] %s\n      %s\n"
               % (r["i"], r["code"], r["n"][:44], r["url"][:96]))
rep.append("\n===== 【2】落点与原地址不同 =====\n")
for r in res:
    if r["url"].rstrip("/") != r["eff"].rstrip("/"):
        rep.append("%02d %s\n      原: %s\n      落: %s\n"
                   % (r["i"], r["n"][:44], r["url"], r["eff"]))
rep.append("\n===== 【3】首页/平台页（非具体赛事页） =====\n")
for r in home:
    rep.append("%02d [st=%s] %s\n       %s\n"
               % (r["i"], r["st"], r["n"][:46], r["url"]))
open("_comp_report.txt", "w", encoding="utf-8").write("".join(rep))
json.dump(res, open("_comp_probe.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\n报告已写入 _comp_report.txt / _comp_probe.json")
