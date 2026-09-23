// 深度自检 v2：执行【构建后的 index.html】，模拟分类筛选点击，并体检运行时链接
const fs = require('fs'); const vm = require('vm');
const B = 'C:\\Users\\22198\\WorkBuddy\\2026-08-11-19-02-45\\ai_daily_site\\';
const html = fs.readFileSync(B + 'index.html', 'utf8');

let pass = 0, fail = 0;
function ok(cond, msg){ if(cond){ pass++; console.log('  [PASS] ' + msg); } else { fail++; console.log('  [FAIL] ' + msg); } }
const count = (s, re) => (s.match(re) || []).length;

console.log('\n[1] 静态结构');
const tabs = [...html.matchAll(/data-tab="([^"]+)"/g)].map(m => m[1]);
ok(tabs.length === 6, `tab 数量 = ${tabs.length}（期望 6）: ${tabs.join(', ')}`);
ok(['daily','rank','comp','learn','ted','forum'].every(v => html.includes(`id="view-${v}"`)), 'view 区块 = 6/6');
ok(html.includes('["daily","rank","comp","learn","ted","forum"]'), 'showTab 数组含全部 6 个视图');
ok(!/<script src="(competitions|ted|forum)\.js"/.test(html), '三个数据文件均已内联（无外链脚本）');
const httpLeft = count(html, /href="http:\/\//g);
ok(httpLeft === 0, `无 http:// 明文链接（剩余 ${httpLeft}）`);

console.log('\n[2] 运行时执行（vm 模拟浏览器）');
const inline = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n');
const store = {}; const listeners = {};
function mkEl(id){
  const e = { id, innerHTML:'', textContent:'', style:{}, dataset:{}, _a:{},
    classList:{add(){},remove(){},toggle(){return false;},contains(){return false;}},
    setAttribute(k,v){e._a[k]=v;}, getAttribute(k){return e._a[k]??null;},
    addEventListener(t,fn){ (listeners[id]=listeners[id]||{})[t]=fn; },
    appendChild(){}, querySelector(){return null;}, querySelectorAll(){return [];},
    closest(){return null;}, focus(){} };
  return e;
}
const sandbox = {
  console, document: { getElementById(id){ return store[id] || (store[id]=mkEl(id)); },
    querySelectorAll(){return [];}, querySelector(){return null;}, createElement(){return mkEl('t');},
    addEventListener(){}, body: mkEl('body') },
  window: { COMP:[], TED:[], FORUM:[], addEventListener(){}, scrollTo(){},
    matchMedia(){return{matches:false,addEventListener(){}};},
    localStorage:{getItem(){return null;},setItem(){},removeItem(){}}, location:{hash:''} },
  localStorage:{getItem(){return null;},setItem(){},removeItem(){}},
  navigator:{clipboard:null}, getSelection:()=>({removeAllRanges(){},addRange(){}}),
  setTimeout:()=>0, setInterval:()=>0, clearTimeout(){}, clearInterval(){},
  AbortController: class { constructor(){ this.signal={}; } abort(){} },
  fetch: () => Promise.reject(new Error('stub')),
  Date, Math, JSON, RegExp, Object, Array, String, Number, Boolean, Error, Promise,
};
sandbox.window.window = sandbox.window;
vm.createContext(sandbox);
try { vm.runInContext(inline, sandbox, {filename:'inline.js'}); ok(true, '脚本执行无异常'); }
catch(e){ ok(false, '脚本执行异常: ' + e.message); }

const cards = sel => count(((store[sel]||{}).innerHTML||''), /<article class="cmp"/g);
const btns = sel => count(((store[sel]||{}).innerHTML||''), /class="filterbtn/g);
ok(cards('ted-list') === 25, `TED 卡片 = ${cards('ted-list')}（期望 25）`);
ok(cards('forum-list') === 26, `成长讲坛卡片 = ${cards('forum-list')}（期望 26）`);
ok(btns('tedFilters') === 6, `TED 筛选按钮 = ${btns('tedFilters')}（期望 6 = 全部+5 大类）`);
ok(btns('forumFilters') === 4, `讲坛筛选按钮 = ${btns('forumFilters')}（期望 4 = 全部+3 类）`);
ok((store['ted-stat']||{}).textContent === '共 25 场（全部 25 场）', `TED 统计: ${(store['ted-stat']||{}).textContent}`);
ok((store['forum-stat']||{}).textContent === '共 26 条（全部 26 条）', `讲坛统计: ${(store['forum-stat']||{}).textContent}`);
ok((store['xinxue-guide']||{}).style.display === 'none', '默认（全部）时心学面板隐藏');

console.log('\n[3] 模拟点击分类筛选');
function fireFilter(elId, cat){
  const fn = (listeners[elId]||{}).click;
  if(!fn){ ok(false, elId + ' 无 click 监听'); return; }
  const b = { getAttribute:(k)=> k==='data-c' ? cat : null };
  fn({ target: { closest:(sel)=> sel==='.filterbtn' ? b : null } });
}
fireFilter('forumFilters', '阳明心学');
ok(cards('forum-list') === 8, `讲坛「阳明心学」→ ${cards('forum-list')} 条（期望 8）`);
const gh = (store['xinxue-guide']||{}).innerHTML || '';
ok((store['xinxue-guide']||{}).style.display === '' && gh.includes('四步入门'), '心学面板显示且含「四步入门」');
ok(['心即理','知行合一','致良知','四句教'].every(k => gh.includes(k)), '面板含四个核心概念');
ok(gh.includes('① 听故事') && gh.includes('④ 落到事上'), '面板含四步路径');
fireFilter('forumFilters', '国学讲坛');
ok(cards('forum-list') === 8 && ((store['xinxue-guide']||{}).innerHTML||'').includes('tv.cctv.com/lm/bjjt/'), `讲坛「国学讲坛」→ 8 条 + 央视百家讲坛官网链接`);
fireFilter('forumFilters', '名人与企业家');
ok(cards('forum-list') === 10, `讲坛「名人与企业家」→ ${cards('forum-list')} 条（期望 10）`);
fireFilter('tedFilters', '学习成长');
ok(cards('ted-list') === 4, `TED「学习成长」→ ${cards('ted-list')} 条（期望 4）`);
fireFilter('tedFilters', '认知思维');
ok(cards('ted-list') === 7, `TED「认知思维」→ ${cards('ted-list')} 条（期望 7）`);

console.log('\n[4] 链接体检（静态 + 运行时渲染）');
const runtime = ['ted-list','forum-list'].map(k => ((store[k]||{}).innerHTML||'')).join('');
const allUrls = [...html.matchAll(/href="(https?:[^"]+)"/g)].map(m => m[1])
  .concat([...runtime.matchAll(/href="(https?:[^"]+)"/g)].map(m => m[1]));
const seen = new Set();
const hosts = {};
let bad = 0;
allUrls.forEach(u => {
  if (seen.has(u)) return; seen.add(u);
  try { const h = new URL(u).host; hosts[h] = (hosts[h]||0)+1; if(!/^https:\/\//.test(u)) bad++; }
  catch(e){ bad++; console.log('    无法解析: ' + u); }
});
ok(bad === 0, `去重后 ${seen.size} 个链接全部合法（bad=${bad}）`);
console.log('     域名分布:', JSON.stringify(hosts, null, 0));

console.log(`\n========== 自检: ${pass} 通过 / ${fail} 失败 ==========`);
process.exit(fail ? 1 : 0);
