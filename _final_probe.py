# -*- coding: utf-8 -*-
"""从 competitions.js 抽出全部条目 → 全量 HTTP 复测 → 报告落盘。"""
import json
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126 Safari/537.36")

# 1) 用 node 可靠地抽出条目
JS = r"""
global.window = {};
require('./competitions.js');
console.log(JSON.stringify(window.COMP));
"""
p = subprocess.run(["node", "-e", JS], capture_output=True, cwd=".")
if p.returncode != 0:
    raise SystemExit("抽取失败：" + p.stderr.decode("utf-8", "replace")[:500])

data = json.loads(p.stdout.decode("utf-8", "replace"))
print("条目数：", len(data))


def probe(it):
    idx, name, url = it
    r = {"i": idx, "n": name, "url": url}
    try:
        q = subprocess.run(
            ["curl", "-sS", "--compressed", "-A", UA, "-L",
             "--max-time", "22", "-o", "/dev/null",
             "-w", "%{http_code}", url],
            capture_output=True, timeout=40,
        )
        r["code"] = q.stdout.decode("ascii", "replace").strip()
    except Exception as e:
        r["code"] = "ERR"
    return r


jobs = [(i + 1, d.get("n", ""), d.get("url", "")) for i, d in enumerate(data)]
with ThreadPoolExecutor(max_workers=8) as ex:
    res = list(ex.map(probe, jobs))

bad = [r for r in res if not r["code"].startswith("2") or r["code"] == "000"]
print("\n异常条目 %d 条（状态码非 2xx）：" % len(bad))
lines = []
for r in bad:
    lines.append("%3d [%s] %s\n     %s" % (r["i"], r["code"], r["n"], r["url"]))
txt = "\n".join(lines)
open("_final_report.txt", "w", encoding="utf-8").write(txt)
print(txt)
print("\n完整结果已存 _final_probe.json")
json.dump(res, open("_final_probe.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
