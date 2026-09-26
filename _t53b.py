# -*- coding: utf-8 -*-
"""T53b: 仅处理 index.src.html 的赛事块前置（cqut.js 已在 _t53.py 完成）。"""
import io
import sys

P2 = "index.src.html"
h = io.open(P2, encoding="utf-8").read()
if "比赛动态 · 正在举办的排最前" in h:
    print("已应用过，跳过")
    sys.exit(0)

i0 = h.index('<div id="view-cqut"')
i1 = h.index('<div id="view-funds"')
blk = h[i0:i1]

iA = blk.index('    <div class="cmp-toolbar" id="cqutFilters">')
iB = blk.index('各学院赛事 · 谁主办')
iB = blk.rindex('<div class="view-head"', 0, iB)
iC = blk.index('全部信源直达', iB)
iC = blk.rindex('<div class="view-head"', 0, iC)

notice_sec = blk[iA:iB]
match_sec = blk[iB:iC]

match_sec = match_sec.replace(
    "各学院赛事 · 谁主办、要干嘛、我能帮你做啥",
    "比赛动态 · 正在举办的排最前")
match_sec = match_sec.replace(
    "从各学院官网和学校新闻里实抓的赛事记录，URL 全都真实可点，没编一条。多数是<b>上一届的获奖通报</b>——想上场得盯下一届的报名通知。",
    "你想报名而不是看别人获奖——所以这块置顶了。实抓自学校/学院官网，URL 全部真实可点。实话：学院通知栏平时基本只发<b>获奖通报</b>，真·报名赛事很少，要打全国赛请配合 <b>🏁 可报名比赛</b> 那个 tab 一起看。")
assert "比赛动态 · 正在举办的排最前" in match_sec

blk2 = blk[:iA] + match_sec + notice_sec + blk[iC:]
blk2 = blk2.replace('<div class="cmp-toolbar" id="cqutFilters">\n      <button class="filterbtn active" data-c="全部">',
                    '<div class="cmp-toolbar" id="cqutFilters" style="margin-top:26px">\n      <button class="filterbtn active" data-c="全部">', 1)
h = h[:i0] + blk2 + h[i1:]
io.open(P2, "w", encoding="utf-8").write(h)
print("index.src.html：赛事块已置顶改名")
