# -*- coding: utf-8 -*-
"""讲坛真刷新：逐条验活 BV + 刷新播放量(B站 view API)。
死链(62002/62004/404/62012)记下不自动删(避免系列<3)；风控(-412)重试、不误判、保留旧值。"""
import re, subprocess, json, time

SITE = r"C:/Users/22198/WorkBuddy/2026-08-11-19-02-45/ai_daily_site"
P = SITE + "/forum.js"
txt = open(P, encoding="utf-8").read()
bvids = list(dict.fromkeys(re.findall(r'"bvid":"(BV[0-9A-Za-z]+)"', txt)))
print("unique bvids:", len(bvids), flush=True)

DEAD = {62002, 62004, 62012, -404, 404, 62003}

def api(bvid):
    for attempt in range(3):
        try:
            r = subprocess.run(
                ["curl", "-s", "-A", "Mozilla/5.0", "-H", "Referer: https://www.bilibili.com",
                 "--max-time", "20", "https://api.bilibili.com/x/web-interface/view?bvid=" + bvid],
                capture_output=True, text=True, timeout=30)
            d = json.loads(r.stdout)
            code = d.get("code")
            if code == 0:
                return {"ok": True, "view": d["data"]["stat"]["view"], "title": d["data"]["title"]}
            if code in DEAD:
                return {"ok": False, "code": code}
            # -412 风控等：退避重试
            time.sleep(1.5 + attempt)
        except Exception:
            time.sleep(1.5)
    return {"ok": False, "code": "THROTTLE"}

res = {}
for i, bv in enumerate(bvids):
    res[bv] = api(bv)
    if i % 25 == 0:
        print(f"  {i}/{len(bvids)}", flush=True)
    time.sleep(0.3)

def repl_line(line):
    m = re.search(r'"bvid":"(BV[0-9A-Za-z]+)"', line)
    if not m:
        return line
    r = res.get(m.group(1))
    if r and r["ok"]:
        return re.sub(r'"play":\d+', '"play":%d' % r["view"], line, count=1)
    return line

newtxt = "\n".join(repl_line(l) for l in txt.split("\n"))
open(P, "w", encoding="utf-8").write(newtxt)

dead = [(bv, r["code"]) for bv, r in res.items() if not r["ok"] and r["code"] != "THROTTLE"]
thr = [bv for bv, r in res.items() if r.get("code") == "THROTTLE"]
print("DEAD:", len(dead))
for bv, c in dead:
    print("  DEAD", c, bv)
print("THROTTLED(保留旧值):", len(thr))
json.dump(res, open(SITE + "/forum_refresh_tmp.json", "w"), ensure_ascii=False)
print("done")
