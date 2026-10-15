const fs = require('fs');
const vm = require('vm');
const path = require('path');
module.exports = async function ({html, inline, sandbox, ok}) {
  function run(transform = x => x) {
    const elements = {};
    const listeners = {};
    function element(id) {
      return elements[id] ||= {id,innerHTML:'',textContent:'',style:{},dataset:{},
        classList:{add(){},remove(){},toggle(){},contains(){return false;}},
        setAttribute(){},getAttribute(){return null;},addEventListener(t,fn){(listeners[id] ||= {})[t]=fn;},
        querySelectorAll(){return [];},querySelector(){return null;},appendChild(){}};
    }
    const ctx = {...sandbox, window:{...sandbox.window}, document:{...sandbox.document,getElementById:element},
      fetch:()=>Promise.reject(new Error('offline test'))};
    let code = inline.replace('render(data.report, meta);', 'window.__renderedDate = date; render(data.report, meta);').replace('  function goto(date, pushHash){','  window.__loadDate = loadDate;\n  function goto(date, pushHash){')
      .replace("    var cb = document.getElementById('cqutMatchCount');", "    window.__deadline = {dlDay:dlDay,isOpen:isOpen,isSoon:isSoon};\n    var cb = document.getElementById('cqutMatchCount');");
    vm.createContext(ctx);
    vm.runInContext(transform(code),ctx);
    return {ctx,elements,listeners};
  }
  const base = run();
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
  ok(tables.length===3 && tables.every(t=>{const n=[...t[1].matchAll(/font-weight:700">([^<]*)</g)].map(m=>parseFloat(m[1]));return n.every((v,i)=>!i||n[i-1]>=v);}), 'AA / TB / SWE 三榜实际渲染降序');
  // Let initialization's intentionally offline fetch settle before exercising request ordering.
  await new Promise(resolve=>setImmediate(resolve));
  const pending={};
  base.ctx.fetch=url=>new Promise((resolve,reject)=>{pending[url.split('/').pop()]={resolve,reject};});
  base.ctx.window.__loadDate('2026-10-14');
  base.ctx.window.__loadDate('2026-10-13');
  pending['2026-10-13'].resolve({ok:true,json:async()=>({report:{}})});
  await new Promise(resolve=>setImmediate(resolve));
  // Empty reports exercise render errors too: a stale response must never replace the resulting UI.
  const latestHTML=base.elements.main.innerHTML;
  pending['2026-10-14'].resolve({ok:true,json:async()=>({report:{}})});
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
  let expected=fs.readFileSync(path.join(__dirname,'index.src.html'),'utf8');
  for(const f of ['competitions','ted','forum','rank','cqut','matches','funds'])expected=expected.replace('<script src="'+f+'.js"></script>','<script>\n'+fs.readFileSync(path.join(__dirname,f+'.js'),'utf8')+'\n</script>');
  ok(['index.html','gh-pages/index.html','ai_intel_station_standalone.html'].every(f=>fs.readFileSync(path.join(__dirname,f),'utf8').replace(/\r\n/g,'\n')===expected.replace(/\r\n/g,'\n')), '三份构建产物均与当前模板和数据一致');
};
