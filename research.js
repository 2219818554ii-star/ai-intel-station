/* 科研展示摘要：只接收六个已审核字段，不读取完整科研总表。 */
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
  function mount(w,doc,opts){

    opts=opts||{};var $=function(id){return doc.getElementById(id);},data=null,currentDay=opts.today||beijingDay(),groups=null,scope='today',limit=12,selectedDay='',query='',category='all',state='all',request=0,controller=null,lastCheck=0;
    var fetcher=opts.fetcher||(typeof fetch==='function'?fetch:null),refreshButton=$('research-refresh');
    function stamp(value){return new Date(value).toLocaleString('zh-CN',{timeZone:'Asia/Shanghai',hour12:false});}
    function riskBox(){
      var undated=groups.risk.filter(function(t){return !t.date;}).length,held=groups.risk.filter(function(t){return t.status==='待条件';}).length,overdue=groups.risk.filter(function(t){return t.date&&t.date<currentDay;}).length;
      $('research-risk-note').textContent=groups.risk.length?groups.risk.length+' 项条件或排期待核对'+(undated?'，含 '+undated+' 项日期未定':'')+(overdue?'、'+overdue+' 项逾期':'')+'。':'展示摘要中暂无已标记风险，执行条件仍须核对。';
    }
    function renderSummary(){
      var complete=groups.done.length,pct=data.tasks.length?Math.round(100*complete/data.tasks.length):0;
      $('research-date').textContent=currentDay+' · 北京时间';
      $('research-focus').textContent=groups.today.length?'今天 '+groups.today.length+' 项待办，预计主动工时 '+hours(groups.today).text+'；已完成事项 '+complete+' 项。':'今天没有已排定的待办；已完成事项 '+complete+' 项，可以查看已完成和未来7天。';
      $('research-stats').innerHTML=[['today','今日待办',groups.today.length,hours(groups.today).text],['week','未来7天',groups.week.length,hours(groups.week).text],['risk','风险待核对',groups.risk.length,'条件 / 日期 / 工时'],['done','已标记完成',complete,'共 '+data.tasks.length+' 项']].map(function(x){return '<button type="button" class="research-stat" data-rscope="'+x[0]+'"><span>'+x[1]+'</span><strong>'+x[2]+'</strong><small>'+esc(x[3])+'</small></button>';}).join('');
      $('research-progress').textContent='已标记完成 '+complete+' / '+data.tasks.length+' 项（'+pct+'%）；此处不表示实验已验收。';
      $('research-progress-fill').style.width=pct+'%';
      $('research-completed-panel').hidden=complete===0;
      $('research-completed-list').innerHTML=groups.done.slice(0,3).map(function(t){return '<a href="https://luohao-research-desk.easyroot8192.chatgpt.site/?task='+encodeURIComponent(t.id)+'" target="_top" rel="noopener"><span>✓ 已完成</span> '+esc(t.id)+' · '+esc(t.title)+'</a>';}).join('');
      $('research-meta').textContent='来源：Google 科研展示表 · 表格更新时间 '+stamp(data.sourceUpdatedAt)+' · 网站同步时间 '+stamp(data.syncedAt)+' · 版本 '+data.revision.slice(0,8);
      var max=Math.max.apply(null,[8].concat(groups.days.map(function(d){return d.hours.known;})));
      $('research-week-chart').innerHTML=groups.days.map(function(d){return '<button type="button" class="research-day'+(d.hours.known>8?' overload':'')+'" data-rday="'+d.date+'" aria-label="'+d.date+'，'+d.tasks.length+'项，'+esc(d.hours.text)+'"><span>'+d.date.slice(5).replace('-','/')+'</span><span class="research-day-track"><i style="height:'+Math.max(d.hours.known?5:0,100*d.hours.known/max)+'%"></i></span><b>'+d.hours.known+' h</b><small>'+d.tasks.length+'项'+(d.hours.missing?' · 待估':'')+'</small></button>';}).join('');
      riskBox();
    }
    function filtered(){
      var q=query.trim().toLowerCase();
      return(groups[scope]||[]).filter(function(t){return (!selectedDay||t.date===selectedDay)&&(category==='all'||t.category===category)&&(state==='all'||t.status===state)&&(!q||[t.id,t.title,t.category,t.status].join(' ').toLowerCase().includes(q));}).slice().sort(function(a,b){return(a.date||'9999').localeCompare(b.date||'9999')||a.id.localeCompare(b.id);});
    }
    function render(){
      if(!data)return;
      var list=filtered(),labels={today:'今日任务',week:'未来7天',risk:'风险待核对',all:'全部任务',done:'已标记完成'};
      doc.querySelectorAll('#view-research [data-rscope]').forEach(function(el){var on=el.dataset.rscope===scope;el.classList.toggle('selected',on);el.setAttribute('aria-pressed',on?'true':'false');});
      $('research-list-heading').textContent=selectedDay?selectedDay+' 的安排':labels[scope];
      $('research-result-count').textContent=list.length+' 项 · '+hours(list).text+(scope==='week'?' · 不含今天':'')+(list.length>limit?' · 已显示 '+limit+' 项':'');
      $('research-list').innerHTML=list.slice(0,limit).map(function(t){var warnings=risks(t,currentDay);return '<article class="research-task'+(warnings.length?' has-risk':'')+'"><div class="research-task-top"><span>'+esc(t.category)+'</span><small>'+esc(t.id)+'</small></div><h3>'+esc(t.title)+'</h3><div class="research-task-tags"><span class="research-state '+(t.status==='已完成'?'done':t.status==='待条件'?'hold':'')+'">'+esc(t.status)+'</span><span>'+esc(t.date||'日期待确认')+'</span><span>预计 '+(t.hours===null?'待估':t.hours+' h')+'</span></div>'+(warnings.length?'<p class="research-task-risk">'+esc(warnings.join('；'))+'</p>':'')+'<div class="research-task-bottom"><small>具体工作见完整科研清单</small><button type="button" data-rfeedback="'+t.id+'">反馈这项</button></div></article>';}).join('')||'<div class="research-empty"><strong>没有匹配的任务</strong><p>可以清除筛选，或查看未来7天和风险待核对。</p></div>';
      $('research-more').hidden=list.length<=limit;
    }
    function setScope(next){scope=['today','week','risk','all','done'].indexOf(next)>=0?next:'today';limit=12;selectedDay='';render();}
    function apply(next){
      data=validate(next);currentDay=opts.today||beijingDay();groups=model(data.tasks,currentDay);
      var cs=categories.filter(function(c){return data.tasks.some(function(t){return t.category===c;});});if(category!=='all'&&cs.indexOf(category)<0)category='all';
      $('research-category').innerHTML='<option value="all">全部分类</option>'+cs.map(function(c){return '<option value="'+esc(c)+'">'+esc(c)+'</option>';}).join('');$('research-category').value=category;
      renderSummary();render();
    }
    async function refresh(){
      var loc=w.location||{};
      if(loc.protocol==='file:'){$('research-sync-status').textContent='当前为本地网页摘要。请打开在线网站读取最新发布数据；本地路径不能供其他设备访问。';return;}
      if(!fetcher)return;
      var mine=++request;if(controller)controller.abort();controller=typeof AbortController!=='undefined'?new AbortController():null;
      var localController=controller,timeout=setTimeout(function(){if(localController)localController.abort();},15000);
      refreshButton.disabled=true;$('research-sync-status').textContent='正在检查最新发布数据…';
      try{
        var response=await fetcher('research-data.json?t='+Date.now(),{cache:'no-store',credentials:'same-origin',signal:controller?controller.signal:undefined});
        if(!response.ok)throw new Error('数据读取失败');var next=validate(await response.json());if(mine!==request)return;
        if(data&&Date.parse(next.syncedAt)<Date.parse(data.syncedAt)){$('research-sync-status').textContent='服务器返回了较旧的摘要，已保留较新版本。请稍后重试。';return;}
        apply(next);lastCheck=Date.now();$('research-sync-status').textContent='已读取最新发布摘要。表格修改后由我同步发布。';
      }catch(e){if(mine!==request)return;$('research-sync-status').textContent=data?'更新检查失败，保留上次有效摘要。请稍后重试；当前不代表已同步。':'任务暂时无法读取，请稍后重试。读取失败不代表没有任务。';}
      finally{clearTimeout(timeout);if(mine===request)refreshButton.disabled=false;}
    }
    $('view-research').addEventListener('click',function(e){
      var b=e.target.closest?e.target.closest('button[data-rscope],button[data-rday],button[data-rfeedback]'):null;if(!b)return;
      if(b.dataset.rscope){setScope(b.dataset.rscope);return;}
      if(b.dataset.rday){scope='week';selectedDay=b.dataset.rday;limit=12;render();$('research-list-heading').scrollIntoView({block:'start',behavior:'auto'});return;}
      var t=data&&data.tasks.find(function(t){return t.id===b.dataset.rfeedback;});if(!t)return;
      $('research-feedback-text').value='任务ID：'+t.id+'\n任务：'+t.title+'\n进展 / 新情况：\n实际日期 / 希望调整到：\n实际主动工时（可选）：\n需要协调的事：';
      $('research-feedback-box').scrollIntoView({block:'start',behavior:'auto'});$('research-feedback-text').focus();
    });
    refreshButton.addEventListener('click',refresh);
    $('research-search').addEventListener('input',function(){query=this.value;limit=12;render();});
    $('research-category').addEventListener('change',function(){category=this.value;limit=12;render();});
    $('research-state').addEventListener('change',function(){state=this.value;limit=12;render();});
    $('research-reset').addEventListener('click',function(){query='';category='all';state='all';selectedDay='';limit=12;$('research-search').value='';$('research-category').value='all';$('research-state').value='all';render();});
    $('research-more').addEventListener('click',function(){limit+=12;render();});
    $('research-copy').addEventListener('click',function(){if(w.AI_COPY)w.AI_COPY($('research-feedback-text').value,this);});
    try{apply(w.RESEARCH_SNAPSHOT);$('research-sync-status').textContent='当前展示随网页发布的摘要；打开科研栏目时会检查更新。';}catch(e){$('research-sync-status').textContent='展示摘要校验失败，未加载任务。请稍后刷新。';}
    if((w.location||{}).hash==='#research')refresh();
    if(w.addEventListener)w.addEventListener('focus',function(){if($('view-research').style.display!=='none'&&Date.now()-lastCheck>30000)refresh();});
    setInterval(function(){if($('view-research').style.display==='none'||!data)return;var today=opts.today||beijingDay();if(today!==currentDay){apply(data);refresh();}else if(Date.now()-lastCheck>300000)refresh();},60000);
    return{refresh:refresh,apply:apply,setScope:setScope,state:function(){return{data:data,scope:scope,day:currentDay};}};
  }
  return{validate:validate,model:model,risks:risks,hours:hours,day:day,addDays:addDays,beijingDay:beijingDay,esc:esc,mount:mount};
});
