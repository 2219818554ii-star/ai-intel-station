# -*- coding: utf-8 -*-
"""T48: comap 换可用入口 + 市调大赛转 open。"""
import io
import sys

P = "competitions.js"
s = io.open(P, encoding="utf-8").read()

JOBS = [
    ('     url:"https://comap.org/undergraduate/contests/"},',
     '     url:"https://comap.org/contests"},'),
    ('    {scope:"me", n:"全国大学生市场调查与分析大赛", type:"管理/统计", st:"closed", ai:4, pri:2, team:"组队 / 单人可",',
     '    {scope:"me", n:"全国大学生市场调查与分析大赛", type:"管理/统计", st:"open · 第十七届报名中（10/31 截止）", ai:4, pri:2, team:"组队 / 单人可",'),
]
for old, new in JOBS:
    if s.count(old) != 1:
        sys.exit("锚点命中 %d 次：%r" % (s.count(old), old[:70]))
    s = s.replace(old, new)
io.open(P, "w", encoding="utf-8").write(s)
print("OK：comap 换 /contests；市调转 open")
