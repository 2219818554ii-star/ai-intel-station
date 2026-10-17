const fs = require('fs');
const vm = require('vm');
const src = fs.readFileSync('cqut.js', 'utf8');
const ctx = { window: {} };
vm.createContext(ctx);
vm.runInContext(src, ctx);
let N = ctx.window.CQUT_NOTICES || [];

// 12 条经去重确认的新通知（url 与 title 均不在现有 282 条内）
const NEW = [
 {t:"关于开通校园驿站的再通知",src:"党政办公室",date:"2026-10-16",cat:"school",tag:"svc",
  sum:"校长办公室会同两江校区管委会自2026年3月13日起开通跨校区校园驿站（两江校区弘远楼一楼114学生服务大厅），专门转递两江—花溪校区间办公文件资料，方便教职工少跑腿。本次“再通知”重申驿站地点、服务时间与使用流程。研究生若需在两校区间递送纸质材料，可走驿站；日常学习影响不大，但跨校区办事的同学可留意，避免白跑。",
  url:"https://www.cqut.edu.cn/info/1101/72457.htm"},
 {t:"关于开展“士继夜校、理继匠心”培训项目宣传周现场咨询活动的通知",src:"继续教育学院",date:"2026-10-16",cat:"school",tag:"act",
  sum:"继续教育学院举办“士继夜校、理继匠心”学生职业能力就业能力提升培训项目宣传周现场咨询活动，覆盖语言出国、公考就业、财经考证、职业技能考证、数字技术工程师、AIGC等方向。全校师生可到场了解报名条件、收费标准、补贴政策、证书发放。想提升就业竞争力或考证的硕博生可重点关注；活动为现场咨询，具体时间地点以通知原文为准。",
  url:"https://www.cqut.edu.cn/info/1101/72456.htm"},
 {t:"关于举行2026级同等学力申硕开班典礼暨现场确认的通知",src:"继续教育学院",date:"2026-10-16",cat:"school",tag:"grad",
  sum:"2026级同等学力申硕开班典礼定于2026年11月1日（周日）8:30—12:00在花溪校区中山图书馆举行，同步开展新生现场确认。面向对象为2026级同等学力申硕新生（已录取）。现场确认须带齐证件材料，按通知要求办理。同等学力申硕属研究生层次教育，相关新生重点关注；全日制统招研究生一般不受影响。",
  url:"https://www.cqut.edu.cn/info/1101/72453.htm"},
 {t:"关于转发科技部国家重点研发计划“面向脑健康的脑机接口新技术开发与产业化应用”等4个重点专项2026年度项目申报指南征求意见的通知",src:"科研院",date:"2026-10-16",cat:"school",tag:"rs",
  sum:"科研院转发科技部国家重点研发计划“面向脑健康的脑机接口新技术开发与产业化应用”等4个重点专项2026年度项目申报指南征求意见，依托国家科技管理信息系统公共信息服务平台查阅。拟牵头或参与相关专项的导师/团队须按通知要求反馈意见、组织申报。涉及脑科学、脑机接口、智能装备等方向的课题组重点关注，截止与报送方式以附件原文为准。",
  url:"https://www.cqut.edu.cn/info/1104/72454.htm"},
 {t:"关于开展2027年度农业主推技术和重大引领性技术申报推荐工作的通知",src:"科研院",date:"2026-10-16",cat:"school",tag:"rs",
  sum:"科研院转发市农业农村委关于征集2027年度重庆市农业主推技术和重大引领性技术的通知，择优向农业农村部推荐。从事农业、生物、食品、资源环境等涉农方向研究的团队可申报/推荐技术成果。申报范围与截止以附件原文为准；与重理工涉农交叉学科（如药学、材料、环境）相关团队可留意。",
  url:"https://www.cqut.edu.cn/info/1104/72452.htm"},
 {t:"关于转发“关于发布2026年度国家自然科学基金委员会管理科学部专项项目‘面向未来产业的政策体系与治理机制’申请指南的通告”等2个项目指南的通告",src:"科研院",date:"2026-10-16",cat:"school",tag:"rs",
  sum:"科研院转发国家自然科学基金委员会管理科学部专项项目“面向未来产业的政策体系与治理机制”等2个项目指南的通告，面向相关二级单位组织申报。管理科学、经济、公共政策等方向教师/团队重点关注；拟申报者按指南要求准备并提交。具体申报条件与截止见附件，建议尽快与科研院对接。",
  url:"https://www.cqut.edu.cn/info/1104/72451.htm"},
 {t:"关于转发科技局征集2026年度重庆市自然科学基金创新发展联合基金（智慧医保）项目指南建议的通知",src:"科研院",date:"2026-10-16",cat:"school",tag:"rs",
  sum:"科研院转发重庆市科技局关于征集2026年度重庆市自然科学基金创新发展联合基金（智慧医保）项目指南建议的通知。联合基金面向智慧医保领域，运用现代信息技术解决医保相关科学问题。从事医药、大数据、人工智能、信息系统等方向、且可能与医保治理交叉的团队可提指南建议。建议征集截止与格式见附件原文。",
  url:"https://www.cqut.edu.cn/info/1104/72445.htm"},
 {t:"【智汇理工·两江讲坛】掌握成功法宝 规划正确人生",src:"研究生院",date:"2026-10-16",cat:"school",tag:"act",
  sum:"研究生院主办“智汇理工·两江讲坛”：校关工委立德树人工作室专家、马克思主义学院原教授江滨主讲“掌握成功法宝 规划正确人生”，引导大学生打破对成功单一迷思、主动设计人生。讲座面向全校学生，研究生可参加，时间地点以通知原文为准。属学术/成长类讲座，可计入相关课外活动。",
  url:"https://www.cqut.edu.cn/info/1341/72435.htm"},
 {t:"【智汇理工·知行讲坛】 Almost mathematics in log-perfectoid toric mirror symmetry",src:"研究生院",date:"2026-06-29",cat:"school",tag:"act",
  sum:"研究生院“智汇理工·知行讲坛”：报告人 D. Vaintrob，题目“Almost mathematics in log-perfectoid toric mirror symmetry”（对数完美胚环面镜像对称中的几乎数学），属基础数学/代数几何前沿报告。面向数学及相关方向研究生与教师，可拓宽学术视野。时间地点以原通知为准（该通知发布较早，留意该场次是否已举办/过期）。",
  url:"https://www.cqut.edu.cn/info/1341/71002.htm"},
 {t:"重庆理工大学关于2026级研究生新生入校报到注册事项的通知",src:"研究生院",date:"2026-08-28",cat:"school",tag:"grad",
  sum:"研究生院发布2026级研究生新生入校报到注册事项通知，明确报到时间、地点、所需材料与注册流程。面向2026级全体研究生新生。该通知为入学季事项（8月底），现已过报到期，但作为新生入学归档依据仍具参考价值；后续年级可参照时间安排提前准备。",
  url:"https://yjsy.cqut.edu.cn/info/1021/5184.htm"},
 {t:"重庆理工大学关于调整2027年全国硕士研究生招生考试（初试）部分专业考试科目的公告",src:"研究生院",date:"2026-07-28",cat:"school",tag:"exam",
  sum:"研究生院公告：调整2027年全国硕士研究生招生考试（初试）部分专业考试科目。凡计划报考重庆理工大学相关专业的2027考研考生须以本通知为准核对考试科目变更。对考研备考同学（含本校拟考研的本科生/同等学力人员）影响直接——可能改变复习科目。务必到研究生院官网核对本人报考专业的具体调整。",
  url:"https://yjsy.cqut.edu.cn/info/1021/5174.htm"},
 {t:"语言与传播学院2026-2027学年国家助学金公示",src:"语言与传播学院",date:"2026-10-16",cat:"college",tag:"money",
  sum:"语言与传播学院公示2026-2027学年本科生国家助学金评定结果，公示时间为2026年10月16日—10月19日。该院家庭经济困难本科生若申请了国家助学金，须在公示期内核对本人信息；如有异议，于10月19日18:00前向学院学工办实名反映（电话62566282）。涉及该院助学金评定，非本院学生无直接影响。",
  url:"https://sfl.cqut.edu.cn/info/1010/2981.htm"}
];

