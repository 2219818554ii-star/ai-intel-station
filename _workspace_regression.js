const fs=require('fs'),path=require('path');
module.exports=async function({html,ok}){
  const api=require('./workspace.js');
  const summary=JSON.parse(fs.readFileSync(path.join(__dirname,'research-data.json'),'utf8'));
  const details=JSON.parse(fs.readFileSync(path.join(__dirname,'research-details.json'),'utf8'));
  const rows=api.index({RESEARCH_SNAPSHOT:summary},id=>details.tasks.find(t=>t.id===id));
  const published={window:{}};
  for(const file of ['matches.js','competitions.js'])require('vm').runInNewContext(fs.readFileSync(path.join(__dirname,file),'utf8'),published);
  const opportunities=api.index(published.window),matchRows=opportunities.filter(r=>r.kind==='match');
  ok(matchRows.length===published.window.MATCHES.length&&matchRows.every(r=>r.route==='cqut'&&api.search(opportunities,r.title,30).some(x=>x.kind==='match'&&x.key===r.key))&&opportunities.filter(r=>r.group==='赛事库').length===published.window.COMP.length,'全站搜索逐项收录报名线索，保留全国赛事库的独立身份与入口');
  ok(api.search(rows,'T001',30).some(r=>r.route==='research'&&r.key==='T001')&&api.search(rows,'运输 接收',30).some(r=>r.key==='T001'),'工作台搜索覆盖真实任务编号及执行正文，多关键词同时匹配');
  const originalOrder=JSON.stringify(rows),precise=api.search(rows,'t015',1);
  ok(precise.length===1&&precise[0].key==='T015'&&precise[0].route==='research'&&JSON.stringify(rows)===originalOrder,'精确任务编号忽略大小写并在截断结果前优先本项，不让正文引用抢先或改动索引');
  ok(api.search(rows,'完全不存在的工作台词条',30).length===0&&api.search(rows,'',5).length===5,'工作台搜索空态与批次数量正确，不用虚构结果填充');
  ok(!api.personalNotice({cat:'college',src:'机械工程学院',tag:'money',t:'本院助学金',sum:'仅影响该院'})&&api.personalNotice({cat:'college',src:'化学化工学院',tag:'money',t:'助学金公示'})&&!api.personalNotice({cat:'school',src:'教务处',tag:'exam',t:'收卷通知',sum:'面向出题教师'})&&api.personalNotice({cat:'school',src:'研究生院',tag:'rs',t:'研究生科研成果奖励申报'}),'首页校园推荐按化工研究生相关性筛选，不把其他学院或教师办理事项放到个人待看首排');
  const noon=api.deadline({st:'报名中',dl:'2026-10-23',deadlineTime:'12:00'});
  ok(noon.at===Date.parse('2026-10-23T12:00:00+08:00')&&api.deadline({st:'报名中',dl:'2026-10-23'}).at===Date.parse('2026-10-23T23:59:59+08:00'),'首页明确时刻精确到截止瞬间，未注明时刻才按北京日末');
  ok([{st:'报名中',dl:'2026-02-30'},{st:'报名中',dl:'2026-10-26',deadlineTime:'24:30'},{st:'报名中',dl:'2026-10-26 12:00',deadlineTime:'18:00'},{st:'报名中',dl:'2026-10-26',deadlineUnverified:true},{st:'已截止',dl:'2026-10-26'}].every(t=>api.deadline(t)===null),'首页不将非法、矛盾、资格未核实或已截止数据伪造成确定报名机会');
  ok(['javascript:alert(1)','data:text/html,hi','https://user:pass@example.org/','//example.org/x','https://example.org/\nraw'].every(u=>!api.safeURL(u))&&api.safeURL('https://example.org/a')==='https://example.org/a','最近打开记录拒绝危险URL与凭据地址，合法入口保留');
  ok(html.includes('id="view-home"')&&html.includes('id="home-tasks"')&&html.includes('id="home-metrics"')&&html.includes('workspace-mobile-nav')&&!/<script src="workspace\.js"/.test(html),'今天工作台与单手快捷入口都存在，运行代码已内联可离线执行');
  const sw=fs.readFileSync(path.join(__dirname,'sw.js'),'utf8');
  ok(sw.includes("url.origin!==self.location.origin")&&sw.includes("request.method!=='GET'")&&sw.includes('research-details.json')&&!sw.includes('chatgpt.site'),'离线层只缓存本站发布资料，不缓存外站登录或发送科研写请求');
  const elements={},events={},documentEvents={},closeQueue=[],focusLog=[];
  const doc={activeElement:null,getElementById(id){
    return elements[id]||(elements[id]={id,tagName:id==='workspace-query'?'INPUT':'BUTTON',innerHTML:'',textContent:'',value:'',style:{},dataset:{},hidden:false,open:false,isConnected:true,
      focus(){doc.activeElement=this;focusLog.push(id);},addEventListener(type,handler){(events[id]||(events[id]={}))[type]=handler;},querySelector(){return null;},querySelectorAll(){return[];},contains(){return false;},setAttribute(name,value){this[name]=value;},showModal(){this.open=true;},close(){this.open=false;closeQueue.push(()=>events[id].close());}});
  },addEventListener(type,handler){documentEvents[type]=handler;}};
  let focusedTask=null,route=null;
  const world={RESEARCH_SNAPSHOT:summary,MATCHES:published.window.MATCHES,AI_RESEARCH:{state(){return{data:summary};},getDetail(id){return details.tasks.find(t=>t.id===id);},focusTask(id){focusedTask=id;doc.getElementById('task-result-heading').focus();}},
    AI_NAV:{go(next,options){route=next;if(options&&options.focus)doc.getElementById('section-heading').focus();},closeMenu(){}},
    localStorage:{getItem(){return null;},setItem(){}},sessionStorage:{getItem(){return null;},setItem(){}},navigator:{},location:{protocol:'https:'},addEventListener(){}};
  api.mount(world,doc);
  const opener=doc.getElementById('workspace-search-open'),field=doc.getElementById('workspace-query'),dialog=doc.getElementById('workspace-search');
  function open(){opener.focus();events['workspace-search-open'].click.call(opener);}
  open();field.value='T015';events['workspace-query'].input();events['workspace-query'].keydown({key:'Enter',preventDefault(){}});
  closeQueue.shift()();
  ok(route==='research'&&focusedTask==='T015'&&doc.activeElement.id==='task-result-heading'&&!dialog.open,'选择搜索结果后迟到的dialog close事件不把焦点从目标正文抢回打开按钮');
  open();field.value='T015';let prevented=false;events['workspace-search'].keydown({key:'Escape',preventDefault(){prevented=true;}});closeQueue.shift()();
  ok(prevented&&!dialog.open&&doc.activeElement===opener,'有文本的搜索框一次Escape即关闭并返回触发点，阻止原生search输入只清空文本');
  open();documentEvents.keydown({key:'k',ctrlKey:true,target:field,preventDefault(){}});events['workspace-search-close'].click();closeQueue.shift()();
  ok(!dialog.open&&doc.activeElement===opener,'已打开搜索时再次CtrlK不丢失原触发点，关闭按钮仍正确还焦点');
  let school='cqut',filter='fit',scrolled=null;
  function allButton(attribute){return {getAttribute(name){return name===attribute?'all':null;},click(){if(attribute==='data-s')school='all';else filter='all';}};}
  doc.getElementById('matchSchoolFilters').querySelectorAll=()=>[allButton('data-s')];
  doc.getElementById('matchFilters').querySelectorAll=()=>[allButton('data-f')];
  const cards=world.MATCHES.map((match,i)=>{const card=doc.getElementById('match-fixture-'+i);card.getAttribute=name=>name==='data-match-name'?match.n:null;card.scrollIntoView=()=>{scrolled=card;};return card;});
  doc.getElementById('match-list').querySelectorAll=()=>school==='all'&&filter==='all'?cards:[];
  doc.getElementById('comp-search').value='保留原赛事筛选';
  const current=world.MATCHES.filter(t=>api.deadline(t));
  for(const match of current){
    school='cqut';filter='fit';doc.getElementById('cqutMatchFold').open=false;scrolled=null;
    const button={dataset:{homeOpportunity:match.n}};
    documentEvents.click({target:{closest(selector){return selector.includes('[data-home-opportunity]')?button:null;}}});
    ok(route==='cqut'&&doc.getElementById('cqutMatchFold').open&&school==='all'&&filter==='all'&&scrolled===doc.activeElement&&doc.activeElement.getAttribute('data-match-name')===match.n&&doc.getElementById('comp-search').value==='保留原赛事筛选','首页报名机会展开并聚焦原始说明，不在全国赛事库制造空搜索：'+match.n);
  }
  const pending=world.MATCHES.find(t=>t.deadlineUnverified);
  school='city';filter='soon';doc.getElementById('cqutMatchFold').open=false;scrolled=null;
  open();field.value=pending.n;events['workspace-query'].input();events['workspace-query'].keydown({key:'Enter',preventDefault(){}});closeQueue.shift()();
  ok(route==='cqut'&&doc.getElementById('cqutMatchFold').open&&scrolled===doc.activeElement&&doc.activeElement.getAttribute('data-match-name')===pending.n&&!dialog.open,'搜索待核实报名线索仍打开对应原说明，关闭搜索不会夺走目标焦点');
};
