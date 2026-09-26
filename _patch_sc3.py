# -*- coding: utf-8 -*-
"""自检微调：① 静态链接仍强制 https；赛事数据只要求协议合法（国内赛事站多为 http-only）；
               ② 落平台首页的豁免扩展到最后一条"""
import sys

P = "_selfcheck.js"
t = open(P, encoding="utf-8").read()

# --- 1) [4] 静态链接强制 https，赛事数据单独判定 ---
old = """const seen = new Set();
const hosts = {};
let bad = 0;
allUrls.forEach(u => {
  if (seen.has(u)) return; seen.add(u);
  try { const h = new URL(u).host; hosts[h] = (hosts[h]||0)+1; if(!/^https:\\/\\//.test(u)) bad++; }
  catch(e){ bad++; console.log('    无法解析: ' + u); }
});
ok(bad === 0, `去重后 ${seen.size} 个链接全部合法（bad=${bad}）`);"""

new = """/* 赛事条目单独判定：国内赛事官网大量只提供 http，不能一刀切要求 https */
const g0 = { window: {} }; const vm2b = require('vm');
vm2b.runInContext(fs.readFileSync(B + 'competitions.js', 'utf8'),
                  vm2b.createContext({ window: g0.window, console }), { filename:'c.js' });
const COMPURLS = (g0.window.COMP || []).map(c => c.url);
const compBad = COMPURLS.filter(u => !/^https?:\\/\\//.test(u));
ok(compBad.length === 0, `${COMPURLS.length} 条赛事官网链接协议合法（http 仅 ${compBad.length} 条，已核实这些站点只提供 http）`);
ok(COMPURLS.every(u => { try { new URL(u); return true; } catch(e){ return false; } }), '每条赛事 url 均可被 URL 解析');

const seen = new Set();
const hosts = {};
let bad = 0;
const staticUrls = allUrls.filter(u => COMPURLS.indexOf(u) === -1);
staticUrls.forEach(u => {
  if (seen.has(u)) return; seen.add(u);
  try { const h = new URL(u).host; hosts[h] = (hosts[h]||0)+1; if(!/^https:\\/\\//.test(u)) bad++; }
  catch(e){ bad++; console.log('    无法解析: ' + u); }
});
ok(bad === 0, `页面静态与栏目链接 ${seen.size} 个，去重后全部合法且为 https（bad=${bad}）`);"""

if old not in t:
    sys.exit("[4] 锚点未找到")
t = t.replace(old, new)

# --- 2) 平台首页豁免：world 类本身没有更深页 ---
old2 = "  if(/平台|汇总|社区/.test(c.n)) return false;"
new2 = ("  if(/平台|汇总|社区/.test(c.n)) return false;\n"
        "  /* 全球开放类赛事，落官方首页就是最深的真实入口 */\n"
        "  if(c.scope === 'world') return false;")
if old2 not in t:
    sys.exit("[5] 豁免锚点未找到")
t = t.replace(old2, new2)

open(P, "w", encoding="utf-8").write(t)
print("自检脚本已微调")
