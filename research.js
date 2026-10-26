/* 科研原生阅读：六字段摘要保持原护栏；正文与只读记录仅接收独立审核导出的同版字段。 */
(function(root,factory){
  var api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(typeof document!=='undefined')root.AI_RESEARCH=api.mount(root,document);
})(typeof window!=='undefined'?window:null,function(){
  'use strict';
  var titles=["历史测量数据溯源", "合格样品测量验证", "安全与接收审批", "实验材料盘点", "实验样品制备", "实验表征与记录", "实验资源协调", "极片工艺小试与质量排查", "极片质量核验", "样品编号与异常记录", "样品编号与质量台账", "电化学测试与数据整理", "电极质量检查", "电池装配与测试核验", "电池装配规范复核", "电池装配记录", "科研记录与数据检查", "科研资料整理提交", "科研阅读与论文撰写", "计划复盘与科研协调", "设备连接与模式核验"];
  var categories=['实验资源','安全与测试','科研整理','样品质量','项目管理','写作','电化学','实验制备','实验表征'];
  var statuses=['计划中','进行中','待条件','待确认','已完成','已取消'];
  var esc=function(v){return String(v==null?'':v).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});};
  function day(value){if(typeof value!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(value))return null;var n=Date.parse(value+'T00:00:00Z');return Number.isFinite(n)&&new Date(n).toISOString().slice(0,10)===value?value:null;}
  function addDays(value,n){var d=new Date(value+'T00:00:00Z');d.setUTCDate(d.getUTCDate()+n);return d.toISOString().slice(0,10);}
  function beijingDay(){var p=new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Shanghai',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date()),r={};p.forEach(function(x){r[x.type]=x.value;});return r.year+'-'+r.month+'-'+r.day;}
  function exact(obj,keys){return obj&&typeof obj==='object'&&!Array.isArray(obj)&&Object.keys(obj).length===keys.length&&keys.every(function(k){return Object.prototype.hasOwnProperty.call(obj,k);});}
  function validate(d){
    if(!exact(d,['schemaVersion','sourceLabel','sourceUpdatedAt','syncedAt','revision','tasks'])||d.schemaVersion!==1||d.sourceLabel!=='Google 科研展示表'||!Array.isArray(d.tasks)||d.tasks.length>999||!/^\d{4}-\d\d-\d\dT.*Z$/.test(d.syncedAt)||!Number.isFinite(Date.parse(d.syncedAt))||!Number.isFinite(Date.parse(d.sourceUpdatedAt))||!/^[a-f0-9]{16}$/.test(d.revision))throw new Error('展示摘要结构异常');
    var ids={};
    d.tasks.forEach(function(t){
      if(!exact(t,['id','date','title','status','hours','category'])||typeof t.id!=='string'||!/^T\d{3,5}$/.test(t.id)||ids[t.id]||t.date!==null&&!day(t.date)||titles.indexOf(t.title)<0||categories.indexOf(t.category)<0||statuses.indexOf(t.status)<0||t.hours!==null&&(typeof t.hours!=='number'||!Number.isFinite(t.hours)||t.hours<0||t.hours>240))throw new Error('出现未审核的展示字段或任务值');
      ids[t.id]=true;
    });
    return d;
  }
  function active(t){return t.status!=='已完成'&&t.status!=='已取消';}
  function risks(t,today){
    if(!active(t))return[];var r=[];
    if(!t.date)r.push('日期待确认');
    if(t.status==='待条件')r.push('前置条件待核对');
    if(t.status==='待确认')r.push('任务状态待确认');
    if(t.date&&t.date<today)r.push('已过建议日期，需复核排期');
    if(t.hours===null)r.push('预计工时待补充');
    if(t.hours>8)r.push('单项预计超过8小时，建议核对或拆分');
    return r;
  }
  function hours(tasks){var known=0,missing=0;tasks.forEach(function(t){if(t.hours===null)missing++;else known+=t.hours;});return{known:Math.round(known*10)/10,missing:missing,text:(missing?'已知 ':'')+(Math.round(known*10)/10)+' h'+(missing?' · '+missing+'项待估':'')};}
  function model(tasks,today){
    var end=addDays(today,7),pending=tasks.filter(active),groups={
      today:pending.filter(function(t){return t.date===today;}),
      week:pending.filter(function(t){return t.date>today&&t.date<=end;}),
      risk:pending.filter(function(t){return risks(t,today).length;}),
      all:tasks.slice(),done:tasks.filter(function(t){return t.status==='已完成';})
    };
    groups.days=Array.from({length:7},function(_,i){var date=addDays(today,i+1),list=groups.week.filter(function(t){return t.date===date;});return{date:date,tasks:list,hours:hours(list)};});
    return groups;
  }
  var detailTaskKeys=['id','title','steps','acceptance','progress','prerequisite','gate'];
  var recordKeys=['id','date','taskIds','work','issues','conditions','observations','next','replan','status','updatedAt','start','end','activeHours','waitingHours','travelHours','breakMinutes'];
  function safeText(v,required){return typeof v==='string'&&v.length<=2400&&(!required||v.trim().length>0)&&!/[A-Za-z]:[\\/]|file:|https?:\/\/|api[_ -]?key|access[_ -]?token|refresh[_ -]?token|client[_ -]?secret|password|passwd|private[_ -]?key|authorization|bearer\s|密码|验证码|(?:^|\D)1[3-9]\d{9}(?!\d)|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}/i.test(v);}
  function validStamp(v){return typeof v==='string'&&Number.isFinite(Date.parse(v));}
  function validateDetails(b,summary){
    validate(summary);
    if(!exact(b,['schemaVersion','summaryRevision','sourceReleaseId','sourceSyncedAt','contentDigest','tasks','records'])||b.schemaVersion!==1||b.summaryRevision!==summary.revision||!/^[a-f0-9]{20}$/.test(b.sourceReleaseId)||!/^[a-f0-9]{64}$/.test(b.contentDigest)||!validStamp(b.sourceSyncedAt)||!Array.isArray(b.tasks)||!Array.isArray(b.records)||b.records.length>2000)throw Error('执行正文与任务摘要版本不一致');
    var ids=Object.create(null),expected=Object.create(null);summary.tasks.forEach(function(t){expected[t.id]=true;});
    b.tasks.forEach(function(t){if(!exact(t,detailTaskKeys)||!expected[t.id]||ids[t.id]||detailTaskKeys.slice(1).some(function(k){return!safeText(t[k],['title','steps','acceptance'].indexOf(k)>=0);}))throw Error('执行正文含未审核字段');ids[t.id]=true;});
    if(Object.keys(ids).length!==summary.tasks.length)throw Error('执行正文任务编号不完整');
    var records=Object.create(null);
    b.records.forEach(function(r){
      if(!exact(r,recordKeys)||!/^LOG-\d{8}-\d{3}$/.test(r.id)||records[r.id]||!day(r.date)||!Array.isArray(r.taskIds)||new Set(r.taskIds).size!==r.taskIds.length||r.taskIds.some(function(id){return!ids[id];})||['待核对','已核对','需补充','已更正'].indexOf(r.status)<0)throw Error('实验记录编号、关联或状态异常');
      records[r.id]=true;
      if(['work','issues','conditions','observations','next','replan'].some(function(k){return!safeText(r[k],k==='work');})||['updatedAt','start','end'].some(function(k){return r[k]!==null&&!validStamp(r[k]);})||r.start&&r.end&&r.end<r.start)throw Error('实验记录文字或时间异常');
      ['activeHours','waitingHours','travelHours','breakMinutes'].forEach(function(k){var n=r[k],max=k==='waitingHours'?744:k==='breakMinutes'?1440:24;if(n!==null&&(typeof n!=='number'||!Number.isFinite(n)||n<0||n>max))throw Error('实验记录工时异常');});
    });return b;
  }
  function copy(value){return value==null?value:JSON.parse(JSON.stringify(value));}
  function digestText(b){return JSON.stringify([b.tasks.map(function(t){var r={};detailTaskKeys.forEach(function(k){r[k]=t[k];});return r;}),b.records.map(function(t){var r={};recordKeys.forEach(function(k){r[k]=t[k];});return r;})]);}
  /* This is a view-only integration boundary. The caller must authenticate its
     service before calling it; this module never fetches or stores cloud data. */
  function validateCloud(b,base){
    validate(base);
    if(!exact(b,['schemaVersion','baseRevision','revision','updatedAt','patches'])||b.schemaVersion!==1||b.baseRevision!==base.revision||typeof b.revision!=='string'||!/^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$/.test(b.revision)||typeof b.updatedAt!=='string'||!/^\d{4}-\d\d-\d\dT(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d(?:\.\d{1,3})?Z$/.test(b.updatedAt)||!day(b.updatedAt.slice(0,10))||!Array.isArray(b.patches)||b.patches.length>base.tasks.length)throw Error('云端安排版本或结构异常');
    var known=Object.create(null),seen=Object.create(null),allowed=['id','status','suggestedDate','plannedHours','progress'];base.tasks.forEach(function(t){known[t.id]=true;});
    b.patches.forEach(function(p){
      if(!p||typeof p!=='object'||Array.isArray(p)||Object.keys(p).length<2||Object.keys(p).some(function(k){return allowed.indexOf(k)<0;})||!Object.prototype.hasOwnProperty.call(p,'id')||typeof p.id!=='string'||!known[p.id]||seen[p.id])throw Error('云端安排含未知字段、编号或重复任务');seen[p.id]=true;
      if(Object.prototype.hasOwnProperty.call(p,'status')&&statuses.indexOf(p.status)<0||Object.prototype.hasOwnProperty.call(p,'suggestedDate')&&p.suggestedDate!==null&&!day(p.suggestedDate)||Object.prototype.hasOwnProperty.call(p,'plannedHours')&&p.plannedHours!==null&&(typeof p.plannedHours!=='number'||!Number.isFinite(p.plannedHours)||p.plannedHours<0||p.plannedHours>240)||Object.prototype.hasOwnProperty.call(p,'progress')&&(!safeText(p.progress,false)||/[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/.test(p.progress)))throw Error('云端安排的状态、日期、预计工时或进展异常');
    });return b;
  }
  function mount(w,doc,opts){
    opts=opts||{};var $=function(id){return doc.getElementById(id);},data=null,baseData=null,details=null,detailMap=Object.create(null),cloud=null,cloudMap=Object.create(null),currentDay=opts.today||beijingDay(),groups=null,scope='today',limit=12,selectedDay='',query='',category='all',state='all',request=0,controller=null,lastCheck=0,recordTask='all',recordQuery='',recordLimit=12,focusId='';
    var fetcher=opts.fetcher||(typeof fetch==='function'?fetch:null),refreshButton=$('research-refresh');
    function stamp(value){return new Date(value).toLocaleString('zh-CN',{timeZone:'Asia/Shanghai',hour12:false});}
    function notify(action){if(w.dispatchEvent&&typeof w.CustomEvent==='function')w.dispatchEvent(new w.CustomEvent('research-updated',{detail:{revision:baseData.revision,cloudRevision:cloud?cloud.revision:null,action:action||'base'}}));}
    function title(t){return detailMap[t.id]?detailMap[t.id].title:t.title;}
    function riskBox(){var undated=groups.risk.filter(function(t){return!t.date;}).length,overdue=groups.risk.filter(function(t){return t.date&&t.date<currentDay;}).length;$('research-risk-note').textContent=groups.risk.length?groups.risk.length+' 项条件或排期待核对'+(undated?'，含 '+undated+' 项日期未定':'')+(overdue?'、'+overdue+' 项已过建议日期':'')+'；网站不会自行改期或批准实验。':'当前摘要暂无已标记风险，执行条件仍须核对。';}
    function renderSummary(){
      var complete=groups.done.length,pct=data.tasks.length?Math.round(100*complete/data.tasks.length):0;
      $('research-date').textContent=currentDay+' · 北京时间';
      $('research-focus').textContent=groups.today.length?'今天 '+groups.today.length+' 项待办，预计主动工时 '+hours(groups.today).text+'。步骤与完成标准直接在下面读。':'今天没有已排定待办；可以查看未来7天、全部任务或待协调事项。';
      $('research-stats').innerHTML=[['today','今日待办',groups.today.length,hours(groups.today).text],['week','未来7天',groups.week.length,hours(groups.week).text],['risk','待协调',groups.risk.length,'条件 / 日期 / 工时'],['all','全部任务',data.tasks.length,'含已完成与已取消']].map(function(x){return '<button type="button" class="research-stat" data-rscope="'+x[0]+'"><span>'+x[1]+'</span><strong>'+x[2]+'</strong><small>'+esc(x[3])+'</small></button>';}).join('');
      $('research-progress').textContent='已标记完成 '+complete+' / '+data.tasks.length+' 项（'+pct+'%）；执行完成不等于实验验收通过。';$('research-progress-fill').style.width=pct+'%';
      $('research-completed-panel').hidden=complete===0;
      $('research-completed-list').innerHTML=groups.done.slice(0,3).map(function(t){return '<button type="button" data-ropen="'+t.id+'"><span>✓ 已完成</span> '+esc(t.id)+' · '+esc(title(t))+'</button>';}).join('');
      $('research-meta').textContent='摘要源更新时间 '+stamp(baseData.sourceUpdatedAt)+' · 网站同步 '+stamp(baseData.syncedAt)+' · 摘要版本 '+baseData.revision.slice(0,8)+(details?' · 正文与记录源时间 '+stamp(details.sourceSyncedAt)+' · 同版 '+details.sourceReleaseId:' · 正文暂未载入')+(cloud?' · 云端安排 '+stamp(cloud.updatedAt)+'；仅叠加任务状态、建议日期、预计工时与用户进展，原始摘要及实验记录未改。':'');
      $('research-details-note').textContent=details?'完整执行内容与 '+details.records.length+' 条只读记录已载入；来源核对时间 '+stamp(details.sourceSyncedAt)+(Date.now()-Date.parse(details.sourceSyncedAt)>48*3600000?'。源快照已超过48小时，执行前核对近期反馈，未知进展不自动补写。':'。'):'完整正文暂未载入，当前仅显示已核对摘要；请检查更新。';
      var max=Math.max.apply(null,[8].concat(groups.days.map(function(d){return d.hours.known;})));
      $('research-week-chart').innerHTML=groups.days.map(function(d){return '<button type="button" class="research-day'+(d.hours.known>8?' overload':'')+'" data-rday="'+d.date+'" aria-label="'+d.date+'，'+d.tasks.length+'项，'+esc(d.hours.text)+'"><span>'+d.date.slice(5).replace('-','/')+'</span><span class="research-day-track"><i style="height:'+Math.max(d.hours.known?5:0,100*d.hours.known/max)+'%"></i></span><b>'+d.hours.known+' h</b><small>'+d.tasks.length+'项'+(d.hours.missing?' · 待估':'')+'</small></button>';}).join('');riskBox();
    }
    function filtered(){var words=query.trim().toLowerCase().split(/\s+/).filter(Boolean);return(groups[scope]||[]).filter(function(t){var d=detailMap[t.id]||{},c=cloudMap[t.id]||{},text=[t.id,t.title,t.category,t.status,d.title,d.steps,d.acceptance,d.progress,d.prerequisite,d.gate,c.progress].join(' ').toLowerCase();return(!focusId||t.id===focusId)&&(!selectedDay||t.date===selectedDay)&&(category==='all'||t.category===category)&&(state==='all'||t.status===state)&&words.every(function(word){return text.includes(word);});}).slice().sort(function(a,b){return(a.date||'9999').localeCompare(b.date||'9999')||a.id.localeCompare(b.id);});}
    function render(){
      if(!data)return;var list=filtered(),labels={today:'今日任务',week:'未来7天',risk:'待协调与风险',all:'全部任务',done:'已标记完成'};
      doc.querySelectorAll('#view-research [data-rscope]').forEach(function(el){var on=el.dataset.rscope===scope;el.classList.toggle('selected',on);el.setAttribute('aria-pressed',String(on));});
      $('research-list-heading').textContent=selectedDay?selectedDay+' 的安排':labels[scope];$('research-result-count').textContent=list.length+' 项 · '+hours(list).text+(scope==='week'?' · 不含今天':'')+(list.length>limit?' · 已显示 '+limit+' 项':'');
      $('research-list').innerHTML=list.slice(0,limit).map(function(t){var d=detailMap[t.id],c=cloudMap[t.id],warnings=risks(t,currentDay),recordCount=details?details.records.filter(function(r){return r.taskIds.includes(t.id);}).length:0;
        var body=d?'<dl class="research-task-details"><dt>怎么推进</dt><dd>'+esc(d.steps)+'</dd><dt>做到什么算完成</dt><dd>'+esc(d.acceptance)+'</dd>'+(d.progress?'<dt>已发布进展</dt><dd>'+esc(d.progress)+'</dd>':'')+(d.prerequisite&&d.prerequisite!=='无'?'<dt>前置条件</dt><dd>'+esc(d.prerequisite)+'</dd>':'')+(d.gate.startsWith('HOLD')?'<dt>安全与条件限制</dt><dd>'+esc(d.gate)+'</dd>':'')+'</dl>':'<p class="research-chart-note">执行正文暂未载入，当前为摘要。</p>';
        if(c)body+='<p class="research-chart-note">云端安排覆盖本项部分状态、排期或预计工时；不代表实验条件放行或结果验收。</p>'+(c.progress?'<dl class="research-task-details"><dt>云端用户进展 · 未作实验结果核验</dt><dd>'+esc(c.progress)+'</dd></dl>':'');
        return '<article id="research-task-'+t.id+'" tabindex="-1" class="research-task'+(warnings.length?' has-risk':'')+'"><div class="research-task-top"><span>'+esc(t.category)+'</span><small>'+esc(t.id)+'</small></div><h3>'+esc(title(t))+'</h3><div class="research-task-tags"><span class="research-state '+(t.status==='已完成'?'done':t.status==='待条件'?'hold':'')+'">'+esc(t.status)+'</span><span>建议日期 '+esc(t.date||'待确认')+'</span><span>预计 '+(t.hours===null?'待估':t.hours+' h')+'</span></div>'+(warnings.length?'<p class="research-task-risk">'+esc(warnings.join('；'))+'</p>':'')+body+'<div class="research-task-bottom">'+(recordCount?'<button type="button" data-rrecords="'+t.id+'">本项记录 · '+recordCount+'</button>':'')+'<button type="button" data-rfeedback="'+t.id+'">反馈这项</button></div></article>';
      }).join('')||'<div class="research-empty"><strong>没有匹配的任务</strong><p>可以清除筛选，或查看未来7天、全部任务和已完成。</p></div>';$('research-more').hidden=list.length<=limit;
    }
    function renderRecords(){
      var records=details?details.records:[],words=recordQuery.trim().toLowerCase().split(/\s+/).filter(Boolean),list=records.filter(function(r){return(recordTask==='all'||r.taskIds.includes(recordTask))&&words.every(function(q){return[r.id,r.work,r.issues,r.conditions,r.observations,r.next,r.replan].join(' ').toLowerCase().includes(q);});}).slice().sort(function(a,b){return b.date.localeCompare(a.date)||b.id.localeCompare(a.id);});
      $('research-record-count').textContent=list.length+' 条已发布记录'+(recordTask!=='all'?' · '+recordTask:'');
      function duration(v,unit){return v===null?'待补充':v+' '+unit;}
      $('research-record-list').innerHTML=list.slice(0,recordLimit).map(function(r){var fields=[['条件与操作补充',r.conditions],['观察结果',r.observations],['异常与边界',r.issues],['当时记录的下一步',r.next],['当时的排期说明',r.replan]].filter(function(x){return x[1];});return '<article class="research-record"><div class="research-task-top"><time>'+esc(r.date)+'</time><small>'+esc(r.id)+' · '+esc(r.status)+'</small></div><h4>'+esc(r.work)+'</h4><div class="research-task-tags">'+r.taskIds.map(function(id){return '<button type="button" data-ropen="'+id+'">'+id+' · 查看任务</button>';}).join('')+'</div><p class="research-record-times">开始 '+esc(r.start?r.start.replace('T',' '):'未记录')+' · 结束 '+esc(r.end?r.end.replace('T',' '):'未记录')+'<br>主动 '+duration(r.activeHours,'h')+' · 等待 '+duration(r.waitingHours,'h')+' · 交通 '+duration(r.travelHours,'h')+' · 休息 '+duration(r.breakMinutes,'分钟')+'</p><dl class="research-task-details">'+fields.map(function(f){return '<dt>'+f[0]+'</dt><dd>'+esc(f[1])+'</dd>';}).join('')+'</dl></article>';}).join('')||'<div class="research-empty">'+(details?'暂无匹配的已发布记录。任务安排不会自动生成实际记录。':'记录正文暂未载入。')+'</div>';$('research-record-more').hidden=list.length<=recordLimit;
    }
    function setScope(next){focusId='';scope=['today','week','risk','all','done'].includes(next)?next:'today';limit=12;selectedDay='';render();}
    function focusTask(id){if(!data||!data.tasks.some(function(t){return t.id===id;}))return false;focusId=id;scope='all';query=id;category='all';state='all';selectedDay='';limit=12;$('research-search').value=id;$('research-category').value='all';$('research-state').value='all';render();var target=$('research-task-'+id)||$('research-list-heading');if(target&&target.scrollIntoView)target.scrollIntoView({block:'start',behavior:'auto'});if(target&&target.focus)target.focus({preventScroll:true});return true;}
    function showRecords(id){recordTask=id;recordQuery='';recordLimit=12;$('research-record-task').value=id;$('research-record-query').value='';renderRecords();var el=$('research-record-heading');if(el&&el.scrollIntoView)el.scrollIntoView({block:'start',behavior:'auto'});if(el&&el.focus)el.focus({preventScroll:true});}
    function derive(){
      data=copy(baseData);cloudMap=Object.create(null);if(cloud)cloud.patches.forEach(function(p){cloudMap[p.id]=p;});
      data.tasks.forEach(function(t){var p=cloudMap[t.id];if(!p)return;if(Object.prototype.hasOwnProperty.call(p,'status'))t.status=p.status;if(Object.prototype.hasOwnProperty.call(p,'suggestedDate'))t.date=p.suggestedDate;if(Object.prototype.hasOwnProperty.call(p,'plannedHours'))t.hours=p.plannedHours;});
      currentDay=opts.today||beijingDay();groups=model(data.tasks,currentDay);
    }
    function paint(action){
      var previousFocus=doc.activeElement,panel=$('view-research'),previousFocusId=previousFocus&&previousFocus.id;
      var preserveFocus=previousFocusId&&panel&&panel.contains&&panel.contains(previousFocus)&&panel.style.display!=='none';
      var cs=categories.filter(function(c){return data.tasks.some(function(t){return t.category===c;});});if(category!=='all'&&!cs.includes(category))category='all';$('research-category').innerHTML='<option value="all">全部分类</option>'+cs.map(function(c){return '<option value="'+esc(c)+'">'+esc(c)+'</option>';}).join('');$('research-category').value=category;
      var linked=details?data.tasks.filter(function(t){return details.records.some(function(r){return r.taskIds.includes(t.id);});}):[];
      $('research-record-task').innerHTML='<option value="all">全部关联任务</option>'+linked.map(function(t){return '<option value="'+t.id+'">'+t.id+' · '+esc(title(t))+'</option>';}).join('');if(recordTask!=='all'&&!linked.some(function(t){return t.id===recordTask;}))recordTask='all';$('research-record-task').value=recordTask;renderSummary();render();renderRecords();
      if(preserveFocus&&previousFocus.isConnected===false){var nextFocus=$(previousFocusId);if(nextFocus&&panel.contains(nextFocus)&&nextFocus.focus)nextFocus.focus({preventScroll:true});}
      notify(action);
    }
    function apply(next,bundle){
      var candidate=copy(validate(next)),native=bundle?copy(validateDetails(bundle,candidate)):details&&details.summaryRevision===candidate.revision?details:null;
      if(baseData&&JSON.stringify(baseData)!==JSON.stringify(candidate))cloud=null;
      baseData=candidate;details=native;detailMap=Object.create(null);if(details)details.tasks.forEach(function(t){detailMap[t.id]=t;});derive();paint('base');
    }
    function applyCloud(bundle){
      if(!baseData)throw Error('任务基线尚未载入');var candidate=copy(validateCloud(bundle,baseData));
      if(cloud&&(Date.parse(candidate.updatedAt)<Date.parse(cloud.updatedAt)||Date.parse(candidate.updatedAt)===Date.parse(cloud.updatedAt)&&JSON.stringify(candidate)!==JSON.stringify(cloud)))throw Error('拒绝较旧或同时间冲突的云端安排');
      cloud=candidate;derive();paint('cloud');return true;
    }
    function clearCloud(){
      if(!cloud)return false;cloud=null;derive();paint('cloud-clear');return true;
    }
    async function verifyNative(bundle,summary){
      validateDetails(bundle,summary);if(!w.crypto||!w.crypto.subtle||typeof TextEncoder==='undefined')throw Error('无法校验正文发布版本');
      var bytes=await w.crypto.subtle.digest('SHA-256',new TextEncoder().encode(digestText(bundle))),hex=Array.from(new Uint8Array(bytes)).map(function(b){return b.toString(16).padStart(2,'0');}).join('');if(hex!==bundle.contentDigest)throw Error('正文校验值不一致');return bundle;
    }
    async function refresh(){
      if((w.location||{}).protocol==='file:'){$('research-sync-status').textContent='当前为本地打包的任务、正文与记录；在线检查请打开主站。';return;}if(!fetcher)return;
      var mine=++request;if(controller)controller.abort();controller=typeof AbortController!=='undefined'?new AbortController():null;var ctrl=controller,timeout=setTimeout(function(){if(ctrl)ctrl.abort();},15000);refreshButton.disabled=true;$('research-sync-status').textContent='正在检查任务与正文的同版发布…';
      try{
        var options={cache:'no-store',credentials:'same-origin',signal:ctrl?ctrl.signal:undefined},suffix='?t='+Date.now(),responses=await Promise.all([fetcher('research-data.json'+suffix,options),fetcher('research-details.json'+suffix,options)]);if(mine!==request)return;if(responses.some(function(r){return!r.ok;}))throw Error('数据读取失败');
        var payload=await Promise.all(responses.map(function(r){return r.json();}));if(mine!==request)return;var next=validate(payload[0]);if(data&&Date.parse(next.syncedAt)<Date.parse(data.syncedAt)){$('research-sync-status').textContent='服务器返回了较旧的摘要，已保留较新版本。';return;}
        var bundle=await verifyNative(payload[1],next);if(mine!==request)return;if(details&&Date.parse(bundle.sourceSyncedAt)<Date.parse(details.sourceSyncedAt)){$('research-sync-status').textContent='服务器返回了较旧的正文，已保留较新版本。';return;}apply(next,bundle);lastCheck=Date.now();var saved=responses.some(function(r){return r.headers&&r.headers.get&&r.headers.get('X-Workspace-Snapshot')==='saved';});$('research-sync-status').textContent=w.navigator&&w.navigator.onLine===false?'当前离线：已读取保存的有效版本，暂不能核实最新发布。':saved?'当前显示已保存的有效版本，暂不能核实最新发布；来源时间见说明。':'已读取同域有效的任务、执行正文与只读记录；来源时间见说明，可能来自保存的副本。';
      }catch(e){if(mine!==request)return;$('research-sync-status').textContent=data?'更新检查失败，保留上次有效任务和正文；当前不代表已同步。':'任务暂时无法读取。读取失败不代表没有任务。';}
      finally{clearTimeout(timeout);if(mine===request)refreshButton.disabled=false;}
    }
    $('view-research').addEventListener('click',function(e){var b=e.target.closest?e.target.closest('button[data-rscope],button[data-rday],button[data-rfeedback],button[data-ropen],button[data-rrecords]'):null;if(!b)return;
      if(b.dataset.rscope){setScope(b.dataset.rscope);return;}if(b.dataset.ropen){focusTask(b.dataset.ropen);return;}if(b.dataset.rrecords){showRecords(b.dataset.rrecords);return;}
      if(b.dataset.rday){focusId='';scope='week';selectedDay=b.dataset.rday;limit=12;render();if($('research-list-heading').scrollIntoView)$('research-list-heading').scrollIntoView({block:'start',behavior:'auto'});return;}
      var t=data&&data.tasks.find(function(t){return t.id===b.dataset.rfeedback;});if(!t)return;$('research-feedback-text').value='任务ID：'+t.id+'\n任务：'+title(t)+'\n进展 / 新情况：\n实际日期 / 希望调整到：\n实际主动工时（可选）：\n需要协调的事：';if($('research-feedback-box').scrollIntoView)$('research-feedback-box').scrollIntoView({block:'start',behavior:'auto'});$('research-feedback-text').focus();
    });
    refreshButton.addEventListener('click',refresh);
    $('research-search').addEventListener('input',function(){focusId='';query=this.value;limit=12;render();});$('research-category').addEventListener('change',function(){focusId='';category=this.value;limit=12;render();});$('research-state').addEventListener('change',function(){focusId='';state=this.value;limit=12;render();});
    $('research-reset').addEventListener('click',function(){focusId='';query='';category='all';state='all';selectedDay='';limit=12;$('research-search').value='';$('research-category').value='all';$('research-state').value='all';render();});$('research-more').addEventListener('click',function(){var before=limit;limit+=12;render();var cards=doc.querySelectorAll('#research-list article');if(cards[before]&&cards[before].focus)cards[before].focus();});
    $('research-record-task').addEventListener('change',function(){recordTask=this.value;recordLimit=12;renderRecords();});$('research-record-query').addEventListener('input',function(){recordQuery=this.value;recordLimit=12;renderRecords();});$('research-record-reset').addEventListener('click',function(){recordTask='all';recordQuery='';recordLimit=12;$('research-record-task').value='all';$('research-record-query').value='';renderRecords();});$('research-record-more').addEventListener('click',function(){recordLimit+=12;renderRecords();});
    $('research-copy').addEventListener('click',function(){if(w.AI_COPY)w.AI_COPY($('research-feedback-text').value,this);});
    try{apply(w.RESEARCH_SNAPSHOT,w.RESEARCH_DETAILS);$('research-sync-status').textContent=details?'当前展示随网页发布的完整执行内容与记录；打开栏目时检查同域更新。':'当前仅展示已核对摘要，正文暂未载入。';}catch(e){try{apply(w.RESEARCH_SNAPSHOT,null);$('research-sync-status').textContent='正文版本校验失败，暂保留有效摘要；请检查更新。';}catch(ignore){$('research-sync-status').textContent='任务摘要校验失败，未加载任务。';}}
    if((w.location||{}).hash==='#research')refresh();if(w.addEventListener)w.addEventListener('focus',function(){if($('view-research').style.display!=='none'&&Date.now()-lastCheck>30000)refresh();});
    setInterval(function(){if($('view-research').style.display==='none'||!data)return;var today=opts.today||beijingDay();if(today!==currentDay){derive();paint('day');refresh();}else if(Date.now()-lastCheck>300000)refresh();},60000);
    return{refresh:refresh,apply:apply,applyCloud:applyCloud,clearCloud:clearCloud,setScope:setScope,focusTask:focusTask,getDetail:function(id){var d=copy(detailMap[id]||null);if(d&&cloudMap[id]&&Object.prototype.hasOwnProperty.call(cloudMap[id],'progress'))d.cloudProgress=cloudMap[id].progress;return d;},getModel:function(){return copy(groups);},getBaseModel:function(){return baseData?copy(model(baseData.tasks,currentDay)):null;},state:function(){return{data:copy(data),baseData:copy(baseData),details:copy(details),cloud:copy(cloud),scope:scope,day:currentDay};}};
  }

  return{validate:validate,validateDetails:validateDetails,validateCloud:validateCloud,model:model,risks:risks,hours:hours,day:day,addDays:addDays,beijingDay:beijingDay,esc:esc,mount:mount};
});
