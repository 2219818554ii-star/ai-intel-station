/* AI 情报站 - 重庆理工大学通知（学校 / 各学院 / 各部门 / 学生会）
   数据抓取于 2026-09-25，来源均为官网真实页面，URL 未编造。
   cat: school=学校各部门 | college=各学院 | student=团委·学生会
   每日 08:00 自动化任务会重建本文件（抓取各源最新通知后）。 */
window.CQUT_UPDATED = "2026-09-25";
window.CQUT_NOTICES = [
  /* ===== 学校各部门通知（来源：cqut.edu.cn/tzgg/bmtz 部门通知） ===== */
  {t:"关于2026年下半年全国大学英语四、六级考试报名的通知【教务通知】", src:"教务处", date:"2026-09-14", cat:"school",
   sum:"研究生也能报。笔试 12/12、口语 11/21–22，花溪考点 CET 容量 6150 人，手慢无，看到就冲。",
   url:"https://www.cqut.edu.cn/info/1103/71974.htm"},
  {t:"关于本科教务管理系统服务暂停的通知【教务通知】", src:"教务处", date:"2026-09-24", cat:"school",
   sum:"9/28 20:00–9/29 10:00 教务系统停服。别卡点选课、交材料、查成绩，提前办完。",
   url:"https://www.cqut.edu.cn/info/1103/72170.htm"},
  {t:"关于召开2026年第三季度科研工作例会暨科研诚信警示工作会通知【科研通知】", src:"科学技术研究院", date:"2026-09-24", cat:"school",
   sum:"9/28 9:00 明德楼129，主题含科研诚信警示。写论文、报项目前必看——这块的红线踩了代价很大。",
   url:"https://www.cqut.edu.cn/info/1104/72182.htm"},
  {t:"关于重庆理工大学2025年度科研成果奖培育项目（自然科学类）拟立项的公示【科研通知】", src:"科学技术研究院", date:"2026-09-24", cat:"school",
   sum:"13 个项目拟立项，公示 9/24–9/28。有异议要在期内实名书面提，想了解学校培育方向可看清单。",
   url:"https://www.cqut.edu.cn/2025clnr.jsp?urltype=news.NewsContentUrl&wbtreeid=1104&wbnewsid=72171"},
  {t:"关于转发“2026年度国家自然科学基金委员会管理科学部专项项目申请指南”等2个项目指南的通告【科研通知】", src:"科学技术研究院", date:"2026-09-24", cat:"school",
   sum:"国自然管理科学部专项、2 项指南出来。做交叉/管理方向的老师可评估申报。",
   url:"https://www.cqut.edu.cn/info/1104/72184.htm"},
  {t:"关于转发科技部《重点新材料研发及应用国家科技重大专项 2026年度第三批与2027年度第一批项目》的通知【科研通知】", src:"科学技术研究院", date:"2026-09-23", cat:"school",
   sum:"共 2 个专项，材料/化工/复合方向的课题可能对得上，值得让导师评估。",
   url:"https://www.cqut.edu.cn/info/1104/72142.htm"},
  {t:"图书馆关于中秋节、国庆节开放安排的通知【图书馆通知】", src:"图书馆", date:"2026-09-24", cat:"school",
   sum:"10/1–10/3 闭馆，9/29–30、10/4–7 正常开。数字资源 24 小时可用，假期查文献走数据库。",
   url:"https://www.cqut.edu.cn/info/1111/72158.htm"},
  {t:"图书馆关于开展2026级新生入馆培训教育的通知【图书馆通知】", src:"图书馆", date:"2026-09-24", cat:"school",
   sum:"分校区分批培训，教借阅和文献检索。要写论文、找外文资料的正好借这次机会把检索技巧学会。",
   url:"https://www.cqut.edu.cn/info/1111/72157.htm"},
  {t:"关于举办十月“心晴氧吧”朋辈心理支持活动的通知【学生工作通知】", src:"党委学生工作部", date:"2026-09-24", cat:"school",
   sum:"十月启动朋辈心理支持，主题「深度联结」。论文压力大、状态闷的时候可以找个地方聊聊。",
   url:"https://www.cqut.edu.cn/info/1106/72151.htm"},
  {t:"关于开展全市教育强市建设典型案例征集工作的通知【科研通知】", src:"科学技术研究院", date:"2026-09-23", cat:"school",
   sum:"重庆市教科院向高校征集典型案例，主题围绕教育现代化八项行动，重在经验总结。",
   url:"https://www.cqut.edu.cn/info/1104/72141.htm"},

  /* ===== 研究生院（对研究生最相关） ===== */
  {t:"关于开展2026年研究生国家奖学金评选工作的通知", src:"研究生院", date:"2026-09-02", cat:"school",
   sum:"国奖评定启动，涉及学业成绩与科研成果，是研二研三最该盯的一条。",
   url:"https://yjsy.cqut.edu.cn/index/tzgg.htm"},
  {t:"关于开展2026年研究生学业奖学金评定工作的通知", src:"研究生院", date:"2026-09-02", cat:"school",
   sum:"学业奖学金评定办法启动，额度与评选细则看附件，早点准备材料。",
   url:"https://yjsy.cqut.edu.cn/index/tzgg.htm"},
  {t:"关于2026级研究生学籍档案归档工作的通知", src:"研究生院", date:"2026-09-11", cat:"school",
   sum:"全日制研究生档案必须归档，到研究生院（至善楼111）领空档案袋与密封条，别漏。",
   url:"https://www.cqut.edu.cn/tzgg/bmtz/664.htm"},
  {t:"关于组织开展博士研究生综合考试的通知", src:"研究生院", date:"2026-09-02", cat:"school",
   sum:"博士综合考试是学位前的关键考核，课程结束后、论文前，博一博二重点关注。",
   url:"https://yjsy.cqut.edu.cn/index/tzgg.htm"},

  /* ===== 团委 · 学生会（青春重理工） ===== */
  {t:"关于开展2026年下半年团员统计、注册及团费收缴工作的通知", src:"校团委·学生会", date:"2026-09-16", cat:"student",
   sum:"团员统计+团费收缴，按期完成，否则影响团组织关系转接和入党材料。",
   url:"https://qnzx.cqut.edu.cn/info/1016/2231.htm"},
  {t:"关于做好2026-2027学年基层团支部换届及新生团支部成立工作的通知", src:"校团委·学生会", date:"2026-09-07", cat:"student",
   sum:"基层团支部换届+新生团支部成立。想进班委、团支部的看清楚岗位和时间。",
   url:"https://qnzx.cqut.edu.cn/info/1016/2161.htm"},
  {t:"重庆理工大学2026年9月团组织生活指引", src:"校团委·学生会", date:"2026-09-11", cat:"student",
   sum:"9 月团日生活的主题与要求，支部要开展并留痕，党员发展也看这块。",
   url:"https://qnzx.cqut.edu.cn/info/1016/2174.htm"},
  {t:"重庆理工大学2026年6月团组织生活指引", src:"校团委·学生会", date:"2026-06-01", cat:"student",
   sum:"6 月团日指引（已过期，存档备查）。",
   url:"https://qnzx.cqut.edu.cn/info/1016/2155.htm"},

  /* ===== 化学化工学院（本专业） ===== */
  {t:"关于化学化工学院2025-2026学年综合奖学金的公示", src:"化学化工学院", date:"2026-09-22", cat:"college",
   sum:"本专业综合奖学金名单，看评定名次和依据。绩点靠前的别错过。",
   url:"https://chem.cqut.edu.cn/info/1116/5311.htm"},
  {t:"关于化学化工学院2026年研究生教育教学改革研究项目推荐申报的公示", src:"化学化工学院", date:"2026-09-11", cat:"college",
   sum:"化工研究生教改项目推荐名单，想知道谁在立项、可以借鉴怎么申报。",
   url:"https://chem.cqut.edu.cn/info/1116/5301.htm"},
  {t:"化学化工学院2026级特种能源材料教改班报名学生集中面试考核的安排", src:"化学化工学院", date:"2026-09-02", cat:"college",
   sum:"特种能源材料教改班面试安排，想进这个方向的要看准时间地点。",
   url:"https://chem.cqut.edu.cn/info/1116/5281.htm"},
  {t:"化学化工学院关于特种能源材料教改班报名学生资格审查结果公示通知", src:"化学化工学院", date:"2026-08-26", cat:"college",
   sum:"教改班资格审查结果，没通过的看原因是哪一条。",
   url:"https://chem.cqut.edu.cn/info/1116/5276.htm"},

  /* ===== 机械工程学院 ===== */
  {t:"机械工程学院2023级研究生毕业答辩安排", src:"机械工程学院", date:"2026-05-09", cat:"college",
   sum:"研究生毕业答辩的时间与流程安排，是了解本校答辩要求的现成模板。",
   url:"https://jxgc.cqut.edu.cn/info/1073/7591.htm"},
  {t:"重庆理工大学学生退学处理告知书", src:"机械工程学院", date:"2026-06-01", cat:"college",
   sum:"警示性文件：学业、学籍相关的红线，别等收到才知道。",
   url:"https://jxgc.cqut.edu.cn/info/1073/7670.htm"},
  {t:"机械工程学院2026年博士研究生普通招考第二批次考核录取实施细则", src:"机械工程学院", date:"2026-05-07", cat:"college",
   sum:"博士招考考核细则，含参考书目与考核形式，申博前值得对照。",
   url:"https://jxgc.cqut.edu.cn/info/1073/7563.htm"}
];

