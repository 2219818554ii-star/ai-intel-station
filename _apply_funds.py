# -*- coding: utf-8 -*-
"""把 _refresh_funds.py 抓到的真值写回 funds.js。
每处 old 子串必须唯一匹配(==1)，否则中止、不写坏文件。"""
import json, sys

SITE = r"C:/Users/22198/WorkBuddy/2026-08-11-19-02-45/ai_daily_site"
P = SITE + "/funds.js"
data = json.load(open(SITE + "/funds_refresh_tmp.json", encoding="utf-8"))
nav, astk, ustk = data["nav"], data["astk"], data["ustk"]

def s(x):
    """float -> 最短十进制串（去尾零，保留符号）"""
    t = ("%f" % x).rstrip("0").rstrip(".")
    return t if t not in ("", "-0") else "0"

def build_prefix(ds, price, chg):
    pct = ("+" if chg >= 0 else "") + ("%.2f%%" % (chg * 100))
    prev = round(price / (1 + chg), 2) if (1 + chg) else 0
    return "%s 收 %.2f（%s，昨收 %.2f）" % (ds, price, pct, prev)

txt = open(P, encoding="utf-8").read()
pairs = []  # (old, new, 说明)

# ---- 1) 基金净值 unit/dayPct/navDate ----
NAV_OLD = {
    "012920": ("3.7460", "-0.0036", "2026-09-30"),
    "024480": ("1.7465", "-0.0448", "2026-10-08"),
    "022432": ("1.1848", "-0.0147", "2026-10-08"),
    "016452": ("2.3425", "0.0014", "2026-09-30"),
}
for c, (ou, op, od) in NAV_OLD.items():
    n = nav[c]
    old = 'unit: %s, dayPct: %s, navDate: "%s"' % (ou, op, od)
    new = 'unit: %s, dayPct: %s, navDate: "%s"' % (s(n["unit"]), s(n["dayPct"]), n["navDate"])
    pairs.append((old, new, "净值 " + c))

# ---- 2) 重点个股 price/cur/chg/date + trend 行情前缀 ----
STK = {
    "300502": ('price:370.20, cur:"¥", chg:-0.0219, date:2026-10-09', '10-09 收 370.20（-2.19%，昨收 378.50）'),
    "300308": ('price:775.29, cur:"¥", chg:-0.0098, date:2026-10-09', '10-09 收 775.29（-0.98%，昨收 783.00）'),
    "688498": ('price:1206.01, cur:"¥", chg:-0.0654, date:2026-10-09', '10-09 收 1206.01（-6.54%，昨收 1290.40）'),
    "688256": ('price:985.99, cur:"¥", chg:0.0051, date:2026-10-09', '10-09 收 985.99（+0.51%，昨收 981.00）'),
    "300750": ('price:297.75, cur:"¥", chg:0.0384, date:2026-10-09', '10-09 收 297.75（+3.84%，昨收 286.75）'),
    "603986": ('price:326.46, cur:"¥", chg:-0.0237, date:2026-10-09', '10-09 收 326.46（-2.37%，昨收 334.40）'),
    "002371": ('price:594.04, cur:"¥", chg:-0.0105, date:2026-10-09', '10-09 收 594.04（-1.05%，昨收 600.32）'),
    "NVDA":   ('price:230.48, cur:"$", chg:-0.0294, date:2026-10-08', '10-08 收 230.48（-2.94%，昨收 237.47）'),
    "AMD":    ('price:620.68, cur:"$", chg:-0.039, date:2026-10-08', '10-08 收 620.68（-3.90%，昨收 645.86）'),
    "TSM":    ('price:457.99, cur:"$", chg:-0.0301, date:2026-10-08', '10-08 收 457.99（-3.01%，昨收 472.20）'),
    "MU":     ('price:1035.84, cur:"$", chg:-0.0479, date:2026-10-08', '10-08 收 1035.84（-4.79%，昨收 1088.0）'),
}
for code, (old_line, old_pref) in STK.items():
    if code in astk:
        n, cur, ds = astk[code], "¥", "10-14"
    else:
        n, cur, ds = ustk[code], "$", "10-13"
    price, chg, date = n["price"], n["chg"], n["date"]
    new_line = 'price:%.2f, cur:"%s", chg:%s, date:%s' % (price, cur, s(chg), date)
    new_pref = build_prefix(ds, price, chg)
    pairs.append((old_line, new_line, "价格 " + code))
    pairs.append((old_pref, new_pref, "行情前缀 " + code))

# ---- 校验唯一性 ----
bad = 0
for old, new, tag in pairs:
    c = txt.count(old)
    if c != 1:
        print("!! [%s] 匹配 %d 次(期望1)：%r" % (tag, c, old[:60]))
        bad += 1
if bad:
    print("中止：%d 处未唯一匹配，未写盘" % bad)
    sys.exit(1)

# ---- 应用 ----
for old, new, tag in pairs:
    txt = txt.replace(old, new)
open(P, "w", encoding="utf-8").write(txt)
print("已写回 funds.js：%d 处替换（4 净值 + 11 价格行 + 11 行情前缀）" % len(pairs))
