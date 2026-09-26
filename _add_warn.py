# -*- coding: utf-8 -*-
"""给 2026-09-26 实测无法打开的赛事加「官网状态」如实标注；另修两条可用地址。"""
import sys

P = "competitions.js"
L = open(P, encoding="utf-8").read().split("\n")

WARN = ('     warn:"2026-09-26 实测：这台机器打不开该站（返回 %s）。'
        '域名本身还在、可能是境外网络或站点临时故障，但**没法替你确认它现在是活的**。'
        '报名前请在校内网或问同学再核一次，别直接点这条链接。"')

# url 原值 -> 状态码（用于生成标注文案），None 表示只改 url 不加标注
JOBS = [
    ("https://neurips.cc/", "000", None),
    ("https://wmt-conf.net/", "000", None),
    ("http://www.chalearn.org/", "502", None),
    ("https://solardecathlon.net/", "连接失败", None),
    ("https://www.darpa.mil/", "000", None),
    ("https://www.icho.science/", "000", None),
    ("https://www.spaceappschallenge.org/", "403", None),
    ("http://www.huacanjiang.com/", "503", None),
    ("https://www.cmatd.cn/", "000", None),
    ("https://www.matibei.com/", "000", None),
    ("https://comap.org/undergraduate/contests", "404",
     "https://comap.org/undergraduate/contests/"),
    ("https://www.autodrive.ai/", "403", None),
    ("https://waymo.com/open/", "000", None),
    ("https://spacenet.ai/", "000", None),
    ("http://www.csec.org.cn", "404", None),
    ("http://www.biopharm.org.cn", "502", None),
    ("http://www.siemenscup.com", "502", None),
    ("https://www.robocon.net", "000", None),
    ("http://www.putiyi.com", "403", None),
    ("https://neurips.cc", "000", None),
    ("https://developers.google.com/solution-challenge", "000", None),
    ("https://codingcompetitions.withgoogle.com/codejam", "000", None),
    ("https://www.facebook.com/hackercup", "000", None),
    ("https://quantum-computing.ibm.com", "403", None),
    ("https://huggingface.co/challenges", "000", None),
    # 两条只改可用地址，不加标注
    ("https://www.c4best.cn/", None, "http://www.c4best.cn/"),
    ("https://ches.mwr.cn", None, "http://www.cahee.org.cn/"),
]

for oldu, code, newu in JOBS:
    hits = [i for i, s in enumerate(L) if s.strip().startswith('url:"%s"' % oldu)]
    if len(hits) != 1:
        sys.exit("url 命中 %d 次（应为 1）：%s" % (len(hits), oldu))
    i = hits[0]
    if newu:
        L[i] = '     url:"%s"},' % newu
    if code:
        L.insert(i, WARN % code)

open(P, "w", encoding="utf-8").write("\n".join(L))
print("已处理 %d 条（含 %d 条加标注）" % (len(JOBS), sum(1 for _, c, _ in JOBS if c)))
