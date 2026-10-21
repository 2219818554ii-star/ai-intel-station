const fs = require('fs');
const vm = require('vm');
const path = require('path');
module.exports = async function ({html, inline, sandbox, ok}) {
  function run(transform = x => x, saved = {}) {
    const elements = {};
    const listeners = {};
    function element(id) {
      return elements[id] ||= {id,innerHTML:'',textContent:'',style:{},dataset:{},
        classList:{add(){},remove(){},toggle(){},contains(){return false;}},
        _attrs:{},setAttribute(k,v){this._attrs[k]=v;},getAttribute(k){return this._attrs[k]??null;},removeAttribute(k){delete this._attrs[k];if(k==='src')delete this.src;},addEventListener(t,fn){(listeners[id] ||= {})[t]=fn;},
        querySelectorAll(){return [];},querySelector(){return null;},appendChild(){},focus(){}};
    }
    const documentEvents={};
    const ctx = {...sandbox, window:{...sandbox.window,sessionStorage:{getItem(k){return saved[k]||null;},setItem(k,v){saved[k]=v;}}}, document:{...sandbox.document,getElementById:element,addEventListener(t,fn){documentEvents[t]=fn;}},
      fetch:()=>Promise.reject(new Error('offline test'))};
    let code = inline.replace('render(data.report, meta);', 'window.__renderedDate = date; render(data.report, meta);').replace('  function goto(date, pushHash){','  window.__loadDate = loadDate;\n  function goto(date, pushHash){')
      .replace("    var cb = document.getElementById('cqutMatchCount');", "    window.__deadline = {dlDay:dlDay,isOpen:isOpen,isSoon:isSoon};\n    var cb = document.getElementById('cqutMatchCount');")
      .replace('  function renderComp(){', '  window.__compUX={deadline:compDeadline,status:compStatus,set:function(list,q){COMP=list;COMP_SCOPE="all";COMP_FILTER="open";COMP_SORT="deadline";COMP_QUERY=q||"";COMP_PAGE=1;renderComp();}};\n  function renderComp(){')
      .replace('  function routeHash(tab){', '  window.__routeUX={show:showTab,hash:routeHash,sync:syncRoute};\n  function routeHash(tab){')
      .replace('  function applyFilter(){', '  window.__applyDailyFilter=applyFilter;\n  function applyFilter(){');
    vm.createContext(ctx);
    vm.runInContext(transform(code),ctx);
    return {ctx,elements,listeners,documentEvents};
  }
  const base = run();
  const compCheckDates=run(x=>x.replace('var COMP = window.COMP || [];','var COMP = window.COMP || [];window.COMP_CHECKED="2099-01-01";'));
  ok(compCheckDates.elements['comp-check-note'].textContent.includes('2099-01-01')&&!compCheckDates.elements['comp-updated'].textContent.includes('2099-01-01'), '比赛来源核查日与最近成功内容更新日独立显示');
  const focus = base.ctx.window.FUNDS_STOCKS.focus;
  ok(focus.length>0 && focus.every(f=>typeof f.date==='string' && /^\d{4}-\d{2}-\d{2}$/.test(f.date)), '个股行情日期均为 ISO 字符串，未被当减法执行');
  ok(!base.elements['funds-stats'].innerHTML.includes('昨日收益') && base.elements['funds-stats'].innerHTML.includes('2026-10-15'), '快照当日收益显示快照日期');
  const nullNav=run(x=>x.replace('var H = window.FUNDS_HOLD || [];','var H = window.FUNDS_HOLD || []; H.forEach(f=>f.navAt=String(f.unit)); H[0].unit=null;'));
  ok(/估算市值（最新净值）[\s\S]*?>—</.test(nullNav.elements['funds-stats'].innerHTML) && /估算持有盈亏[\s\S]*?>—</.test(nullNav.elements['funds-stats'].innerHTML), '缺失任一净值时组合估算市值及盈亏均不汇总');
  const invalidNav=run(x=>x.replace('var H = window.FUNDS_HOLD || [];','var H = window.FUNDS_HOLD || []; H.forEach(f=>f.navAt=String(f.unit)); H[0].unit=Infinity;'));
  ok(invalidNav.elements['funds-stats'].innerHTML.includes('净值或基准数据缺失'), '非有限净值同样阻止组合汇总');
  const estimated=run(x=>x.replace('var H = window.FUNDS_HOLD || [];','var H = window.FUNDS_HOLD || []; H.forEach(f=>f.navAt=String(f.unit));'));
  const H=estimated.ctx.window.FUNDS_HOLD;
  const estPL=H.reduce((a,f)=>a+f.holdPL,0);
  const text=estimated.elements['funds-stats'].innerHTML.replace(/<[^>]*>/g,'');
  ok(text.includes(Math.abs(estPL).toFixed(2)), '已确认基准下总览估算盈亏与明细成本一致（合成测试）');
  const fixture=JSON.parse(fs.readFileSync(path.join(__dirname,'_funds_snapshot_2026-10-15.json'),'utf8'));
  ok(fixture.funds.every(expected=>{const f=base.ctx.window.FUNDS_HOLD.find(f=>f.code===expected.code);return f && Object.keys(expected).every(k=>f[k]===expected[k]);}), '基金金额、日收益、持有收益、收益率及累计收益与清晰截图转录基线一致');
  const cash=base.ctx.window.FUNDS_CASH || [];
  ok(cash.length===1 && cash[0].n==='余额宝' && cash[0].amt===270.15 && cash[0].dayPL===0.01 && cash[0].cumulativePL===0.92 && !cash[0].code, '余额宝单列现金管理，不伪造基金代码或持有收益');
  ok(base.elements['funds-stats'].innerHTML.replace(/,/g,'').includes('2532.55') && base.elements['funds-stats'].innerHTML.includes('52.91'), '资产总额及日收益包含余额宝，分别为2532.55及-52.91');
  ok(base.ctx.window.FUNDS_HOLD.every(f=>f.navAt===null) && base.elements['funds-stats'].innerHTML.includes('净值或基准数据缺失'), '新快照缺少份额基准时不沿用旧份额估算');
  const d=base.ctx.window.__deadline;
  ok(d.dlDay({dl:'2026-10-16 12:00（校赛）'})===Date.parse('2026-10-16T12:00:00+08:00'), '比赛明确截止时刻按北京时间解析');
  ok(d.dlDay({dl:'2026-10-16'})===Date.parse('2026-10-16T23:59:59+08:00'), '仅日期的截止保留到北京时间当天末');
  ok(d.dlDay({dl:'2026-09-28 起各校不一'})===null && d.dlDay({dl:'以通知为准（2026-09-28 发布）'})===null, '开始日期和发布日期不误当截止');
  ok(!d.isOpen({st:'报名中',dl:'2000-01-01'}) && !d.isSoon({st:'报名中',dl:'2000-01-01'}), '已过期比赛退出正在报名和快截止');
  ok(!d.isSoon({st:'报名中',dl:new Date(Date.now()+86400000).toISOString().slice(0,10),deadlineUnverified:true})&&!d.isOpen({st:'报名中',dl:'2000-01-01',deadlineUnverified:true}), '待核实截止不生成临近提示，也不能让已过期报名重新开放');
  const pendingMatch=run(x=>x.replace('var M = window.MATCHES || [];','var M = window.MATCHES || []; M=M.map((m,i)=>i?m:{...m,deadlineUnverified:true,verificationNote:"独立原文年份待核实"});'));
  ok(pendingMatch.elements['match-list'].innerHTML.includes('截止待核实')&&pendingMatch.elements['match-list'].innerHTML.includes('独立原文年份待核实')&&pendingMatch.elements['matchOpenCount'].textContent.includes('条待核实'), '报名候选中待核实项目单独计数并在卡片解释来源限制');
  const matchMarkup=run(x=>x.replace('var M = window.MATCHES || [];','var M = window.MATCHES || []; M=M.map((m,i)=>i?m:{...m,intro:"<b>重点说明</b><img src=x onerror=alert(1)>"});'));
  const matchMarkupHtml=matchMarkup.elements['match-list'].innerHTML;
  ok(matchMarkupHtml.includes('重点说明')&&!matchMarkupHtml.includes('&lt;b&gt;')&&matchMarkupHtml.includes('&lt;img src=x onerror=alert(1)&gt;')&&!matchMarkupHtml.includes('<img'), '比赛正文不显示旧加粗标记，其他HTML仍严格转义');
  const ux=base.ctx.window.__compUX;
  ok(ux.deadline({reg:'报名 9/1 – 10/23 12:00'})?.time===Date.parse('2026-10-23T12:00:00+08:00'), '比赛列表从明确报名区间提取北京时间截止时刻');
  ok(ux.deadline({reg:'即日起 – 2026/10/20 24:00'})?.time===Date.parse('2026-10-21T00:00:00+08:00'), '比赛列表正确处理截止日期的24:00');
  ok(['全年滚动','官网2026-09-28 发布','报名 10/20（赛题延至10/27）','2027/1/28 美东截止','12/1 – 1/5','2026/2/30 截止'].every(reg=>ux.deadline({reg})===null), '滚动、发布、延期、多时区、跨年不明及非法日期不生成虚假倒计时');
  const fixtureComp=(n,reg)=>({scope:'me',st:'open',pri:2,ai:3,n,reg,type:'数据',team:'1–3人',url:'https://example.org/'+encodeURIComponent(n)});
  ux.set([{...fixtureComp('旧入口已失效','全年滚动'),entryUnavailable:true,alt:'https://example.org/official-archive'}]);
  const archivedEntry=base.elements['comp-list'].innerHTML;
  ok((archivedEntry.match(/class="go" href="https:\/\/example.org\/official-archive"/g)||[]).length===2&&(archivedEntry.match(/官方历史资料/g)||[]).length===2&&!archivedEntry.includes('href="https://example.org/'+encodeURIComponent('旧入口已失效')+'"'), '已核实失效入口的主按钮及展开按钮均转向明确标注的官方历史资料');
  ux.set([fixtureComp('晚截止','2099/12/30 截止'),fixtureComp('已过期','2000/1/1 截止'),fixtureComp('早截止','2099/11/30 截止'),fixtureComp('滚动赛','全年滚动')]);
  const compOrdered=base.elements['comp-list'].innerHTML;
  ok(compOrdered.indexOf('早截止')<compOrdered.indexOf('晚截止') && compOrdered.indexOf('晚截止')<compOrdered.indexOf('滚动赛') && !compOrdered.includes('已过期'), '截止最近排序生效，未知日期沉底且过期赛事退出可报名');
  ux.set([fixtureComp('AI 模型','2099/12/30 截止'),fixtureComp('数学建模','2099/12/30 截止')],'ai');
  ok(base.elements['comp-list'].innerHTML.includes('AI 模型') && !base.elements['comp-list'].innerHTML.includes('数学建模'), '比赛关键词搜索实际过滤数据');
  ux.set([fixtureComp('AI 模型','2099/12/30 截止')],'不存在的词');
  ok(base.elements['comp-list'].innerHTML.includes('没有找到匹配'), '比赛搜索无结果时提供恢复操作提示');
  const route=base.ctx.window.__routeUX;
  base.ctx.window.location.hash='#funds'; route.sync();
  ok(base.elements['view-funds'].style.display==='' && base.elements['view-daily'].style.display==='none' && route.hash('funds')==='#funds', '基金独立链接打开基金栏目，不被日报覆盖');
  base.ctx.window.location.hash='#research'; route.sync();
  ok(base.elements['view-research'].style.display==='' && base.elements['view-funds'].style.display==='none' && route.hash('research')==='#research', '科研独立链接切换栏目且隐藏前一栏目');
  const researchMarkup=html.split('id="view-research"')[1].split('id="view-funds"')[0];
  ok(researchMarkup.includes('id="research-list"') && !researchMarkup.includes('<iframe'), '科研在原栏目直接展示任务，不再嵌入或跳转重复网站');
  ok(!html.includes('1-dfc8ry6ARxWM071wltd-LSZq30FtxxQwPoKD9zMuFw'), '科研公开页面不包含完整总表ID');
  ok(researchMarkup.includes('实验记录 · 私有') && researchMarkup.includes('?view=journal') && !html.includes('LOG-20261021-001') && !html.includes('journal-data.json'), '科研提供私有实验记录入口，实际记录未进入公开页面');
  ok(researchMarkup.includes('保持私有') && researchMarkup.includes('展示表') && researchMarkup.includes('工时'), '科研说明明确展示来源、工时性质和私有边界');
  await require('./_research_regression.js')({ok});
  base.ctx.window.location.hash='#rank';route.sync();
  ok(base.elements['view-rank'].style.display==='' && base.elements['view-funds'].style.display==='none', '栏目地址变化正确切换可见视图');
  const restored=run(x=>x,{'ai-view-scroll':JSON.stringify({funds:1400}),'ai-comp-state':JSON.stringify({query:'人工智能',sort:'pri',scope:'all',filter:'all',page:2})});
  const scrollCalls=[];restored.ctx.window.scrollTo=x=>scrollCalls.push(x);
  restored.ctx.window.location.hash='#funds';restored.ctx.window.__routeUX.sync();
  restored.documentEvents.DOMContentLoaded();
  ok(scrollCalls.at(-1)?.top===1400,'重新打开栏目在数据和控件渲染完成后恢复阅读位置');
  ok(restored.elements['comp-search'].value==='人工智能'&&restored.elements['comp-list'].innerHTML.includes('人工智能'),'刷新后比赛关键词与筛选状态保留');
  restored.listeners['comp-reset'].click();
  const clearedComp=JSON.parse(restored.ctx.window.sessionStorage.getItem('ai-comp-state'));
  ok(restored.elements['comp-search'].value===''&&clearedComp.scope==='me'&&clearedComp.filter==='open'&&clearedComp.page===1,'清除比赛筛选恢复默认列表与第一页');
  const newsCard={style:{},getAttribute(){return 'alpha learning';}}, summaryCard={style:{},getAttribute(){return null;}};
  const newsBlock={id:'sec-models',style:{},querySelector(){return newsCard.style.display==='none'?null:newsCard;}},summaryBlock={id:'daily-summary',style:{}};
  base.ctx.document.querySelectorAll=sel=>sel==='#main .card[data-search]'?[newsCard]:(sel==='#main .card'?[newsCard,summaryCard]:(sel==='#main .block'?[newsBlock,summaryBlock]:[]));
  base.elements.search.value='alpha';let filterError=null;
  try{base.ctx.window.__applyDailyFilter();}catch(e){filterError=e;}
  ok(!filterError&&newsCard.style.display===''&&summaryBlock.style.display==='none'&&base.elements.matchInfo.innerHTML.includes('1 / 1'),'日报搜索排除总结卡片，不报错且命中统计准确');
  base.elements.search.value='missing';base.ctx.window.__applyDailyFilter();
  ok(base.elements['daily-search-empty'].hidden===false&&newsBlock.style.display==='none','日报搜索无结果时显示可恢复的空状态');
  base.listeners['daily-reset'].click();
  ok(base.elements.search.value===''&&summaryBlock.style.display===''&&newsCard.style.display==='','清除日报搜索恢复新闻与总结');
  ok(base.elements['p-models'].innerHTML.includes('rank-mobile') && base.elements['p-tools'].innerHTML.includes('评分与说明') && html.includes('top:var(--appbar-height'), '手机摘要与动态顶部避让结构存在，完整桌面表格保留');
  const noticeSearch=base.listeners['cqut-search'].input;
  noticeSearch({target:{value:'不会存在的通知关键词'}});
  ok(base.elements['cqut-list'].innerHTML.includes('没有匹配') && base.elements['cqut-search-count'].textContent.includes('0'), '通知搜索及零结果计数生效');
  const review=JSON.parse(fs.readFileSync(path.join(__dirname,'_matches_review_2026-10-17.json'),'utf8'));
  const retiredMatches=base.ctx.window.MATCH_RETIRED||[];
  ok(review.added.every(x=>base.ctx.window.MATCHES.concat(retiredMatches).filter(m=>m.n===x.n&&m.url===x.url&&m.dl===x.dl).length===1) && review.removed.every(x=>!base.ctx.window.MATCHES.some(m=>m.n===x.name)), '新增赛项身份在活跃/有据退役中唯一可追溯，旧清退条目未回流');
  base.listeners['cqut-reset'].click();
  const firstNotices=base.elements['cqut-list'].innerHTML;
  base.listeners['cqut-pager'].click({target:{closest(){return{disabled:false,getAttribute(){return '2';}};}}});
  ok((firstNotices.match(/<article /g)||[]).length===30 && base.elements['cqut-list'].innerHTML!==firstNotices && base.elements['cqut-search-count'].textContent.includes('31–60') && JSON.parse(base.ctx.window.sessionStorage.getItem('ai-cqut-state')).page===2, '通知分页真实显示下一批30条，页码与阅读状态保存');
  base.listeners['cqut-search'].input({target:{value:'奖学金'}});
  ok(JSON.parse(base.ctx.window.sessionStorage.getItem('ai-cqut-state')).page===1 && base.elements['cqut-search-count'].textContent.includes(String(base.ctx.window.CQUT_NOTICES.filter(n=>[n.t,n.src,n.sum,n.date].join(' ').includes('奖学金')).length)), '分页后搜索仍覆盖全部通知，并回到第一页');
  const escaped=run(x=>x.replace('var RANK = window.RANK || {};','var RANK = window.RANK || {}; RANK.combos[0].score="<img src=x onerror=alert(1)>"; RANK.tables.aa.rows[0][1]="<img src=x onerror=alert(1)>";'));
  ok(!escaped.elements['p-combos'].innerHTML.includes('<img') && !escaped.elements['p-tables'].innerHTML.includes('<img'), '排行榜评级及分数不会插入 HTML 标签');
  const empty=run(x=>x.replace('var RANK = window.RANK || {};','var RANK = {};'));
  ok(empty.elements['funds-list'].innerHTML.includes('012920'), '缺少排行榜数据不阻断其他栏目初始化');
  for(const [id,column] of [['p-models',2],['p-tools',2],['p-combos',2]]) {
    const rows=[...base.elements[id].innerHTML.matchAll(/<tbody>([\s\S]*?)<\/tbody>/g)][0][1];
    const vals=[...rows.matchAll(/<tr>(.*?)<\/tr>/g)].map(r=>[...r[1].matchAll(/<td[^>]*>(.*?)<\/td>/g)][column][1].replace(/<[^>]*>/g,''));
    const n=vals.map(v=>id==='p-combos'?({S:3,A:2,B:1}[v]||0):(v==='—'?-Infinity:Number(v)));
    ok(n.every((v,i)=>!i||n[i-1]>=v), id+' 实际渲染按分降序且无分沉底');
  }
  const tables=[...base.elements['p-tables'].innerHTML.matchAll(/<tbody>([\s\S]*?)<\/tbody>/g)];
  ok(tables.length===4 && tables.every(t=>{const n=[...t[1].matchAll(/font-weight:700">([^<]*)</g)].map(m=>parseFloat(m[1]));return n.every((v,i)=>!i||n[i-1]>=v);}), 'AA / TB / SWE Verified / SWE Pro 分别实际渲染降序');
  const rank=base.ctx.window.RANK;
  const toolCells=[...base.elements['p-tools'].innerHTML.matchAll(/<tr>(.*?)<\/tr>/g)].map(row=>[...row[1].matchAll(/<td[^>]*>(.*?)<\/td>/g)].map(cell=>cell[1].replace(/<[^>]*>/g,''))).filter(row=>row.length===8);
  const sortedTools=rank.tools.slice().sort((a,b)=>(b.tb??-1)-(a.tb??-1));
  ok(toolCells.length===sortedTools.length&&sortedTools.every((tool,i)=>toolCells[i][5]===(tool.t.up||tool.t['上手']||'—')&&toolCells[i][6]===(tool.t.os||tool.t['开源']||'—')), '工具桌面评级与实际中文/英文键数据逐项一致，和手机卡保持一致');
  const currentRankProof=JSON.parse(fs.readFileSync(path.join(__dirname,'_rank_review_'+base.ctx.window.RANK_UPDATED+'.json'),'utf8'));
  ok(currentRankProof.checkedAt===base.ctx.window.RANK_UPDATED&&JSON.stringify(rank.tables.aa.rows)===JSON.stringify(currentRankProof.aaApplied), '当前AA选录逐项对应独立官方核查报告，不混用型号与推理档位');
  const rankReview=JSON.parse(fs.readFileSync(path.join(__dirname,'_rank_review_2026-10-19.json'),'utf8'));
  ok(rank.tables.swe.rows.length===4 && rank.tables.swe.rows.every(r=>r[0].endsWith(' — Verified')) && rank.tables.swe_pro.rows.length===3 && rank.tables.swe_pro.rows.every(r=>r[0].endsWith(' — Pro')) && JSON.stringify(rank.tables.swe.rows)===JSON.stringify(rankReview.sweApplied.verified) && JSON.stringify(rank.tables.swe_pro.rows)===JSON.stringify(rankReview.sweApplied.pro), 'SWE历史分数完整保留、按基准分组且没有误混TB成绩');
  // Let initialization's intentionally offline fetch settle before exercising request ordering.
  await new Promise(resolve=>setImmediate(resolve));
  const pending={};
  base.ctx.fetch=url=>new Promise((resolve,reject)=>{pending[url.split('/').pop()]={resolve,reject};});
  base.ctx.window.__loadDate('2026-10-14');
  base.ctx.window.__loadDate('2026-10-13');
  pending['2026-10-13'].resolve({ok:true,json:async()=>({report:{date:'2026-10-13',sections:[]}})});
  await new Promise(resolve=>setImmediate(resolve));
  // Empty reports exercise render errors too: a stale response must never replace the resulting UI.
  const latestHTML=base.elements.main.innerHTML;
  pending['2026-10-14'].resolve({ok:true,json:async()=>({report:{date:'2026-10-14',sections:[]}})});
  await new Promise(resolve=>setImmediate(resolve));
  ok(base.elements.main.innerHTML===latestHTML && base.ctx.window.__renderedDate==='2026-10-13', '旧日报响应不能覆盖较新请求的页面');
  base.ctx.window.__loadDate('2026-10-12');
  base.ctx.window.__loadDate('2026-10-11');
  pending['2026-10-12'].reject(new Error('STALE_ERROR_SENTINEL'));
  await new Promise(resolve=>setImmediate(resolve));
  ok(!base.elements.main.innerHTML.includes('STALE_ERROR_SENTINEL') && base.elements.refreshBtn.disabled, '旧请求失败不能显示错误或解锁新请求按钮');
  pending['2026-10-11'].reject(new Error('LATEST_ERROR_SENTINEL'));
  await new Promise(resolve=>setImmediate(resolve));
  ok(base.elements.main.innerHTML.includes('LATEST_ERROR_SENTINEL') && !base.elements.refreshBtn.disabled, '最新请求失败正常显示错误并恢复刷新按钮');
  for(const badDate of [undefined,'2026-02-30','2026-10-09']){
    base.ctx.window.__loadDate('2026-10-10');
    pending['2026-10-10'].resolve({ok:true,json:async()=>({report:{date:badDate,sections:[]}})});
    await new Promise(resolve=>setImmediate(resolve));
    ok(base.elements.main.innerHTML.includes('日报日期无效或与所选日期不符')&&!base.elements.hero.innerHTML.includes('NaN'), '缺失、非法或错期日报拒绝渲染：'+String(badDate));
  }
  let expected=fs.readFileSync(path.join(__dirname,'index.src.html'),'utf8');
  for(const f of ['competitions','ted','forum','rank','cqut','matches','funds','magazines'])expected=expected.replace('<script src="'+f+'.js"></script>','<script>\n'+fs.readFileSync(path.join(__dirname,f+'.js'),'utf8')+'\n</script>');
  expected=expected.replace('<script id="research-data-snapshot"></script>','<script>\nwindow.RESEARCH_SNAPSHOT='+JSON.stringify(JSON.parse(fs.readFileSync(path.join(__dirname,'research-data.json'),'utf8'))).replace(/</g,'\\u003c')+';\n</script>');
  expected=expected.replace('<script src="research.js"></script>','<script>\n'+fs.readFileSync(path.join(__dirname,'research.js'),'utf8')+'\n</script>');
  ok(['index.html','gh-pages/index.html','ai_intel_station_standalone.html'].every(f=>fs.readFileSync(path.join(__dirname,f),'utf8').replace(/\r\n/g,'\n')===expected.replace(/\r\n/g,'\n')), '三份构建产物均与当前模板和数据一致');
  await require('./_daily_recovery_regression.js')({inline,sandbox,ok});
  await require('./_magazines_regression.js')({html,inline,sandbox,ok});
  await require('./_section_rankings_regression.js')({inline,sandbox,ok});
};
