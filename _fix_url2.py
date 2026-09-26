# -*- coding: utf-8 -*-
"""按行号替换 url 行，只改域名/路径，逐行 assert 原串一致。"""
import sys

P = "competitions.js"
L = open(P, encoding="utf-8").read().split("\n")

# (行号1-based, 行内必须包含的赛事名, 原 url 值, 新 url 值)
JOBS = [
    (113, "工创杯", "https://www.saikr.com/vse/2026RGZN", "https://new.saikr.com/vse/2026RGZN"),
    (418, "MCM/ICM", "https://www.comap.com/undergraduate/contests", "https://comap.org/undergraduate/contests"),
    (578, "水利", "http://www.ches.org.cn", "https://ches.mwr.cn"),
    (583, "油气储运", "http://www.cup.edu.cn", "https://www.cup.edu.cn"),
    (633, "RoboMaster", "https://www.robomaster.com", "https://www.robomaster.com/zh-CN"),
    (693, "华为ICT", "https://e.huawei.com", "https://e.huawei.com/cn/"),
    (743, "勘探地球物理", "http://www.cup.edu.cn", "https://www.cup.edu.cn"),
]

for ln, key, oldu, newu in JOBS:
    i = ln - 1
    line = L[i]
    exp = '     url:"%s"},' % oldu
    if line != exp:
        sys.exit("L%d 原串不符：%r\n期望：%r" % (ln, line, exp))
    if key not in L[i - 4] + L[i - 3] + L[i - 2] + L[i - 1]:
        sys.exit("L%d 上下文找不到赛事名「%s」" % (ln, key))
    L[i] = '     url:"%s"},' % newu

open(P, "w", encoding="utf-8").write("\n".join(L))
print("已改 %d 行" % len(JOBS))
