const vm = require('vm');

// Exercise the real daily loader with a recoverable API and a minimal DOM.
// No live network and no weakened freshness or data-identity assertions.
module.exports = async function ({inline, sandbox, ok}) {
  const fmt = new Intl.DateTimeFormat('en-CA', {timeZone:'Asia/Shanghai',year:'numeric',month:'2-digit',day:'2-digit'});
  function iso(d) {
    const parts=fmt.formatToParts(d), value=t=>parts.find(p=>p.type===t).value;
    return value('year')+'-'+value('month')+'-'+value('day');
  }
  const today=iso(new Date());
  const noon=Date.parse(today+'T12:00:00+08:00');
  const yesterday=iso(new Date(noon-86400000));
  const older=iso(new Date(noon-2*86400000));
  const settle=async()=>{await new Promise(setImmediate);await new Promise(setImmediate);};

  function run({failIndex=false, hash=''}={}) {
    const elements={}, listeners={}, calls=[];
    const api={failIndex, dates:[yesterday,older]};
    function element(id) {
      return elements[id] ||= {id,innerHTML:'',textContent:'',style:{},dataset:{},
        classList:{add(){},remove(){},toggle(){},contains(){return false;}},
        setAttribute(){},getAttribute(){return null;},
        addEventListener(type, fn){(listeners[id] ||= {})[type]=fn;},
        querySelectorAll(){return [];},querySelector(){return null;},appendChild(){}};
    }
    const ctx={...sandbox,
      window:{...sandbox.window,location:{hash},sessionStorage:{getItem(){return null;},setItem(){}}},
      document:{...sandbox.document,getElementById:element},
      history:{replaceState(){},pushState(){}},
      fetch:async url=>{
        calls.push(url);
        if(url.includes('/dailies?')) {
          if(api.indexGate) await api.indexGate;
          if(api.failIndex) throw new Error('RECOVERABLE_INDEX_ERROR');
          return {ok:true,json:async()=>({items:api.dates.map(date=>({date,leadTitle:'fixture '+date}))})};
        }
        const date=url.split('/').pop();
        return {ok:true,json:async()=>({report:{date,sections:[]}})};
      }};
    ctx.location=ctx.window.location;
    const code=inline.replace('  function goto(date, pushHash){',
      '  window.__dailyRecovery={refresh:autoRefreshNow,goto:goto,current:function(){return CURRENT;}};\n  function goto(date, pushHash){');
    vm.createContext(ctx);
    vm.runInContext(code,ctx);
    return {ctx,elements,listeners,calls,api,audit:ctx.window.__dailyRecovery};
  }

  const retry=run({failIndex:true});
  await settle();
  ok(retry.elements.main.innerHTML.includes('RECOVERABLE_INDEX_ERROR'), '日报索引失败明确展示错误，可进入重试流程');
  retry.api.failIndex=false;
  retry.calls.length=0;
  const retryClick=retry.listeners.retryBtn && retry.listeners.retryBtn.click;
  if(retryClick) retryClick();
  await settle();
  ok(!!retryClick && retry.calls.some(u=>u.includes('/dailies?')) && retry.calls.some(u=>u.endsWith('/'+yesterday)) && !retry.calls.some(u=>u.endsWith('/null')) && retry.audit.current()===yesterday && !retry.elements.main.innerHTML.includes('拉取失败'),
    '首次日报索引失败后，重试重新获取索引并恢复有效日报，不请求空日期');

  const latest=run();
  await settle();
  latest.calls.length=0;
  latest.api.dates=[today,yesterday,older];
  latest.audit.refresh();
  await settle();
  ok(latest.audit.current()===today && latest.calls.some(u=>u.endsWith('/'+today)),
    '阅读最新一期时，定时检查发现新刊会加载新一期');

  const historical=run();
  await settle();
  historical.audit.goto(older);
  await settle();
  historical.calls.length=0;
  historical.api.dates=[today,yesterday,older];
  historical.audit.refresh();
  await settle();
  ok(historical.audit.current()===older && !historical.calls.some(u=>u.endsWith('/'+today)),
    '主动阅读历史日报时，定时检查新刊保留当前历史日期');

  const switching=run();
  await settle();
  let releaseIndex;
  switching.api.indexGate=new Promise(resolve=>{releaseIndex=resolve;});
  switching.api.dates=[today,yesterday,older];
  switching.audit.refresh();
  switching.audit.goto(older);
  await settle();
  releaseIndex();
  await settle();
  ok(switching.audit.current()===older,
    '定时检查等待索引期间切换历史日期，迟到的检查不会打断阅读');
};
