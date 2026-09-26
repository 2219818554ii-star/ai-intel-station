# -*- coding: utf-8 -*-
"""T51a: TED 从 25 条扩到 40 条（全部公认经典，官方 slug 留底）。"""
import io
import sys

P = "ted.js"
s = io.open(P, encoding="utf-8").read()

OLD = 'window.TED_UPDATED = "2026-09-22";'
NEW = 'window.TED_UPDATED = "2026-09-26";'
assert s.count(OLD) == 1
s = s.replace(OLD, NEW)

ADD = '''  /* ===== 2026-09-26 扩容 +15 条 ===== */
  /* ===== 学习成长 ===== */
  {en:"Try something new for 30 days", zh:"用 30 天尝试新事物", sp:"Matt Cutts", yr:2011, dur:3, cat:"学习成长", sub:"习惯养成",
   intro:"Google 工程师的 3 分钟小实验：把想做的事拆成 30 天挑战。时间短到没借口，最适合当『开始行动』的第一支 TED。",
   url:"https://www.ted.com/talks/matt_cutts_try_something_new_for_30_days"},
  {en:"Every kid needs a champion", zh:"每个孩子都需要一个坚定支持者", sp:"Rita Pierson", yr:2013, dur:7, cat:"学习成长", sub:"师生关系",
   intro:"从教 40 年的名师金句：『孩子不跟讨厌的人学』。讲师生关系如何决定学习效果——读研跟导师相处同样适用。",
   url:"https://www.ted.com/talks/rita_pierson_every_kid_needs_a_champion"},
  {en:"Inside the mind of a master procrastinator", zh:"拖延症大师的脑子里在想什么", sp:"Tim Urban", yr:2016, dur:14, cat:"学习成长", sub:"拖延症",
   intro:"instant gratification monkey（及时行乐猴）梗的出处，写论文的人都懂。幽默+自嘲，听力友好，看完你会立刻去改稿。",
   url:"https://www.ted.com/talks/tim_urban_inside_the_mind_of_a_master_procrastinator"},

  /* ===== 心理幸福 ===== */
  {en:"The power of vulnerability", zh:"脆弱的力量", sp:"Brené Brown", yr:2010, dur:20, cat:"心理幸福", sub:"自我接纳",
   intro:"TED 史上播放量第二。Brown 用十年研究讲『允许自己脆弱』才是连接感和勇气的来源。科研受挫时看，比鸡汤管用。",
   url:"https://www.ted.com/talks/brene_brown_the_power_of_vulnerability"},
  {en:"How to make stress your friend", zh:"如何让压力成为你的朋友", sp:"Kelly McGonigal", yr:2013, dur:14, cat:"心理幸福", sub:"压力管理",
   intro:"健康心理学家反转结论：杀人的不是压力本身，而是『压力有害』这个信念。实验设计讲得清楚，顺便学健康心理学词汇。",
   url:"https://www.ted.com/talks/kelly_mcgonigal_how_to_make_stress_your_friend"},
  {en:"Sleep is your superpower", zh:"睡眠是你的超能力", sp:"Matt Walker", yr:2019, dur:19, cat:"心理幸福", sub:"睡眠",
   intro:"睡眠科学家讲睡眠如何影响记忆、免疫与寿命——对做实验、赶 deadline 的研究生是刚需。数据多但语速稳。",
   url:"https://www.ted.com/talks/matt_walker_sleep_is_your_superpower"},
  {en:"My philosophy for a happy life", zh:"我的幸福人生哲学", sp:"Sam Berns", yr:2013, dur:12, cat:"心理幸福", sub:"生活态度",
   intro:"患早衰症的 17 岁少年讲他的三条幸福哲学。听完你对自己的『实验失败』『论文被拒』会有新的容忍度。",
   url:"https://www.ted.com/talks/sam_berns_my_philosophy_for_a_happy_life"},

  /* ===== 习惯自律 ===== */
  {en:"The puzzle of motivation", zh:"动机之谜", sp:"Dan Pink", yr:2009, dur:18, cat:"习惯自律", sub:"内在动机",
   intro:"用 40 年行为科学证明：胡萝卜加大棒只对机械活有效，创造性工作靠 autonomy/mastery/purpose。管理自己读研进度同样适用。",
   url:"https://www.ted.com/talks/dan_pink_the_puzzle_of_motivation"},
  {en:"How to gain control of your free time", zh:"如何掌控你的自由时间", sp:"Laura Vanderkam", yr:2016, dur:12, cat:"习惯自律", sub:"时间管理",
   intro:"时间管理专家拆穿『没时间』：不是没时间，是没优先级。168 小时拆给你看，论文+竞赛双线并行必看。",
   url:"https://www.ted.com/talks/laura_vanderkam_how_to_gain_control_of_your_free_time"},
  {en:"Why you should define your fears instead of your goals", zh:"为什么该定义恐惧而不是目标", sp:"Tim Ferriss", yr:2017, dur:13, cat:"习惯自律", sub:"决策",
   intro:"fear-setting：把最坏情况写下来的三栏法。纠结要不要换课题/要不要参赛时，用它做决定比列 pros/cons 更狠。",
   url:"https://www.ted.com/talks/tim_ferriss_why_you_should_define_your_fears_instead_of_your_goals"},

  /* ===== 沟通领导 ===== */
  {en:"How to speak so that people want to listen", zh:"怎样说话别人才愿意听", sp:"Julian Treasure", yr:2013, dur:10, cat:"沟通领导", sub:"表达",
   intro:"声音专家讲七宗『说罪』和 HAIL 四要素。组会汇报、答辩陈述前看一遍，立刻能用。",
   url:"https://www.ted.com/talks/julian_treasure_how_to_speak_so_that_people_want_to_listen"},
  {en:"The skill of self confidence", zh:"自信是一门技能", sp:"Ivan Joseph", yr:2012, dur:13, cat:"沟通领导", sub:"自信",
   intro:"体育心理教练讲自信如何像肌肉一样练：自我对话、想象力训练、赞美清单。答辩怯场的解药。",
   url:"https://www.ted.com/talks/ivan_joseph_the_skill_of_self_confidence"},
  {en:"10 ways to have a better conversation", zh:"好好交谈的 10 条建议", sp:"Celeste Headlee", yr:2015, dur:12, cat:"沟通领导", sub:"倾听",
   intro:"职业主持人给 10 条反直觉建议（别重复问题、别抢话『我也是』…）。和导师、师兄沟通质量直接受益。",
   url:"https://www.ted.com/talks/celeste_headlee_10_ways_to_have_a_better_conversation"},

  /* ===== 认知思维 ===== */
  {en:"How great leaders inspire action", zh:"伟大的领导者如何激发行动", sp:"Simon Sinek", yr:2009, dur:18, cat:"认知思维", sub:"黄金圈法则",
   intro:"Start with why（黄金圈法则）出处。写本子/做答辩先讲 why 再讲 what，说服逻辑直接升一级。",
   url:"https://www.ted.com/talks/simon_sinek_how_great_leaders_inspire_action"},
  {en:"Where good ideas come from", zh:"好想法从哪里来", sp:"Steven Johnson", yr:2010, dur:18, cat:"认知思维", sub:"创新",
   intro:"好点子来自『慢 hunch 的碰撞』而不是灵光一闪。讲 coffeehouse 与创新史，顺便理解为什么组会讨论这么重要。",
   url:"https://www.ted.com/talks/steven_johnson_where_good_ideas_come_from"},
]'''

idx = s.rindex("];")
head = s[:idx].rstrip()
if not head.endswith("},"):
    head += ","
s = head + "\n" + ADD + "\n"
io.open(P, "w", encoding="utf-8").write(s)
print("ted.js 已扩容")
