# -*- coding: utf-8 -*-
"""T53c: 自检断言更新（赛事 17 条 / 日期 09-26 / 正在举办>=2）。"""
import io

P = "_selfcheck.js"
t = io.open(P, encoding="utf-8").read()
a = "ok(MATCHES.length === 16, `各学院赛事条数 = ${MATCHES.length}（期望 16）`);"
b = "ok(MATCHES.length === 17, `比赛动态条数 = ${MATCHES.length}（期望 17）`);"
assert t.count(a) == 1
t = t.replace(a, b)

a = "ok((store['cqut-match-updated']||{}).textContent === '2026-09-25', `赛事更新日期: ${(store['cqut-match-updated']||{}).textContent}`);"
b = "ok((store['cqut-match-updated']||{}).textContent === '2026-09-26', `赛事更新日期: ${(store['cqut-match-updated']||{}).textContent}`);"
assert t.count(a) == 1
t = t.replace(a, b)

a = "ok(MATCHES.filter(m => m.st.indexOf('正在举办') === 0).length >= 1,"
b = "ok(MATCHES.filter(m => m.st.indexOf('正在举办') === 0).length >= 2,"
assert t.count(a) == 1
t = t.replace(a, b)
io.open(P, "w", encoding="utf-8").write(t)
print("断言已更新")
