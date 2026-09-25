/* AI 情报站 - 重庆理工大学通知（学校 / 各学院 / 各部门 / 学生会）
   数据抓取于 2026-09-25，来源均为官网真实页面，URL 未编造。
   cat: school=学校各部门 | college=各学院 | student=团委·学生会
   tag: 二级细分类，按「对研究生实际有影响的事」分，比 cat 更贴合筛选需求
   每日 08:45 自动化任务会重建本文件（抓取各源最新通知后）。 */
window.CQUT_UPDATED = "2026-09-25";

/* 二级细分类（筛选按钮直接用它） */
window.CQUT_TAGS = [
  {k:"exam",   n:"📝 考试考务"},
  {k:"grad",   n:"🎓 研究生事务"},
  {k:"rs",     n:"🔬 科研项目管理"},
  {k:"money",  n:"💰 奖助学金"},
  {k:"pub",    n:"📋 评优公示"},
  {k:"act",    n:"🎪 学生活动"},
  {k:"party",  n:"🚩 团务党建"},
  {k:"svc",    n:"🔧 服务通知"}
];

window.CQUT_NOTICES = [
  /* ===== 学校各部门通知（来源：cqut.edu.cn/tzgg/bmtz 部门通知） ===== */
  {t:"关于2026年下半年全国大学英语四、六级考试报名的通知【教务通知】", src:"教务处", date:"2026-09-14", cat:"school", tag:"exam",
   sum:"研究生也能报。笔试 12/12、口语 11/21–22，花溪考点 CET 容量 6150 人，手慢无，看到就冲。",
   url:"https://www.cqut.edu.cn/info/1103/71974.htm"},
  {t:"关于本科教务管理系统服务暂停的通知【教务通知】", src:"教务处", date:"2026-09-24", cat:"school", tag:"svc",
   sum:"9/28 20:00–9/29 10:00 教务系统停服。别卡点选课、交材料、查成绩，提前办完。",
   url:"https://www.cqut.edu.cn/info/1103/72170.htm"},
  {t:"关于召开2026年第三季度科研工作例会暨科研诚信警示工作会通知【科研通知】", src:"科学技术研究院", date:"2026-09-24", cat:"school", tag:"rs",
   sum:"9/28 9:00 明德楼129，主题含科研诚信警示。写论文、报项目前必看——这块的红线踩了代价很大。",
   url:"https://www.cqut.edu.cn/info/1104/72182.htm"},
  {t:"关于重庆理工大学2025年度科研成果奖培育项目（自然科学类）拟立项的公示【科研通知】", src:"科学技术研究院", date:"2026-09-24", cat:"school", tag:"rs",
   sum:"13 个项目拟立项，公示 9/24–9/28。有异议要在期内实名书面提，想了解学校培育方向可看清单。",
   url:"https://www.cqut.edu.cn/2025clnr.jsp?urltype=news.NewsContentUrl&wbtreeid=1104&wbnewsid=72171"},
  {t:"关于转发“2026年度国家自然科学基金委员会管理科学部专项项目申请指南”等2个项目指南的通告【科研通知】", src:"科学技术研究院", date:"2026-09-24", cat:"school", tag:"rs",
   sum:"国自然管理科学部专项、2 项指南出来。做交叉/管理方向的老师可评估申报。",
   url:"https://www.cqut.edu.cn/info/1104/72184.htm"},
  {t:"关于转发科技部《重点新材料研发及应用国家科技重大专项 2026年度第三批与2027年度第一批项目》的通知【科研通知】", src:"科学技术研究院", date:"2026-09-23", cat:"school", tag:"rs",
   sum:"共 2 个专项，材料/化工/复合方向的课题可能对得上，值得让导师评估。",
   url:"https://www.cqut.edu.cn/info/1104/72142.htm"},
  {t:"图书馆关于中秋节、国庆节开放安排的通知【图书馆通知】", src:"图书馆", date:"2026-09-24", cat:"school", tag:"svc",
   sum:"10/1–10/3 闭馆，9/29–30、10/4–7 正常开。数字资源 24 小时可用，假期查文献走数据库。",
   url:"https://www.cqut.edu.cn/info/1111/72158.htm"},
  {t:"图书馆关于开展2026级新生入馆培训教育的通知【图书馆通知】", src:"图书馆", date:"2026-09-24", cat:"school", tag:"act",
   sum:"分校区分批培训，教借阅和文献检索。要写论文、找外文资料的正好借这次机会把检索技巧学会。",
   url:"https://www.cqut.edu.cn/info/1111/72157.htm"},
  {t:"关于举办十月“心晴氧吧”朋辈心理支持活动的通知【学生工作通知】", src:"党委学生工作部", date:"2026-09-24", cat:"school", tag:"act",
   sum:"十月启动朋辈心理支持，主题「深度联结」。论文压力大、状态闷的时候可以找个地方聊聊。",
   url:"https://www.cqut.edu.cn/info/1106/72151.htm"},
  {t:"关于开展全市教育强市建设典型案例征集工作的通知【科研通知】", src:"科学技术研究院", date:"2026-09-23", cat:"school", tag:"rs",
   sum:"重庆市教科院向高校征集典型案例，主题围绕教育现代化八项行动，重在经验总结。",
   url:"https://www.cqut.edu.cn/info/1104/72141.htm"},

  /* ===== 研究生院（对研究生最相关） ===== */
  {t:"关于开展2026年研究生国家奖学金评选工作的通知", src:"研究生院", date:"2026-09-02", cat:"school", tag:"money",
   sum:"国奖评定启动，涉及学业成绩与科研成果，是研二研三最该盯的一条。",
   url:"https://yjsy.cqut.edu.cn/index/tzgg.htm"},
  {t:"关于开展2026年研究生学业奖学金评定工作的通知", src:"研究生院", date:"2026-09-02", cat:"school", tag:"money",
   sum:"学业奖学金评定办法启动，额度与评选细则看附件，早点准备材料。",
   url:"https://yjsy.cqut.edu.cn/index/tzgg.htm"},
  {t:"关于2026级研究生学籍档案归档工作的通知", src:"研究生院", date:"2026-09-11", cat:"school", tag:"grad",
   sum:"全日制研究生档案必须归档，到研究生院（至善楼111）领空档案袋与密封条，别漏。",
   url:"https://www.cqut.edu.cn/tzgg/bmtz/664.htm"},
  {t:"关于组织开展博士研究生综合考试的通知", src:"研究生院", date:"2026-09-02", cat:"school", tag:"grad",
   sum:"博士综合考试是学位前的关键考核，课程结束后、论文前，博一博二重点关注。",
   url:"https://yjsy.cqut.edu.cn/index/tzgg.htm"},

  /* ===== 团委 · 学生会（青春重理工） ===== */
  {t:"关于开展2026年下半年团员统计、注册及团费收缴工作的通知", src:"校团委·学生会", date:"2026-09-16", cat:"student", tag:"party",
   sum:"团员统计+团费收缴，按期完成，否则影响团组织关系转接和入党材料。",
   url:"https://qnzx.cqut.edu.cn/info/1016/2231.htm"},
  {t:"关于做好2026-2027学年基层团支部换届及新生团支部成立工作的通知", src:"校团委·学生会", date:"2026-09-07", cat:"student", tag:"party",
   sum:"基层团支部换届+新生团支部成立。想进班委、团支部的看清楚岗位和时间。",
   url:"https://qnzx.cqut.edu.cn/info/1016/2161.htm"},
  {t:"重庆理工大学2026年9月团组织生活指引", src:"校团委·学生会", date:"2026-09-11", cat:"student", tag:"party",
   sum:"9 月团日生活的主题与要求，支部要开展并留痕，党员发展也看这块。",
   url:"https://qnzx.cqut.edu.cn/info/1016/2174.htm"},
  {t:"重庆理工大学2026年6月团组织生活指引", src:"校团委·学生会", date:"2026-06-01", cat:"student", tag:"party",
   sum:"6 月团日指引（已过期，存档备查）。",
   url:"https://qnzx.cqut.edu.cn/info/1016/2155.htm"},

  /* ===== 化学化工学院（本专业） ===== */
  {t:"关于化学化工学院2025-2026学年综合奖学金的公示", src:"化学化工学院", date:"2026-09-22", cat:"college", tag:"money",
   sum:"本专业综合奖学金名单，看评定名次和依据。绩点靠前的别错过。",
   url:"https://chem.cqut.edu.cn/info/1116/5311.htm"},
  {t:"关于化学化工学院2026年研究生教育教学改革研究项目推荐申报的公示", src:"化学化工学院", date:"2026-09-11", cat:"college", tag:"rs",
   sum:"化工研究生教改项目推荐名单，想知道谁在立项、可以借鉴怎么申报。",
   url:"https://chem.cqut.edu.cn/info/1116/5301.htm"},
  {t:"化学化工学院2026级特种能源材料教改班报名学生集中面试考核的安排", src:"化学化工学院", date:"2026-09-02", cat:"college", tag:"exam",
   sum:"特种能源材料教改班面试安排，想进这个方向的要看准时间地点。",
   url:"https://chem.cqut.edu.cn/info/1116/5281.htm"},
  {t:"化学化工学院关于特种能源材料教改班报名学生资格审查结果公示通知", src:"化学化工学院", date:"2026-08-26", cat:"college", tag:"pub",
   sum:"教改班资格审查结果，没通过的看原因是哪一条。",
   url:"https://chem.cqut.edu.cn/info/1116/5276.htm"},

  /* ===== 机械工程学院 ===== */
  {t:"机械工程学院2023级研究生毕业答辩安排", src:"机械工程学院", date:"2026-05-09", cat:"college", tag:"grad",
   sum:"研究生毕业答辩的时间与流程安排，是了解本校答辩要求的现成模板。",
   url:"https://jxgc.cqut.edu.cn/info/1073/7591.htm"},
  {t:"重庆理工大学学生退学处理告知书", src:"机械工程学院", date:"2026-06-01", cat:"college", tag:"grad",
   sum:"警示性文件：学业、学籍相关的红线，别等收到才知道。",
   url:"https://jxgc.cqut.edu.cn/info/1073/7670.htm"},
  {t:"机械工程学院2026年博士研究生普通招考第二批次考核录取实施细则", src:"机械工程学院", date:"2026-05-07", cat:"college", tag:"grad",
   sum:"博士招考考核细则，含参考书目与考核形式，申博前值得对照。",
   url:"https://jxgc.cqut.edu.cn/info/1073/7563.htm"}
];

