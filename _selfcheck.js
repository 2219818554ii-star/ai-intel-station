// 深度自检 v2：执行【构建后的 index.html】，模拟分类筛选点击，并体检运行时链接
const fs = require('fs'); const vm = require('vm');
const B = 'C:\\Users\\22198\\WorkBuddy\\2026-08-11-19-02-45\\ai_daily_site\\';
const html = fs.readFileSync(B + 'index.html', 'utf8');

let pass = 0, fail = 0;
function ok(cond, msg){ if(cond){ pass++; console.log('  [PASS] ' + msg); } else { fail++; console.log('  [FAIL] ' + msg); } }
const count = (s, re) => (s.match(re) || []).length;

console.log('\n[1] 静态结构');
const tabs = [...html.matchAll(/data-tab="([^"]+)"/g)].map(m => m[1]);
ok(tabs.length === 8, `tab 数量 = ${tabs.length}（期望 8）: ${tabs.join(', ')}`);
ok(['daily','rank','comp','learn','ted','forum','cqut','funds'].every(v => html.includes(`id="view-${v}"`)), 'view 区块 = 8/8');
ok(html.includes('["daily","rank","comp","learn","ted","forum","cqut","funds"]'), 'showTab 数组含全部 8 个视图');
ok(!/<script src="(competitions|ted|forum|rank|cqut|funds)\.js"/.test(html), '六个数据文件均已内联（无外链脚本）');
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
  encodeURIComponent, decodeURIComponent,
};
sandbox.window.window = sandbox.window;
vm.createContext(sandbox);
try { vm.runInContext(inline, sandbox, {filename:'inline.js'}); ok(true, '脚本执行无异常'); }
catch(e){ ok(false, '脚本执行异常: ' + e.message); }

