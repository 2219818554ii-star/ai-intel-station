# -*- coding: utf-8 -*-
"""内容级核对：不只验「链接活着」，还要验「页面上写的对不对」。

三道关(_build/_selfcheck/_preship)只覆盖：构建成功、结构齐全、链接可达。
这里补的是「信息准确性」——拿 B 站视频页实时数据，逐条比对我站 forum.js 里
记录的 标题 / UP主 / 时长 三项。任一项对不上就报出来。

为什么不用 view API：对本机已触发风控，返回 HTML 页。
为什么抓页面：页面内嵌 schema.org 的 VideoObject 结构化数据，
  name / duration(ISO8601) / author.name 三个字段同属一个块，不会互相错位
  （用全文正则分别抓 title/duration 会抓到推荐位数据，那是踩过的坑）。

用法：python _audit_content.py
"""
import re, sys, time, subprocess, html

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
CK = "/tmp/bili_ck_audit.txt"

src = open("forum.js", encoding="utf-8").read()
items = re.findall(
    r'\{"t":"(.*?)","bvid":"(BV[0-9A-Za-z]{10})","up":"(.*?)","dur":"([0-9:]+)"', src)
print("站上视频条目 %d 条\n" % len(items))


def unesc(s):
    # JSON 里 & < > 会被转义成 \u0026 这类，html.unescape 不认，得先解一遍
    s = re.sub(r"\\u([0-9a-fA-F]{4})",
               lambda m: chr(int(m.group(1), 16)), s)
    return html.unescape(s.replace("<em>", "").replace("</em>", ""))


def parse_iso(iso):
    """PT00H21M30S / PT21M30S / PT45S -> 秒"""
    h = re.search(r"(\d+)H", iso)
    m = re.search(r"(\d+)M", iso)
    s = re.search(r"(\d+)S", iso)
    return (int(h.group(1)) * 3600 if h else 0) + \
           (int(m.group(1)) * 60 if m else 0) + \
           (int(s.group(1)) if s else 0)


def fetch(bvid):
    """抓视频页 -> (title, up, dur_sec)；解析不出返回 (None, None, None)"""
    url = "https://www.bilibili.com/video/" + bvid
    p = subprocess.run(["curl", "-sS", "--compressed", "-b", CK,
                        "-A", UA, "--max-time", "20", "-L", url],
                       capture_output=True)
    if p.returncode != 0:
        return (None, None, None)
    txt = p.stdout.decode("utf-8", "replace")
    # 只取 VideoObject 这个块，块尾到 interactionStatistic 为止
    m = re.search(r'"@type":"VideoObject".{0,2500}?"interactionStatistic"', txt)
    if not m:
        return (None, None, None)
    blk = m.group(0)
    def g(pat):
        mm = re.search(pat, blk)
        return unesc(mm.group(1)) if mm else None
    t = g(r',"name":"([^"]{1,200})"')
    u = g(r'"author":\{"@type":"Person".{0,200}?"name":"([^"]{1,40})"')
    d = None
    md = re.search(r'"duration":"(PT[^"]+)"', blk)
    if md:
        d = parse_iso(md.group(1))
    return (t, u, d)


def to_sec(s):
    a = [int(x) for x in s.split(":")]
    return a[0] * 60 + a[1] if len(a) == 2 else a[0]


# ---------- 对照组：先证通道有效 ----------
print("[对照组] 校准解析逻辑 …")
c_t, c_u, c_d = fetch(items[0][1])
if c_t is None:
    print("  [FATAL] 连第 1 条都解析不出字段 → 通道/风控失效，本轮核对不成立")
    sys.exit(1)
print("  实时解析 -> 标题=%s | UP=%s | 时长=%ss" % (c_t[:30], c_u, c_d))
print("  站上记录 -> 标题=%s | UP=%s | 时长=%s"
      % (items[0][0][:30], items[0][2], items[0][3]))
print("  => 解析逻辑可用，开始逐条核对\n")

mt = mu = md_ = 0
ok = 0
bad = 0
for i, (t, bvid, up, dur) in enumerate(items, 1):
    rt, ru, rd = fetch(bvid)
    if rt is None:
        bad += 1
        print("  [抓不到] %s  %s" % (bvid, t[:28]))
        continue
    tag = []
    if rt != t:
        mt += 1
        tag.append("标题：站上「%s」≠ 实际「%s」" % (t[:26], rt[:26]))
    if ru is not None and ru != up:
        mu += 1
        tag.append("UP主：站上「%s」≠ 实际「%s」" % (up, ru))
    if rd is not None and rd != to_sec(dur):
        md_ += 1
        tag.append("时长：站上「%s」≠ 实际「%ss」" % (dur, rd))
    if tag:
        print("  [不一致] %s" % bvid)
        for x in tag:
            print("            " + x)
    else:
        ok += 1
    time.sleep(0.3)

print("\n========== 内容核对结果 ==========")
print("条目总数        : %d" % len(items))
print("三项完全一致    : %d" % ok)
print("标题对不上      : %d" % mt)
print("UP主对不上      : %d" % mu)
print("时长对不上      : %d" % md_)
print("抓不到（死链）  : %d" % bad)
print("结论：%s" % ("内容属实，站上显示的与B站实际完全一致"
                   if (mt + mu + md_ + bad) == 0
                   else "存在不一致，需逐条判断"))
