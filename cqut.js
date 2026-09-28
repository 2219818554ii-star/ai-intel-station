/* AI 情报站 - 重庆理工大学通知（学校 / 各学院 / 各部门 / 学生会）
   数据抓取于 2026-09-28，来源均为官网真实页面，URL 未编造。
   cat: school=学校各部门 | college=各学院 | student=团委·学生会
   tag: 二级细分类，按「对研究生实际有影响的事」分，比 cat 更贴合筛选需求
   刷新后必须同步更新下面的 window.CQUT_UPDATED；_selfcheck.js 会卡住「超过 2 天未更新」的回退。 */
window.CQUT_UPDATED = "2026-09-28";

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
  /* 按 date 倒序；cat: school=学校各部门 | college=各学院 | student=团委·学生会；tag ∈ 8 类枚举 */
  {t:"关于加快2026-2027学年第一学期重新学习及2021-2022级学生补修报名进度的通知【教务通知】", src:"教务处", date:"2026-09-28", cat:"school", tag:"exam", sum:"9/15 就已经开始的重新学习、补修报名，还没做完的同学今天就得收尾——漏报要等下学期补，别拖。", url:"https://www.cqut.edu.cn/info/1103/72233.htm"},
  {t:"弘毅讲坛——太赫兹近场扫描显微镜技术【研究生院通知】", src:"研究生院", date:"2026-09-27", cat:"school", tag:"act", sum:"讲座就在明天（9/28）15:00 至善楼300，讲超分辨成像表征。做材料/界面表征的，值得白跑一趟看这台设备能测到什么尺度。", url:"https://www.cqut.edu.cn/info/1105/72231.htm"},
  {t:"关于举办第二届超星杯・重庆理工大学师生AI共创课程思政案例大赛-院赛通知", src:"化学化工学院", date:"2026-09-27", cat:"college", tag:"act", sum:"师生 AI 共创课程思政案例大赛，院内选拔。你做化工方向，正好拿自己的课题练手做案例，还能蹭一波 AI 实操；具体院赛时间看化工学院后续通知。", url:"https://chem.cqut.edu.cn/info/1116/5342.htm"},
  {t:"关于公示2026年大学生“AI+信息素养”大赛重庆理工大学省赛晋级名单的通知【图书馆通知】", src:"图书馆", date:"2026-09-26", cat:"school", tag:"act", sum:"校赛已结束，964 名研究生报名。查一下名单里有没有你自己——晋级了就要进省赛，备赛节奏按省赛来。", url:"https://www.cqut.edu.cn/info/1111/72203.htm"},
  {t:"关于组织开展2026年度国家民委民族研究后期资助项目申报工作的通知【科研通知】", src:"科学技术研究院", date:"2026-09-26", cat:"school", tag:"rs", sum:"国家民委后期资助项目申报。跟工科课题基本不搭界，但它是本批次唯一在 9/26 发的科研项目申报，做人文社科方向的老师可评估。（勉强归 rs：是科研项目管理通知，只是主题对化工无用）", url:"https://www.cqut.edu.cn/info/1104/72207.htm"},
  {t:"关于转发科技部国家重点研发计划“公共卫生与主动健康”等5个重点专项2026年度项目申报指南征求意见的通知【科研通知】", src:"科学技术研究院", date:"2026-09-26", cat:"school", tag:"rs", sum:"5 个重点专项的申报指南征求意见，导师若在做相关方向可先摸清指南口径。（勉强归 rs：申报类通知，方向与化工材料不对口）", url:"https://www.cqut.edu.cn/info/1104/72204.htm"},
  {t:"关于召开重庆理工大学2026年高等教育事业统计工作布置会的通知", src:"发展规划处", date:"2026-09-26", cat:"school", tag:"svc", sum:"全校高教事业统计布置会，9/27（今天）15:00 明德楼500，科研院等线上配合填报。跟你关系不大，但导师若被抽去配合数据填报，心里有数就行。", url:"https://www.cqut.edu.cn/info/1101/72206.htm"},
  {t:"关于化学化工学院2025-2026学年本科生国家奖学金拟推荐名单的公示", src:"化学化工学院", date:"2026-09-26", cat:"college", tag:"pub", sum:"化工学院本科生国奖拟推荐名单公示。虽是本科，但能看清本院国奖评选的硬门槛和排序逻辑，想冲国奖的对照着看自己还差哪块。", url:"https://chem.cqut.edu.cn/info/1116/5321.htm"},
  {t:"关于举办 2026 年“天翼 AI”杯重庆高校人工智能大赛（重庆理工大学赛区）的通知【学校通知】", src:"学校办公室", date:"2026-09-24", cat:"school", tag:"act", sum:"学校联合电信办的高校 AI 大赛，分校园管理、教育教学、科研攻关等赛道。你日常就在用 AI 干活，拿自己的课题做个 AI 应用案例参赛，成本不高、加分管用。", url:"https://www.cqut.edu.cn/2025clnr.jsp?urltype=news.NewsContentUrl&wbnewsid=72172&wbtreeid=1101"},
  {t:"关于本科教务管理系统服务暂停的通知【教务通知】", src:"教务处", date:"2026-09-24", cat:"school", tag:"svc", sum:"9/28 20:00–9/29 10:00 教务系统停服。别卡点选课、交材料、查成绩，提前办完。", url:"https://www.cqut.edu.cn/info/1103/72170.htm"},
  {t:"关于召开2026年第三季度科研工作例会暨科研诚信警示工作会通知【科研通知】", src:"科学技术研究院", date:"2026-09-24", cat:"school", tag:"rs", sum:"9/28 9:00 明德楼129，主题含科研诚信警示。写论文、报项目前必看——这块的红线踩了代价很大。", url:"https://www.cqut.edu.cn/info/1104/72182.htm"},
  {t:"关于重庆理工大学2025年度科研成果奖培育项目（自然科学类）拟立项的公示【科研通知】", src:"科学技术研究院", date:"2026-09-24", cat:"school", tag:"rs", sum:"13 个项目拟立项，公示 9/24–9/28。有异议要在期内实名书面提，想了解学校培育方向可看清单。", url:"https://www.cqut.edu.cn/2025clnr.jsp?urltype=news.NewsContentUrl&wbtreeid=1104&wbnewsid=72171"},
  {t:"关于转发“2026年度国家自然科学基金委员会管理科学部专项项目申请指南”等2个项目指南的通告【科研通知】", src:"科学技术研究院", date:"2026-09-24", cat:"school", tag:"rs", sum:"国自然管理科学部专项、2 项指南出来。做交叉/管理方向的老师可评估申报。", url:"https://www.cqut.edu.cn/info/1104/72184.htm"},
  {t:"图书馆关于中秋节、国庆节开放安排的通知【图书馆通知】", src:"图书馆", date:"2026-09-24", cat:"school", tag:"svc", sum:"10/1–10/3 闭馆，9/29–30、10/4–7 正常开。数字资源 24 小时可用，假期查文献走数据库。", url:"https://www.cqut.edu.cn/info/1111/72158.htm"},
  {t:"图书馆关于开展2026级新生入馆培训教育的通知【图书馆通知】", src:"图书馆", date:"2026-09-24", cat:"school", tag:"act", sum:"分校区分批培训，教借阅和文献检索。要写论文、找外文资料的正好借这次机会把检索技巧学会。", url:"https://www.cqut.edu.cn/info/1111/72157.htm"},
  {t:"关于举办十月“心晴氧吧”朋辈心理支持活动的通知【学生工作通知】", src:"党委学生工作部", date:"2026-09-24", cat:"school", tag:"act", sum:"十月启动朋辈心理支持，主题「深度联结」。论文压力大、状态闷的时候可以找个地方聊聊。", url:"https://www.cqut.edu.cn/info/1106/72151.htm"},
  {t:"关于校园网网络及信息化服务暂停的通知【学校通知】", src:"学校办公室", date:"2026-09-23", cat:"school", tag:"svc", sum:"9/29 00:00–06:00 数据中心机房供电维护，校园网及信息化服务（一卡通、教务、图书馆窗口系统等）整体停摆。当天别卡点交材料、进系统，VPN 也别指望。", url:"https://www.cqut.edu.cn/info/1101/72152.htm"},
  {t:"关于转发科技部《重点新材料研发及应用国家科技重大专项 2026年度第三批与2027年度第一批项目》的通知【科研通知】", src:"科学技术研究院", date:"2026-09-23", cat:"school", tag:"rs", sum:"共 2 个专项，材料/化工/复合方向的课题可能对得上，值得让导师评估。", url:"https://www.cqut.edu.cn/info/1104/72142.htm"},
  {t:"关于开展全市教育强市建设典型案例征集工作的通知【科研通知】", src:"科学技术研究院", date:"2026-09-23", cat:"school", tag:"rs", sum:"重庆市教科院向高校征集典型案例，主题围绕教育现代化八项行动，重在经验总结。", url:"https://www.cqut.edu.cn/info/1104/72141.htm"},
  {t:"关于组织开展2026年下半年保密学习教育的通知【学校通知】", src:"学校办公室", date:"2026-09-22", cat:"school", tag:"party", sum:"即日起至 12/20 完成，学习对象含全体师生。做课题涉及前人未公开数据、合作方资料的，这条是硬约束，别当走过场。（勉强归 party：属全员思想教育/合规学习，8 类里只有团务党建最贴近）", url:"https://www.cqut.edu.cn/2025clnr.jsp?urltype=news.NewsContentUrl&wbnewsid=72128&wbtreeid=1101"},
  {t:"关于转发科技部国家重点研发计划“资源循环利用”等6个重点专项2026年度项目申报指南征求意见的通知【科研通知】", src:"科学技术研究院", date:"2026-09-22", cat:"school", tag:"rs", sum:"6 个重点专项指南征求意见，其中资源循环利用与固废、生物质、碳材料方向能对上。你手上的柚子皮碳、硅碳负极课题，值得让导师按指南口径补一补立项理由。", url:"https://www.cqut.edu.cn/info/1104/72122.htm"},
  {t:"关于化学化工学院2025-2026学年综合奖学金的公示", src:"化学化工学院", date:"2026-09-22", cat:"college", tag:"money", sum:"本专业综合奖学金名单，看评定名次和依据。绩点靠前的别错过。", url:"https://chem.cqut.edu.cn/info/1116/5311.htm"},
  {t:"关于开展2026-2027学年第一学期心理活动的通知【学生工作通知】", src:"党委学生工作部", date:"2026-09-21", cat:"school", tag:"act", sum:"各学院本学期的心理活动排期（手作疗愈、羽毛球友谊赛等，10 月到 12 月逐场开展）。论文写崩的时候有现成的解压场合，看看化工学院排到哪天。", url:"https://www.cqut.edu.cn/info/1106/72091.htm"},
  {t:"中山讲堂信息素养教育专题（2026-6）——AI浪潮中信息素养教育的坚守与进化【图书馆通知】", src:"图书馆", date:"2026-09-21", cat:"school", tag:"act", sum:"清华图书馆韩丽风讲 AI 时代的信息素养怎么变。想省时间可以只看这场，它基本回答了「AI 检索到底该怎么用才不翻车」。", url:"https://www.cqut.edu.cn/info/1111/72084.htm"},
  {t:"关于开展2026-2027学年第一学期（秋季学期）研究生“三助一辅”岗位选聘的通知", src:"研究生院", date:"2026-09-21", cat:"school", tag:"grad", sum:"秋季学期研究生三助一辅（助研/助教/助管/辅导员）进入选聘阶段，申请已截止。想拿岗位津贴的盯紧学院后续通知，错过等下学期。", url:"https://yjsy.cqut.edu.cn/info/1021/5254.htm"},
  {t:"关于开展2026年国家奖学金、国家励志奖学金评定工作的通知【学生工作通知】", src:"党委学生工作部", date:"2026-09-20", cat:"school", tag:"money", sum:"本科生国奖+励志奖学金校级评定启动，与化工学院 9/26 的拟推荐公示是一套流程。想看国奖到底评什么，那就照着这个细则反推自己缺哪块。（勉强归 money：面向本科生，但奖学金评定逻辑与研究生国奖同源）", url:"https://www.cqut.edu.cn/2025clnr.jsp?urltype=news.NewsContentUrl&wbtreeid=1106&wbnewsid=72067"},
  {t:"关于开展2026年研究生国家奖学金评选工作的通知", src:"研究生院", date:"2026-09-17", cat:"school", tag:"money", sum:"国奖评定启动，涉及学业成绩与科研成果，是研二研三最该盯的一条。", url:"https://yjsy.cqut.edu.cn/info/1021/5235.htm"},
  {t:"关于开展2026年研究生学业奖学金评定工作的通知", src:"研究生院", date:"2026-09-17", cat:"school", tag:"money", sum:"学业奖学金评定办法启动，额度与评选细则看附件，早点准备材料。", url:"https://yjsy.cqut.edu.cn/info/1021/5234.htm"},
  {t:"关于开展2026年下半年团员统计、注册及团费收缴工作的通知", src:"校团委·学生会", date:"2026-09-16", cat:"student", tag:"party", sum:"团员统计+团费收缴，按期完成，否则影响团组织关系转接和入党材料。", url:"https://qnzx.cqut.edu.cn/info/1016/2231.htm"},
  {t:"中山讲堂数字资源使用培训专题（2026-20）——科研写作提效与投稿决策——基于 Web of Science / AI 的全流程实战【图书馆通知】", src:"图书馆", date:"2026-09-15", cat:"school", tag:"act", sum:"明确写了「助力研究生」，用 WoS + AI 串起找热点、理文献线、写初稿、定期刊。你现在的改稿流程正好卡在投稿决策这步，去听一次能省几天。", url:"https://www.cqut.edu.cn/info/1111/71977.htm"},
  {t:"关于开展2026年重庆理工大学“丸美”十佳大学生评选活动的通知【学生工作通知】", src:"党委学生工作部", date:"2026-09-15", cat:"school", tag:"pub", sum:"参评范围是「当学年学籍注册的在校学生」，研究生也在内。评审看德智体美劳，拿得出成果的别自己埋没。（勉强归 pub：荣誉评选类，但名额主要给本科生）", url:"https://www.cqut.edu.cn/info/1106/71981.htm"},
  {t:"关于2026年下半年全国大学英语四、六级考试报名的通知【教务通知】", src:"教务处", date:"2026-09-14", cat:"school", tag:"exam", sum:"研究生也能报。笔试 12/12、口语 11/21–22，花溪考点 CET 容量 6150 人，手慢无，看到就冲。", url:"https://www.cqut.edu.cn/info/1103/71974.htm"},
  {t:"关于2026级研究生学籍档案归档工作的通知", src:"研究生院", date:"2026-09-11", cat:"school", tag:"grad", sum:"全日制研究生档案必须归档，到研究生院（至善楼111）领空档案袋与密封条，别漏。", url:"https://www.cqut.edu.cn/tzgg/bmtz/664.htm"},
  {t:"重庆理工大学2026年9月团组织生活指引", src:"校团委·学生会", date:"2026-09-11", cat:"student", tag:"party", sum:"9 月团日生活的主题与要求，支部要开展并留痕，党员发展也看这块。", url:"https://qnzx.cqut.edu.cn/info/1016/2174.htm"},
  {t:"关于化学化工学院2026年研究生教育教学改革研究项目推荐申报的公示", src:"化学化工学院", date:"2026-09-11", cat:"college", tag:"rs", sum:"化工研究生教改项目推荐名单，想知道谁在立项、可以借鉴怎么申报。", url:"https://chem.cqut.edu.cn/info/1116/5301.htm"},
  {t:"中山讲堂信息素养教育专题（2026-5）——从“会聊天”到“能干活”：基于 Workbuddy 的信息素养教学与科研新体验【图书馆通知】", src:"图书馆", date:"2026-09-09", cat:"school", tag:"act", sum:"专门讲 Workbuddy 的五大能力（多模态生成、智能体编排、知识库 RAG、工具调用、文档处理）。你已经在用这套了，去听一遍能挖出自己没用上的功能。", url:"https://www.cqut.edu.cn/info/1111/71893.htm"},
  {t:"关于做好2026-2027学年基层团支部换届及新生团支部成立工作的通知", src:"校团委·学生会", date:"2026-09-07", cat:"student", tag:"party", sum:"基层团支部换届+新生团支部成立。想进班委、团支部的看清楚岗位和时间。", url:"https://qnzx.cqut.edu.cn/info/1016/2161.htm"},
  {t:"关于组织开展博士研究生综合考试的通知", src:"研究生院", date:"2026-09-02", cat:"school", tag:"grad", sum:"博士综合考试是学位前的关键考核，课程结束后、论文前，博一博二重点关注。", url:"https://yjsy.cqut.edu.cn/index/tzgg.htm"},
  {t:"化学化工学院2026级特种能源材料教改班报名学生集中面试考核的安排", src:"化学化工学院", date:"2026-09-02", cat:"college", tag:"exam", sum:"特种能源材料教改班面试安排，想进这个方向的要看准时间地点。", url:"https://chem.cqut.edu.cn/info/1116/5281.htm"},
  {t:"化学化工学院关于特种能源材料教改班报名学生资格审查结果公示通知", src:"化学化工学院", date:"2026-08-26", cat:"college", tag:"pub", sum:"教改班资格审查结果，没通过的看原因是哪一条。", url:"https://chem.cqut.edu.cn/info/1116/5276.htm"},
  {t:"重庆理工大学2026年6月团组织生活指引", src:"校团委·学生会", date:"2026-06-01", cat:"student", tag:"party", sum:"6 月团日指引（已过期，存档备查）。", url:"https://qnzx.cqut.edu.cn/info/1016/2155.htm"},
  {t:"重庆理工大学学生退学处理告知书", src:"机械工程学院", date:"2026-06-01", cat:"college", tag:"grad", sum:"警示性文件：学业、学籍相关的红线，别等收到才知道。", url:"https://jxgc.cqut.edu.cn/info/1073/7670.htm"},
  {t:"机械工程学院2023级研究生毕业答辩安排", src:"机械工程学院", date:"2026-05-09", cat:"college", tag:"grad", sum:"研究生毕业答辩的时间与流程安排，是了解本校答辩要求的现成模板。", url:"https://jxgc.cqut.edu.cn/info/1073/7591.htm"},
  {t:"机械工程学院2026年博士研究生普通招考第二批次考核录取实施细则", src:"机械工程学院", date:"2026-05-07", cat:"college", tag:"grad", sum:"博士招考考核细则，含参考书目与考核形式，申博前值得对照。", url:"https://jxgc.cqut.edu.cn/info/1073/7563.htm"}
];;

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
/* -------------------------------------------------------------------------
 * 【已并入 matches.js】原 CQUT_MATCHES 里放的是获奖通稿和已结束的赛事。
 * 罗浩明确要求：只留还能参加的，获奖喜报一条不留。
 * 现在比赛板块统一由 matches.js 的 window.MATCHES 驱动，按学校分类。
 * ---------------------------------------------------------------------- */
window.CQUT_MATCH_UPDATED = "2026-09-26";
window.CQUT_MATCH_TAGS = [];
window.CQUT_MATCHES = [];

