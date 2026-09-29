# -*- coding: utf-8 -*-
"""基金看板「风格暴露」重算 + 合计校验 + 净值体检。

用法：python _recalc_funds.py [--write]
  --write  若重算出的风格暴露与 funds.js 现有值不一致，则写回 funds.js。
           默认只体检、不写盘（避免自动化误提交）。

说明：
  * funds.js 是 JS，含对象字面量，Python 无法 exec，改用 Node 的 vm 求值。
  * amt / holdPL / holdPct 是罗浩本人账户数据，本脚本只读，绝不改动。
  * unit / dayPct / navDate 是每日例抓的最新已公布净值，本脚本只体检一致性。
"""
import io
import json
import os
import subprocess
import sys
import tempfile

BASE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(BASE, "funds.js")
NODE_CANDIDATES = [
    r"C:\Users\22198\.workbuddy\binaries\node\versions\22.22.2-3\node.exe",
    "node",
]


def find_node():
    for c in NODE_CANDIDATES:
        if os.path.exists(c):
            return c
    import shutil
    return shutil.which("node") or "node"

JS_HOOK = r"""
const fs = require('fs');
const vm = require('vm');
const win = {};
win.window = win;
const ctx = vm.createContext({ window: win, console });
vm.runInContext(fs.readFileSync(process.argv[2], 'utf8'), ctx, { filename: 'funds.js' });
const H = win.FUNDS_HOLD || [];
const E = win.FUNDS_EXPOSURE || [];
const D = (win.FUNDS_DEEP || {}).byCode || {};
/* 注意：JS 的 Math.round(x, n) 会忽略第 2 个参数，只取整，必须自己按百分位收 */
const r2 = x => Math.round(x * 100) / 100;
const agg = {};
for (const f of H) agg[f.style] = r2((agg[f.style] || 0) + (f.amt || 0));
const stamps = {};
for (const f of H) { const d = D[f.code] || {}; stamps[f.code] = { unit: f.unit, navDate: f.navDate, dayPct: f.dayPct, deepNav: d.nav, deepDate: d.navDate }; }
const out = {
  agg: agg,
  exposure: E,
  newExposure: Object.keys(agg).map(k => ({ k: k, v: agg[k] })).sort((a, b) => b.v - a.v),
  n: H.length,
  totalAmt: r2(H.reduce((a, f) => a + (f.amt || 0), 0)),
  totalPL: r2(H.reduce((a, f) => a + (f.holdPL || 0), 0)),
  stamps: stamps
};
console.log('__JSON__' + JSON.stringify(out));
"""


def run_node(path):
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
        f.write(JS_HOOK)
        hook = f.name
    try:
        r = subprocess.run([find_node(), hook, path], capture_output=True,
                           text=True, encoding="utf-8", timeout=60)
        if r.returncode != 0:
            print("!! node 执行失败:", r.stderr.strip(), file=sys.stderr)
            return None
        for line in r.stdout.splitlines():
            if line.startswith("__JSON__"):
                return json.loads(line[len("__JSON__"):])
        print("!! 未拿到 JSON 输出", file=sys.stderr)
        return None
    finally:
        os.unlink(hook)


def main():
    write = "--write" in sys.argv
    res = run_node(P)
    if res is None:
        return 1

    print("== 风格暴露（按持仓 amt 归集） ==")
    old = {e["k"]: e["v"] for e in res["exposure"]}
    for k, v in sorted(res["agg"].items(), key=lambda x: -x[1]):
        d = "" if old.get(k) == v else f"  ← funds.js 现值 {old.get(k)}"
        print(f"  {k}: {v}{d}")

    drift = [e for e in res["newExposure"] if old.get(e["k"]) != e["v"]]
    if drift:
        print(f"  差异 {len(drift)} 项 → 建议 `python _recalc_funds.py --write` 写回")
        if write:
            txt = io.open(P, encoding="utf-8").read()
            newmap = {e["k"]: e["v"] for e in res["newExposure"]}
            import re as _re
            def _rep(m):
                k = m.group(1)
                return m.group(0).split(":")[0] + f': "{k}", v: {newmap[k]}'
            txt2 = _re.sub(r'\{ k: "([^"]+)", v: [\d.]+ \}',
                           lambda m: m.group(0).split(":")[0] + f': "{m.group(1)}", v: {newmap[m.group(1)]}', txt)
            io.open(P, "w", encoding="utf-8").write(txt2)
            print("  → 已写回 funds.js")
        else:
            return 2
    else:
        print("  与 funds.js 现有值完全一致，无需改动")

    print("== 合计校验 ==")
    print(f"  持仓条数 = {res['n']}（期望 4）")
    print(f"  合计持有金额 amt = {res['totalAmt']}")
    print(f"  合计持有收益 holdPL = {res['totalPL']}")
    tot_pct = res["totalPL"] / res["totalAmt"] if res["totalAmt"] else 0
    print(f"  总收益率 = {tot_pct * 100:.2f}%")

    print("== 最新已公布净值 + 持仓/深度档案一致性 ==")
    bad = 0
    for c, s in res["stamps"].items():
        miss = s["unit"] is None or not s["navDate"]
        if miss:
            bad += 1
        same = (s["unit"] == s["deepNav"] and s["navDate"] == s["deepDate"])
        if not same:
            bad += 1
        print(f"  {c}  单位净值={s['unit']}  日增长率={s['dayPct']}  净值日={s['navDate']}"
              f"  [{'OK' if not miss else '净值缺失'}{'' if same else ' / 与深度档案不一致'}]")
    if bad:
        print(f"!! {bad} 处异常（缺失或漂移），页面可能显示「—」", file=sys.stderr)
        return 3
    print("  OK：4 只净值齐全，持仓与深度档案一致")
    return 0


if __name__ == "__main__":
    sys.exit(main())
