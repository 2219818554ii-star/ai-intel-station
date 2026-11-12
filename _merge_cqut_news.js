'use strict';
const fs = require('fs');
const vm = require('vm');
const path = require('path');

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
  'window.CQUT_UPDATED = "2026-11-12";\n\n' +
  'window.CQUT_TAGS = ' + tagsSrc + ';\n\n' +
  'window.CQUT_NOTICES = ' + JSON.stringify(merged, null, 2) + ';\n\n' +
  tail;

fs.writeFileSync(file, out, 'utf8');

// full-file syntax validation (catches unterminated comment / broken script)
new vm.Script(out);
console.log('syntax OK; total notices now:', merged.length, ' UPDATED=2026-11-12');
