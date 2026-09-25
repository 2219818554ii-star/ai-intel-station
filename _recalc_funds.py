# -*- coding: utf-8 -*-
"""
基金数据重算 _recalc_funds.py
==============================
作用：改完 funds.js 的持仓数字后，自动重算「风格暴露」，不用手算也不会算错。

只做两件事：
  1. 按每只基金的 style 字段（A股 / 海外）重新聚合成 window.FUNDS_EXPOSURE
  2. 打印合计校验值（持仓市值、持有收益、成本、总收益率），供人工比对

用法：python _recalc_funds.py
"""
import io
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
try:
    sys.stdout.reconfigure(encoding="cp936", errors="replace")
except Exception:
    pass


def load(path):
    with io.open(path, encoding="utf-8") as f:
        return f.read()


def main():
    src = load(os.path.join(BASE, "funds.js"))

    m = re.search(r"window\.FUNDS_HOLD\s*=\s*\[(.*?)\];", src, re.S)
    if not m:
        print("❌ 在 funds.js 里找不到 window.FUNDS_HOLD")
        return 1
    body = m.group(1)

    items = []
    for blk in re.findall(r"\{([^{}]*?)\}", body, re.S):
        def g(k):
            mm = re.search(k + r':\s*("(?:[^"\\]|\\.)*"|[\-0-9.eE+]+)', blk)
            if not mm:
                return None
            v = mm.group(1)
            if v.startswith('"'):
                return v.strip('"')
            try:
                return float(v)
            except Exception:
                return v
        items.append({"n": g("n"), "code": g("code"), "style": g("style"),
                      "amt": g("amt"), "holdPL": g("holdPL")})

    bad = [x for x in items if not x["n"] or x["amt"] is None or x["holdPL"] is None]
    if bad:
        print("❌ 有 %d 条持仓缺 amt / holdPL，无法重算：" % len(bad))
        for x in bad:
            print("   ", x["n"], x["code"])
        return 1

    sumAmt = sum(x["amt"] for x in items)
    sumPL = sum(x["holdPL"] for x in items)
    sumCost = sumAmt - sumPL
    totalPct = (sumPL / sumCost) if sumCost > 0 else None

    styles = {}
    for x in items:
        styles[x["style"]] = styles.get(x["style"], 0) + x["amt"]
    total = sum(styles.values()) or 1
    rows = ["{ k: %s, v: %s }" % ('"%s"' % k, round(v, 2)) for k, v in sorted(styles.items(), key=lambda a: -a[1])]
    new_expo = "window.FUNDS_EXPOSURE = [\n  " + ",\n  ".join(rows) + "\n];"

    if re.search(r"window\.FUNDS_EXPOSURE\s*=\s*\[[\s\S]*?\];", src):
        src = re.sub(r"window\.FUNDS_EXPOSURE\s*=\s*\[[\s\S]*?\];", lambda _m: new_expo, src, count=1)
        with io.open(os.path.join(BASE, "funds.js"), "w", encoding="utf-8", newline="") as f:
            f.write(src)

    print("✅ 风格暴露已重算：")
    for k, v in sorted(styles.items(), key=lambda a: -a[1]):
        print("   %-12s %10.2f  (%5.1f%%)" % (k, v, v / total * 100))
    print("")
    print("合计校验（与支付宝对一下）：")
    print("   持仓市值  = %10.2f" % sumAmt)
    print("   持有收益  = %10.2f" % sumPL)
    print("   成本      = %10.2f" % sumCost)
    print("   总收益率  = %s" % ("%+.2f%%" % (totalPct * 100) if totalPct is not None else "—"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