/* ===== 全部信源直达（学校各部门 / 15 个学院 / 学生组织）=====
   用户点一下就能去官网对应栏目看最新，不依赖天天抓取。 */
window.CQUT_SOURCES = {
  gov: [
    {n:"学校官网", u:"https://www.cqut.edu.cn/"},
    {n:"部门通知（全）", u:"https://www.cqut.edu.cn/tzgg/bmtz.htm"},
    {n:"教务处·教务通知", u:"https://www.cqut.edu.cn/info/1103/"},
    {n:"研究生院", u:"https://yjsy.cqut.edu.cn/"},
    {n:"研究生招生网", u:"https://zs.yjs.cqut.edu.cn/"},
    {n:"科学技术研究院", u:"https://www.cqut.edu.cn/info/1104/"},
    {n:"学生处·学生工作", u:"https://www.cqut.edu.cn/info/1106/"},
    {n:"图书馆", u:"https://www.cqut.edu.cn/info/1111/"},
    {n:"学术讲座", u:"https://www.cqut.edu.cn/tzgg/xsjz.htm"},
    {n:"两江校区管委会", u:"https://ljxq.cqut.edu.cn/"}
  ],
  college: [
    {n:"化学化工学院", u:"https://chem.cqut.edu.cn/"},
    {n:"机械工程学院", u:"https://jxgc.cqut.edu.cn/"},
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
  ],
  student: [
    {n:"校团委·学生会", u:"https://qnzx.cqut.edu.cn/"},
    {n:"团委通知公告", u:"https://qnzx.cqut.edu.cn/tzgg.htm"},
    {n:"研究生会", u:"https://yjsy.cqut.edu.cn/yjsgl/yjsh.htm"},
    {n:"两江校区学生会", u:"https://ljxq.cqut.edu.cn/"}
  ]
};
