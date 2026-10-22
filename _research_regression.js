const fs=require('fs'),vm=require('vm'),path=require('path');
module.exports=async function({ok}){
 const raw=JSON.parse(fs.readFileSync(path.join(__dirname,'research-data.json'),'utf8'));
 const clone=x=>JSON.parse(JSON.stringify(x));
 const timers=[];const ctx={module:{exports:{}},setInterval(){},setTimeout(fn){timers.push(fn);return timers.length;},clearTimeout(){},Intl,Date,AbortController};vm.createContext(ctx);vm.runInContext(fs.readFileSync(path.join(__dirname,'research.js'),'utf8'),ctx);
 const api=ctx.module.exports;
 const m=api.model(raw.tasks,'2026-10-22');
 ok(api.validate(raw)===raw&&raw.tasks.length===136&&raw.tasks.every(t=>Object.keys(t).length===6),'科研仅接收展示表六字段，136项任务无丢失');
 ok(m.today.length===1&&api.hours(m.today).known===2.5&&m.done.length===5,'22日剩逐颗映射1项2.5h；5项执行完成，验收仍独立');
 ok(m.week.length===9&&m.days.length===7&&m.days[0].date==='2026-10-23'&&m.days[6].date==='2026-10-29','未来7天按北京时间日期范围分组，不混入今天');
 ok(m.risk.length===10&&m.risk.filter(t=>!t.date).length===3,'展示表10项待条件含3项日期未定，风险合并去重');
 let t=clone(raw.tasks[0]);t.hours=null;
 ok(api.hours([t]).known===0&&api.hours([t]).missing===1&&api.hours([t]).text.includes('待估')&&api.risks(t,'2026-10-22').includes('预计工时待补充'),'缺工时明确标为待估，不伪造为已知零工时');
 ok(api.day('2026-02-30')===null&&api.day('2028-02-29')==='2028-02-29'&&api.addDays('2026-12-31',1)==='2027-01-01','非法日期拒绝，闰日和跨年正确');
 let done={...raw.tasks[0],status:'已完成'},cancel={...raw.tasks[1],status:'已取消'};
 ok(api.model([done,cancel],'2026-10-22').today.length===0&&api.model([done,cancel],'2026-10-22').done.length===1,'已完成和已取消退出待办，取消不计完成');
 ok(api.risks({...raw.tasks[0],date:'2026-10-20'},'2026-10-22').some(x=>x.includes('已过'))&&api.risks({...raw.tasks[0],hours:9},'2026-10-22').some(x=>x.includes('8小时')),'过期排期和单项高工时均有明确提醒');
 const bad=[x=>x.tasks[0].evidence='private',x=>x.tasks[0].title='<img src=x onerror=alert(1)>',x=>x.tasks[1].id=x.tasks[0].id,x=>x.tasks[0].date='2026-02-30',x=>x.tasks[0].hours=-1,x=>x.tasks[0].hours=Infinity,x=>x.secret='private',x=>x.tasks[0].status='假完成'];
 for(const mutate of bad){const d=clone(raw);mutate(d);let rejected=false;try{api.validate(d);}catch(e){rejected=true;}ok(rejected,'科研拒绝异常或未审核数据：'+bad.indexOf(mutate));}
 function run(fetcher,protocol='https:',snapshot=raw){
   const elements={},events={};function el(id){return elements[id]??={id,value:'',innerHTML:'',textContent:'',style:{},hidden:false,classList:{toggle(){}},addEventListener(k,fn){(events[id]??={})[k]=fn;},focus(){},scrollIntoView(){}};}
   const w={RESEARCH_SNAPSHOT:snapshot,location:{protocol,hash:''},addEventListener(){},AI_COPY(value){w.copied=value;}};
   const doc={getElementById:el,querySelectorAll(){return[];}};
   const app=api.mount(w,doc,{fetcher,today:'2026-10-22'});return{app,e:elements,events,w,click(data){events['view-research'].click({target:{closest(){return{dataset:data};}}});}};
 }
 let calls=[];let next=clone(raw);next.tasks[25].status='进行中';next.tasks[25].hours=2;next.revision='2222222222222222';next.syncedAt='2099-01-01T00:00:00Z';
 let r=run(async(url,opts)=>{calls.push({url,opts});return{ok:true,json:async()=>next};});
 ok(r.e['research-list'].innerHTML.includes('T026')&&r.e['research-list'].innerHTML.includes('预计 2.5 h'),'内联摘要可立即展示今天任务与工时');
 ok(!r.e['research-list'].innerHTML.includes('T013')&&!r.e['research-completed-panel'].hidden&&r.e['research-completed-list'].innerHTML.includes('T002')&&r.e['research-completed-list'].innerHTML.includes('科研资料整理提交'),'T002以已完成事项显著展示，不再混入待办或丢失历史');
 r.click({rscope:'done'});ok(r.e['research-list'].innerHTML.includes('T002')&&r.e['research-list-heading'].textContent==='已标记完成','已完成视图真实可查看已完成任务');r.app.setScope('today');
 ok(r.e['research-list'].innerHTML.includes('chatgpt.site/?task=T026')&&r.e['research-list'].innerHTML.includes('在上方清单直接查看')&&r.e['research-list'].innerHTML.includes('rel="noopener"')&&r.e['research-list'].innerHTML.includes('target="_top"'),'每项任务提供按编号定位的私有详情入口，公共摘要未增加字段');
 await r.app.refresh();
 ok(r.e['research-list'].innerHTML.includes('进行中')&&r.e['research-list'].innerHTML.includes('预计 2 h')&&r.app.state().data.revision===next.revision,'刷新实际替换状态和工时，不只是改变更新时间文案');
 ok(calls[0].opts.cache==='no-store'&&calls[0].url.startsWith('research-data.json?t=')&&calls[0].opts.credentials==='same-origin','刷新绕过浏览器缓存，仅请求本站展示摘要');
 r.app.setScope('all');ok(r.e['research-result-count'].textContent.includes('136 项')&&!r.e['research-more'].hidden,'全部任务保留总数并按12项分页');
 r.events['research-more'].click();ok((r.e['research-list'].innerHTML.match(/<article/g)||[]).length===24,'加载更多实际增加任务卡片');
 r.e['research-search'].value='T135';r.events['research-search'].input.call(r.e['research-search']);ok(r.e['research-result-count'].textContent.includes('1 项')&&r.e['research-list'].innerHTML.includes('T135'),'任务编号搜索覆盖全部任务而非当前页');
 r.e['research-search'].value='无匹配关键词';r.events['research-search'].input.call(r.e['research-search']);ok(r.e['research-list'].innerHTML.includes('没有匹配的任务'),'无匹配给出清除筛选提示');
 r.events['research-reset'].click();r.e['research-category'].value='实验资源';r.events['research-category'].change.call(r.e['research-category']);ok(!r.e['research-list'].innerHTML.includes('科研阅读与论文撰写'),'分类筛选实际过滤任务');
 r.events['research-reset'].click();r.click({rday:'2026-10-23'});ok(r.e['research-list-heading'].textContent.includes('2026-10-23')&&r.e['research-result-count'].textContent.includes('3 项'),'工时图点击日期会定位当天计划');
 r.click({rfeedback:'T001'});r.events['research-copy'].click.call(r.e['research-copy']);ok(r.w.copied.includes('T001')&&r.w.copied.includes('实际主动工时'),'任务反馈带编号，复制当前反馈文本');
 let fail=run(async()=>{throw Error('offline');});await fail.app.refresh();ok(fail.e['research-list'].innerHTML.includes('T026')&&fail.e['research-sync-status'].textContent.includes('不代表已同步'),'网络失败保留有效摘要并明确同步未确认');
 let invalid=run(async()=>({ok:true,json:async()=>({tasks:[]})}));await invalid.app.refresh();ok(invalid.e['research-list'].innerHTML.includes('T026')&&invalid.e['research-sync-status'].textContent.includes('失败'),'异常响应不清空已有任务或显示假空态');
 let localCalls=0,local=run(async()=>{localCalls++;},'file:');await local.app.refresh();ok(localCalls===0&&local.e['research-sync-status'].textContent.includes('本地'),'本地文件使用打包摘要，不将文件读取失败声称为已同步');
 let older=clone(raw);older.syncedAt='2000-01-01T00:00:00Z';let old=run(async()=>({ok:true,json:async()=>older}));await old.app.refresh();ok(old.app.state().data.syncedAt===raw.syncedAt&&old.e['research-sync-status'].textContent.includes('较旧'),'服务器旧缓存不覆盖较新的内联摘要');
 const waiting=[];let race=run(()=>new Promise(resolve=>waiting.push(resolve)));let one=race.app.refresh(),two=race.app.refresh();waiting[1]({ok:true,json:async()=>next});await two;waiting[0]({ok:true,json:async()=>raw});await one;ok(race.app.state().data.revision===next.revision,'连续刷新时迟到的旧请求不能覆盖最新状态');
 let timeout=run((url,opts)=>new Promise((resolve,reject)=>opts.signal.addEventListener('abort',()=>reject(Error('timeout')))));let pending=timeout.app.refresh();timers.at(-1)();await pending;ok(!timeout.e['research-refresh'].disabled&&timeout.e['research-list'].innerHTML.includes('T026')&&timeout.e['research-sync-status'].textContent.includes('失败'),'刷新超时会恢复按钮并保留原任务，不会无限卡在加载中');
};
