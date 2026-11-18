'use strict';
const fs = require('fs');
const vm = require('vm');
const path = require('path');
const relevance = require('./_cqut_relevance.js');

const file = path.join(__dirname, 'cqut.js');
const text = fs.readFileSync(file, 'utf8');

// --- extract arrays via vm (valid JS literals) ---
function extractArray(varName) {
  const m = text.match(new RegExp('window\\.' + varName + '\\s*=\\s*(\\[[\\s\\S]*?\\n\\];)'));
  if (!m) throw new Error('cannot find ' + varName);
  const lit = m[1].replace(/;\s*$/, '');
  return vm.runInNewContext(lit);
}
const existing = extractArray('CQUT_NOTICES');
const tags = extractArray('CQUT_TAGS');
console.log('existing notices:', existing.length, 'tags:', tags.length);

// --- new items filling the MAIN-PORTAL news/通知 gap (homepage extraction, verified where noted) ---
// verified: true -> use provided sum; otherwise bounded summary from title/date/col (no fabrication)
// URL_MAP supplies the real official URLs (from the homepage extraction) for every new item.
const URL_MAP = {
  '停电施工通知': 'https://www.cqut.edu.cn/2025clnr.jsp?urltype=news.NewsContentUrl&wbnewsid=72969&wbtreeid=1101',
  '重庆理工大学2026年拟聘工作人员公示（第七批）': 'https://www.cqut.edu.cn/2025clnr.jsp?urltype=news.NewsContentUrl&wbnewsid=72963&wbtreeid=1101',
  '关于开展2026-2027学年第一学期期中研究生评教工作的通知': 'https://www.cqut.edu.cn/info/1101/72962.htm',
  '关于开展2026-2027学年第一学期期中本科生集中终结性评教工作的通知': 'https://www.cqut.edu.cn/info/1101/72961.htm',
  '学校承办第十届亚洲人工智能技术大会': 'https://www.cqut.edu.cn/info/1049/72763.htm',
  '学校举行两江新区2026年“名企校园行”启动仪式': 'https://www.cqut.edu.cn/info/1262/72855.htm',
  '重庆市财政局会计处来校调研并开展主题党日活动': 'https://www.cqut.edu.cn/info/1262/72829.htm',
  '学校举办2026年辅导员业务专题培训': 'https://www.cqut.edu.cn/info/1262/72828.htm',
  '学校召开2027年教育部人文社科项目申报经验分享暨动员会': 'https://www.cqut.edu.cn/info/1262/72814.htm',
  '学校组织开展纪法知识测试': 'https://www.cqut.edu.cn/info/1262/72795.htm',
  '学校与巴南区开展困境学生心理关爱合作座谈': 'https://www.cqut.edu.cn/info/1262/72785.htm',
  '学校举办“数智财会聚力 校政园企同行”产教融合对接交流会': 'https://www.cqut.edu.cn/info/1263/72978.htm',
  '重庆市注册会计师行业信息化能力提升培训班（第二期）顺利开班': 'https://www.cqut.edu.cn/info/1263/72948.htm',
  '学校举办“青春探智，AI筑城”大学生科普创作挑战赛': 'https://www.cqut.edu.cn/info/1263/72941.htm',
  '学校承办第五届大学生标准创新大赛': 'https://www.cqut.edu.cn/info/1263/72881.htm',
  '学校举行2026级“AI+金融”教改班“四维导师”见面会': 'https://www.cqut.edu.cn/info/1263/72860.htm',
  '学校药学与生物工程学院青年教师及团队在国际药学权威期刊Acta Pharmaceutica Sinica B发表综述论文 提出中性粒细胞膜"治疗界面"新概念': 'https://www.cqut.edu.cn/info/1264/72164.htm',
  '学校研究生在国际学术期刊 Knowledge-Based Systems 发表论文': 'https://www.cqut.edu.cn/info/1264/72942.htm',
  '学校研究生在材料科学领域国际顶级期刊 Progress in Materials Science 发表海外联合培养成果': 'https://www.cqut.edu.cn/info/1264/72751.htm',
  '爱沙尼亚塔尔图大学技术研究所Alvo Aabloo教授来校作学术报告': 'https://www.cqut.edu.cn/info/1264/72505.htm',
  '中国科学院院士叶向东、张平做客蝴蝶山数学论坛': 'https://www.cqut.edu.cn/info/1264/72489.htm',
  '学校应用技术学院与万友汽车投资有限公司签订合作协议': 'https://www.cqut.edu.cn/info/1265/72929.htm',
  '学校举办“科创天府·智汇蓉城”双流—两江新区成渝协同供需对接会专场活动': 'https://www.cqut.edu.cn/info/1265/72923.htm',
  '学校举行智能网联新能源汽车热管理创新论坛暨重理工-广电计量联合实验室揭牌活动': 'https://www.cqut.edu.cn/info/1265/72892.htm',
  '学校重庆知识产权学院教师张莉做客“两江讲坛”': 'https://www.cqut.edu.cn/info/1266/72815.htm',
  '学校应用技术学院走进龙骏社区开展志愿服务活动': 'https://www.cqut.edu.cn/info/1266/72685.htm',
  '学校校友、盛海科技联合创始人卢延武做客“两江讲坛”': 'https://www.cqut.edu.cn/info/1266/72661.htm',
  '学校举行第五届低碳打卡挑战赛': 'https://www.cqut.edu.cn/info/1266/72646.htm',
  '学校“语你同行”国际志愿服务团队开展涉外志愿服务专题培训': 'https://www.cqut.edu.cn/info/1266/72598.htm',
  '学校举办第二十三届“科研杯”教职工羽毛球团体赛': 'https://www.cqut.edu.cn/info/1266/72947.htm',
  '学校举办2026年荧光夜跑活动': 'https://www.cqut.edu.cn/info/1266/72943.htm',
  '重庆工商大学文学与新闻学院副教授杨霞做客“两江讲坛”': 'https://www.cqut.edu.cn/info/1266/72930.htm',
  '学校开展辅导员心理健康工作专项培训': 'https://www.cqut.edu.cn/info/1266/72875.htm',
  '西南大学文学院教授张兴成做客“两江讲坛”': 'https://www.cqut.edu.cn/info/1266/72833.htm',
};
const NEW = [
  // ===== 4 screenshot items (individually verified on official page) =====
  { t:`实现突破！学校获批13项国家社会科学基金项目`, src:`科学技术研究院`, date:`2026-11-11`, cat:`school`, tag:`news`, col:`学校要闻`,
    url:`https://www.cqut.edu.cn/info/1049/72946.htm`,
    sum:`11月10日全国哲学社会科学工作办公室公布2026年国家社科基金年度项目立项结果，学校获批年度项目12项（重点1、一般3、西部5、青年3），另获全国教育科学规划西部项目1项，共13项，较2025年增长160%，创历史新高。来源：科学技术研究院（2026-11-11）。` },
  { t:`从“一把扳手”到世界冠军，张雪来了！`, src:`车辆工程学院`, date:`2026-10-30`, cat:`school`, tag:`news`, col:`学校要闻`,
    url:`https://www.cqut.edu.cn/info/1049/72705.htm`,
    sum:`10月29日张雪机车创始人张雪走进重理工作校园宣讲，校党委书记康骞会见并围绕产教融合达成共识；张雪分享从农村少年到摩托车维修工、再到WSBK世界赛道之巅的历程，现场校招计划招录超100人、研发岗占70%以上。来源：车辆工程学院（2026-10-30）。` },
  { t:`学校学子在第十届全国医药院校药学/中药学专业大学生实验技能展示活动中斩获一、三等奖`, src:`药学与生物工程学院`, date:`2026-11-11`, cat:`school`, tag:`news`, col:`学校要闻`,
    url:`https://www.cqut.edu.cn/info/1049/72945.htm`,
    sum:`11月6—8日第十届全国医药院校药学/中药学专业大学生实验技能展示活动在安徽举办，学校药学与生物工程学院本科生李晟涛、黄涛分获一等奖、三等奖，实现学校在该项全国权威赛事历史性突破。来源：药学与生物工程学院（2026-11-11）。` },
  { t:`校领导带队参加2026年全国高校仪器类专业教学研讨会并作主题报告`, src:`机械工程学院`, date:`2026-11-11`, cat:`school`, tag:`news`, col:`学校要闻`,
    url:`https://www.cqut.edu.cn/info/1049/72952.htm`,
    sum:`11月5—7日2026年全国高校仪器类专业教学研讨会在杭州召开，校党委常委、副校长彭艳教授带队参会并围绕“产教协同育人”作大会报告，展示学校仪器科学与技术学科产教融合育人改革成效，期间赴杭州华澜微电子座谈拓展合作。来源：机械工程学院（2026-11-11）。` },

  // ===== 通知公告 (recent) =====
  { t:`停电施工通知`, src:`后勤保障处`, date:`2026-11-12`, cat:`school`, tag:`svc`, col:`通知公告` },
  { t:`重庆理工大学2026年拟聘工作人员公示（第七批）`, src:`人事处`, date:`2026-11-11`, cat:`school`, tag:`pub`, col:`通知公告` },
  { t:`关于开展2026-2027学年第一学期期中研究生评教工作的通知`, src:`研究生院`, date:`2026-11-11`, cat:`school`, tag:`grad`, col:`通知公告` },
  { t:`关于开展2026-2027学年第一学期期中本科生集中终结性评教工作的通知`, src:`教务处`, date:`2026-11-11`, cat:`school`, tag:`exam`, col:`通知公告` },

  // ===== 采购与招投标 =====
  { t:`MBA学院"新华语典"标准版服务采购单一来源采购方式公示`, src:`MBA学院`, date:`2026-11-04`, cat:`school`, tag:`svc`, col:`招标信息`, url:`https://www.cqut.edu.cn/info/1056/72818.htm` },
  { t:`经济金融学院Wind资讯金融终端数据服务单一来源采购方式公示`, src:`经济金融学院`, date:`2026-11-04`, cat:`school`, tag:`svc`, col:`招标信息`, url:`https://www.cqut.edu.cn/info/1056/72812.htm` },
  { t:`重庆理工大学图书馆中文社会科学引文索引（CSSCI）2027-2028采购公示`, src:`图书馆`, date:`2026-10-19`, cat:`school`, tag:`svc`, col:`招标信息`, url:`https://www.cqut.edu.cn/info/1056/72481.htm` },

  // ===== 学校要闻 (其余) =====
  { t:`学校承办第十届亚洲人工智能技术大会`, src:`学校`, date:`2026-11-02`, cat:`school`, tag:`news`, col:`学校要闻` },

  // ===== 工作动态 =====
  { t:`学校举行两江新区2026年“名企校园行”启动仪式`, src:`招生就业处`, date:`2026-11-05`, cat:`school`, tag:`act`, col:`工作动态` },
  { t:`重庆市财政局会计处来校调研并开展主题党日活动`, src:`会计学院`, date:`2026-11-04`, cat:`school`, tag:`party`, col:`工作动态` },
  { t:`学校举办2026年辅导员业务专题培训`, src:`学生工作部（处）`, date:`2026-11-04`, cat:`school`, tag:`svc`, col:`工作动态` },
  { t:`学校召开2027年教育部人文社科项目申报经验分享暨动员会`, src:`社会科学处`, date:`2026-11-04`, cat:`school`, tag:`rs`, col:`工作动态` },
  { t:`学校组织开展纪法知识测试`, src:`纪委`, date:`2026-11-03`, cat:`school`, tag:`svc`, col:`工作动态` },
  { t:`学校与巴南区开展困境学生心理关爱合作座谈`, src:`学生工作部（处）`, date:`2026-11-03`, cat:`school`, tag:`svc`, col:`工作动态` },

  // ===== 人才培养 =====
  { t:`学校举办“数智财会聚力 校政园企同行”产教融合对接交流会`, src:`会计学院`, date:`2026-11-12`, cat:`school`, tag:`rs`, col:`人才培养` },
  { t:`重庆市注册会计师行业信息化能力提升培训班（第二期）顺利开班`, src:`会计学院`, date:`2026-11-11`, cat:`school`, tag:`svc`, col:`人才培养` },
  { t:`学校举办“青春探智，AI筑城”大学生科普创作挑战赛`, src:`团委`, date:`2026-11-11`, cat:`school`, tag:`act`, col:`人才培养` },
  { t:`学校承办第五届大学生标准创新大赛`, src:`标准化学院`, date:`2026-11-06`, cat:`school`, tag:`act`, col:`人才培养` },
  { t:`学校举行2026级“AI+金融”教改班“四维导师”见面会`, src:`相关学院`, date:`2026-11-06`, cat:`school`, tag:`rs`, col:`人才培养` },

  // ===== 学术科研 =====
  { t:`学校药学与生物工程学院青年教师及团队在国际药学权威期刊Acta Pharmaceutica Sinica B发表综述论文 提出中性粒细胞膜"治疗界面"新概念`, src:`药学与生物工程学院`, date:`2026-09-24`, cat:`school`, tag:`rs`, col:`学术科研` },
  { t:`学校研究生在国际学术期刊 Knowledge-Based Systems 发表论文`, src:`研究生院`, date:`2026-11-11`, cat:`school`, tag:`rs`, col:`学术科研` },
  { t:`学校研究生在材料科学领域国际顶级期刊 Progress in Materials Science 发表海外联合培养成果`, src:`研究生院`, date:`2026-11-02`, cat:`school`, tag:`rs`, col:`学术科研` },
  { t:`爱沙尼亚塔尔图大学技术研究所Alvo Aabloo教授来校作学术报告`, src:`国际合作处`, date:`2026-10-20`, cat:`school`, tag:`rs`, col:`学术科研` },
  { t:`中国科学院院士叶向东、张平做客蝴蝶山数学论坛`, src:`数学学科`, date:`2026-10-19`, cat:`school`, tag:`rs`, col:`学术科研` },

  // ===== 对外合作 =====
  { t:`学校应用技术学院与万友汽车投资有限公司签订合作协议`, src:`应用技术学院`, date:`2026-11-10`, cat:`school`, tag:`svc`, col:`对外合作` },
  { t:`学校举办“科创天府·智汇蓉城”双流—两江新区成渝协同供需对接会专场活动`, src:`产学研合作处`, date:`2026-11-10`, cat:`school`, tag:`svc`, col:`对外合作` },
  { t:`学校举行智能网联新能源汽车热管理创新论坛暨重理工-广电计量联合实验室揭牌活动`, src:`相关学院`, date:`2026-11-09`, cat:`school`, tag:`rs`, col:`对外合作` },

  // ===== 文化活动 =====
  { t:`学校重庆知识产权学院教师张莉做客“两江讲坛”`, src:`重庆知识产权学院`, date:`2026-11-04`, cat:`school`, tag:`act`, col:`文化活动` },
  { t:`学校应用技术学院走进龙骏社区开展志愿服务活动`, src:`应用技术学院`, date:`2026-10-29`, cat:`school`, tag:`act`, col:`文化活动` },
  { t:`学校校友、盛海科技联合创始人卢延武做客“两江讲坛”`, src:`校友`, date:`2026-10-29`, cat:`school`, tag:`act`, col:`文化活动` },
  { t:`学校举行第五届低碳打卡挑战赛`, src:`团委`, date:`2026-10-28`, cat:`school`, tag:`act`, col:`文化活动` },
  { t:`学校“语你同行”国际志愿服务团队开展涉外志愿服务专题培训`, src:`国际学院`, date:`2026-10-26`, cat:`school`, tag:`act`, col:`文化活动` },
  { t:`学校举办第二十三届“科研杯”教职工羽毛球团体赛`, src:`工会`, date:`2026-11-11`, cat:`school`, tag:`act`, col:`文化活动` },
  { t:`学校举办2026年荧光夜跑活动`, src:`团委`, date:`2026-11-11`, cat:`school`, tag:`act`, col:`文化活动` },
  { t:`重庆工商大学文学与新闻学院副教授杨霞做客“两江讲坛”`, src:`重庆工商大学`, date:`2026-11-10`, cat:`school`, tag:`act`, col:`文化活动` },
  { t:`学校开展辅导员心理健康工作专项培训`, src:`学生工作部（处）`, date:`2026-11-06`, cat:`school`, tag:`svc`, col:`文化活动` },
  { t:`西南大学文学院教授张兴成做客“两江讲坛”`, src:`西南大学`, date:`2026-11-04`, cat:`school`, tag:`act`, col:`文化活动` },

  // ===== 2026-11-13 维护：补全主站可读源漏抓（全量覆盖口径；xxyw 学校要闻列表 + 主页 通知公告/工作动态 核实） =====
  { t:`关于选派教职工在职攻读博士、硕士学位的通知`, src:`人事处`, date:`2026-11-13`, cat:`school`, tag:`svc`, col:`通知公告`,
    url:`https://www.cqut.edu.cn/info/1101/72992.htm` },
  { t:`学校成功获批机械工程博士后科研流动站`, src:`研究生院`, date:`2026-11-12`, cat:`school`, tag:`news`, col:`学校要闻`,
    url:`https://www.cqut.edu.cn/info/1049/72990.htm` },
  { t:`学校党委理论学习中心组（扩大）会专题学习贯彻党的二十届五中全会精神`, src:`党委宣传部`, date:`2026-11-12`, cat:`school`, tag:`news`, col:`工作动态`,
    url:`https://www.cqut.edu.cn/info/1262/72989.htm` },
  { t:`学校举行2026年新进教职工校内岗前培训开班仪式`, src:`人事处`, date:`2026-11-10`, cat:`school`, tag:`news`, col:`学校要闻`,
    url:`https://www.cqut.edu.cn/info/1049/72928.htm` },
  { t:`2026年西部陆海新通道知识产权高校联盟年会暨中国—东盟知识产权人才培养论坛在校举行`, src:`重庆知识产权学院`, date:`2026-11-09`, cat:`school`, tag:`news`, col:`学校要闻`,
    url:`https://www.cqut.edu.cn/info/1049/72906.htm` },

  // ===== 2026-11-15 维护：补全主站可读源漏抓（全量覆盖口径；xxtz1 学校通知 + bmtz 部门通知 + zbxx 采购 列表核实） =====
  { t:`关于举行"九秩长征路·万里薪火传"全国高校接力宣讲活动（重庆理工大学站）启动仪式暨示范宣讲的通知`, src:`党委研究生工作部 研究生院`, date:`2026-11-14`, cat:`school`, tag:`act`, col:`通知公告`,
    url:`https://www.cqut.edu.cn/info/1101/73014.htm`,
    sum:`2026年是中国工农红军长征胜利90周年，由全国高校青年宣讲联盟发起、我校承办的"九秩长征路·万里薪火传"全国高校接力宣讲活动启动仪式暨示范宣讲，定于2026年11月16日（星期一）14:30在花溪校区丸美学生活动中心影剧场举行；参会含市教委领导、兄弟高校研工部负责人、校领导、各学院书记副书记及研究生辅导员、研究生宣讲团成员、本硕博学生代表等。联系人曾老师 62563405。来源：党委研究生工作部·研究生院（2026-11-14）。` },
  { t:`关于举办重庆理工大学"清廉校园"创意作品大赛的通知`, src:`纪委`, date:`2026-11-13`, cat:`school`, tag:`act`, col:`通知公告`,
    url:`https://www.cqut.edu.cn/2025clnr.jsp?urltype=news.NewsContentUrl&wbnewsid=73011&wbtreeid=1101` },
  { t:`关于开展重庆理工大学2026届毕业生就业工作先进集体和先进个人评选的通知`, src:`招生就业处`, date:`2026-11-13`, cat:`school`, tag:`pub`, col:`通知公告`,
    url:`https://www.cqut.edu.cn/info/1101/73004.htm` },
  { t:`关于做好2026年终关账及2027年开账相关事项的通知`, src:`财务处`, date:`2026-11-10`, cat:`school`, tag:`svc`, col:`通知公告`,
    url:`https://www.cqut.edu.cn/2025clnr.jsp?urltype=news.NewsContentUrl&wbnewsid=72932&wbtreeid=1101` },
  { t:`关于召开纪法教育专题培训的通知`, src:`纪委`, date:`2026-11-10`, cat:`school`, tag:`svc`, col:`通知公告`,
    url:`https://www.cqut.edu.cn/2025clnr.jsp?urltype=news.NewsContentUrl&wbnewsid=72925&wbtreeid=1101` },
  { t:`重庆理工大学"三审三校"审核与发布管理系统建设项目（融媒体二期）单一来源采购公示`, src:`采购与招投标管理中心`, date:`2026-11-12`, cat:`school`, tag:`svc`, col:`招标信息`,
    url:`https://www.cqut.edu.cn/info/1056/72984.htm`,
    sum:`重庆理工大学"三审三校"审核与发布管理系统建设项目（融媒体二期）（2026FW-0076）单一来源采购公示：拟由四川云华天成科技有限公司承接，预算¥180000元，将"三审三校"审核与发布管理能力扩展至全校20个二级学院，公示期2026年11月13日—11月17日。来源：采购与招投标管理中心（2026-11-12）。` },
  { t:`关于2026年重庆市优秀硕士学位论文拟推荐人选的公示`, src:`研究生院`, date:`2026-11-13`, cat:`school`, tag:`grad`, col:`部门通知`,
    url:`https://www.cqut.edu.cn/info/1105/73003.htm` },
  { t:`关于参加2026年重庆理工大学化学实验创新设计大赛暨第六届大学生化学实验创新设计大赛选拔赛的通知`, src:`教务处`, date:`2026-11-13`, cat:`school`, tag:`act`, col:`部门通知`,
    url:`https://www.cqut.edu.cn/info/1103/73002.htm` },
  { t:`关于举办2026-2027学年第1学期《高等数学》课程讲座的通知`, src:`教务处`, date:`2026-11-13`, cat:`school`, tag:`act`, col:`部门通知`,
    url:`https://www.cqut.edu.cn/info/1103/73001.htm` },
  { t:`关于公布第十八届全国大学生数学竞赛考场安排的通知`, src:`教务处`, date:`2026-11-13`, cat:`school`, tag:`exam`, col:`部门通知`,
    url:`https://www.cqut.edu.cn/info/1103/72901.htm` },
  { t:`第二十届一研究生学术活动月专家学术报告——基于强瞬变功率输出特性的预测辅助分频MPC能量管理策略`, src:`研究生院`, date:`2026-11-12`, cat:`school`, tag:`grad`, col:`部门通知`,
    url:`https://www.cqut.edu.cn/info/1105/72988.htm` },
  { t:`第二十届一研究生学术活动月专家学术报告——锂离子电池健康状态估计的可解释距离特征与跨工况自适应模型`, src:`研究生院`, date:`2026-11-12`, cat:`school`, tag:`grad`, col:`部门通知`,
    url:`https://www.cqut.edu.cn/info/1105/72987.htm` },
  { t:`第二十届一研究生学术活动月专家学术报告——原子级催化材料的结构设计及在高性能锂硫电池中的应用`, src:`研究生院`, date:`2026-11-12`, cat:`school`, tag:`grad`, col:`部门通知`,
    url:`https://www.cqut.edu.cn/info/1105/72986.htm` },
  { t:`关于举办重庆理工大学第八届"书山寻宝"大赛的通知`, src:`图书馆`, date:`2026-11-12`, cat:`school`, tag:`act`, col:`部门通知`,
    url:`https://www.cqut.edu.cn/info/1111/72981.htm` },
  { t:`图书馆中山讲堂数字资源使用培训专题（2026-24）——大学学习为什么需要文献检索`, src:`图书馆`, date:`2026-11-12`, cat:`school`, tag:`svc`, col:`部门通知`,
    url:`https://www.cqut.edu.cn/info/1111/72976.htm` },
  { t:`"读人：MBTI十六人格分析"个人成长小组招募通知`, src:`学生工作部（处）`, date:`2026-11-12`, cat:`school`, tag:`act`, col:`部门通知`,
    url:`https://www.cqut.edu.cn/info/1106/72973.htm` },

  // ===== 2026-11-16 维护：主站首页/学术讲座栏目可读源新增与漏抓补全（全量覆盖口径，逐条按官网标题+日期核实） =====
  { t:`学校举办2026年哈密市科技创新能力提升培训班`, src:`继续教育学院、高等教育自学考试办公室`, date:`2026-11-16`, cat:`school`, tag:`news`, col:`工作动态`,
    url:`https://www.cqut.edu.cn/info/1262/73026.htm`,
    sum:`2026年哈密市科技创新能力提升培训班由新疆哈密市科技局主办、学校继续教育学院承办，11月7日至13日在花溪校区举办，30名哈密科技系统管理干部与科技骨干参训；培训聚焦高端科创能力、企业自主创新、产学研融合等，并组织赴储能、智能网联汽车相关科研机构与企业现场研学。属校园运行/对外合作动态，与研究生科研无直接安排。来源：继续教育学院、高等教育自学考试办公室（2026-11-16）。` },
  { t:`【智汇理工·两江讲坛】从人工智能到脑科学：跨学科科研探索与创新实践`, src:`两江人工智能学院`, date:`2026-11-16`, cat:`school`, tag:`act`, col:`学术讲座`,
    url:`https://www.cqut.edu.cn/info/1341/73028.htm`,
    sum:`【智汇理工·两江讲坛】从人工智能到脑科学：跨学科科研探索与创新实践，主讲人何东毅（香港理工大学语言科学与技术系博士研究生、重理工两江人工智能学院2022-2026届校友），2026年11月16日16:30在两江校区汇文楼学术报告厅举行。内容围绕科研认知—学术成长—科研创新—学科前沿，分享科研选题、文献阅读、实验设计、SCI论文写作发表路径及AI与脑科学交叉前沿。对研究生科研思维与论文写作有参考价值。来源：两江校区党工委/管委会、两江人工智能学院官方学术讲座页（单篇日期2026-11-16）。` },
  { t:`扁担挑初心 金融照长征——“扁担银行的长征记忆”专题展在校开展`, src:`经济金融学院`, date:`2026-11-15`, cat:`school`, tag:`news`, col:`学校要闻`,
    url:`https://www.cqut.edu.cn/info/1049/73021.htm`,
    sum:`“扁担银行的长征记忆——纪念中国工农红军长征胜利90周年红色货币专题展”全国高校巡展（重庆站）11月11日起在花溪校区开展，由党委宣传部、经济金融学院党委联合中国钱币博物馆等策划，设五大板块按时间轴梳理红色金融从萌芽到赓续的发展脉络。属红色文化育人活动。来源：经济金融学院（2026-11-15）。` },
  { t:`学校与市棋牌运动管理中心举行棋牌项目合作签约仪式`, src:`学校`, date:`2026-11-13`, cat:`school`, tag:`news`, col:`学校要闻`,
    url:`https://www.cqut.edu.cn/info/1049/73005.htm` },
  { t:`学校士继方程式车队斩获2026“吉利杯”FSCC全国一等奖`, src:`学校`, date:`2026-11-13`, cat:`school`, tag:`news`, col:`学校要闻`,
    url:`https://www.cqut.edu.cn/info/1049/72998.htm`,
    sum:`据重庆理工大学官网（栏目：学校要闻，发布日期 2026-11-13）核实，标题原文以「喜讯」标注车队斩获2026“吉利杯”中国大学生方程式汽车大赛（FSCC）全国总成绩一等奖，为建队以来首个 FSCC 全国一等奖，刷新参赛历史最佳战绩。点击官方链接查看正文详情。` },
  { t:`学校召开2026年秋季学期第三次学科建设与研究生教育工作例会`, src:`研究生院`, date:`2026-11-13`, cat:`school`, tag:`news`, col:`工作动态`,
    url:`https://www.cqut.edu.cn/info/1262/73009.htm` },
  { t:`巴南区税务局来校调研并开展涉税业务交流活动`, src:`学校`, date:`2026-11-13`, cat:`school`, tag:`news`, col:`工作动态`,
    url:`https://www.cqut.edu.cn/info/1262/72993.htm` },
  { t:`【智汇理工·重理工期刊谷】名篇精读系列｜《智能技术学报（英文）》作者分享会（第12期）`, src:`期刊社`, date:`2026-11-12`, cat:`school`, tag:`act`, col:`学术讲座`,
    url:`https://www.cqut.edu.cn/info/1341/72983.htm` },
  { t:`学校第二十一届研究生学术活动月开幕式暨首届博硕学术创新论坛顺利举行`, src:`党委研究生工作部 研究生院`, date:`2026-11-12`, cat:`school`, tag:`news`, col:`学术科研`,
    url:`https://www.cqut.edu.cn/info/1264/72980.htm` },

  // ===== 2026-11-17 维护：主站首页全栏目可读源新增（全量覆盖口径，逐条按官网标题+单篇日期核实） =====
  // ===== 2026-11-18 维护：研究生院学术活动栏目弘毅讲坛 806-809 期（见下方新条目） =====
  { t:`学校举办2026年下半年党员发展对象培训`, src:`党委组织部、党委党校`, date:`2026-11-16`, cat:`school`, tag:`party`, col:`工作动态`,
    url:`https://www.cqut.edu.cn/info/1262/73031.htm`,
    sum:`学校党委党校举办2026年下半年党员发展对象培训，全校329名党员发展对象参加，采取专题辅导、实践观摩、研讨交流相结合；专题报告涵盖纪律作风、习近平新时代中国特色社会主义思想与青年成长、文化自信、党史学习，并赴校史馆与红岩精神展览馆现场教学。来源：党委组织部、党委党校（单篇正文日期 2026-11-16，已读取核实）。` },
  { t:`学校教师在第十九届图书馆管理与服务创新论坛征文中获一等奖并作大会报告`, src:`图书馆`, date:`2026-11-16`, cat:`school`, tag:`news`, col:`学校要闻`,
    url:`https://www.cqut.edu.cn/info/1049/73032.htm`,
    sum:`第十九届图书馆管理与服务创新论坛在海南海口举办，学校图书馆王丽娜老师论文《AI+HI协同的高校图书馆垂域知识服务生态构建研究——以重庆理工大学图书馆"科研态势数字驾驶舱"为例》获优秀论文一等奖并作大会报告，系重庆市高校图工委2026年度科研项目阶段性成果。论坛由教育部高校图指委、CALIS管理中心等主办。来源：图书馆（单篇正文日期 2026-11-16，已读取核实；标题去掉原文"喜讯"前缀）。` },
  { t:`让长征精神在当代青年身上打下"思想钢印"——重庆理工大学站接力宣讲启动`, src:`党委宣传部`, date:`2026-11-16`, cat:`school`, tag:`act`, col:`学校要闻`,
    url:`https://www.cqut.edu.cn/info/1049/73042.htm`,
    sum:`"九秩长征路·万里薪火传"全国高校接力宣讲活动重庆理工大学站在花溪校区启动，市教委二级巡视员卢明伦、校党委书记康骞出席致辞，校党委常委、副校长李璐主持，活动由全国高校青年宣讲联盟与学校主办。来源：学校要闻（单篇日期 2026-11-16；正文页 WAF 仅返回导航，标题经首页栏目与正文页标题核实，未编造细节）。` },
  { t:`学校承办第四届中国研究生企业管理创新大赛工商管理案例赛道西部赛区复赛`, src:`学校`, date:`2026-11-16`, cat:`school`, tag:`act`, col:`人才培养`,
    url:`https://www.cqut.edu.cn/info/1263/73034.htm`,
    sum:`由教育部学位管理与研究生教育司指导，中国学位与研究生教育学会、全国工商管理专业学位研究生教育指导委员会联合主办，学校承办的第四届中国研究生企业管理创新大赛工商管理案例赛道西部赛区复赛近日举行。属研究生学科竞赛承办动态。来源：人才培养栏目（单篇日期 2026-11-16，正文返回无可读内容，据首页栏目核实标题与日期，未编造正文细节）。` },
  { t:`学校学子在第十一届中国高校计算机大赛—移动应用创新赛中斩获三等奖`, src:`重庆知识产权学院`, date:`2026-11-16`, cat:`school`, tag:`act`, col:`人才培养`,
    url:`https://www.cqut.edu.cn/info/1263/73037.htm`,
    sum:`第十一届"中国高校计算机大赛—移动应用创新赛"决赛在浙江大学紫金港校区举行，学校重庆知识产权学院电子商务及法律专业2025级本科生于修齐在曹峥林、贾铠桦老师指导下，凭作品《PixPet——番茄钟专注与像素宠物养成》获启航赛三等奖。属本科生学科竞赛获奖动态。来源：人才培养栏目（单篇日期 2026-11-16，正文返回无可读内容，据首页栏目核实标题与日期，未编造正文细节）。` },
  { t:`【智汇理工·两江讲坛】迈向超级智能（S1）：S1时代智能医学工程人才的学习与成长`, src:`药学与生物工程学院`, date:`2026-11-11`, cat:`school`, tag:`act`, col:`学术讲座`,
    url:`https://www.cqut.edu.cn/info/1341/72953.htm`,
    sum:`主讲人杨万荣（英国利物浦大学计算机科学系博士研究生，重理工药学与生物工程学院2019-2023届本科校友），结合"医学—工程—智能"交叉领域的学术成长经历，探讨独立思辨、批判性判断、跨学科创新及人机协作能力培养，并分享奖学金申请、学科竞赛与学生科研实践成长经验；由刘盛平主持，2026年11月12日14:30在两江校区汇文楼国际学术报告厅举行。对研究生学术成长与科研实践有参考价值。来源：学术讲座页（单篇发布日期 2026-11-11，已读取核实）。` },

  // ===== 2026-11-18 维护：研究生院学术活动栏目新增（第二十届研究生学术活动月专家学术报告·弘毅讲坛 806-809 期） =====
  { t:`弘毅讲坛——从涉电公共安全视角谈配电电缆风险治理的思考与实践（研究生系列学术讲座第809期）`, src:`研究生院`, date:`2026-11-18`, cat:`school`, tag:`grad`, col:`学术讲座`,
    url:`https://yjsy.cqut.edu.cn/info/1024/5484.htm`,
    sum:`研究生院「第二十届研究生学术活动月专家学术报告暨弘毅讲坛」第809期，报告题目《从涉电公共安全视角谈配电电缆风险治理的思考与实践》，报告人方钦国（国网重庆市南供电公司运检部主任），主持人马志鹏，时间 2026年11月20日。面向全校研究生，属电力工程/公共安全跨学科讲座。来源：研究生院学术活动栏目列表页（单篇发布日期 2026-11-18，标题/日期/报告人/时间据列表页核实；正文页 WebFetch 仅返回导航、未读取到正文细节，主办承办单位等未编造）。` },
  { t:`弘毅讲坛——电测量设备可靠性评价技术与应用（研究生系列学术讲座第808期）`, src:`研究生院`, date:`2026-11-18`, cat:`school`, tag:`grad`, col:`学术讲座`,
    url:`https://yjsy.cqut.edu.cn/info/1024/5480.htm`,
    sum:`研究生院「第二十届研究生学术活动月专家学术报告暨弘毅讲坛」第808期，报告题目《电测量设备可靠性评价技术与应用》，报告人王蕊（国网重庆市电力公司营销服务中心高级工程师、IEC 国际电工委员会注册专家、国网公司国际标准化创新团队核心成员），主持人蒋东荣教授，时间 2026年11月19日（周四）10:00，地点花溪校区至善楼300，组织单位研究生院、承办电气与电子工程学院。报告介绍基于指数分布的可靠性验证试验方法与电能表可靠性快速评价体系。面向全校研究生，属电气工程跨学科讲座。来源：研究生院官方正文（单篇发布日期 2026-11-18，已读取核实）。` },
  { t:`弘毅讲坛——给机器装上"眼睛"和"大脑"：从红外测温到脑机接口的智能感知之旅（研究生系列学术讲座第807期）`, src:`研究生院`, date:`2026-11-17`, cat:`school`, tag:`grad`, col:`学术讲座`,
    url:`https://yjsy.cqut.edu.cn/info/1024/5478.htm`,
    sum:`研究生院「第二十届研究生学术活动月专家学术报告暨弘毅讲坛」第807期，报告题目《给机器装上"眼睛"和"大脑"——从红外测温到脑机接口的智能感知之旅》，报告人陈昌川（重庆邮电大学副教授、博士生导师、清华大学访问学者），时间 2026年11月18日（周三）10:00，地点两江校区崇文楼313，主办研究生院、重庆物理学会半导体物理专委会，承办物理与新能源学院。报告从红外测温出发讲智能感知与脑机接口交叉前沿，面向全校研究生，属智能感知/脑科学跨学科讲座。来源：研究生院官方正文（单篇发布日期 2026-11-17，已读取核实）。` },
  { t:`弘毅讲坛——面向未来的终极零碳能源：可控核聚变的发展历程、研究现状与技术前沿（研究生系列学术讲座第806期）`, src:`研究生院`, date:`2026-11-17`, cat:`school`, tag:`grad`, col:`学术讲座`,
    url:`https://yjsy.cqut.edu.cn/info/1024/5475.htm`,
    sum:`研究生院「第二十届研究生学术活动月专家学术报告暨弘毅讲坛」第806期，报告题目《面向未来的终极零碳能源——可控核聚变的发展历程、研究现状与技术前沿》，报告人程时葵（重庆理工大学副教授、硕士生导师，中国科学技术大学等离子体物理博士），时间 2026年11月18日（周三）9:00，地点两江校区崇文楼313，主办研究生院、重庆物理学会半导体物理专委会，承办物理与新能源学院。报告梳理核聚变能技术路线与高温等离子体约束、材料等关键挑战，面向全校研究生，属零碳能源/材料跨学科讲座。来源：研究生院官方正文（单篇发布日期 2026-11-17，已读取核实）。` },
];

