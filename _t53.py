# -*- coding: utf-8 -*-
"""T53: 重理工栏目赛事块前置 + 新增逐梦杯 + 更新自检。"""
import io
import sys

# ---------- 1) cqut.js：加逐梦杯、更新日期、改天翼文案 ----------
P = "cqut.js"
s = io.open(P, encoding="utf-8").read()

old_date = 'window.CQUT_MATCH_UPDATED = "2026-09-25";'
new_date = 'window.CQUT_MATCH_UPDATED = "2026-09-26";'
if s.count(old_date) != 1:
    sys.exit("MATCH_UPDATED 锚点异常")
s = s.replace(old_date, new_date)

old_tail = ('   url:"https://www.cqut.edu.cn/2025clnr.jsp?urltype=news.NewsContentUrl&wbtreeid=1101&wbnewsid=72172"}\n];')
new_tail = '''   url:"https://www.cqut.edu.cn/2025clnr.jsp?urltype=news.NewsContentUrl&wbtreeid=1101&wbnewsid=72172"},
  {n:"关于举办2026年重庆理工大学第十届“逐梦杯”学生男子五人制足球比赛的通知", org:"学校体育运动委员会（体育部指导 · 学生体育联盟承办）", lv:"校级",
   st:"正在举办 · 报名进行中", date:"2026-09-21", tag:"oth", fit:0,
   intro:"【正在举办的赛事，不是获奖报道】第十届“逐梦杯”学生男子五人制足球赛，面向各学院组队。这是学校通知栏里 9 月新发的另一条真·报名赛事——别看是足球，学院组队走的是辅导员/体育委员渠道。",
   todo:"以学院为单位组队报名。主办：校体育运动委员会；指导：体育部；承办：学生体育联盟。报名口径、赛程、人数限制以源通知正文为准，点开读完再找你们学院体育委员。",
   help:"跟你科研主线无关，纯属校园生活项。要参加我能帮你：① 把通知拆成「报名条件/人数/时间/联系人」速览；② 给你一份五人制战术速成小抄。",
   url:"https://www.cqut.edu.cn/info/1101/72107.htm"}
];'''
if s.count(old_tail) != 1:
    sys.exit("天翼条目尾部锚点异常")
s = s.replace(old_tail, new_tail)

old_intro = "这是本栏目里目前唯一一条真正在办的比赛。"
new_intro = "学校通知栏 9 月共两条真·报名赛事，这是其中之一（另一条是逐梦杯足球赛）。"
if s.count(old_intro) != 1:
    sys.exit("天翼 intro 锚点异常")
s = s.replace(old_intro, new_intro)
io.open(P, "w", encoding="utf-8").write(s)
print("cqut.js：+逐梦杯，日期 09-26")

# ---------- 2) index.src.html：赛事块挪到最前并改名 ----------
P2 = "index.src.html"
h = io.open(P2, encoding="utf-8").read()
i0 = h.index('<div id="view-cqut"')
i1 = h.index('<div id="view-funds"')
blk = h[i0:i1]

MARK_A = '    <div class="cmp-toolbar" id="cqutFilters">'
MARK_B = '    <div class="view-head" style="margin-top:32px">\n      <h2 style="font-size:20px">? 各学院赛事'
iA = blk.index(MARK_A)
iB = blk.index(MARK_B)
iC = blk.index('    <div class="view-head" style="margin-top:30px">\n      <h2 style="font-size:20px">? 全部信源直达')
notice_sec = blk[iA:iB]          # 通知筛选+列表
match_sec = blk[iB:iC]           # 赛事节（view-head + 筛选 + list + tip）

# 改赛事节标题与说明
match_sec = match_sec.replace(
    '? 各学院赛事 · 谁主办、要干嘛、我能帮你做啥',
    '🏁 比赛动态 · 正在举办的排最前')
match_sec = match_sec.replace(
    '从各学院官网和学校新闻里实抓的赛事记录，URL 全都真实可点，没编一条。多数是<b>上一届的获奖通报</b>——想上场得盯下一届的报名通知。',
    '你想报名而不是看别人获奖——所以这条置顶了。实抓自学校/学院官网，URL 全部真实可点。实话：学院通知栏平时基本只发<b>获奖通报</b>，真·报名赛事很少，要打全国赛请配合 <b>🏁 可报名比赛</b> 那个 tab 一起看。')

blk2 = blk[:iA] + match_sec + notice_sec + blk[iC:]
# 赛事节挪上去后，通知块的筛选条紧跟其后，间距微调
blk2 = blk2.replace('<div class="cmp-toolbar" id="cqutFilters">\n      <button class="filterbtn active" data-c="全部">全部</button>',
                    '<div class="cmp-toolbar" id="cqutFilters" style="margin-top:26px">\n      <button class="filterbtn active" data-c="全部">全部</button>', 1)
h = h[:i0] + blk2 + h[i1:]
io.open(P2, "w", encoding="utf-8").write(h)
print("index.src.html：赛事块已置顶改名")

# ---------- 3) _selfcheck.js：16→17、日期 ----------
P3 = "_selfcheck.js"
t = io.open(P3, encoding="utf-8").read()
t = t.replace("ok(MATCHES.length === 16, `各学院赛事条数 = ${MATCHES.length}（期望 16）`);",
              "ok(MATCHES.length === 17, `比赛动态条数 = ${MATCHES.length}（期望 17）`);")
t = t.replace("ok((store['cqut-match-updated']||{}).textContent === '2026-09-25', `赛事更新日期: ${(store['cqut-match-updated']||{}).textContent}`);",
              "ok((store['cqut-match-updated']||{}).textContent === '2026-09-26', `赛事更新日期: ${(store['cqut-match-updated']||{}).textContent}`);")
# 至少 1 条正在举办 → 至少 2 条（天翼 + 逐梦杯）
t = t.replace("ok(MATCHES.filter(m => m.st.indexOf('正在举办') === 0).length >= 1,",
              "ok(MATCHES.filter(m => m.st.indexOf('正在举办') === 0).length >= 2,")
io.open(P3, "w", encoding="utf-8").write(t)
print("_selfcheck.js：断言已更新")
