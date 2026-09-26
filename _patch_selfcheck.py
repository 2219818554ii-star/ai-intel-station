# -*- coding: utf-8 -*-
"""给 _selfcheck.js 补：① 比赛卡片链接纳入链接体检 ② 赛事数据级回归断言。"""
import sys

P = "_selfcheck.js"
s = open(P, encoding="utf-8").read()

# ---- 1) 把 comp-list 的运行时 HTML 纳入链接体检 ----
old4 = ("const runtime = ['ted-list','forum-list'].map(k => ((store[k]||{}).innerHTML||'')).join('');")
new4 = ("const runtime = ['ted-list','forum-list','comp-list']\n"
        "  .map(k => ((store[k]||{}).innerHTML||'')).join('');")
if old4 not in s:
    sys.exit("未找到 [4] runtime 行")
s = s.replace(old4, new4)

# ---- 2) 在收尾统计前插入赛事数据断言 ----
anchor = "console.log(`\\n========== 自检:"
if anchor not in s:
    sys.exit("未找到自检收尾行")

BLOCK = r"""
console.log('\n[5] 可报名比赛·数据级回归（2026-09-26 内容级核查后固化）');
const g = {}; g.window = { COMP: null };
const code = fs.readFileSync(B + 'competitions.js', 'utf8');
const vm2 = require('vm');
const ctx = vm2.createContext({ window: g.window, console });
vm2.runInContext(code, ctx, { filename: 'competitions.js' });
const CP = g.window.COMP || [];
ok(CP.length === 172, `赛事条目 = ${CP.length}（期望 172）`);

const need = ['n','type','st','ai','pri','team','org','reg','run','desc','fit','help','url'];
const miss = [];
CP.forEach(function(c){ need.forEach(function(k){ if(!c[k]) miss.push(c.n + ' 缺 ' + k); }); });
ok(miss.length === 0, `每条赛事字段齐全（缺失 ${miss.length} 处）` + (miss.length ? ' 例: ' + miss.slice(0,3).join(' / ') : ''));

const badUrl = CP.filter(c => !/^https?:\/\//.test(c.url || ''));
ok(badUrl.length === 0, `所有 url 均为合法 http(s)（异常 ${badUrl.length} 条）`);

/* 平台首页兜底：落首页/平台页的条目，必须显式说明原因（停办 / warn 标注） */
const platform = CP.filter(function(c){
  const u = c.url.replace(/\/+$/, '');
  const isRoot = /^https?:\/\/(cpipc\.acge\.org\.cn|www\.saikr\.com|www\.drivendata\.org|numer\.ai)$/.test(u);
  if(!isRoot) return false;
  return !(c.st || '').includes('停办') && !c.warn && !c.org.includes('未设');
});
ok(platform.length === 0, `落平台首页的条目均已显式说明（无说明 ${platform.length} 条）`
   + (platform.length ? ' 例: ' + platform.slice(0,3).map(c=>c.n).join(' / ') : ''));

/* 关键官网防回退：这些是 2026-09-26 查实替换过的，改回去即为回归 */
const byName = {}; CP.forEach(function(c){ byName[c.n] = c.url; });
const guard = [
  ['全国大学生金相技能大赛', 'https://www.jxds.tech/'],
  ['全国大学生统计建模大赛', 'http://tjjmds.ai-learning.net/'],
  ['光威杯中国复合材料学会大学生科技创新竞赛（原全国大学生碳纤维复合材料创新应用设计大赛）', 'https://cmtic.csfcm.org.cn/'],
  ['全国大学生市场调查与分析大赛', 'http://www.china-cssc.org/'],
  ['全国大学生能源经济学术创意大赛', 'https://energy.qibebt.ac.cn/eneco/'],
  ['全国大学生结构设计竞赛', 'http://www.structurecontest.com/'],
  ['全国大学生物联网设计竞赛', 'https://iot.sjtu.edu.cn/'],
  ['中国创翼创业创新大赛', 'http://www.cxcyds.com/'],
  ['共享杯科技资源共享服务创新大赛', 'https://www.escience.org.cn/'],
];
const rolled = guard.filter(function(p){ return byName[p[0]] !== p[1]; });
ok(rolled.length === 0, `${guard.length} 条已核实官网均未回退` + (rolled.length ? ' 例: ' + rolled.map(r=>r[0]).join(' / ') : ''));

/* 停办 / 失效必须写清楚 */
const stop1 = CP.filter(c => (c.st || '').includes('停办'));
ok(stop1.every(c => (c.reg || '').includes('停办') || (c.reg||'').includes('不办') || (c.warn||'')), `停办类赛事均写明原因（${stop1.length} 条）`);
ok(CP.filter(c => (c.warn||'').length).length >= 25, `官网状态标注 >= 25 条（当前 ${CP.filter(c => (c.warn||'').length).length}）`);

/* 页面必须能把 warn 渲染出来 */
ok(html.includes("c.warn?") || html.includes("c.warn'"), '卡片模板支持渲染「官网状态」标注行');
ok(html.includes('warn-row'), 'warn-row 样式已定义');

"""

s = s.replace(anchor, BLOCK + anchor)
open(P, "w", encoding="utf-8").write(s)
print("自检脚本已增强")