// 合并 + 去重（按 url 保留较新；再按 title 去重，保留较新）
const all = N.concat(NEW);
const byUrl = {};
for (const n of all) {
  const k = (n.url||'').trim();
  if (!k) continue;
  if (!byUrl[k] || (n.date > byUrl[k].date)) byUrl[k] = n;
}
let merged = Object.values(byUrl);
const byTitle = {};
for (const n of merged) {
  const k = (n.t||'').trim();
  if (!k) continue;
  if (!byTitle[k] || (n.date > byTitle[k].date)) byTitle[k] = n;
}
merged = Object.values(byTitle);

// 按 date 倒序排列
merged.sort((a,b) => (b.date||'').localeCompare(a.date||''));

// 写回：仅替换 NOTICES 块，保留 TAGS / SOURCES / 头部注释
const idxNAssign = src.indexOf('window.CQUT_NOTICES =');
const idxSources = src.indexOf('window.CQUT_SOURCES');
if (idxNAssign < 0 || idxSources < 0) { console.error('未定位 NOTICES/SOURCES 边界'); process.exit(2); }
const head = src.slice(0, idxNAssign);   // 含 CQUT_UPDATED、CQUT_TAGS 等头部
const tail = src.slice(idxSources);        // 从 window.CQUT_SOURCES = { 起

const NL = src.includes('\r\n') ? '\r\n' : '\n';
let newBlock = ('window.CQUT_NOTICES = ' + JSON.stringify(merged, null, 2) + ';\n\n').replace(/\n/g, NL);

let newSrc = head + newBlock + tail;

// 更新更新日期与头部抓取日期
newSrc = newSrc.replace('window.CQUT_UPDATED = "2026-10-16"', 'window.CQUT_UPDATED = "2026-10-17"');
newSrc = newSrc.replace('数据抓取于 2026-10-16', '数据抓取于 2026-10-17');

fs.writeFileSync('cqut.js', newSrc, 'utf8');

// 复核
const c2 = { window: {} };
vm.createContext(c2); vm.runInContext(newSrc, c2);
const NN = c2.window.CQUT_NOTICES || [];
const urls = NN.map(n=>n.url);
const dupU = urls.length - new Set(urls).size;
const tags = c2.window.CQUT_TAGS.map(t=>t.k);
const badTag = NN.filter(n=>!tags.includes(n.tag));
const noSum = NN.filter(n=>!n.sum||!n.url||!n.date);
console.log('MERGED COUNT=' + NN.length);
console.log('UPDATED=' + c2.window.CQUT_UPDATED);
console.log('DUP_URL=' + dupU);
console.log('BAD_TAG=' + badTag.length);
console.log('MISSING_FIELD=' + noSum.length);
console.log('TAGS=' + JSON.stringify(tags));
const usedTags = [...new Set(NN.map(n=>n.tag))];
console.log('USED_TAGS=' + JSON.stringify(usedTags));
console.log('NEW_ADDED=' + NEW.length);
