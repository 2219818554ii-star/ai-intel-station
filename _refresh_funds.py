# -*- coding: utf-8 -*-
"""基金真刷新：抓最新净值(天天基金 pingzhongdata) + A股/美股最新价(新浪)。
只抓取并打印核验，--write 才写回 funds.js。"""
import re, subprocess, json, datetime, sys, time

SITE = r"C:/Users/22198/WorkBuddy/2026-08-11-19-02-45/ai_daily_site"
FUNDS = ["012920", "024480", "022432", "016452"]

# 重点个股 focus：code -> (mkt, sina_key)
A_STOCKS = {
    "300502": "新易盛", "300308": "中际旭创", "688498": "源杰科技", "688256": "寒武纪",
    "300750": "宁德时代", "603986": "兆易创新", "002371": "北方华创",
}
US_STOCKS = {"NVDA": "英伟达", "AMD": "AMD", "TSM": "台积电", "MU": "美光"}

def curl(url, referer=None):
    cmd = ["curl", "-s", "-A", "Mozilla/5.0", "--max-time", "30"]
    if referer:
        cmd += ["-H", "Referer: " + referer]
    cmd.append(url)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           encoding="utf-8", errors="ignore", timeout=45)
        return r.stdout
    except Exception as e:
        return ""

def bj_date(epoch_ms):
    return (datetime.datetime.utcfromtimestamp(epoch_ms / 1000.0)
            + datetime.timedelta(hours=8)).strftime("%Y-%m-%d")

def fetch_fund_nav(code):
    txt = curl("https://fund.eastmoney.com/pingzhongdata/%s.js" % code)
    m = re.search(r'Data_netWorthTrend\s*=\s*(\[.*?\]);', txt, re.S)
    if not m:
        return None
    try:
        arr = json.loads(m.group(1))
    except Exception:
        return None
    valid = [e for e in arr if isinstance(e, dict) and e.get("y") not in (None, 0, "0")]
    if not valid:
        return None
    last = valid[-1]
    return {"unit": round(float(last["y"]), 4),
            "dayPct": round(float(last.get("equityReturn", 0) or 0) / 100.0, 4),
            "navDate": bj_date(last["x"])}

def fetch_a_share(code):
    mkt = "sh" if code[0] == "6" else "sz"
    txt = curl("http://hq.sinajs.cn/list=%s%s" % (mkt, code), "https://finance.sina.com.cn")
    m = re.search(r'"([^"]*)"', txt)
    if not m:
        return None
    f = m.group(1).split(",")
    if len(f) < 4:
        return None
    prev = float(f[2]); cur = float(f[3])
    dm = re.search(r'(\d{4}-\d{2}-\d{2})', txt)
    return {"price": round(cur, 2), "chg": round((cur - prev) / prev, 4) if prev else 0,
            "date": dm.group(1) if dm else "?"}

def fetch_us(ticker):
    txt = curl("http://hq.sinajs.cn/list=gb_%s" % ticker.lower(), "https://finance.sina.com.cn")
    m = re.search(r'"([^"]*)"', txt)
    if not m:
        return None
    f = m.group(1).split(",")
    cur = float(f[1])
    # 涨跌幅：sina 直接给 f[2]（百分数）
    try:
        chg = round(float(f[2]) / 100.0, 4)
    except Exception:
        chg = 0
    # 美股交易日 = EDT 收盘日，如 "Oct 13 04:00PM EDT"
    MON = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}
    dm = re.search(r'([A-Z][a-z]{2}) (\d{1,2}) \d{2}:\d{2}(AM|PM) EDT', txt)
    date = "?"
    if dm and dm.group(1) in MON:
        date = "2026-%02d-%02d" % (MON[dm.group(1)], int(dm.group(2)))
    return {"price": round(cur, 2), "chg": chg, "date": date}

print("===== 基金净值（天天基金 pingzhongdata）=====")
nav = {}
for c in FUNDS:
    r = fetch_fund_nav(c)
    nav[c] = r
    print("  %s -> %s" % (c, r))
    time.sleep(0.4)

print("===== A股重点股（新浪 hq）=====")
astk = {}
for c, n in A_STOCKS.items():
    r = fetch_a_share(c)
    astk[c] = r
    print("  %s %s -> %s" % (c, n, r))
    time.sleep(0.3)

print("===== 美股重点股（新浪 hq gb_）=====")
ustk = {}
for t, n in US_STOCKS.items():
    r = fetch_us(t)
    ustk[t] = r
    print("  %s %s -> %s" % (t, n, r))
    time.sleep(0.3)

json.dump({"nav": nav, "astk": astk, "ustk": ustk},
          open(SITE + "/funds_refresh_tmp.json", "w"), ensure_ascii=False, indent=1)
print("\nsaved funds_refresh_tmp.json (fetch-only, not written to funds.js)")
