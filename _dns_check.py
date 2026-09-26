# -*- coding: utf-8 -*-
"""对探测中不可达的站点做 DNS 层验证，区分「域名已死」与「境外被墙/站点自身故障」。"""
import json
import socket
import subprocess
from concurrent.futures import ThreadPoolExecutor

HOSTS = [
    "neurips.cc", "wmt-conf.net", "www.chalearn.org", "solardecathlon.net",
    "www.darpa.mil", "www.icho.science", "www.spaceappschallenge.org",
    "www.huacanjiang.com", "www.cmatd.cn", "www.matibei.com", "www.c4best.cn",
    "www.comap.com", "www.flyai.com", "www.autodrive.ai", "waymo.com",
    "spacenet.ai", "www.csec.org.cn", "www.jxskills.cn", "www.gw-cup.com",
    "www.biopharm.org.cn", "www.ches.org.cn", "www.ceeea.org",
    "www.china-cma.org", "www.siemenscup.com",
    "www.smartcar.au.tsinghua.edu.cn", "www.robocon.net", "www.putiyi.com",
    "www.physlab.cn", "www.structure.org.cn", "www.cxcyds.cn",
    "www.iotcontest.net", "share.escience.net.cn", "tjjmds.aii.edu.cn",
    "codalab.lisn.upsaclay.fr", "developers.google.com",
    "codingcompetitions.withgoogle.com", "www.facebook.com",
    "quantum-computing.ibm.com", "huggingface.co",
    "image-net.org", "www.chemecar.cn", "www.nfsoc.org.cn", "www.cres.org.cn",
    "www.csm.org.cn", "www.frp.cn", "www.cmes.org",
]


def check(h):
    h2 = h.split("/")[0]
    out = {"host": h2, "dns": None, "ip": None, "err": None}
    try:
        infos = socket.getaddrinfo(h2, None)
        ips = sorted({i[4][0] for i in infos})
        out["dns"] = "OK"
        out["ip"] = ",".join(ips[:2])
    except Exception as e:
        out["err"] = str(e)[:80]
    return out


with ThreadPoolExecutor(max_workers=10) as ex:
    res = list(ex.map(check, HOSTS))

bad_dns = [r for r in res if r["dns"] != "OK"]
ok_dns = [r for r in res if r["dns"] == "OK"]
print("DNS 解析失败（域名可能已注销/未注册）：%d 条" % len(bad_dns))
for r in bad_dns:
    print("   ", r["host"], "->", r["err"])
print("\nDNS 正常（站点仍在，502/000 多为境外访问限制或站点临时故障）：%d 条" % len(ok_dns))
for r in ok_dns:
    print("   ", r["host"], "->", r["ip"])

with open("_dns_report.json", "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
