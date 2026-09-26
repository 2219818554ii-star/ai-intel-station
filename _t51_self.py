# -*- coding: utf-8 -*-
"""T51 自检动态化：TED 断言跟随数据，不再写死。"""
import io

P = "_selfcheck.js"
t = io.open(P, encoding="utf-8").read()

a = "ok(cards('ted-list') === 25, `TED 卡片 = ${cards('ted-list')}（期望 25）`);"
b = "const TD = sandbox.window.TED || [];\nok(cards('ted-list') === TD.length && TD.length >= 40, `TED 卡片 = ${cards('ted-list')}（=数据 ${TD.length} 条，要求 >=40）`);"
assert t.count(a) == 1
t = t.replace(a, b)

a = "ok((store['ted-stat']||{}).textContent === '共 25 场（全部 25 场）', `TED 统计: ${(store['ted-stat']||{}).textContent}`);"
b = "ok((store['ted-stat']||{}).textContent === `共 ${TD.length} 场（全部 ${TD.length} 场）`, `TED 统计: ${(store['ted-stat']||{}).textContent}`);"
assert t.count(a) == 1
t = t.replace(a, b)

a = "ok(cards('ted-list') === 4, `TED「学习成长」→ ${cards('ted-list')} 条（期望 4）`);"
b = ("const expLearn = TD.filter(x => x.cat === '学习成长').length;\n"
     "ok(cards('ted-list') === expLearn, `TED「学习成长」→ ${cards('ted-list')} 条（期望 ${expLearn}）`);")
assert t.count(a) == 1
t = t.replace(a, b)

a = "ok(cards('ted-list') === 7, `TED「认知思维」→ ${cards('ted-list')} 条（期望 7）`);"
b = ("const expCog = TD.filter(x => x.cat === '认知思维').length;\n"
     "ok(cards('ted-list') === expCog, `TED「认知思维」→ ${cards('ted-list')} 条（期望 ${expCog}）`);")
assert t.count(a) == 1
t = t.replace(a, b)

io.open(P, "w", encoding="utf-8").write(t)
print("TED 断言已动态化")