const cards = sel => count(((store[sel]||{}).innerHTML||''), /<article class="cmp"/g);
const btns = sel => count(((store[sel]||{}).innerHTML||''), /class="filterbtn/g);
ok(cards('ted-list') === 25, `TED 卡片 = ${cards('ted-list')}（期望 25）`);
const tedHtml = (store['ted-list']||{}).innerHTML || '';
ok(tedHtml.includes('TED官方搜索') && tedHtml.includes('YouTube') && tedHtml.includes('B站'), 'TED 多平台观看入口已渲染（TED官方搜索/YouTube/B站）');
ok(tedHtml.includes('background:#16a34a') && tedHtml.includes('TED官方搜索'), 'TED 免费入口（TED官方搜索）染绿色');
ok(!tedHtml.includes('ted.com/talks/'), 'TED 已弃用易 404 的 ted.com/talks/<slug> 直链');
/* [2a-2] 成长讲坛 v2：系列 -> 视频两级直达（2026-09-25 按用户反馈重构） */
const FS = sandbox.window.FORUM_SERIES || [];
const FV = FS.reduce((a,s)=>a+s.vids.length, 0);
ok(FS.length === 25, `讲坛系列数 = ${FS.length}（期望 25）`);
ok(FV >= 100, `讲坛视频总数 = ${FV}（期望 >=100，实抓 B站真实视频）`);
ok(FS.every(s => s.cat && s.who && s.desc && Array.isArray(s.vids) && s.vids.length >= 3), '每个系列含 cat/who/desc/vids 且视频数>=3');
ok(FS.every(s => s.vids.every(v => /^BV[1-9A-HJ-NP-Za-km-z]{10}$/.test(v.bvid||'') && v.t && v.up && v.dur && typeof v.play==='number')), '每条视频 bvid 格式正确且 t/up/dur/play 齐全');
ok(cards('forum-list') === FS.length, `系列卡片 = ${cards('forum-list')}（期望 = 系列数 ${FS.length}）`);
const forumHtml0 = (store['forum-list']||{}).innerHTML || '';
ok(!forumHtml0.includes('search.bilibili.com'), '讲坛已不再落 B站搜索列表页（用户核心吐槽）');
ok(!forumHtml0.includes('bilibili.com/video/'), '系列层不放视频直链（先进系列再看视频）');
ok(forumHtml0.includes('进入视频清单') && forumHtml0.includes('系列'), '系列卡片含「进入视频清单」入口');
ok(btns('tedFilters') === 6, `TED 筛选按钮 = ${btns('tedFilters')}（期望 6 = 全部+5 大类）`);
ok(btns('forumFilters') === 4, `讲坛筛选按钮 = ${btns('forumFilters')}（期望 4 = 全部+3 类）`);
ok((store['ted-stat']||{}).textContent === '共 25 场（全部 25 场）', `TED 统计: ${(store['ted-stat']||{}).textContent}`);
ok((store['forum-stat']||{}).textContent === `共 ${FS.length} 个系列 / ${FV} 个视频，点系列进入视频清单`, `讲坛统计: ${(store['forum-stat']||{}).textContent}`);
ok((store['xinxue-guide']||{}).style.display === 'none', '默认（全部）时心学面板隐藏');

console.log('\n[2b] 排行榜渲染（验证 rank.js 已内联且数据正常）');
ok(((store['p-models']||{}).innerHTML||'').includes('Claude Fable 5.1'), '排行榜·大模型 已渲染');
ok(((store['p-tools']||{}).innerHTML||'').includes('Claude Code'), '排行榜·编程工具 已渲染');
ok(((store['p-combos']||{}).innerHTML||'').includes('Claude Code + Claude Fable'), '排行榜·组合 已渲染');
ok(((store['p-tables']||{}).innerHTML||'').includes('Artificial Analysis'), '排行榜·真实榜单 已渲染');

console.log('\n[2d] 基金看板渲染');
const fHold = sandbox.window.FUNDS_HOLD || [];
const fList = (store['funds-list']||{}).innerHTML || '';
const fStats = (store['funds-stats']||{}).innerHTML || '';
ok(fHold.length === 4, `持仓条数 = ${fHold.length}（期望 4）`);
ok(fList.split('<article').length - 1 === 4, `基金看板卡片 = ${fList.split('<article').length - 1}（期望 4）`);
ok(fHold.every(f => /^\d{6}$/.test(f.code||'')), '每只基金代码均为 6 位数字');
ok(fHold.every(f => f.n && typeof f.amt === 'number' && typeof f.dayPL === 'number' && typeof f.holdPL === 'number'), '每只基金 amt/dayPL/holdPL 字段齐全');
const sumAmt = fHold.reduce((a,f) => a + (f.amt||0), 0);
const sumPL  = fHold.reduce((a,f) => a + (f.holdPL||0), 0);
ok(Math.abs(sumAmt - 2492.32) < 0.01, `持仓市值合计 = ${sumAmt.toFixed(2)}（期望 2492.32）`);
ok(Math.abs(sumPL + 315.35) < 0.01, `持有收益合计 = ${sumPL.toFixed(2)}（期望 -315.35）`);
const fStatsFlat = fStats.replace(/,/g, '');
ok(fStatsFlat.includes('2492.32') && fStatsFlat.includes('-¥315.35'), '总览卡显示合计金额与持有收益（千分位随运行环境有无 ICU，只去逗号比）');
ok(fStats.includes('-11.23%'), '总览卡显示总收益率 -11.23%');
ok(fList.includes('fund.eastmoney.com/016452.html'), '基金卡片带天天基金直达链接');
ok(fList.includes('#e02424') && fList.includes('#16a34a'), '涨跌配色中国习惯（涨红 #e02424 / 跌绿 #16a34a）');
ok(fList.includes('color:#e02424') && fHold.some(f => f.holdPL > 0), '正收益的持仓确实染成红色');
ok(fList.includes('color:#16a34a') && fHold.some(f => f.holdPL < 0), '负收益的持仓确实染成绿色');
ok(((store['funds-updated']||{}).textContent||'').indexOf('2026-09-25') === 0, `基金更新日期: ${(store['funds-updated']||{}).textContent}`);
const expoHtml = (store['funds-exposure']||{}).innerHTML || '';
ok(expoHtml.includes('A股') && expoHtml.includes('海外'), '风格暴露条含 A 股 / 海外');
ok((store['funds-updated']||{}).textContent && fList.length > 500, '基金看板渲染非空');

console.log('\n[3] 模拟点击分类筛选');
function fireFilter(elId, cat){
  const fn = (listeners[elId]||{}).click;
  if(!fn){ ok(false, elId + ' 无 click 监听'); return; }
  const b = { getAttribute:(k)=> k==='data-c' ? cat : null };
  fn({ target: { closest:(sel)=> sel==='.filterbtn' ? b : null } });
}
/* 讲坛两级导航模拟：点系列卡片 / 点返回按钮 */
function openForumSeries(who){
  const fn = (listeners['forum-list']||{}).click;
  if(!fn){ ok(false, 'forum-list 无 click 监听'); return; }
  const c = { getAttribute:(k)=> k==='data-open' ? who : null };
  fn({ target:{ closest:(sel)=> sel==='[data-open]' ? c : null } });
}
function forumBack(){
  const fn = (listeners['forum-list']||{}).click;
  if(fn) fn({ target:{ closest:(sel)=> sel==='#forum-back' ? {} : null } });
}
fireFilter('forumFilters', '阳明心学');
const xxCnt = FS.filter(s=>s.cat==='阳明心学').length;
ok(cards('forum-list') === xxCnt, `讲坛「阳明心学」→ ${cards('forum-list')} 个系列（期望 ${xxCnt}）`);
const gh = (store['xinxue-guide']||{}).innerHTML || '';
ok((store['xinxue-guide']||{}).style.display === '' && gh.includes('四步入门'), '心学面板显示且含「四步入门」');
ok(['心即理','知行合一','致良知','四句教'].every(k => gh.includes(k)), '面板含四个核心概念');
ok(gh.includes('① 听故事') && gh.includes('④ 落到事上'), '面板含四步路径');
/* 两级导航实测：马云系列 -> 视频清单 -> 返回
   ⚠ 必须先切回「全部」筛选，否则当前列表里根本没有马云这个系列（真实浏览器里也同理） */
fireFilter('forumFilters', '全部');
openForumSeries('马云');
const mSeries = FS.find(s=>s.who==='马云');
const mvHtml = (store['forum-list']||{}).innerHTML || '';
ok(mSeries && cards('forum-list') === mSeries.vids.length, `点「马云」系列 → ${cards('forum-list')} 张视频卡（期望 ${mSeries?mSeries.vids.length:'?'}）`);
ok(mvHtml.includes('← 返回系列列表'), '视频清单含「← 返回系列列表」按钮');
ok(mvHtml.split('bilibili.com/video/').length - 1 === (mSeries?mSeries.vids.length:0), '每条视频都是 bilibili.com/video/<BV> 直达播放页链接');
ok(mvHtml.includes('在B站播放'), '视频卡片含「在B站播放」按钮');
ok(mvHtml.includes('👤') && mvHtml.includes('播放'), '视频卡片显示 UP主（👤）与播放量');
forumBack();
ok(cards('forum-list') === FS.length, '点返回 → 回到全量系列列表');
fireFilter('forumFilters', '全部');

console.log('\n[2c] 重庆理工通知渲染');
const cqHtml = (store['cqut-list']||{}).innerHTML || '';
ok(cards('cqut-list') === 25, `理工通知卡片 = ${cards('cqut-list')}（期望 25）`);
ok(cqHtml.includes('我该关注啥') && cqHtml.includes('源地址'), '理工通知含「我该关注啥」与「源地址」');
ok(cqHtml.includes('href="https://') && !cqHtml.includes('href="#"'), '理工通知链接均为真实 https 源地址');
const srcHtml = (store['cqut-sources']||{}).innerHTML || '';
ok(srcHtml.includes('化学化工学院') && srcHtml.includes('机械工程学院'), '理工信源矩阵含各学院');
ok(srcHtml.includes('校团委') && srcHtml.includes('研究生会'), '理工信源矩阵含学生组织');
ok((store['cqut-updated']||{}).textContent === '2026-09-25', `理工更新日期: ${(store['cqut-updated']||{}).textContent}`);
/* 分类体系是固定 8 个枚举，新通知必须归入其一，不能自创也不能漏填 */
const cqTags = sandbox.window.CQUT_TAGS || [];
const cqNotices = sandbox.window.CQUT_NOTICES || [];
const tagKeys = cqTags.map(x => x.k);
ok(tagKeys.length === 8, `理工细分类定义 = ${tagKeys.length}（期望 8）: ${tagKeys.join(',')}`);
const badTag = cqNotices.filter(n => !n.tag || tagKeys.indexOf(n.tag) < 0);
ok(badTag.length === 0, `理工每条通知都有合法 tag（非法 ${badTag.length} 条）${badTag.length ? ' → ' + badTag.map(n=>n.t).join('; ') : ''}`);
const usedTags = cqNotices.map(n => n.tag).filter((v, i, a) => a.indexOf(v) === i);
ok(usedTags.length === tagKeys.length, `8 个细分类都有通知覆盖（实际用到 ${usedTags.length}）`);
ok(!cqNotices.some(n => !n.sum || !n.url || !n.date), '理工每条通知的 sum/url/date 均完整');

const tagBtns = count(((store['cqutTagFilters']||{}).innerHTML||''), /class="filterbtn/g);
ok(tagBtns === 9, `理工二级分类按钮 = ${tagBtns}（期望 9 = 全部分类 + 8 个细分类）`);
ok(cqHtml.includes('💰') && cqHtml.includes('🎓'), '理工卡片显示细分类徽章');

/* [2c-2] 各学院赛事区块 */
const MATCHES = sandbox.window.CQUT_MATCHES || [];
const mHtml = (store['cqut-match-list']||{}).innerHTML || '';
ok(MATCHES.length === 15, `各学院赛事条数 = ${MATCHES.length}（期望 15）`);
ok(mHtml.includes('具体要干啥') && mHtml.includes('我能帮你做啥') && mHtml.includes('简介'), '赛事卡片含「简介 / 具体要干啥 / 我能帮你做啥」三行');
ok(cards('cqut-match-list') === MATCHES.length, `赛事卡片数 = ${cards('cqut-match-list')}，与数据条数一致`);
ok(MATCHES.every(m => m.intro && m.todo && m.help && m.url && m.org && m.date && m.lv && m.st), '每条赛事的 intro/todo/help/url/org/date/lv/st 均完整');
ok(MATCHES.every(m => /^https:\/\/[a-z0-9.\-]+\.cqut\.edu\.cn\//i.test(m.url)), '每条赛事的源地址都是真实 cqut.edu.cn 页面');
const needFields = ['https://cl.cqut.edu.cn/info/1034/6103.htm', 'https://cl.cqut.edu.cn/info/1034/6074.htm'];
ok(needFields.every(u => mHtml.includes(u)), '两条材料学院对口赛事链接已渲染');
ok(mHtml.includes('🎯 跟你专业对口'), '对口赛事显示了「跟你专业对口」标记');
ok((store['cqut-match-updated']||{}).textContent === '2026-09-25', `赛事更新日期: ${(store['cqut-match-updated']||{}).textContent}`);
const mBtns = count(((store['cqutMatchFilters']||{}).innerHTML||''), /class="filterbtn/g);
ok(mBtns === 5, `赛事筛选按钮 = ${mBtns}（期望 5 = 全部 + 4 个分类）`);
ok(mHtml.includes('机械工程学院') && mHtml.includes('材料科学与工程学院'), '赛事卡片显示主办学院');
fireFilter('forumFilters', '国学讲坛');
const gxCnt = FS.filter(s=>s.cat==='国学讲坛').length;
ok(cards('forum-list') === gxCnt, `讲坛「国学讲坛」→ ${cards('forum-list')} 个系列（期望 ${gxCnt}）`);
fireFilter('forumFilters', '名人与企业家');
const mrCnt = FS.filter(s=>s.cat==='名人与企业家').length;
ok(cards('forum-list') === mrCnt, `讲坛「名人与企业家」→ ${cards('forum-list')} 个系列（期望 ${mrCnt}）`);
openForumSeries('雷军');
const lj = FS.find(s=>s.who==='雷军');
ok(lj && cards('forum-list') === lj.vids.length, `名人分类下点「雷军」系列 → ${cards('forum-list')} 张视频卡`);
ok(((store['forum-list']||{}).innerHTML||'').includes('年度演讲'), '雷军系列视频与年度演讲相关');
forumBack();
fireFilter('forumFilters', '全部');
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