/* ===== 全部信源直达（学校各部门 / 15 个学院 / 学生组织）=====
   用户点一下就能去官网对应栏目看最新，不依赖天天抓取。 */
window.CQUT_SOURCES = {
  teach: [
    {n:"教务处·教务通知", u:"https://www.cqut.edu.cn/info/1103/"},
    {n:"研究生院", u:"https://yjsy.cqut.edu.cn/"},
    {n:"研究生招生网", u:"https://zs.yjs.cqut.edu.cn/"},
    {n:"化学化工学院", u:"https://chem.cqut.edu.cn/"},
    {n:"机械工程学院", u:"https://jxgc.cqut.edu.cn/"},
    {n:"材料科学与工程学院", u:"https://cl.cqut.edu.cn/"},
    {n:"车辆工程学院", u:"https://clgc.cqut.edu.cn/"},
    {n:"电气与电子工程学院", u:"https://dz.cqut.edu.cn/"},
    {n:"计算机科学与工程学院", u:"https://cs.cqut.edu.cn/"},
    {n:"研究生会", u:"https://yjsy.cqut.edu.cn/yjsgl/yjsh.htm"}
  ],
  sci: [
    {n:"科学技术研究院", u:"https://www.cqut.edu.cn/info/1104/"},
    {n:"学术讲座", u:"https://www.cqut.edu.cn/tzgg/xsjz.htm"},
    {n:"科研成果奖培育公示", u:"https://www.cqut.edu.cn/2025clnr.jsp?urltype=news.NewsContentUrl&wbtreeid=1104&wbnewsid=72171"}
  ],
  stu: [
    {n:"党委学生工作部", u:"https://www.cqut.edu.cn/info/1106/"},
    {n:"学生处·学生工作通知", u:"https://www.cqut.edu.cn/tzgg/bmtz.htm"},
    {n:"图书馆", u:"https://www.cqut.edu.cn/info/1111/"},
    {n:"两江校区管委会", u:"https://ljxq.cqut.edu.cn/"}
  ],
  party: [
    {n:"校团委·学生会", u:"https://qnzx.cqut.edu.cn/"},
    {n:"团委通知公告", u:"https://qnzx.cqut.edu.cn/tzgg.htm"},
    {n:"两江校区学生会", u:"https://ljxq.cqut.edu.cn/"}
  ],
  college: [
    {n:"机械工程学院", u:"https://jxgc.cqut.edu.cn/"},
    {n:"化学化工学院", u:"https://chem.cqut.edu.cn/"},
    {n:"材料科学与工程学院", u:"https://cl.cqut.edu.cn/"},
    {n:"车辆工程学院", u:"https://clgc.cqut.edu.cn/"},
    {n:"电气与电子工程学院", u:"https://dz.cqut.edu.cn/"},
    {n:"计算机科学与工程学院", u:"https://cs.cqut.edu.cn/"},
    {n:"管理学院", u:"https://glxy.cqut.edu.cn/"},
    {n:"会计学院", u:"https://kj.cqut.edu.cn/"},
    {n:"经济金融学院", u:"https://jj.cqut.edu.cn/"},
    {n:"理学院", u:"https://lxy.cqut.edu.cn/"},
    {n:"药学与生物工程学院", u:"https://ys.cqut.edu.cn/"},
    {n:"外国语学院", u:"https://sfl.cqut.edu.cn/"},
    {n:"重庆知识产权学院", u:"https://ipschool.cqut.edu.cn/"},
    {n:"两江国际学院", u:"https://lic.cqut.edu.cn/"},
    {n:"两江人工智能学院", u:"https://ai.cqut.edu.cn/"}
  ]
};