// build final objects, bounded summary for non-verified
for (const it of NEW) {
  if (!it.url && URL_MAP[it.t]) it.url = URL_MAP[it.t];
  if (!it.sum) {
    it.sum = `据重庆理工大学官网（栏目：${it.col}，发布日期 ${it.date}）核实，标题为《${it.t}》。点击官方链接查看正文详情与具体要求。`;
  }
  delete it.col;
}

// dedupe by url (skip if already present)
const have = new Set(existing.map(x => x.url));
const fresh = NEW.filter(x => !have.has(x.url));
console.log('new unique items to add:', fresh.length, ' skipped(dup):', NEW.length - fresh.length);

// insert in date-desc order, preserving existing order
const merged = existing.slice();
for (const item of fresh.sort((a,b)=> b.date.localeCompare(a.date))) {
  let idx = merged.findIndex(e => e.date < item.date);
  if (idx < 0) idx = merged.length;
  merged.splice(idx, 0, item);
}

// ensure news tag exists
if (!tags.some(t => t.k === 'news')) {
  tags.push({ k: 'news', n: '📰 学校要闻/动态' });
}

// 「🎯 与我相关」标记：由 _cqut_relevance.js 单一事实来源重算，保证每日维护幂等、不可手工漂移。
// _selfcheck.js 会对每条复算并断言一致；新增/改写通知后只需重跑本脚本。
const mergedWithRel = relevance.apply(merged);

