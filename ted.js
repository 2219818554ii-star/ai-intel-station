/* AI 情报站 - TED 英语演讲（认知提升 + 英语听力素材） */
window.TED_UPDATED = "2026-09-26";
/* ============ TED TALKS (curated 2026-09-23) ============
   选片原则：① 全网公认、播放量极高的经典 TED/TEDx 演讲；
            ② 主题能提升认知（学习/心理幸福/习惯/沟通领导/思维）；
            ③ 英文原声 + 官方字幕，适合作英语听力与地道表达素材。
   字段：en 英文标题｜zh 中文译名｜sp 演讲者｜yr 年份｜dur 时长(分)｜
        cat 大类(仅 5 种，用于筛选)｜sub 细分主题｜intro 简介+看点｜
        url 官方直链（仅作数据留底，渲染已改多平台入口，见 renderTED）
   渲染策略（2026-09-22 修订）：弃用易 404 的 ted.com/talks/<slug> 直链，
        改为「TED 官方搜索(免费) + YouTube + B站(中英字幕)」三入口，
        哪个通点哪个，彻底解决视频打不开的问题。 */
window.TED = [
  /* ===== 学习成长 ===== */
  {en:"Do schools kill creativity?", zh:"学校如何扼杀创造力", sp:"Ken Robinson", yr:2006, dur:19, cat:"学习成长", sub:"创造力",
   intro:"史上播放量最高的 TED 演讲。Robinson 主张创造力与 literacy 同等重要，教育系统却在系统性地削弱它。语速平缓、用词经典，适合练听力，也能反思自己的科研训练。",
   url:"https://www.ted.com/talks/ken_robinson_schools_kill_creativity"},
  {en:"Grit: The power of passion and perseverance", zh:"坚毅：热情与坚持的力量", sp:"Angela Lee Duckworth", yr:2013, dur:6, cat:"学习成长", sub:"坚毅",
   intro:"心理学家 Duckworth 提出：决定长期成就的不是天赋而是『grit（坚毅）』——对长远目标持续的热情与毅力。短小精悍，是积累学术英语高频词的极佳入门。",
   url:"https://www.ted.com/talks/angela_lee_duckworth_grit_the_power_of_passion_and_perseverance"},
  {en:"The power of believing that you can improve", zh:"相信你能进步的力量（成长型思维）", sp:"Carol Dweck", yr:2014, dur:10, cat:"学习成长", sub:"成长型思维",
   intro:"『Not yet（尚未）』比『做不到』更有力量。Dweck 用 growth mindset（成长型思维）解释为什么把失败当练习能改大脑。可顺带积累 mindset、neuroplasticity 等地道词。",
   url:"https://www.ted.com/talks/carol_dweck_the_power_of_believing_that_you_can_improve"},
  {en:"How to learn? From mistakes", zh:"如何学习？从错误中学习", sp:"Diana Laufenberg", yr:2010, dur:10, cat:"学习成长", sub:"从错误学习",
   intro:"从教 15 年的老师分享三点教学洞见，核心是从错误里学习比追求正确更重要。口语化强、故事多，适合中级听力与叙事表达积累。",
   url:"https://www.ted.com/talks/diana_laufenberg_how_to_learn_from_mistakes"},

  /* ===== 心理幸福 ===== */
  {en:"The surprising science of happiness", zh:"关于幸福的惊人科学", sp:"Dan Gilbert", yr:2004, dur:21, cat:"心理幸福", sub:"幸福科学",
   intro:"哈佛心理学者 Gilbert 讲『预知自己未来感受』为何总出错——我们高估得失、低估适应力。逻辑清晰、笑点密，是练学术英语听力的好素材。",
   url:"https://www.ted.com/talks/dan_gilbert_the_surprising_science_of_happiness"},
  {en:"The psychology of your future self", zh:"你未来自我的心理学", sp:"Dan Gilbert", yr:2014, dur:7, cat:"心理幸福", sub:"未来自我",
   intro:"我们总误以为『现在的自己』就是终点，Gilbert 用『end of history illusion（历史终结错觉）』解释人为何不爱为未来投资。短小深刻，适合精听。",
   url:"https://www.ted.com/talks/dan_gilbert_the_psychology_of_your_future_self"},
  {en:"What makes a good life? Lessons from the longest study on happiness", zh:"什么造就美好人生？最长幸福研究的启示", sp:"Robert Waldinger", yr:2015, dur:13, cat:"心理幸福", sub:"幸福研究",
   intro:"哈佛 75 年追踪研究结论极简：决定幸福的是『人际关系的质量』而非财富或名望。语速慢、结构清楚，适合做跟读与词汇笔记。",
   url:"https://www.ted.com/talks/robert_waldinger_what_makes_a_good_life_lessons_from_the_longest_study_on_happiness"},
  {en:"The happy secret to better work", zh:"更快乐的秘密，也是更好的工作", sp:"Shawn Achor", yr:2011, dur:12, cat:"心理幸福", sub:"积极心理学",
   intro:"Achor 反转因果：不是成功带来快乐，而是快乐提升效能。可积累 positive psychology、rewire 等表达，幽默好懂。",
   url:"https://www.ted.com/talks/shawn_achor_the_happy_secret_to_better_work"},
  {en:"The habits of happiness", zh:"幸福的习惯", sp:"Matthieu Ricard", yr:2004, dur:23, cat:"心理幸福", sub:"幸福习惯",
   intro:"被称『世界上最幸福的人』的法国分子生物学家、僧人 Ricard，从训练心智谈可持续的幸福。用词偏书面，适合中高阶听力挑战。",
   url:"https://www.ted.com/talks/matthieu_ricard_the_habits_of_happiness"},
  {en:"How to make stress your friend", zh:"如何让压力成为朋友", sp:"Kelly McGonigal", yr:2013, dur:14, cat:"心理幸福", sub:"压力管理",
   intro:"健康心理学家 McGonigal 翻转『压力有害』叙事：当你视压力为助力，生理反应反而有益。与研究生高压科研极相关，词汇实用。",
   url:"https://www.ted.com/talks/kelly_mcgonigal_how_to_make_stress_your_friend"},

  /* ===== 习惯自律 ===== */
  {en:"A simple way to break a bad habit", zh:"戒掉坏习惯的一个简单方法", sp:"Judson Brewer", yr:2015, dur:10, cat:"习惯自律", sub:"正念戒瘾",
   intro:"神经科学家 Brewer 用『正念觉察奖励回路』解释戒烟戒拖。医学英语地道，适合积累 craving、habitual loop 等词。",
   url:"https://www.ted.com/talks/judson_brewer_a_simple_way_to_break_a_bad_habit"},
  {en:"Inside the mind of a master procrastinator", zh:"拖延症晚期患者的内心世界", sp:"Tim Urban", yr:2016, dur:14, cat:"习惯自律", sub:"拖延症",
   intro:"作家 Urban 用『即时满足猴』与『恐慌怪』把拖延讲成段子，却精准戳中每个 DDL 战士。笑点多、口语地道，极适合放松练听。",
   url:"https://www.ted.com/talks/tim_urban_inside_the_mind_of_a_master_procrastinator"},
  {en:"How to gain control of your free time", zh:"如何掌控你的空闲时间", sp:"Laura Vanderkam", yr:2016, dur:12, cat:"习惯自律", sub:"时间管理",
   intro:"『不是有时间才做要事，而是把要事排进日程才有时间。』时间管理干货，逻辑强、例子具体，适合做笔记跟读。",
   url:"https://www.ted.com/talks/laura_vanderkam_how_to_gain_control_of_your_free_time"},

  /* ===== 沟通领导 ===== */
  {en:"Your body language may shape who you are", zh:"肢体语言塑造你", sp:"Amy Cuddy", yr:2012, dur:21, cat:"沟通领导", sub:"自信表达",
   intro:"『高能量姿势（power pose）』能在几分钟内改变激素与自信。组会汇报、答辩开场直接能用，表达地道、情绪感染力强。",
   url:"https://www.ted.com/talks/amy_cuddy_your_body_language_may_shape_who_you_are"},
  {en:"How great leaders inspire action", zh:"伟大领导者如何激励行动", sp:"Simon Sinek", yr:2009, dur:18, cat:"沟通领导", sub:"黄金圈法则",
   intro:"『Start With Why』与黄金圈法则：人不为你做什么买单，而为相信什么买单。商英经典，积累 inspire、purpose 等高频词。",
   url:"https://www.ted.com/talks/simon_sinek_how_great_leaders_inspire_action"},
  {en:"Why good leaders make you feel safe", zh:"好领导为何让你感到安全", sp:"Simon Sinek", yr:2014, dur:11, cat:"沟通领导", sub:"团队信任",
   intro:"Sinek 谈『圈层安全（circle of safety）』：信任型领导激发团队奉献。与组会带人、实验室协作相通，语速适中。",
   url:"https://www.ted.com/talks/simon_sinek_why_good_leaders_make_you_feel_safe"},
  {en:"How to speak so that people want to listen", zh:"如何说话让人愿意听", sp:"Julian Treasure", yr:2013, dur:10, cat:"沟通领导", sub:"说话之道",
   intro:"声音与沟通专家 Treasure 讲『七年不说（HAIL）』与避开的说话陷阱。对组会汇报、答辩陈述极实用，可逐句跟读练发音。",
   url:"https://www.ted.com/talks/julian_treasure_how_to_speak_so_that_people_want_to_listen"},
  {en:"The power of vulnerability", zh:"脆弱的力量", sp:"Brené Brown", yr:2010, dur:20, cat:"沟通领导", sub:"勇气与连接",
   intro:"研究者 Brown 谈『敢于示弱』才是建立连接与勇气的来源。情感浓度高、用词优美，适合中高阶听力与写作表达积累。",
   url:"https://www.ted.com/talks/brene_brown_the_power_of_vulnerability"},

  /* ===== 认知思维 ===== */
  {en:"The danger of a single story", zh:"单一故事的危险", sp:"Chimamanda Ngozi Adichie", yr:2009, dur:19, cat:"认知思维", sub:"认知偏见",
   intro:"作家 Adichie 警示：只听一个故事，就会形成刻板印象。提升批判性思维、打破认知偏见的必看，叙事强、修辞漂亮。",
   url:"https://www.ted.com/talks/chimamanda_adichie_the_danger_of_a_single_story"},
  {en:"The puzzle of motivation", zh:"动机的谜题", sp:"Dan Pink", yr:2009, dur:19, cat:"认知思维", sub:"动机机制",
   intro:"Pink 用行为科学推翻『胡萝卜加大棒』：对复杂任务，内在动机（自主/专精/使命）远胜外部奖励。商英+学术英语双修素材。",
   url:"https://www.ted.com/talks/dan_pink_the_puzzle_of_motivation"},
  {en:"Your elusive creative genius", zh:"你难以捉摸的创意天才", sp:"Elizabeth Gilbert", yr:2009, dur:19, cat:"认知思维", sub:"创意焦虑",
   intro:"《美食祈祷恋爱》作者谈如何与『创作焦虑』共处：把灵感看作外来造访。写作、科研卡壳时极治愈，语速舒适好跟读。",
   url:"https://www.ted.com/talks/elizabeth_gilbert_your_elusive_creative_genius"},
  {en:"How to build your creative confidence", zh:"如何建立创意自信", sp:"David Kelley", yr:2012, dur:11, cat:"认知思维", sub:"创意自信",
   intro:"IDEO 创始人 Kelley 讲『人人都有创造力，只是被恐惧封印』，用设计思维重建创意自信。适合突破科研与写作的畏难。",
   url:"https://www.ted.com/talks/david_kelley_how_to_build_your_creative_confidence"},
  {en:"How to spot a liar", zh:"如何识破谎言", sp:"Pamela Meyer", yr:2010, dur:19, cat:"认知思维", sub:"识谎",
   intro:"『说谎』研究权威 Meyer 拆解骗子的语言与微表情破绽。逻辑缜密、趣味强，是练听力细节捕捉的优质素材。",
   url:"https://www.ted.com/talks/pamela_meyer_how_to_spot_a_liar"},
  {en:"The art of choosing", zh:"选择的艺术", sp:"Sheena Iyengar", yr:2010, dur:21, cat:"认知思维", sub:"决策与选择",
   intro:"《选择的艺术》作者谈『选择过载』与东西方决策差异。学术词汇偏多（autonomy、paradox of choice），适合中高阶精听。",
   url:"https://www.ted.com/talks/sheena_iyengar_the_art_of_choosing"},
  {en:"The power of introverts", zh:"内向者的力量", sp:"Susan Cain", yr:2012, dur:19, cat:"认知思维", sub:"性格与专注",
   intro:"《安静》作者 Cain 为内向者正名：深度思考与沉淀本身就是力量。与科研需要的专注气质高度共鸣，表达温柔有力。",
   url:"https://www.ted.com/talks/susan_cain_the_power_of_introverts"},
  /* ===== 2026-09-26 扩容 +15 条 ===== */
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
]
