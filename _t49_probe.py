# -*- coding: utf-8 -*-
"""抽取 view-learn 区块全部链接并探测可达性。"""
import io
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

sys.stdout.reconfigure(encoding="cp936", errors="replace")

s = io.open("index.src.html", encoding="utf-8").read()
m = re.search(r'<div id="view-learn"[\s\S]*?(?=<div id="view-ted")', s)
blk = m.group(0)
urls = re.findall(r'href="(https?:[^"]+)"', blk)
urls = list(dict.fromkeys(urls))
print("view-learn 链接数:", len(urls))

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126 Safari/537.36")


def probe(u):
    try:
        p = subprocess.run(
            ["curl", "-sS", "--compressed", "-A", UA, "-L", "--max-time", "20",
             "-o", "/dev/null", "-w", "%{http_code}", u],
            capture_output=True, timeout=35,
        )
        return u, p.stdout.decode("ascii", "replace").strip()
    except Exception:
        return u, "ERR"


with ThreadPoolExecutor(max_workers=8) as ex:
    res = list(ex.map(probe, urls))

bad = [(u, c) for u, c in res if not c.startswith("2") and c != "301"]
print("\n非 2xx：")
for u, c in bad:
    print("  [%s] %s" % (c, u))
