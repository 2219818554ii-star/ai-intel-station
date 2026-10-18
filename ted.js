/* AI 情报站 - TED 英语演讲（认知提升 + 英语听力素材） */
window.TED_UPDATED = "2026-10-18";
/* ============ TED TALKS (curated 2026-09-23，2026-09-28 re-verified；2026-10-18 全量复核40个官网页面并刷新封面图/官网播放量) ============
   选片原则：① 全网公认、播放量极高的经典 TED/TEDx 演讲；
            ② 主题能提升认知（学习/心理幸福/习惯/沟通领导/思维）；
            ③ 英文原声 + 官方字幕，适合作英语听力与地道表达素材。
   字段：en 英文标题｜zh 中文译名｜sp 演讲者｜yr 年份｜dur 时长(分)｜
        cat 大类(仅 5 种，用于筛选)｜sub 细分主题｜intro 简介+看点｜
        url 官方直链（TED 官网，2026-10-18 已逐条请求，40个页面均返回200；Adichie 旧 slug 已更正为 ngozi 全名）｜
        cover 封面图直链（pi.tedcdn.com CDN，已验 200 image/jpeg）｜
        views TED 官网播放量（整数，2026-10-18 抓取；null=该条页面未暴露播放数）
   渲染策略：TED 官网直达为主入口，另备 YouTube / B站搜索；搜索结果不保证字幕或上传授权。
   复核范围：官网页面与公开元数据；HTTP 200 不等于已在本机完整播放视频。 */
