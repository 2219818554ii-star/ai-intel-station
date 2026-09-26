# -*- coding: utf-8 -*-
"""按行号替换赛事官网：全部来自 2026-09-26 实测（200）或教育部竞赛目录/组委会通知。
   每条都带上下文校验，任一不匹配即中止，不落盘。"""
import sys

P = "competitions.js"
L = open(P, encoding="utf-8").read().split("\n")

# (行号1based, 前一行须含的赛事名关键字, 原 url 值, 新 url 值)
JOBS = [
    (533, "金相技能", "http://www.jxskills.cn", "https://www.jxds.tech/"),
    (548, "光威杯", "http://www.gw-cup.com", "https://cmtic.csfcm.org.cn/"),
    (588, "能源经济", "http://www.ceeea.org", "https://energy.qibebt.ac.cn/eneco/"),
    (603, "市场调查", "http://www.china-cma.org", "http://www.china-cssc.org/"),
    (628, "智能汽车", "http://www.smartcar.au.tsinghua.edu.cn",
     "https://www.eepw.com.cn/event/action/freescale_car2012/"),
    (678, "物理实验", "http://www.physlab.cn", "https://wlsycx.moocollege.com/home/homepage"),
    (683, "结构设计", "http://www.structure.org.cn", "http://www.structurecontest.com/"),
    (713, "中国创翼", "http://www.cxcyds.cn", "http://www.cxcyds.com/"),
    (723, "物联网设计", "http://www.iotcontest.net", "https://iot.sjtu.edu.cn/"),
    (748, "统计建模", "http://tjjmds.aii.edu.cn", "http://tjjmds.ai-learning.net/"),
    (538, "材料热处理", "http://www.cmes.org", "https://www.cmes.org/cmes"),
    (543, "复合材料", "http://www.frp.cn", "http://frp.cn/"),
]

for ln, key, oldu, newu in JOBS:
    i = ln - 1
    exp = '     url:"%s"},' % oldu
    if L[i] != exp:
        sys.exit("L%d 原串不符：%r\n期望：%r" % (ln, L[i], exp))
    if key not in "".join(L[max(0, i - 7):i]):
        sys.exit("L%d 上下文找不到赛事名「%s」" % (ln, key))
    L[i] = '     url:"%s"},' % newu

open(P, "w", encoding="utf-8").write("\n".join(L))
print("已改 %d 条官网" % len(JOBS))
