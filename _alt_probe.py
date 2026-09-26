# -*- coding: utf-8 -*-
"""对剩余异常站点尝试备选入口，找出可用的那个。"""
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126 Safari/537.36")

CANDS = [
    ("MCM/ICM", ["https://comap.org/undergraduate/contests/",
                 "https://comap.com/undergraduate/contests",
                 "https://www.comap.org/undergraduate/contests/mcm-icm"]),
    ("IChO", ["https://icho.science/", "http://www.icho.science/",
              "https://www.icho.science/"])  ,
    ("水利创新设计", ["http://www.cahee.org.cn/", "https://ches.mwr.cn/"]),
    ("数字媒体", ["https://www.cmatd.cn/", "http://www.cmatd.cn/"]),
    ("码蹄杯", ["https://www.matibei.com/", "http://www.matibei.com/"]),
    ("高校计算机大赛", ["https://www.c4best.cn/", "http://www.c4best.cn/"]),
    ("生物制药", ["http://www.biopharm.org.cn", "https://www.biopharm.org.cn"]),
    ("环境生态", ["http://www.csec.org.cn", "https://www.csec.org.cn/"]),
    ("西门子杯", ["http://www.siemenscup.com", "https://www.siemenscup.com/"]),
    ("华灿奖", ["http://www.huacanjiang.com/", "https://www.huacanjiang.com/"]),
    ("普译赛", ["http://www.putiyi.com", "https://www.putiyi.com/"]),
    ("ChaLearn", ["http://www.chalearn.org/", "https://challenge.chalearn.org/"]),
    ("NeurIPS", ["https://neurips.cc/", "https://neurips.cc"]),
    ("Waymo", ["https://waymo.com/open/", "https://waymo.com/"]),
    ("SpaceNet", ["https://spacenet.ai/", "https://www.spacenet.ai/"]),
    ("RoboCon", ["https://www.robocon.net", "http://www.robocon.net/"]),
]


def probe(item):
    name, urls = item
    for u in urls:
        try:
            q = subprocess.run(
                ["curl", "-sS", "--compressed", "-A", UA, "-L", "--max-time", "20",
                 "-o", "/dev/null", "-w", "%{http_code}", u],
                capture_output=True, timeout=35,
            )
            c = q.stdout.decode("ascii", "replace").strip()
        except Exception:
            c = "ERR"
        yield (name, u, c)


out = []
with ThreadPoolExecutor(max_workers=8) as ex:
    for r in ex.map(probe, CANDS):
        out.extend(r)

for name, u, c in out:
    print("%-6s %-4s %s" % (name, c, u))
print("\n200 可用：")
for name, u, c in out:
    if c == "200":
        print("   ", name, "->", u)
json.dump(out, open("_alt_probe.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
