# -*- coding: utf-8 -*-
"""T50c: 自检补参赛指令/平台赛分析断言。"""
import io
import sys

P = "_selfcheck.js"
t = io.open(P, encoding="utf-8").read()

anchor = "/* 页面必须能把 warn 渲染出来 */"
if anchor not in t:
    sys.exit("锚点未找到")

ADD = """/* 参赛指令 + 平台赛分析（2026-09-26 需求） */
const subN = CP.filter(c => (c.sub || '').length).length;
ok(subN >= 4, `平台型赛事「内含赛怎么挑」分析 >= 4 条（当前 ${subN}）`);
ok(html.includes('cpPrompt'), '参赛指令生成函数 cpPrompt 已内联');
const compHtml = (store['comp-list'] || {}).innerHTML || '';
ok(compHtml.includes('复制参赛指令'), '比赛卡片渲染出「复制参赛指令」按钮');
ok(html.includes('内含赛怎么挑'), '卡片模板支持渲染平台赛分析行');

"""
t = t.replace(anchor, ADD + anchor)
io.open(P, "w", encoding="utf-8").write(t)
print("自检已补")
