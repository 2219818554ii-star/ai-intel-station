/* Personal dashboard and cross-section finding. Everything here uses published data. */
(function(root,factory){var api=factory();if(typeof module==='object'&&module.exports)module.exports=api;if(root&&typeof document!=='undefined')root.AI_WORKSPACE=api.mount(root,document);})(typeof window==='undefined'?null:window,function(){
  'use strict';
  var routes={home:'今天',research:'科研',cqut:'校园通知',comp:'赛事机会',daily:'AI 日报',rank:'模型与工具',learn:'AI 学习',magazines:'期刊阅读',ted:'TED 英语',forum:'成长讲坛',funds:'资产记录'};
  function esc(v){return String(v==null?'':v).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
  function day(){var p=new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Shanghai',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date()),d={};p.forEach(function(x){d[x.type]=x.value;});return d.year+'-'+d.month+'-'+d.day;}
  function safeURL(value){if(typeof value!=='string'||!/^https?:\/\//i.test(value)||/[\u0000-\u0020\u007f\\]/.test(value))return '';try{var u=new URL(value);return u.hostname&&!u.username&&!u.password?u.href:'';}catch(e){return '';}}
  function list(value){return Array.isArray(value)?value.filter(function(x){return x&&typeof x==='object'&&!Array.isArray(x);}):[];}
  function words(value){return String(value||'').toLowerCase().trim().split(/\s+/).filter(Boolean);}
  function personalNotice(t){
    var title=String(t.t||''),body=String(t.sum||''),source=String(t.src||'');
    if(t.cat==='college'&&!/化学化工/.test(source)&&!/全校研究生|全校学生/.test(body))return false;
    if(/对其他学院无直接影响|仅影响该院|面向出题教师|不必处理收卷|该场次已于|错过可关注|学科交叉分中心|优势特色学科群/.test(title+' '+body))return false;
    return ['grad','money','exam'].indexOf(t.tag)>=0||/研究生.*(?:奖励|申报|培养|学位|毕业)/.test(title);
  }
  function deadline(t){
    var m=/^(\d{4}-\d\d-\d\d)(?: (\d\d:\d\d))?$/.exec(String(t.dl||''));
    if(!m||t.deadlineUnverified||t.st!=='报名中'||m[2]&&t.deadlineTime&&m[2]!==t.deadlineTime)return null;
    var explicit=m[2]||t.deadlineTime,clock=explicit||'23:59',stamp=Date.parse(m[1]+'T00:00:00Z');
    if(!Number.isFinite(stamp)||new Date(stamp).toISOString().slice(0,10)!==m[1]||!/^([01]\d|2[0-3]):[0-5]\d$/.test(clock))return null;
    var at=Date.parse(m[1]+'T'+clock+':'+(explicit?'00':'59')+'+08:00');return {t:t,at:at,date:m[1]+(explicit?' '+clock:'')};
  }
  function search(entries,query,limit){
    var terms=words(query),exactTask=terms.length===1&&/^t\d{3,5}$/.test(terms[0])?terms[0]:"";
    var found=entries.filter(function(e){return terms.every(function(t){return e.hay.indexOf(t)>=0;});});
    if(exactTask)found.sort(function(a,b){return Number(b.route==='research'&&String(b.key||'').toLowerCase()===exactTask)-Number(a.route==='research'&&String(a.key||'').toLowerCase()===exactTask);});
    return found.slice(0,limit||25);
  }
  function index(data,details){
    var result=[];
    function add(e){e.hay=[e.title,e.group,e.text,e.key].filter(Boolean).join(' ').toLowerCase();result.push(e);}
    Object.keys(routes).forEach(function(route){add({route:route,title:routes[route],group:'栏目',text:route});});
    list(data.RESEARCH_SNAPSHOT&&data.RESEARCH_SNAPSHOT.tasks).forEach(function(t){var d=details&&details(t.id)||{};add({route:'research',key:t.id,title:d.title||t.title,group:'科研任务 · '+t.id,text:[t.title,t.category,t.status,d.steps,d.acceptance,d.progress,d.prerequisite,d.gate].join(' ')});});
    list(data.CQUT_NOTICES).forEach(function(t){add({route:'cqut',title:t.t,key:t.t,group:'校园通知 · '+t.date,text:[t.src,t.sum].join(' ')});});
    list(data.COMP).forEach(function(t){add({route:'comp',title:t.n,key:t.n,group:'赛事库',text:[t.type,t.reg,t.org,t.fit].join(' ')});});
    list(data.MAGAZINE_ARTICLES).forEach(function(t){var p=list(data.MAGAZINES).find(function(p){return p.id===t.publication;});add({route:'magazines',title:t.title,key:t.title,group:'期刊 · '+(p?p.name:t.publication),text:[t.summary,t.featuredReason].join(' ')});});
    list(data.TED).forEach(function(t){add({route:'ted',title:t.en,key:t.en,group:'TED · '+(t.sp||''),text:[t.cn,t.cat,t.why].join(' ')});});
    list(data.FORUM_SERIES).forEach(function(s){list(s.vids).forEach(function(v){add({route:'forum',title:v.t,key:v.t,who:s.who,group:'讲坛 · '+s.who,text:[v.up,s.cat].join(' ')});});});
    list(data.RANK&&data.RANK.models).forEach(function(t){add({route:'rank',title:t.name,group:'模型与工具',text:t.note});});
    return result;
  }
  function mount(w,doc){
    var home=doc.getElementById('home-metrics');if(!home)return null;
    var dialog=doc.getElementById('workspace-search'),query=doc.getElementById('workspace-query'),results=doc.getElementById('workspace-search-results'),searchEntries=[],currentResults=[],trigger=null,pendingSearchCloses=[],KEY='ai-workspace-opened-v1';
    function go(route,opts){if(w.AI_NAV)w.AI_NAV.go(route,opts||{});else{var tab=doc.getElementById('tab-'+route);if(tab&&tab.click)tab.click();}}
    function input(id,value,type){var e=doc.getElementById(id);if(e){e.value=value;if(typeof Event!=='undefined')e.dispatchEvent(new Event(type||'input',{bubbles:true}));}}
    function clickButton(id,attribute,value){var box=doc.getElementById(id);if(!box)return;var el=Array.prototype.find.call(box.querySelectorAll('button'),function(b){return b.getAttribute(attribute)===value;});if(el)el.click();}
    function closeSearch(restoreFocus){
      if(!dialog||!dialog.open)return;
      pendingSearchCloses.push({restore:restoreFocus!==false,trigger:trigger});dialog.close();
    }
    function openEntry(e){
      closeSearch(false);go(e.route,{focus:true});
      if(e.route==='research'&&e.key&&w.AI_RESEARCH&&w.AI_RESEARCH.focusTask){w.AI_RESEARCH.focusTask(e.key);return;}
      if(!e.key)return;
      if(e.route==='cqut'){var reset=doc.getElementById('cqut-reset');if(reset)reset.click();input('cqut-search',e.key);}
      if(e.route==='comp'){clickButton('compScope','data-s','all');clickButton('compFilters','data-f','all');input('comp-search',e.key);}
      if(e.route==='magazines'){doc.getElementById('magazine-reset').click();input('magazine-query',e.key);}
      if(e.route==='ted'||e.route==='forum'){
        var view=doc.getElementById('view-'+e.route),resetLibrary=view&&view.querySelector('[data-library-reset]');if(resetLibrary)resetLibrary.click();
        if(e.route==='forum'){clickButton('forumFilters','data-c','全部');var list=doc.getElementById('forum-list'),series=Array.prototype.find.call(list.querySelectorAll('[data-open]'),function(x){return x.getAttribute('data-open')===e.who;});if(series)series.click();}
        var field=view&&view.querySelector('.library-tools input[type="search"]');if(field){field.value=e.key;field.dispatchEvent(new Event('input',{bubbles:true}));}
      }
    }
    function readRecent(){try{var r=JSON.parse(w.localStorage.getItem(KEY)||'null');if(r&&routes[r.route]&&typeof r.title==='string'&&safeURL(r.url)&&Number.isFinite(r.at))return r;}catch(e){}return null;}
    function renderRecent(){var r=readRecent(),el=doc.getElementById('home-opened');if(!r){el.textContent='打开过的文章或课程会出现在这里；打开不会自动标为已读。';return;}
      el.className='home-list';el.innerHTML='<a class="home-list-item" href="'+esc(r.url)+'" target="_blank" rel="noopener noreferrer"><strong>'+esc(r.title)+'</strong><small>'+esc(routes[r.route])+' · 仅记录打开，不代表读完</small></a>';
    }
    function renderResume(){var e=doc.getElementById('home-resume'),route='';try{route=w.sessionStorage.getItem('ai-workspace-last-view')||'';}catch(error){}e.hidden=!routes[route]||route==='home';if(!e.hidden){e.className='home-resume';e.innerHTML='<div><small>接着上次的位置</small><strong>'+esc(routes[route])+' · 保留这个窗口的阅读位置</strong></div><button class="top-btn" type="button" data-go="'+esc(route)+'">继续 ↗</button>';}}
    function renderHome(){
      var now=day(),app=w.AI_RESEARCH,raw=app&&app.state?app.state().data:w.RESEARCH_SNAPSHOT;
      var tasks=raw&&Array.isArray(raw.tasks)?raw.tasks:[],active=tasks.filter(function(t){return t.status!=='已完成'&&t.status!=='已取消';}),overdue=active.filter(function(t){return t.date&&t.date<now;}),model=app&&app.getModel?app.getModel():null;
      var today=model?model.today:active.filter(function(t){return t.date===now;}),week=model?model.week:active.filter(function(t){return t.date>now&&t.date<=new Date(Date.parse(now+'T00:00:00Z')+7*86400000).toISOString().slice(0,10);}),risk=model?model.risk:active.filter(function(t){return !t.date||t.date<now||t.status==='待条件'||t.status==='待确认'||t.hours===null||t.hours>8;});
      function hrs(list){var n=0,missing=0;list.forEach(function(t){if(t.hours===null)missing++;else if(Number.isFinite(t.hours))n+=t.hours;});return(missing?'已知 ':'')+(Math.round(n*10)/10)+' h'+(missing?' · 含待估':'');}
      var dateLabel=new Intl.DateTimeFormat('zh-CN',{timeZone:'Asia/Shanghai',month:'long',day:'numeric',weekday:'long'}).format(new Date());
      doc.getElementById('home-date').textContent=now+' · '+dateLabel;doc.getElementById('workspace-header-date').textContent=dateLabel;
      home.innerHTML=[['today','今天待办',today.length,'预计 '+hrs(today),'任务来自已同步的科研安排'],['week','未来7天',week.length,'预计 '+hrs(week),'不包含今天'],['risk','需要核对',risk.length,'条件 / 排期 / 工时','待核对不等于实际未完成']].map(function(x){return '<button type="button" class="home-metric" data-home-scope="'+x[0]+'"><span>'+x[1]+'</span><strong>'+x[2]+'</strong><small>'+esc(x[3])+'</small><em>'+x[4]+'</em></button>';}).join('');
      doc.getElementById('home-tasks').innerHTML=today.length?today.slice(0,3).map(function(t){var d=app&&app.getDetail?app.getDetail(t.id):null;return '<article class="home-task"><div class="home-task-meta"><span>'+esc(t.id)+'</span><span>'+esc(t.category)+'</span><span class="home-task-state">'+esc(t.status)+'</span><span>预计 '+(t.hours===null?'待估':t.hours+' h')+'</span></div><h3>'+esc(d&&d.title||t.title)+'</h3><p>'+esc(d&&d.steps?d.steps.slice(0,165)+(d.steps.length>165?'…':''):'查看执行步骤与完成标准，按已核对安排推进。')+'</p><button type="button" class="top-btn" data-home-task="'+t.id+'">查看完整执行内容 →</button></article>';}).join(''):'<div class="home-empty"><p>今天没有已排定的待办。可以先核对未来7天和待确认事项，不自动把旧计划顺延到今天。</p><button type="button" class="top-btn" data-go="research">查看科研安排 →</button></div>';
      doc.getElementById('home-attention').innerHTML=overdue.length?'<button type="button" class="home-attention" data-home-scope="risk">'+overdue.length+' 项建议日期已过，等待你复核排期；不代表任务实际未完成。 →</button>':'';
      doc.getElementById('home-research-stamp').textContent=raw?'任务版本 '+raw.revision.slice(0,8)+' · 原记录同步 '+raw.syncedAt.slice(0,10)+'；可在科研栏记录进展，核对后应用安排。':'任务暂不可读，其他栏目仍可使用。';
      var notices=list(w.CQUT_NOTICES).filter(personalNotice).slice().sort(function(a,b){return String(b.date).localeCompare(String(a.date));}).slice(0,3);
      doc.getElementById('home-notices').innerHTML=notices.map(function(t){return '<button type="button" class="home-list-item" data-home-notice="'+esc(t.t)+'"><strong>'+esc(t.t)+'</strong><small>'+esc(t.date)+' · '+esc(t.src||'学校原文')+'</small></button>';}).join('')||'<div class="home-empty">暂无已收录的相关通知，仍可直接查看学校官方入口。</div>';
      doc.getElementById('home-notice-stamp').textContent='最近成功内容 '+(w.CQUT_UPDATED||'待核对')+' · 来源核查 '+(w.CQUT_CHECKED||'待核对')+'；通知是否与你有关仍需看原文。';
      var matches=list(w.MATCHES).map(deadline).filter(function(x){return x&&x.at>=Date.now();}).sort(function(a,b){return a.at-b.at;}).slice(0,3);
      doc.getElementById('home-opportunities').innerHTML=matches.map(function(x){return '<button type="button" class="home-list-item" data-home-opportunity="'+esc(x.t.n)+'"><strong>'+esc(x.t.n)+'</strong><small>已收录报名截止 '+esc(x.date)+' · '+(x.t.fit?'专业适配推荐':'资格与投入待核对')+'</small></button>';}).join('')||'<div class="home-empty">当前没有能按明确截止排列的精选报名线索；可到赛事库查看其他方向。</div>';
      var chosen=list(w.MAGAZINE_ARTICLES).filter(function(a){return typeof a.featuredReason==='string'&&a.featuredReason;}).slice().sort(function(a,b){return(a.featuredPriority||999)-(b.featuredPriority||999);}).slice(0,2);
      doc.getElementById('home-reading').innerHTML=chosen.map(function(a){var p=list(w.MAGAZINES).find(function(p){return p.id===a.publication;});return '<div class="home-task home-reading-item"><div class="home-task-meta">'+esc(p?p.name:a.publication)+' · '+esc(a.publishedAt||'原文未标日期')+'</div><button class="home-list-item" type="button" data-home-article="'+esc(a.title)+'"><strong>'+esc(a.title)+'</strong></button><p>'+esc(a.featuredReason)+'</p></div>';}).join('');
      doc.getElementById('home-content-state').textContent='期刊 '+(w.MAGAZINES_CHECKED||'待核对')+'核查 · '+list(w.MAGAZINE_ARTICLES).length+'篇选读';
      searchEntries=index({RESEARCH_SNAPSHOT:raw,CQUT_NOTICES:w.CQUT_NOTICES,COMP:w.COMP,MAGAZINE_ARTICLES:w.MAGAZINE_ARTICLES,MAGAZINES:w.MAGAZINES,TED:w.TED,FORUM_SERIES:w.FORUM_SERIES,RANK:w.RANK},app&&app.getDetail?app.getDetail:null);renderRecent();renderResume();
    }
    function renderSearch(){currentResults=search(searchEntries,query.value,30);results.innerHTML=currentResults.length?currentResults.map(function(e,i){return '<button type="button" class="workspace-search-result" data-search-result="'+i+'"><span>'+esc(e.group)+'</span><strong>'+esc(e.title)+'</strong></button>';}).join(''):'<div class="workspace-search-empty">没有找到。可以用任务编号、刊物名、研究方向或更短的关键词重试。</div>';}
    function openSearch(button){if(!dialog.open){trigger=button||doc.activeElement;var menu=doc.getElementById('workspace-menu');if(menu&&menu.contains&&menu.contains(trigger))trigger=doc.getElementById('workspace-search-open');}if(w.AI_NAV&&w.AI_NAV.closeMenu)w.AI_NAV.closeMenu({restoreFocus:false});query.value='';renderSearch();if(dialog.showModal&&!dialog.open)dialog.showModal();else if(!dialog.open)dialog.setAttribute('open','');query.focus();}
    if(dialog){
      doc.getElementById('workspace-search-open').addEventListener('click',function(){openSearch(this);});doc.getElementById('workspace-search-close').addEventListener('click',function(){closeSearch(true);});query.addEventListener('input',renderSearch);results.addEventListener('click',function(e){var b=e.target.closest&&e.target.closest('[data-search-result]');if(b&&currentResults[Number(b.dataset.searchResult)])openEntry(currentResults[Number(b.dataset.searchResult)]);});
      dialog.addEventListener('close',function(){var action=pendingSearchCloses.shift()||{restore:true,trigger:trigger};if(!dialog.open&&action.restore&&action.trigger&&action.trigger.isConnected!==false&&action.trigger.focus)action.trigger.focus({preventScroll:true});});
      dialog.addEventListener('keydown',function(e){if(e.key==='Escape'){e.preventDefault();closeSearch(true);}});
      query.addEventListener('keydown',function(e){if(e.key==='ArrowDown'){var first=results.querySelector('button');if(first){e.preventDefault();first.focus();}}if(e.key==='Enter'&&currentResults[0]){e.preventDefault();openEntry(currentResults[0]);}});
    }
    doc.addEventListener('keydown',function(e){var tag=(e.target&&e.target.tagName||'').toLowerCase();if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){e.preventDefault();openSearch(doc.activeElement);}else if(e.key==='/'&&!['input','textarea','select'].includes(tag)&&!e.altKey&&!e.ctrlKey&&!e.metaKey){e.preventDefault();openSearch(doc.activeElement);}});
    doc.addEventListener('click',function(e){
      var el=e.target.closest&&e.target.closest('[data-home-task],[data-home-scope],[data-home-notice],[data-home-opportunity],[data-home-article]');
      if(el){if(el.dataset.homeTask)openEntry({route:'research',key:el.dataset.homeTask});if(el.dataset.homeScope){go('research',{focus:true});if(w.AI_RESEARCH)w.AI_RESEARCH.setScope(el.dataset.homeScope);}if(el.dataset.homeNotice)openEntry({route:'cqut',key:el.dataset.homeNotice});if(el.dataset.homeOpportunity)openEntry({route:'comp',key:el.dataset.homeOpportunity});if(el.dataset.homeArticle)openEntry({route:'magazines',key:el.dataset.homeArticle});}
      var a=e.target.closest&&e.target.closest('a[href]');if(!a||!safeURL(a.href))return;var view=a.closest&&a.closest('#view-magazines,#view-ted,#view-forum,#view-learn');if(!view)return;var article=a.closest('article'),title=article&&article.querySelector('h4,h3,.cmp-name'),record={route:view.id.slice(5),url:a.href,title:(title?title.textContent:a.textContent).trim().slice(0,400),at:Date.now()};if(!record.title)return;try{w.localStorage.setItem(KEY,JSON.stringify(record));}catch(error){}renderRecent();
    });
    if(w.addEventListener){w.addEventListener('research-updated',renderHome);w.addEventListener('workspace:route',function(e){var route=e.detail&&e.detail.tab;if(route&&route!=='home')try{w.sessionStorage.setItem('ai-workspace-last-view',route);}catch(error){}if(route==='home')renderHome();});}
    var installPrompt=null,install=doc.getElementById('workspace-install');
    if(w.addEventListener&&install)w.addEventListener('beforeinstallprompt',function(e){e.preventDefault();installPrompt=e;install.hidden=false;});
    if(install)install.addEventListener('click',function(){if(installPrompt){installPrompt.prompt();installPrompt=null;install.hidden=true;}});
    if(w.navigator&&w.navigator.serviceWorker&&/^https?:$/.test(w.location.protocol))w.navigator.serviceWorker.register('sw.js',{updateViaCache:'none'}).catch(function(){});
    function network(){var el=doc.getElementById('workspace-network');if(el)el.textContent=w.navigator&&w.navigator.onLine===false?'离线：显示已保存内容':'访问后可保留离线副本';}
    if(w.addEventListener){w.addEventListener('offline',network);w.addEventListener('online',network);}network();renderHome();
    return{render:renderHome,search:function(q){return search(searchEntries,q,30);},go:go};
  }
  return{mount:mount,index:index,search:search,day:day,safeURL:safeURL,deadline:deadline,personalNotice:personalNotice};
});
