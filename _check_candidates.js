const fs = require('fs');
const existing = JSON.parse(fs.readFileSync('_cqut_existing.json','utf8'));
const exUrls = new Set(existing.map(e=>e.u));
const exTitles = new Set(existing.map(e=>e.t));

// candidate: [url, title, date, src, cat, tag]
const C = [
 ["https://www.cqut.edu.cn/info/1101/72457.htm","关于开展校园驿站再通知相关事项的通知","2026-10-16","党政办公室","school","svc"],
 ["https://www.cqut.edu.cn/info/1101/72456.htm","关于开展“士继夜校、理继匠心”培训项目宣传周现场咨询活动的通知","2026-10-16","继续教育学院","school","act"],
 ["https://www.cqut.edu.cn/info/1101/72453.htm","关于举行2026级同等学力申硕开班典礼暨现场确认的通知","2026-10-16","继续教育学院","school","grad"],
 ["https://www.cqut.edu.cn/info/1104/72454.htm","关于转发科技部国家重点研发计划“面向脑健康的脑机接口新技术开发与产业化应用”等4个重点专项2026年度项目申报指南征求意见的通知","2026-10-16","科研院","school","rs"],
 ["https://www.cqut.edu.cn/info/1104/72452.htm","关于开展2027年度农业主推技术和重大引领性技术申报推荐工作的通知","2026-10-16","科研院","school","rs"],
 ["https://www.cqut.edu.cn/info/1104/72451.htm","关于转发“关于发布2026年度国家自然科学基金委员会管理科学部专项项目‘面向未来产业的政策体系与治理机制’申请指南的通告”等2个项目指南的通告","2026-10-16","科研院","school","rs"],
 ["https://www.cqut.edu.cn/info/1104/72445.htm","关于转发科技局征集2026年度重庆市自然科学基金创新发展联合基金（智慧医保）项目指南建议的通知","2026-10-16","科研院","school","rs"],
 ["https://www.cqut.edu.cn/info/1105/72340.htm","关于开展2026年博士研究生导师信息采集的通知","2026-10-10","研究生院","school","grad"],
 ["https://www.cqut.edu.cn/info/1105/72324.htm","“笔端红岩・墨润理工”书法大讲堂活动的通知","2026-10-09","研究生院","school","act"],
 ["https://www.cqut.edu.cn/info/1105/72232.htm","弘毅讲坛——人工智能赋能未来战争","2026-09-27","研究生院","school","act"],
 ["https://www.cqut.edu.cn/info/1105/72231.htm","弘毅讲坛——太赫兹近场扫描显微镜技术","2026-09-27","研究生院","school","act"],
 ["https://www.cqut.edu.cn/info/1105/72139.htm","弘毅讲坛——法布里-珀罗谐振腔型电致变色新技术","2026-09-23","研究生院","school","act"],
 ["https://www.cqut.edu.cn/info/1105/72106.htm","关于开展2026-2027学年第一学期（秋季学期）研究生“三助一辅”岗位选聘的通知","2026-09-21","研究生院","school","grad"],
 ["https://www.cqut.edu.cn/info/1341/72435.htm","【智汇理工·两江讲坛】掌握成功法宝 规划正确人生","2026-10-16","研究生院","school","act"],
 ["https://www.cqut.edu.cn/info/1341/72369.htm","【智汇理工·两江讲坛】大力弘扬教育家精神建设高素质专业化教师队伍","2026-10-12","研究生院","school","act"],
 ["https://www.cqut.edu.cn/info/1341/72368.htm","【智汇理工·两江讲坛】田野故事：非遗需要知识产权保护吗","2026-10-12","研究生院","school","act"],
 ["https://www.cqut.edu.cn/info/1341/72367.htm","【智汇理工·两江讲坛】《重庆市青年创业促进条例》专题宣讲会","2026-10-12","研究生院","school","act"],
 ["https://www.cqut.edu.cn/info/1341/72365.htm","【智汇理工·重理工期刊谷】逐光而行，向新而生 —— 中国激光杂志社发展之路","2026-10-12","研究生院","school","act"],
 ["https://www.cqut.edu.cn/info/1341/72323.htm","【智汇理工·国际大讲堂第6讲】异质结构双合金复合材料变形过程中的微观组织演变","2026-10-08","研究生院","school","act"],
 ["https://www.cqut.edu.cn/info/1341/72313.htm","【智汇理工·知行讲坛】漫谈Fourier分析与偏微分方程","2026-10-08","研究生院","school","act"],
 ["https://www.cqut.edu.cn/info/1341/72312.htm","【智汇理工·知行讲坛】动力系统与组合数论","2026-10-08","研究生院","school","act"],
 ["https://www.cqut.edu.cn/info/1341/71002.htm","【智汇理工·知行讲坛】 Almost mathematics in log-perfectoid toric mirror symmetry","2026-06-29","研究生院","school","act"],
 ["https://qnzx.cqut.edu.cn/info/1016/2243.htm","关于做好2026年下半年推荐优秀团员作为入党积极分子工作的通知","2026-10-11","校团委·学生会","student","party"],
 ["https://qnzx.cqut.edu.cn/info/1016/2242.htm","重庆理工大学2026年10月团组织生活指引","2026-10-11","校团委·学生会","student","party"],
 ["https://qnzx.cqut.edu.cn/info/1016/2231.htm","关于开展2026年下半年团员统计、注册及团费收缴工作的通知","2026-09-16","校团委·学生会","student","party"],
 ["https://qnzx.cqut.edu.cn/info/1016/2174.htm","重庆理工大学2026年9月团组织生活指引","2026-09-11","校团委·学生会","student","party"],
 ["https://qnzx.cqut.edu.cn/info/1016/2161.htm","关于做好2026-2027学年基层团支部换届及新生团支部成立工作的通知","2026-09-07","校团委·学生会","student","party"],
 ["https://yjsy.cqut.edu.cn/info/1021/5294.htm","关于举行2027年考研宣讲咨询会的通知","2026-10-09","研究生院","school","exam"],
 ["https://yjsy.cqut.edu.cn/info/1021/5235.htm","关于开展2026年研究生国家奖学金评选工作的通知","2026-09-17","研究生院","school","money"],
 ["https://yjsy.cqut.edu.cn/info/1021/5234.htm","关于开展2026年研究生学业奖学金评定工作的通知","2026-09-17","研究生院","school","money"],
 ["https://yjsy.cqut.edu.cn/info/1021/5214.htm","关于2026级研究生学籍档案归档工作的通知","2026-09-11","研究生院","school","grad"],
 ["https://yjsy.cqut.edu.cn/info/1021/5204.htm","关于申请设置2026-2027学年第一学期（秋季学期）研究生“三助一辅”岗位的通知","2026-09-11","研究生院","school","grad"],
 ["https://yjsy.cqut.edu.cn/info/1021/5184.htm","重庆理工大学关于2026级研究生新生入校报到注册事项的通知","2026-08-28","研究生院","school","grad"],
 ["https://yjsy.cqut.edu.cn/info/1021/5174.htm","重庆理工大学关于调整2027年全国硕士研究生招生考试（初试）部分专业考试科目的公告","2026-07-28","研究生院","school","exam"],
 ["https://www.cqut.edu.cn/info/1103/72345.htm","关于组织参加“津创津彩”—— 江津区创新创业大赛的通知","2026-10-10","教务处","school","act"],
 ["https://www.cqut.edu.cn/info/1103/72315.htm","关于组织参加2026年和美乡村创意设计大赛的通知","2026-09-09","教务处","school","act"],
 ["https://www.cqut.edu.cn/info/1103/72314.htm","关于收集2026年本科生省（市）级及以上学科竞赛获奖证书（文件）的通知","2026-10-08","教务处","school","act"],
 ["https://www.cqut.edu.cn/info/1103/72308.htm","关于开展2026-2027学年第一学期普通话水平智能测试工作的通知","2026-10-08","教务处","school","exam"],
 ["https://www.cqut.edu.cn/info/1103/72304.htm","关于领取中国国际大学生创新大赛（2026）校赛获奖证书的通知","2026-10-08","教务处","school","act"],
 ["https://www.cqut.edu.cn/info/1106/72351.htm","周末影院之“心随影动”经典电影赏析：《长安的荔枝》","2026-10-12","党委学生工作部","school","act"],
 ["https://www.cqut.edu.cn/info/1106/72343.htm","关于开展十月心理团体辅导的通知","2026-10-10","党委学生工作部","school","act"],
 ["https://www.cqut.edu.cn/info/1106/72333.htm","周末影院之“心随影动”经典电影赏析：《飞驰人生3》","2026-10-09","党委学生工作部","school","act"],
 ["https://www.cqut.edu.cn/info/1106/72307.htm","关于举办重庆理工大学第六届辅导员素质能力大赛的通知","2026-10-08","党委学生工作部","school","act"],
 ["https://www.cqut.edu.cn/info/1106/72303.htm","关于举行 2026 年世界精神卫生日心理义诊活动的通知","2026-10-08","党委学生工作部","school","act"],
 ["https://jxgc.cqut.edu.cn/content.jsp?urltype=news.NewsContentUrl&wbnewsid=7942&wbtreeid=1073","关于2026年下半年重庆理工大学机械工程学院入党积极分子推荐结果的公示","2026-10-12","机械工程学院","college","party"],
 ["https://sfl.cqut.edu.cn/info/1010/2981.htm","语言与传播学院2026-2027学年国家助学金公示","2026-10-16","语言与传播学院","college","money"]
];

const NEW = [];
const DUP = [];
for (const c of C) {
  const [u,t] = c;
  const dupU = exUrls.has(u);
  const dupT = exTitles.has(t);
  if (dupU || dupT) DUP.push({u,t,reason: dupU?'url':'title'});
  else NEW.push(c);
}
console.log('=== NEW ('+NEW.length+') ===');
NEW.forEach(c=>console.log(c[2]+' | '+c[5]+' | '+c[4]+' | '+c[3]+' | '+c[1]+' | '+c[0]));
console.log('\n=== DUP ('+DUP.length+') ===');
DUP.forEach(d=>console.log(d.reason+' | '+d.t+' | '+d.u));
