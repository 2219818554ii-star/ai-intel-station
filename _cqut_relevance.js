/* 「🎯 与我相关」判定的唯一事实来源（single source of truth）。
   罗浩画像：重庆理工大学化工/材料方向在读研究生；实验室做硅基负极、配位聚合物、
   水凝胶吸附剂、柚子皮衍生碳；同时参加研究生数模等学科竞赛、做论文改稿与文献检索。
   规则只读取可核实字段 src / tag / t（标题），绝不读 sum（历史策展文案里大量出现
   「研究生」等字样，会污染判定）。每条给出 rel(0/1)、w(2 强相关 / 1 可能相关)、
   why(简短理由)，便于页面显示徽章、自检复算与审计。
   标记只是快捷筛选：默认「全部通知」仍展示所有条目，不隐藏任何学校通知。 */
'use strict';

// 强相关来源：研究生口 + 化工/材料学院
var STRONG_SRC = /研究生院|党委研究生工作部|党委研工部|研工部|研究生教育|学位评定|化学化工学院|化工学院|材料科学与工程学院|材料学院/;

// 标题关键词分组
var KW = {
  grad:     /研究生|博士|硕士|学位|导师|博硕|推免|考研|研究生教育/,
  chem:     /化工|化学|材料|电池|储能|吸附|催化|电化学|新能源|碳材料|硅基|纳米|复合材料|冶金/,
  research: /科研|基金|项目申报|项目立项|课题|论文|期刊|专利|知识产权|成果转化|实验室/,
  contest:  /竞赛|大赛|挑战杯|数学建模|双碳|创新创业|技能展示|技能展|标准创新|科普创作|研究生学术活动月/,
  money:    /奖学金|奖助|助学金|资助|学费|国家助学贷款/,
  lib:      /图书馆|文献|数据库|检索|知网|数字资源|情报/,
  // 纯人文/社交/文体讲座不标；只有同时命中 chem/research 的理工类讲座才由上面规则捕获
  campus:   /停电|停水|网络|封闭|施工|校车|宿舍|实验室安全|食堂/,
  other:    /教职工|离退休|退休|工会|附属小学|幼儿园|教代会|本科生集中|本科生专属|教职工羽/,
  // 他院/校级的名单公示（拟聘、推优、评定结果、获奖名单等）：对罗浩没有可执行信息
  publicList: /拟聘|推荐人选|拟推荐|评定结果|获奖情况|名单公示|入党积极分子|发展对象|推优|任职前公示|先进集体|优秀个人|公示公告/
};

function classify(n) {
  var t = String((n && n.t) || '');
  var src = String((n && n.src) || '');
  var tag = (n && n.tag) || '';
  function hit(rel, w, why) { return { rel: rel, w: w, why: why }; }

  // 1) 明确他群专属：先排除，避免把本科生/教职工专属误标成相关
  if (KW.other.test(t)) return hit(0, 0, '');

  // 1b) 他院/校级名单公示：除非来自研究生口或标题明确研究生，否则没有可执行信息
  if (KW.publicList.test(t) && !STRONG_SRC.test(src) && !KW.grad.test(t)) return hit(0, 0, '');

  // 2) 强来源：研究生院/研工部、化学化工学院、材料学院
  if (STRONG_SRC.test(src)) return hit(1, 2, '研究生院 / 化工·材料口');

  // 3) 研究生培养、学位、招生、导师
  if (KW.grad.test(t)) return hit(1, 2, '研究生培养与学位');
  if (tag === 'grad') return hit(1, 2, '研究生事务');

  // 4) 化工·材料·电化学方向（与实验室课题直接相关）
  if (KW.chem.test(t)) return hit(1, 2, '化工·材料方向');

  // 5) 科研、项目、论文、专利
  if (KW.research.test(t)) return hit(1, 2, '科研项目与成果');

  // 6) 学科竞赛与创新实践
  if (KW.contest.test(t)) return hit(1, 2, '学科竞赛');

  // 7) 奖助学金与资助：只收「可申报/评选/政策」类，不收他院名单公示
  if (KW.money.test(t) && (KW.grad.test(t) || /申报|评选|评选办法|管理办法|通知|开展/.test(t))) {
    return hit(1, 1, '奖助与资助');
  }

  // 8) 文献、数据库与信息素养（论文改稿/检索刚需）
  if (KW.lib.test(t) || /图书馆/.test(src)) return hit(1, 1, '文献与信息素养');

  // 9) 影响实验室/宿舍的校园运行通知
  if (tag === 'svc' && KW.campus.test(t)) return hit(1, 1, '校园运行');

  return hit(0, 0, '');
}

// 给整份通知列表补充 rel / w / why；不改动其他任何字段，幂等。
function apply(notices) {
  return (notices || []).map(function (n) {
    var c = classify(n);
    var o = {};
    Object.keys(n).forEach(function (k) { o[k] = n[k]; });
    o.rel = c.rel; o.w = c.w; o.why = c.why;
    return o;
  });
}

module.exports = { classify: classify, apply: apply, KW: KW, STRONG_SRC: STRONG_SRC };