window.TED = [
  /* ===== 学习成长 ===== */
  {en:"Why you thought school was a waste of time", zh:"为什么你觉得上学是浪费时间", sp:"Charlie Robinson", yr:2020, dur:15, cat:"学习成长", sub:"教育反思",
   intro:"TEDxWoking 现场。讲者从自己逃课、被劝退的经历讲起，反驳「 school = 无用」这种极端结论——真正的问题是教育把人塞进统一模具，而研究生的创造力恰恰需要跳出这套模具。语速平、故事多，练听力顺带反思自己被训练成什么样。",
   url:"https://www.ted.com/talks/charlie_robinson_why_you_thought_school_was_a_waste_of_time", cover:"https://pi.tedcdn.com/r/talkstar-photos.s3.amazonaws.com/uploads/a18066a3-3a24-405d-bca9-f8ca57670259/mqdefault.jpg", views:15691},
  {en:"Grit: The power of passion and perseverance", zh:"坚毅：热情与坚持的力量", sp:"Angela Lee Duckworth", yr:2013, dur:6, cat:"学习成长", sub:"坚毅",
   intro:"心理学家 Duckworth 提出：决定长期成就的不是天赋而是『grit（坚毅）』——对长远目标持续的热情与毅力。短小精悍，是积累学术英语高频词的极佳入门。",
   url:"https://www.ted.com/talks/angela_lee_duckworth_grit_the_power_of_passion_and_perseverance", cover:"https://pi.tedcdn.com/r/talkstar-photos.s3.amazonaws.com/uploads/49490c34-ef8e-45b1-8037-a4958efc2609/AngelaDuckworth_2013S-embed.jpg", views:39139293},
  {en:"The power of believing that you can improve", zh:"相信你能进步的力量（成长型思维）", sp:"Carol Dweck", yr:2014, dur:10, cat:"学习成长", sub:"成长型思维",
   intro:"『Not yet（尚未）』比『做不到』更有力量。Dweck 用 growth mindset（成长型思维）解释为什么把失败当练习能改大脑。可顺带积累 mindset、neuroplasticity 等地道词。",
   url:"https://www.ted.com/talks/carol_dweck_the_power_of_believing_that_you_can_improve", cover:"https://pi.tedcdn.com/r/pe.tedcdn.com/images/ted/85582d553035da22504c315ba5ec7ed727f16354_2880x1620.jpg", views:18299303},
  {en:"How to learn? From mistakes", zh:"如何学习？从错误中学习", sp:"Diana Laufenberg", yr:2010, dur:10, cat:"学习成长", sub:"从错误学习",
   intro:"从教 15 年的老师分享三点教学洞见，核心是从错误里学习比追求正确更重要。口语化强、故事多，适合中级听力与叙事表达积累。",
   url:"https://www.ted.com/talks/diana_laufenberg_how_to_learn_from_mistakes", cover:"https://pi.tedcdn.com/r/pe.tedcdn.com/images/ted/5e5ffce52162fbe4c59cf923ab53adcd9e99587a_1600x1200.jpg", views:2481763},

  /* ===== 心理幸福 ===== */
  {en:"The surprising science of happiness", zh:"关于幸福的惊人科学", sp:"Dan Gilbert", yr:2004, dur:21, cat:"心理幸福", sub:"幸福科学",
   intro:"哈佛心理学者 Gilbert 讲『预知自己未来感受』为何总出错——我们高估得失、低估适应力。逻辑清晰、笑点密，是练学术英语听力的好素材。",
   url:"https://www.ted.com/talks/dan_gilbert_the_surprising_science_of_happiness", cover:"https://pi.tedcdn.com/r/pe.tedcdn.com/images/ted/016a827cc0757092a0439ab2a63feca8655b6c29_1600x1200.jpg", views:21156696},
  {en:"The psychology of your future self", zh:"你未来自我的心理学", sp:"Dan Gilbert", yr:2014, dur:7, cat:"心理幸福", sub:"未来自我",
   intro:"我们总误以为『现在的自己』就是终点，Gilbert 用『end of history illusion（历史终结错觉）』解释人为何不爱为未来投资。短小深刻，适合精听。",
   url:"https://www.ted.com/talks/dan_gilbert_the_psychology_of_your_future_self", cover:"https://pi.tedcdn.com/r/pe.tedcdn.com/images/ted/d7c5293df469e90b62ed7bfced793ed7f2bad6c2_1600x1200.jpg", views:7853529},
  {en:"What makes a good life? Lessons from the longest study on happiness", zh:"什么造就美好人生？最长幸福研究的启示", sp:"Robert Waldinger", yr:2015, dur:13, cat:"心理幸福", sub:"幸福研究",
   intro:"哈佛 75 年追踪研究结论极简：决定幸福的是『人际关系的质量』而非财富或名望。语速慢、结构清楚，适合做跟读与词汇笔记。",
   url:"https://www.ted.com/talks/robert_waldinger_what_makes_a_good_life_lessons_from_the_longest_study_on_happiness", cover:"https://pi.tedcdn.com/r/talkstar-photos.s3.amazonaws.com/uploads/1dc3550a-4ff0-44cf-9be6-2aa6ef9c43dd/RobertWaldinger_2015X-embed.jpg", views:53423928},
  {en:"The happy secret to better work", zh:"更快乐的秘密，也是更好的工作", sp:"Shawn Achor", yr:2011, dur:12, cat:"心理幸福", sub:"积极心理学",
   intro:"Achor 反转因果：不是成功带来快乐，而是快乐提升效能。可积累 positive psychology、rewire 等表达，幽默好懂。",
   url:"https://www.ted.com/talks/shawn_achor_the_happy_secret_to_better_work", cover:"https://pi.tedcdn.com/r/pe.tedcdn.com/images/ted/e02ed13dcc2684221ce59429a722479dd13661fb_2880x1620.jpg", views:27349089},
  {en:"The habits of happiness", zh:"幸福的习惯", sp:"Matthieu Ricard", yr:2004, dur:23, cat:"心理幸福", sub:"幸福习惯",
   intro:"被称『世界上最幸福的人』的法国分子生物学家、僧人 Ricard，从训练心智谈可持续的幸福。用词偏书面，适合中高阶听力挑战。",
   url:"https://www.ted.com/talks/matthieu_ricard_the_habits_of_happiness", cover:"https://pi.tedcdn.com/r/talkstar-photos.s3.amazonaws.com/uploads/e819fff6-a202-484a-a2ab-65c8f736fa3e/MatthieuRicard_2004-embed.jpg", views:10948451},
  {en:"How to make stress your friend", zh:"如何让压力成为朋友", sp:"Kelly McGonigal", yr:2013, dur:14, cat:"心理幸福", sub:"压力管理",
   intro:"健康心理学家 McGonigal 翻转『压力有害』叙事：当你视压力为助力，生理反应反而有益。与研究生高压科研极相关，词汇实用。",
   url:"https://www.ted.com/talks/kelly_mcgonigal_how_to_make_stress_your_friend", cover:"https://pi.tedcdn.com/r/talkstar-photos.s3.amazonaws.com/uploads/4ebfc94d-c426-4019-9060-20edc54dcec8/KellyMcGonigal_2013G-embed.jpg", views:37367075},

  /* ===== 习惯自律 ===== */
  {en:"A simple way to break a bad habit", zh:"戒掉坏习惯的一个简单方法", sp:"Judson Brewer", yr:2015, dur:10, cat:"习惯自律", sub:"正念戒瘾",
   intro:"神经科学家 Brewer 用『正念觉察奖励回路』解释戒烟戒拖。医学英语地道，适合积累 craving、habitual loop 等词。",
   url:"https://www.ted.com/talks/judson_brewer_a_simple_way_to_break_a_bad_habit", cover:"https://pi.tedcdn.com/r/talkstar-photos.s3.amazonaws.com/uploads/56962f83-978a-41dd-bacb-72dc228be2ff/JudsonBrewer_2015P-embed.jpg", views:24798588},
  {en:"Inside the mind of a master procrastinator", zh:"拖延症晚期患者的内心世界", sp:"Tim Urban", yr:2016, dur:14, cat:"习惯自律", sub:"拖延症",
   intro:"作家 Urban 用『即时满足猴』与『恐慌怪』把拖延讲成段子，却精准戳中每个 DDL 战士。笑点多、口语地道，极适合放松练听。",
   url:"https://www.ted.com/talks/tim_urban_inside_the_mind_of_a_master_procrastinator", cover:"https://pi.tedcdn.com/r/talkstar-photos.s3.amazonaws.com/uploads/d5d00454-d7aa-434c-8fae-ff2bc97c5f02/TimUrban_2016-embed.jpg", views:79205037},
  {en:"How to gain control of your free time", zh:"如何掌控你的空闲时间", sp:"Laura Vanderkam", yr:2016, dur:12, cat:"习惯自律", sub:"时间管理",
   intro:"『不是有时间才做要事，而是把要事排进日程才有时间。』时间管理干货，逻辑强、例子具体，适合做笔记跟读。",
   url:"https://www.ted.com/talks/laura_vanderkam_how_to_gain_control_of_your_free_time", cover:"https://pi.tedcdn.com/r/talkstar-photos.s3.amazonaws.com/uploads/90c69f27-5216-46fa-a1ae-42e3c4243ddd/LauraVanderkam_2016W-embed.jpg", views:16500503},

  /* ===== 沟通领导 ===== */
  {en:"Your body language may shape who you are", zh:"肢体语言塑造你", sp:"Amy Cuddy", yr:2012, dur:21, cat:"沟通领导", sub:"自信表达",
   intro:"『高能量姿势（power pose）』能在几分钟内改变激素与自信。组会汇报、答辩开场直接能用，表达地道、情绪感染力强。",
   url:"https://www.ted.com/talks/amy_cuddy_your_body_language_may_shape_who_you_are", cover:"https://pi.tedcdn.com/r/talkstar-photos.s3.amazonaws.com/uploads/8ff886f0-7953-4f9b-8726-1ce98cae10c6/AmyCuddy_2012G-embed.jpg", views:77736146},
  {en:"How great leaders inspire action", zh:"伟大领导者如何激励行动", sp:"Simon Sinek", yr:2009, dur:18, cat:"沟通领导", sub:"黄金圈法则",
   intro:"『Start With Why』与黄金圈法则：人不为你做什么买单，而为相信什么买单。商英经典，积累 inspire、purpose 等高频词。",
   url:"https://www.ted.com/talks/simon_sinek_how_great_leaders_inspire_action", cover:"https://pi.tedcdn.com/r/pe.tedcdn.com/images/ted/04916ee6e81065c8333e6546184af512eee37bbe_2880x1620.jpg", views:71245207},
  {en:"Why good leaders make you feel safe", zh:"好领导为何让你感到安全", sp:"Simon Sinek", yr:2014, dur:11, cat:"沟通领导", sub:"团队信任",
   intro:"Sinek 谈『圈层安全（circle of safety）』：信任型领导激发团队奉献。与组会带人、实验室协作相通，语速适中。",
   url:"https://www.ted.com/talks/simon_sinek_why_good_leaders_make_you_feel_safe", cover:"https://pi.tedcdn.com/r/pe.tedcdn.com/images/ted/b6cccc7593928f4861601289b937d19dac95bed9_1600x1200.jpg", views:22435806},
  {en:"How to speak so that people want to listen", zh:"如何说话让人愿意听", sp:"Julian Treasure", yr:2013, dur:10, cat:"沟通领导", sub:"说话之道",
   intro:"声音与沟通专家 Treasure 讲『七年不说（HAIL）』与避开的说话陷阱。对组会汇报、答辩陈述极实用，可逐句跟读练发音。",
   url:"https://www.ted.com/talks/julian_treasure_how_to_speak_so_that_people_want_to_listen", cover:"https://pi.tedcdn.com/r/talkstar-photos.s3.amazonaws.com/uploads/46964e3c-1231-42b7-9288-671ff9fdde2e/JulianTreasure_2013U-embed.jpg", views:71442983},
  {en:"The power of vulnerability", zh:"脆弱的力量", sp:"Brené Brown", yr:2010, dur:20, cat:"沟通领导", sub:"勇气与连接",
   intro:"研究者 Brown 谈『敢于示弱』才是建立连接与勇气的来源。情感浓度高、用词优美，适合中高阶听力与写作表达积累。",
   url:"https://www.ted.com/talks/brene_brown_the_power_of_vulnerability", cover:"https://pi.tedcdn.com/r/talkstar-photos.s3.amazonaws.com/uploads/9595cdc1-fd8e-4aa1-863a-2c6641ae3cbb/BreneBrown_2010X-embed.jpg", views:71317096},

  /* ===== 认知思维 ===== */
  {en:"The danger of a single story", zh:"单一故事的危险", sp:"Chimamanda Ngozi Adichie", yr:2009, dur:19, cat:"认知思维", sub:"认知偏见",
   intro:"作家 Adichie 警示：只听一个故事，就会形成刻板印象。提升批判性思维、打破认知偏见的必看，叙事强、修辞漂亮。",
   url:"https://www.ted.com/talks/chimamanda_ngozi_adichie_the_danger_of_a_single_story", cover:"https://pi.tedcdn.com/r/talkstar-photos.s3.amazonaws.com/uploads/8953d163-926f-4331-8f1f-86db90b94f0b/ChimamandaAdichie_2009G-embed.jpg", views:43208384},
  {en:"The puzzle of motivation", zh:"动机的谜题", sp:"Dan Pink", yr:2009, dur:19, cat:"认知思维", sub:"动机机制",
   intro:"Pink 用行为科学推翻『胡萝卜加大棒』：对复杂任务，内在动机（自主/专精/使命）远胜外部奖励。商英+学术英语双修素材。",
   url:"https://www.ted.com/talks/dan_pink_the_puzzle_of_motivation", cover:"https://pi.tedcdn.com/r/pe.tedcdn.com/images/ted/110884_800x600.jpg", views:32591841},
  {en:"Your elusive creative genius", zh:"你难以捉摸的创意天才", sp:"Elizabeth Gilbert", yr:2009, dur:19, cat:"认知思维", sub:"创意焦虑",
   intro:"《美食祈祷恋爱》作者谈如何与『创作焦虑』共处：把灵感看作外来造访。写作、科研卡壳时极治愈，语速舒适好跟读。",
   url:"https://www.ted.com/talks/elizabeth_gilbert_your_elusive_creative_genius", cover:"https://pi.tedcdn.com/r/pe.tedcdn.com/images/ted/f2f6d094758c36a61b3ee7992a9b197eb4c07979_2880x1620.jpg", views:22248302},
  {en:"How to build your creative confidence", zh:"如何建立创意自信", sp:"David Kelley", yr:2012, dur:11, cat:"认知思维", sub:"创意自信",
   intro:"IDEO 创始人 Kelley 讲『人人都有创造力，只是被恐惧封印』，用设计思维重建创意自信。适合突破科研与写作的畏难。",
   url:"https://www.ted.com/talks/david_kelley_how_to_build_your_creative_confidence", cover:"https://pi.tedcdn.com/r/pe.tedcdn.com/images/ted/25308d79fc7c5a343317a5bdbe0d0f62adc4491c_2880x1620.jpg", views:6572315},
  {en:"How to spot a liar", zh:"如何识破谎言", sp:"Pamela Meyer", yr:2010, dur:19, cat:"认知思维", sub:"识谎",
   intro:"『说谎』研究权威 Meyer 拆解骗子的语言与微表情破绽。逻辑缜密、趣味强，是练听力细节捕捉的优质素材。",
   url:"https://www.ted.com/talks/pamela_meyer_how_to_spot_a_liar", cover:"https://pi.tedcdn.com/r/talkstar-photos.s3.amazonaws.com/uploads/40c841c7-43c2-4386-a885-9600f528ea55/PamelaMeyer_2011G-embed.jpg", views:34636399},
  {en:"The art of choosing", zh:"选择的艺术", sp:"Sheena Iyengar", yr:2010, dur:21, cat:"认知思维", sub:"决策与选择",
   intro:"《选择的艺术》作者谈『选择过载』与东西方决策差异。学术词汇偏多（autonomy、paradox of choice），适合中高阶精听。",
   url:"https://www.ted.com/talks/sheena_iyengar_the_art_of_choosing", cover:"https://pi.tedcdn.com/r/talkstar-photos.s3.amazonaws.com/uploads/a40be2d3-65b1-4278-9715-75f91a067118/SheenaIyengar_2010G-embed.jpg", views:4570963},
  {en:"The power of introverts", zh:"内向者的力量", sp:"Susan Cain", yr:2012, dur:19, cat:"认知思维", sub:"性格与专注",
   intro:"《安静》作者 Cain 为内向者正名：深度思考与沉淀本身就是力量。与科研需要的专注气质高度共鸣，表达温柔有力。",
   url:"https://www.ted.com/talks/susan_cain_the_power_of_introverts", cover:"https://pi.tedcdn.com/r/pe.tedcdn.com/images/ted/b542b1ddd2e40cfcf9db3430598bc37cebfec8c1_1600x1200.jpg", views:36422694},
  /* ===== 2026-09-26 扩容 +15 条 ===== */
  /* ===== 学习成长 ===== */
  {en:"Try something new for 30 days", zh:"用 30 天尝试新事物", sp:"Matt Cutts", yr:2011, dur:3, cat:"学习成长", sub:"习惯养成",
   intro:"Google 工程师的 3 分钟小实验：把想做的事拆成 30 天挑战。时间短到没借口，最适合当『开始行动』的第一支 TED。",
   url:"https://www.ted.com/talks/matt_cutts_try_something_new_for_30_days", cover:"https://pi.tedcdn.com/r/talkstar-photos.s3.amazonaws.com/uploads/424e6719-7627-40bc-ae35-1ed70a66ed2a/MattCutts_2011U-embed.jpg", views:16074928},
  {en:"Every kid needs a champion", zh:"每个孩子都需要一个坚定支持者", sp:"Rita Pierson", yr:2013, dur:7, cat:"学习成长", sub:"师生关系",
   intro:"从教 40 年的名师金句：『孩子不跟讨厌的人学』。讲师生关系如何决定学习效果——读研跟导师相处同样适用。",
   url:"https://www.ted.com/talks/rita_pierson_every_kid_needs_a_champion", cover:"https://pi.tedcdn.com/r/pe.tedcdn.com/images/ted/25a5bc18d2472308c8ed2bb401b4a497f49a0265_1600x1200.jpg", views:17710314},

  /* ===== 心理幸福 ===== */
  {en:"Sleep is your superpower", zh:"睡眠是你的超能力", sp:"Matt Walker", yr:2019, dur:19, cat:"心理幸福", sub:"睡眠",
   intro:"睡眠科学家讲睡眠如何影响记忆、免疫与寿命——对做实验、赶 deadline 的研究生是刚需。数据多但语速稳。",
   url:"https://www.ted.com/talks/matt_walker_sleep_is_your_superpower", cover:"https://pi.tedcdn.com/r/talkstar-photos.s3.amazonaws.com/uploads/0a95ffba-8cfe-4d9c-8913-736275f78bf9/MatthewWalker_2019-embed.jpg", views:27043211},
  {en:"My philosophy for a happy life", zh:"我的幸福人生哲学", sp:"Sam Berns", yr:2013, dur:12, cat:"心理幸福", sub:"生活态度",
   intro:"患早衰症的 17 岁少年讲他的三条幸福哲学。听完你对自己的『实验失败』『论文被拒』会有新的容忍度。",
   url:"https://www.ted.com/talks/sam_berns_my_philosophy_for_a_happy_life", cover:"https://pi.tedcdn.com/r/talkstar-photos.s3.amazonaws.com/uploads/dceb97aa-e320-4f5d-905f-14375f6d2a07/Sam+Berns.jpeg", views:49988651},

  /* ===== 习惯自律 ===== */
  {en:"Why you should define your fears instead of your goals", zh:"为什么该定义恐惧而不是目标", sp:"Tim Ferriss", yr:2017, dur:13, cat:"习惯自律", sub:"决策",
   intro:"fear-setting：把最坏情况写下来的三栏法。纠结要不要换课题/要不要参赛时，用它做决定比列 pros/cons 更狠。",
   url:"https://www.ted.com/talks/tim_ferriss_why_you_should_define_your_fears_instead_of_your_goals", cover:"https://pi.tedcdn.com/r/talkstar-photos.s3.amazonaws.com/uploads/6b784c62-b4d0-4b3a-a1de-89de39b002bc/TimFerriss_2017-embed.jpg", views:13022063},

  /* ===== 沟通领导 ===== */
  {en:"Finding Confidence through Failure", zh:"在失败里长出自信", sp:"Adam Velasquez", yr:2019, dur:13, cat:"沟通领导", sub:"自信",
   intro:"TEDxIdahoStateUniversity。讲者坦白自己因为自卑放弃过机会，后来发现自信是「事后被证据堆出来的」，不是等来的。搞科研的人最熟的场景就是投稿被拒、实验失败——这条正好讲怎么把失败当成自信的来源，而不是否定自己的证据。答辩怯场的也顺手看看。",
   url:"https://www.ted.com/talks/adam_velasquez_finding_confidence_through_failure", cover:"https://pi.tedcdn.com/r/talkstar-photos.s3.amazonaws.com/uploads/d480df85-f1d5-4842-9a55-e2193aa2467a/mqdefault.jpg", views:null},
  {en:"10 ways to have a better conversation", zh:"好好交谈的 10 条建议", sp:"Celeste Headlee", yr:2015, dur:12, cat:"沟通领导", sub:"倾听",
   intro:"职业主持人给 10 条反直觉建议（别重复问题、别抢话『我也是』…）。和导师、师兄沟通质量直接受益。",
   url:"https://www.ted.com/talks/celeste_headlee_10_ways_to_have_a_better_conversation", cover:"https://pi.tedcdn.com/r/talkstar-photos.s3.amazonaws.com/uploads/42293f27-ad85-4999-a72b-96b6d5d2c398/CelesteHeadlee_2015X_embed.jpg", views:33146106},

  /* ===== 认知思维 ===== */
  {en:"Where good ideas come from", zh:"好想法从哪里来", sp:"Steven Johnson", yr:2010, dur:18, cat:"认知思维", sub:"创新",
   intro:"好点子来自『慢 hunch 的碰撞』而不是灵光一闪。讲 coffeehouse 与创新史，顺便理解为什么组会讨论这么重要。",
   url:"https://www.ted.com/talks/steven_johnson_where_good_ideas_come_from", cover:"https://pi.tedcdn.com/r/talkstar-photos.s3.amazonaws.com/uploads/c8244a05-ac8e-45c6-9b06-ac22113031db/StevenJohnson-2010G-embed.jpg", views:5931694},

  /* ===== 2026-10-14 去重后补足 +7（均为高播放经典，已逐条验活 200） ===== */
  {en:"Do schools kill creativity?", zh:"学校扼杀创造力吗？", sp:"Sir Ken Robinson", yr:2006, dur:20, cat:"学习成长", sub:"教育反思",
   intro:"TED 史上播放量最高的演讲之一。Robinson 论证现行教育体系为迎合标准化而系统性地牺牲了创造力——对天天被训练成『标准答案』的研究生是当头一棒，也最能激起『要不要跳出模具做科研』的思考。语速适中、金句密。",
   url:"https://www.ted.com/talks/sir_ken_robinson_do_schools_kill_creativity", cover:"https://pi.tedcdn.com/r/pe.tedcdn.com/images/ted/6b6eb940bceab359ca676a9b486aae475c1df883_2880x1620.jpg", views:80651569},
  {en:"Flow, the secret to happiness", zh:"心流：幸福的秘诀", sp:"Mihaly Csikszentmihalyi", yr:2004, dur:19, cat:"心理幸福", sub:"心流",
   intro:"「心流(flow)」概念提出者、积极心理学奠基人：当你完全沉浸在一件难度刚好的事里，时间感与自我都消失，那就是幸福。做实验做到忘记时间的人都有过 flow——这条教你如何主动制造它。",
   url:"https://www.ted.com/talks/mihaly_csikszentmihalyi_flow_the_secret_to_happiness", cover:"https://pi.tedcdn.com/r/pe.tedcdn.com/images/ted/ec28788873dd3e152461bc6c5c35d3694ab69023_2880x1620.jpg", views:8071838},
  {en:"There's more to life than being happy", zh:"人生不只是追求快乐", sp:"Emily Esfahani Smith", yr:2017, dur:14, cat:"心理幸福", sub:"人生意义",
   intro:"《The Power of Meaning》作者：幸福是瞬息情绪，意义才支撑长期幸福，而意义来自归属/目的/超越/叙事四支柱。科研低谷期看这条，比鸡汤更能重建『我为什么做这个』。",
   url:"https://www.ted.com/talks/emily_esfahani_smith_there_s_more_to_life_than_being_happy", cover:"https://pi.tedcdn.com/r/talkstar-photos.s3.amazonaws.com/uploads/500cb54f-211f-4f7d-8202-a99507891b80/EmilyEsfahaniSmith_2017-embed.jpg", views:15353247},
  {en:"How to buy happiness", zh:"如何用钱买到幸福", sp:"Michael Norton", yr:2011, dur:11, cat:"心理幸福", sub:"幸福科学",
   intro:"行为经济学家的实验：把钱花在别人身上比花在自己身上更能提升幸福感，且与金额无关。经费紧张时这条给『钱少也能幸福』一个科学解释，顺带学 experimental design 的表达。",
   url:"https://www.ted.com/talks/michael_norton_how_to_buy_happiness", cover:"https://pi.tedcdn.com/r/talkstar-photos.s3.amazonaws.com/uploads/dac773c5-9c88-4502-a01b-454fb89c5d56/MichaelNorton_2011X-embed.jpg", views:4873478},
  {en:"The art of asking", zh:"请求的艺术", sp:"Amanda Palmer", yr:2013, dur:14, cat:"沟通领导", sub:"表达",
   intro:"音乐人 Palmer 谈『敢于开口求助』：害怕被拒绝是人之常情，但连接恰恰始于请求。对不敢开口问师兄、不敢找导师争取资源的研究生，这是温柔的一推。表达真诚、有感染力。",
   url:"https://www.ted.com/talks/amanda_palmer_the_art_of_asking", cover:"https://pi.tedcdn.com/r/talkstar-photos.s3.amazonaws.com/uploads/d34538ab-7ae8-46ef-92cc-f83c055c1840/AmandaPalmer_2013-embed.jpg", views:13189104},
  {en:"How language shapes the way we think", zh:"语言如何塑造思维", sp:"Lera Boroditsky", yr:2017, dur:14, cat:"认知思维", sub:"语言与思维",
   intro:"认知科学家 Boroditsky：不同语言真的会重塑人对空间、时间、责任的认知。做学术写作的人看这条，能更自觉意识到『语言不只是工具，它在塑造你怎么想』。",
   url:"https://www.ted.com/talks/lera_boroditsky_how_language_shapes_the_way_we_think", cover:"https://pi.tedcdn.com/r/talkstar-photos.s3.amazonaws.com/uploads/7adc2250-de27-4116-b4ea-6fb4637ca98a/LeraBoroditsky_2017W-embed.jpg", views:27175115},
  {en:"Want to be happy? Be grateful", zh:"想幸福？先学会感恩", sp:"David Steindl-Rast", yr:2013, dur:15, cat:"心理幸福", sub:"感恩",
   intro:"僧人学者 Steindl-Rast：幸福不是拥有更多，而是对已有的心怀感激——『机会』与『礼物』只差一念。语速慢、用词温暖，适合精听跟读，也适合科研受挫后平复心态。",
   url:"https://www.ted.com/talks/david_steindl_rast_want_to_be_happy_be_grateful", cover:"https://pi.tedcdn.com/r/pe.tedcdn.com/images/ted/02722e8404d9e8dd2ec003b249db0ce3d05bda19_1600x1200.jpg", views:9692648}
]