/* ===== 各学院赛事 =====
   全部为实抓结果：来源为各学院官网新闻/通知列表页与学校新闻页，URL 真实可点，未编造。
   重要说明：多数条目是「获奖通报」而非「报名通知」——即上一届已经打完并出成绩。
   想参赛要盯下一届的报名通知，届时本栏目会同步跟进。
   tag: mat=材料化工（对口 Pipeline）| mech=机械车辆 | info=电子信息计算机 | oth=其他
   fit: 是否与本校使用者（化工专业研究生）的专业主线相关 */
window.CQUT_MATCH_UPDATED = "2026-09-25";
window.CQUT_MATCH_TAGS = [
  {k:"mat",  n:"🧪 材料·化工（对口）"},
  {k:"mech", n:"⚙️ 机械·车辆·机器人"},
  {k:"info", n:"💻 电子信息·通信"},
  {k:"oth",  n:"🎯 其他"}
];

window.CQUT_MATCHES = [
  /* ===== 材料科学与工程学院（对口的那个） ===== */
  {n:"“大龙杯”第六届全国大学生高分子材料实验实践大赛", org:"材料科学与工程学院", lv:"国家级",
   st:"已出成绩（校内选拔已完成）", date:"2026-06-26", tag:"mat", fit:1,
   intro:"全国高分子材料专业的实验技能擂台。学校由材料科学与工程学院高分子材料与工程系牵头组织，2026 年 3–6 月完成校内选拔，面向 2023/2024 级高分子材料与工程专业全体学生。",
   todo:"三轮硬考核：① 实验安全理论测试 → ② 高分子化学基本操作技能 → ③ 甲基丙烯酸甲酯（MMA）聚合反应实操。考的是动手规范和现场操作，不是写文章。",
   help:"这条跟你日常实验能力直接挂钩。我能帮你：① 按三轮考核范围整理一份复习清单；② 给你一份 MMA 溶液聚合的完整操作自查表（温度、引发剂用量、时间、后处理每一步）；③ 从你平时做的实验里挑几步按赛标重练。",
   url:"https://cl.cqut.edu.cn/info/1034/6103.htm"},

  {n:"第十五届全国大学生金相技能大赛复赛（重庆赛区）暨第四届重庆市大学生金相技能大赛", org:"材料科学与工程学院", lv:"国家级 / 省部级",
   st:"已出成绩", date:"2026-05-25", tag:"mat", fit:1,
   intro:"金相制样技能的比赛。由重庆市教育委员会指导，重庆科技大学承办，来自重庆大学、西南大学、重庆交通大学等 16 所本专科院校的 144 名选手参赛。学校由材料学院牵头组织选拔与集训。",
   todo:"比的是制样硬功夫：取样 → 镶嵌 → 磨抛 → 腐蚀 → 显微镜下读组织并评分。全程看手上的功夫和流程规范，跟理论笔试是两条不同的赛道。",
   help:"你做硅基负极、配位聚合物都要看显微结构，这套流程能直接搬。我能帮你：① 一份通用金相制样 SOP（砂纸目数梯度、抛光布选型、腐蚀剂对照表）；② 常见材料的预期组织清单，方便你自己判断样品做得对不对。",
   url:"https://cl.cqut.edu.cn/info/1034/6074.htm"},

  /* ===== 机械工程学院 ===== */
  {n:"第二十一届全国大学生智能汽车竞赛", org:"机械工程学院", lv:"国家级",
   st:"已出成绩", date:"2026-08-27", tag:"mech", fit:0,
   intro:"全国高校智能车/电控类顶级赛事。学校由机械工程学院组队，本条记录为总决赛二等奖。",
   todo:"官方赛制与当年赛道命题见大赛官网；学院层面的组队、培训与集训安排见源地址这篇报道。",
   help:"我能帮你：① 去智能汽车竞赛官网扒当年赛题和赛道规则，整理成中文速查表；② 评估你跟不跟得上（要写控制算法的话，我可以带你从最基础的 PID 开始补）。",
   url:"https://jxgc.cqut.edu.cn/content.jsp?urltype=news.NewsContentUrl&wbtreeid=1072&wbnewsid=7793"},

  {n:"全国大学生机器人大赛 RoboMaster 2026 机甲大师赛", org:"机械工程学院", lv:"国家级",
   st:"已出成绩", date:"2026-08-27", tag:"mech", fit:0,
   intro:"RoboMaster 是 Robot 界的全国联赛，学校由机械工程学院参赛，本条记录为全国一等奖。",
   todo:"官方赛程与对抗规则见 RoboMaster 官网；学校组队与训练情况见源地址。",
   help:"我能帮你：① 扒当年赛程与规则要点；② 把机械、电控、战术三条线拆成一张职责分工表；③ 如果你要入队，我给你一份机械原理与电路基础的自学路线。",
   url:"https://jxgc.cqut.edu.cn/content.jsp?urltype=news.NewsContentUrl&wbtreeid=1072&wbnewsid=7792"},

  {n:"中国大学生机械工程创新创意大赛全国总决赛", org:"机械工程学院", lv:"国家级",
   st:"已出成绩", date:"2026-08-27", tag:"mech", fit:0,
   intro:"面向机械类专业的全国性创新创意赛事，学校参赛队在总决赛中斩获一等奖。",
   todo:"总决赛题由主办方当年发布，命题方向与机械工程各方向（机构、装备、工艺）相关，见源地址和大赛官网。",
   help:"我能帮你：① 整理往届获奖作品的选题方向清单，帮你判断哪些跟你的机械/动力背景衔接得上；② 帮你把选题写成一份能打的立项书。",
   url:"https://jxgc.cqut.edu.cn/content.jsp?urltype=news.NewsContentUrl&wbtreeid=1072&wbnewsid=7791"},

  {n:"2026 年全国大学生物联网设计竞赛总决赛", org:"机械工程学院", lv:"国家级",
   st:"已出成绩", date:"2026-08-27", tag:"mech", fit:0,
   intro:"物联网设计类的全国性赛事，学校参赛团队在总决赛中斩获一等奖。",
   todo:"赛道设置与当年命题见竞赛官网；学校组队情况见源地址。",
   help:"我能帮你：① 找近三年获奖作品的题目与技术路线，做成一张可抄的立项模板；② 帮你把方案书框架和答辩稿敲出来。",
   url:"https://jxgc.cqut.edu.cn/content.jsp?urltype=news.NewsContentUrl&wbtreeid=1072&wbnewsid=7781"},

  {n:"第十二届全国大学生机械创新设计大赛（2026）", org:"机械工程学院", lv:"国家级",
   st:"已出成绩", date:"2026-07-24", tag:"mech", fit:0,
   intro:"机械创新设计类的全国性赛事，学校学子获一等奖。这类赛事通常本科组占多数，研究生组队需要确认参赛资格。",
   todo:"常规为「指定主题 + 机械创新设计作品现场竞评与演示」，当年的具体主题见大赛官网。",
   help:"我能帮你：① 按往届评审口味帮你挑选题（标准就四条：够简单、能做完、能演示、能拍成视频）；② 帮你画结构图和写演示视频脚本。",
   url:"https://jxgc.cqut.edu.cn/content.jsp?urltype=news.NewsContentUrl&wbtreeid=1072&wbnewsid=7772"},

  {n:"全国大学生机器人大赛 ROBOCON", org:"机械工程学院", lv:"国家级",
   st:"已出成绩", date:"2026-07-18", tag:"mech", fit:0,
   intro:"机器人对抗类赛事，学校参赛队获全国一等奖。",
   todo:"赛题每年由组委会现场发布，机器人对抗规则见源地址和 ROBOCON 官网。",
   help:"我能帮你：① 把往届赛题翻译成一句话需求，再拆成机械、电控、策略三块任务清单；② 帮你做一份赛前两周的训练排期。",
   url:"https://jxgc.cqut.edu.cn/content.jsp?urltype=news.NewsContentUrl&wbtreeid=1072&wbnewsid=7774"},

  /* ===== 学校层面校级组队（新闻未标注具体牵头学院） ===== */
  {n:"2026 中国汽车工程学会巴哈大赛", org:"学校（校级组队）", lv:"国家级",
   st:"已出成绩", date:"2026-09-05", tag:"mech", fit:0,
   intro:"巴哈大赛（Baja）是越野车设计制造类的全国赛事，学校学子斩获二等奖。",
   todo:"车架、传动、制动、赛事规则见大赛官网；学校组队情况见源地址。",
   help:"我能帮你：① 扒一版往年的赛队技术文件结构；② 帮你把部件清单和校核项整理成一张可打勾的表格。",
   url:"https://www.cqut.edu.cn/info/1263/71828.htm"},

  {n:"第二届全国青少年智能无人系统应用大赛总决赛", org:"学校（校级组队）", lv:"国家级",
   st:"已出成绩", date:"2026-09-18", tag:"oth", fit:0,
   intro:"面向青少年的智能无人系统应用类赛事，学校团队获总决赛二等奖。",
   todo:"赛事内容与赛制见大赛官网；本条为获奖通报，不是报名通知。",
   help:"这条偏科普与青少年方向，跟你的科研主线关联不大。只想攒一次大赛经历的话，我能帮你整理一份参赛材料清单（方案、演示、答辩三部分）。",
   url:"https://www.cqut.edu.cn/info/1263/72051.htm"},

  {n:"第 18 届全国大学生广告艺术大赛总决赛", org:"学校（校级组队）", lv:"国家级",
   st:"已出成绩", date:"2026-09-07", tag:"oth", fit:0,
   intro:"全国大学生广告类的顶级赛事，学校学子在总决赛中斩获一等奖 2 项。",
   todo:"赛类别（平面、视频、策划案等）与命题见大赛官网。",
   help:"我能帮你：① 把平面/视频类作品的策划案写成能打的格式；② 文案和排版建议我都能出。",
   url:"https://www.cqut.edu.cn/info/1263/71871.htm"},

  {n:"第十三届大学生新一代信息通信科技大赛", org:"学校（校级组队）", lv:"国家级",
   st:"已出成绩", date:"2026-09-07", tag:"info", fit:0,
   intro:"信息通信类全国性赛事，学校参赛团队获三等奖。",
   todo:"赛道与命题见大赛官网。",
   help:"我能帮你：① 扒往届获奖作品的题目方向；② 帮你把技术方案部分写成能直接交的格式。",
   url:"https://www.cqut.edu.cn/info/1263/71868.htm"},

  {n:"第四届全国大学生通信系统设计大赛西部赛区", org:"学校（校级组队）", lv:"国家级",
   st:"已出成绩", date:"2026-09-07", tag:"info", fit:0,
   intro:"通信系统设计类赛事，学校在西部赛区斩获佳绩。",
   todo:"赛题与赛制见大赛官网。",
   help:"我能帮你：① 找西部赛区往年的赛题和获奖方案；② 帮你把系统设计文档的框架搭出来。",
   url:"https://www.cqut.edu.cn/info/1263/71867.htm"},

  {n:"全国大学生社会保障案例大赛", org:"学校（校级组队）", lv:"国家级",
   st:"已出成绩", date:"2026-08-30", tag:"oth", fit:0,
   intro:"社会保障与公共政策方向的案例赛事，学校学子获一等奖。",
   todo:"案例选题、数据要求与评审标准见大赛官网。",
   help:"我能帮你：① 找往届一等奖案例的分析框架；② 帮你把案例正文的政策分析部分写成结构清楚的样子。",
   url:"https://www.cqut.edu.cn/info/1263/71726.htm"},

  {n:"第十七届中国大学生服务外包创新创业大赛", org:"学校（校级组队）", lv:"国家级",
   st:"已出成绩", date:"2026-08-28", tag:"oth", fit:0,
   intro:"服务外包与创新创业类全国赛事，学校参赛团队获二、三等奖。",
   todo:"企业命题与商务方案要求见大赛官网。",
   help:"我能帮你：① 扒往届获奖的商业计划书结构；② 帮你做一份竞品分析和财务测算的模板。",
   url:"https://www.cqut.edu.cn/info/1263/71717.htm"}
];