// rebuild file: head(full header comment) + UPDATED + TAGS + NOTICES + tail(SOURCES..)
// IMPORTANT: the header comment *prose* mentions window.CQUT_UPDATED, so do NOT slice at
// the first string match — that would cut the comment open and break the whole script.
const head = text.slice(0, text.indexOf('*/') + 2);
const tail = text.slice(text.indexOf('window.CQUT_SOURCES'));
// TAGS 必须保持原始手写格式 k:"exam", n:"📝 考试考务"（键不加引号、冒号后无空格），
// 因为 _preship.py 用文本正则 n:"([^"]+)" / k:"([^"]+)" 解析；JSON.stringify 的 "k": "..." 会解析失败。
// NOTICES 仍用 JSON.stringify（与原始 "t": "..." 风格一致，且对 JS 执行无影响）。
const tagsSrc = '[\n' + tags.map(function(t){
  return '  {k:"' + t.k + '", n:"' + t.n + '"}';
}).join(',\n') + '\n]';
const out =
  head +
  'window.CQUT_UPDATED = "2026-11-18";\n\n' +
  'window.CQUT_REL_NOTE = "🎯 与我相关：按研究生院/研工部、化工·材料学院、研究生培养与学位、科研项目与成果、化工材料方向、学科竞赛、奖助、文献资源、校园运行等公开信号自动标记（依据 src/tag/标题，规则见 _cqut_relevance.js）；仅作快速定位，不替代逐条阅读，也不隐藏任何通知。";\n\n' +
  'window.CQUT_TAGS = ' + tagsSrc + ';\n\n' +
  'window.CQUT_NOTICES = ' + JSON.stringify(mergedWithRel, null, 2) + ';\n\n' +
  tail;

fs.writeFileSync(file, out, 'utf8');

// full-file syntax validation (catches unterminated comment / broken script)
new vm.Script(out);
const relCount = mergedWithRel.filter(n => n.rel === 1).length;
console.log('syntax OK; total notices now:', merged.length, ' UPDATED=2026-11-18',
  ' 与我相关:', relCount, '（强相关', mergedWithRel.filter(n => n.w === 2).length,
  '｜可能相关', mergedWithRel.filter(n => n.w === 1).length, '）');
