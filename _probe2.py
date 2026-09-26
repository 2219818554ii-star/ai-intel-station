# -*- coding: utf-8 -*-
"""探测候选新官网是否可达，输出报告文件防管道截断。"""
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"

URLS = [
    ("金相技能大赛", "https://www.jxds.tech/"),
    ("统计建模大赛", "http://tjjmds.ai-learning.net/"),
    ("统计建模(备)  ", "http://www.ai-learning.net/p91/index.html"),
    ("光威杯复合材料", "https://cmtic.csfcm.org.cn/"),
    ("市场调查与分析", "http://www.china-cssc.org/"),
    ("能源经济", "http://energy.qibebt.ac.cn/eneco/"),
    ("结构设计竞赛", "http://www.structurecontest.com/"),
    ("智能汽车竞赛", "http://www.eepw.com.cn/event/action/freescale_car2012/"),
    ("物理实验竞赛", "https://wlsycx.moocollege.com/home/homepage"),
    ("中国创翼", "http://www.cxcyds.com/"),
    ("物联网设计", "http://www.iotcontest.net/"),
    ("西门子杯", "http://www.siemenscup.com/"),
    ("共享杯", "http://share.escience.net.cn"),
    ("环境生态", "http://www.csec.org.cn"),
    ("生物制药", "http://www.biopharm.org.cn"),
    ("复合材料 frp.cn", "http://www.frp.cn"),
    ("材料热处理", "http://www.cmes.org"),
    ("冶金科技", "http://www.csm.org.cn"),
    ("水利创新设计", "http://www.cahee.org.cn/"),
    ("化工安全设计", "http://www.ciedu.com.cn/"),
]


def probe(item):
    name, url = item
    r = {"name": name, "url": url}
    try:
        p = subprocess.run(
            ["curl", "-sS", "--compressed", "-A", UA, "-L", "--max-time", "25",
             "-o", "-", "-w", "%{http_code}|%{url_effective}", url],
            capture_output=True, timeout=40,
        )
        out = p.stdout.decode("utf-8", "replace")
        r["code"] = out[-80:].strip()
    except Exception as e:
        r["code"] = "ERR " + str(e)[:60]
    return r


with ThreadPoolExecutor(max_workers=8) as ex:
    res = list(ex.map(probe, URLS))

lines = []
for r in res:
    lines.append("%-14s %-55s %s" % (r["name"], r["url"], r["code"]))
txt = "\n".join(lines)
open("_probe2.txt", "w", encoding="utf-8").write(txt)
print(txt)
