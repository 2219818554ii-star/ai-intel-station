(function(root,factory){'use strict';var api=factory();if(typeof module==='object'&&module.exports)module.exports=api;if(root.document)api.mount(root,root.document);})(typeof window!=='undefined'?window:this,function(){
  'use strict';
  var ENDPOINT='https://luohao-workspace-sync.easyroot8192.chatgpt.site/api/v1/action';
/* Client storage and synchronization engine, included in the same cloud factory. */
  var KEY='luohao-cloud-v1',AUTH='luohao-cloud-connection-v1',CLIENT='luohao-cloud-client-v1';
  var EVENT='luohao-cloud-event-v1:',ACK='luohao-cloud-ack-v1:',RESOLVED='luohao-cloud-resolved-v1:';
  function fieldKey(e){return e.namespace+'\n'+e.key+'\n'+e.field;}
  function allowedField(ns,field){return ns==='magazine'?['fav','read'].includes(field):ns==='learning'&&['fav','done'].includes(field);}
  function webURL(value,httpsOnly){try{var u=new URL(value);return typeof value==='string'&&value.length<=2100&&!/[\s<>"'\\]/.test(value)&&!u.username&&!u.password&&(u.protocol==='https:'||!httpsOnly&&u.protocol==='http:');}catch(e){return false;}}
  function validRow(e){return !!(e&&allowedField(e.namespace,e.field)&&typeof e.key==='string'&&e.key.length<=2100&&typeof e.value==='boolean'&&Number.isInteger(e.version)&&e.version>0);}
  function validDate(value){return typeof value==='string'&&/^\d{4}-\d\d-\d\d$/.test(value)&&Number.isFinite(Date.parse(value))&&new Date(value+'T00:00:00Z').toISOString().slice(0,10)===value;}
  function safeMetadata(namespace,key,input,pubs,today){
    input=input&&typeof input==='object'&&!Array.isArray(input)?input:{};
    var out={},url=key,kind='';
    if(namespace==='learning'){var colon=key.indexOf(':');kind=key.slice(0,colon);url=key.slice(colon+1);if(!['learn','ted','forum'].includes(kind)||!webURL(url,false))return null;out.kind=kind;}
    else if(namespace==='magazine'){
      if(!webURL(url,true))return null;
      var host=new URL(url).hostname.toLowerCase(),owners=(Array.isArray(pubs)?pubs:[]).filter(function(p){return p&&Array.isArray(p.hosts)&&p.hosts.includes(host);});
      if(!owners.length)return null;
    }else return null;
    out.url=url;
    if(typeof input.title==='string'&&input.title.trim())out.title=input.title.slice(0,200);
    if(Number.isFinite(input.at)&&input.at>=0)out.at=input.at;
    var article=input.article;
    if(namespace==='magazine'&&article&&typeof article==='object'&&!Array.isArray(article)&&typeof article.title==='string'&&article.title.trim()&&owners.some(function(p){return p.id===article.publication;})){
      out.article={publication:article.publication,title:article.title.slice(0,600),publishedAt:validDate(article.publishedAt)&&article.publishedAt<=today?article.publishedAt:null,summary:typeof article.summary==='string'?article.summary.slice(0,1200):''};
    }
    return out;
  }
  function mount(w,doc){
    var state={token:'',versions:{},outbox:[],conflicts:[]},running=null,again=false,connected=false,proposal=null,modelConfigs=[];
    var epoch=0,sequence=0,memoryEvents=Object.create(null),memoryAcks=Object.create(null),storageProblem=false;
    function id(){return w.crypto.randomUUID();}
    function readJSON(key){try{return JSON.parse(w.localStorage.getItem(key)||'null');}catch(e){return null;}}
    function writeJSON(key,value){try{w.localStorage.setItem(key,JSON.stringify(value));return true;}catch(e){storageProblem=true;return false;}}
    var saved=readJSON(KEY);
    if(saved&&typeof saved.token==='string'&&saved.versions&&typeof saved.versions==='object'&&!Array.isArray(saved.versions)&&Array.isArray(saved.outbox))state=saved;
    state.conflicts=Array.isArray(state.conflicts)?state.conflicts:[];
    var auth=readJSON(AUTH);
    if(!auth||typeof auth.token!=='string'||typeof auth.generation!=='string'){auth={token:state.token,generation:id()};writeJSON(AUTH,auth);}
    state.token=auth.token;
    var client=readJSON(CLIENT);
    if(typeof client!=='string'||!client){client=id();writeJSON(CLIENT,client);}
    var origin=id();
    function current(){var latest=readJSON(AUTH);if(latest&&typeof latest.token==='string'&&typeof latest.generation==='string'&&latest.generation!==auth.generation){auth=latest;state.token=auth.token;epoch++;connected=false;proposal=null;if(w.AI_RESEARCH)w.AI_RESEARCH.clearCloud();}return{token:auth.token,generation:auth.generation,epoch:epoch};}
    function isCurrent(ctx){var now=current();return ctx&&ctx.epoch===now.epoch&&ctx.generation===now.generation&&ctx.token===now.token;}
    function stale(){var e=Error('__cloud_stale_response__');e.stale=true;return e;}
    function guard(ctx){if(!isCurrent(ctx))throw stale();}
    function status(s){if(s==='__cloud_stale_response__')return;var el=doc.getElementById('cloud-status');if(el)el.textContent=s;doc.querySelectorAll('[data-cloud-status]').forEach(function(e){e.textContent=s;});}
    function setAuth(token){epoch++;auth={token:token,generation:id()};state.token=token;writeJSON(AUTH,auth);connected=false;proposal=null;}
    function keys(prefix){var result=[];try{for(var i=0;i<w.localStorage.length;i++){var k=w.localStorage.key(i);if(k&&k.startsWith(prefix))result.push(k);}}catch(e){storageProblem=true;}return result;}
    var dateFormatter=new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Shanghai'});
    function today(){return dateFormatter.format(new Date());}
    function cleanMeta(ns,key,meta){return safeMetadata(ns,key,meta,w.MAGAZINES,today());}
    function eventValid(e){return !!(e&&typeof e.opId==='string'&&e.opId.length<=100&&allowedField(e.namespace,e.field)&&typeof e.key==='string'&&typeof e.value==='boolean'&&Number.isInteger(e.baseVersion)&&e.baseVersion>=0&&cleanMeta(e.namespace,e.key,e.metadata));}
    function journal(){var byId=Object.assign({},memoryEvents);keys(EVENT).forEach(function(k){var e=readJSON(k);if(eventValid(e))byId[e.opId]=e;});return Object.values(byId).filter(eventValid);}
    function acknowledgement(opId){return memoryAcks[opId]||readJSON(ACK+opId);}
    function acknowledgements(){var byId=Object.assign({},memoryAcks);keys(ACK).forEach(function(k){var a=readJSON(k);if(a&&typeof a.opId==='string')byId[a.opId]=a;});return Object.values(byId);}
    function eventOrder(a,b){return(a.createdAt||0)-(b.createdAt||0)||(a.origin===b.origin?(a.sequence||0)-(b.sequence||0):0)||a.opId.localeCompare(b.opId);}
    function putEvent(e){memoryEvents[e.opId]=e;return writeJSON(EVENT+e.opId,e);}
    function pendingEvents(){return journal().filter(function(e){return!acknowledgement(e.opId);}).sort(eventOrder);}
    function conflicts(){return acknowledgements().filter(function(a){return a.status==='conflict'&&!readJSON(RESOLVED+a.opId);}).sort(function(a,b){return eventOrder(a.event,b.event);});}
    function mergeVersions(){var prior=readJSON(KEY);Object.entries(prior&&prior.versions||{}).forEach(function(pair){if(Number.isInteger(pair[1])&&pair[1]>0)state.versions[pair[0]]=Math.max(state.versions[pair[0]]||0,pair[1]);});}
    function persist(){mergeVersions();state.token=current().token;state.outbox=pendingEvents();state.conflicts=conflicts();return writeJSON(KEY,state);}
    function ack(e,kind,row,successor){
      if(acknowledgement(e.opId))return;
      var event=Object.assign({},e);if(kind==='accepted')delete event.metadata;
      var record={opId:e.opId,status:kind,event:event,row:row?{namespace:row.namespace,key:row.key,field:row.field,value:row.value,version:row.version}:null,successorOpId:successor||null,at:Date.now()};
      memoryAcks[e.opId]=record;
      if(writeJSON(ACK+e.opId,record)){try{w.localStorage.removeItem(EVENT+e.opId);}catch(error){storageProblem=true;}delete memoryEvents[e.opId];}
    }
    function rebaseOwnAcknowledged(){
      var pending=pendingEvents(),accepted=acknowledgements().filter(function(a){return a.status==='accepted'&&a.event&&a.event.client===client&&a.row&&Number.isInteger(a.row.version);}).sort(function(a,b){return a.row.version-b.row.version;});
      accepted.forEach(function(a){pending.forEach(function(e){
        if(e.client===client&&fieldKey(e)===fieldKey(a.event)&&eventOrder(e,a.event)>0&&e.baseVersion===a.event.baseVersion){e.baseVersion=a.row.version;putEvent(e);}
      });});
      return pendingEvents();
    }
    function coalesced(){
      var pending=rebaseOwnAcknowledged(),latest=Object.create(null);
      pending.forEach(function(e){latest[fieldKey(e)]=e;});
      pending.forEach(function(e){var chosen=latest[fieldKey(e)];if(chosen.opId!==e.opId)ack(e,'superseded',null,chosen.opId);});
      return Object.values(latest).sort(eventOrder);
    }
    // Per-operation keys are authoritative; another tab cannot replace a queue.
    (Array.isArray(state.outbox)?state.outbox:[]).forEach(function(e){if(eventValid(e)&&!acknowledgement(e.opId)){e=Object.assign({client:client,origin:origin,sequence:++sequence,createdAt:Date.now()},e);putEvent(e);}});
    state.conflicts.forEach(function(c){if(c&&c.event&&eventValid(c.event)&&!acknowledgement(c.opId))ack(c.event,'conflict',c.row);});
    async function request(action,data,anonymous,ctx){
      ctx=ctx||current();guard(ctx);
      try{
        var r=await w.fetch(ENDPOINT,{method:'POST',mode:'cors',cache:'no-store',headers:Object.assign({'Content-Type':'application/json'},!anonymous&&ctx.token?{Authorization:'Bearer '+ctx.token}:{}),body:JSON.stringify(Object.assign({action:action},data||{})),signal:AbortSignal.timeout(action==='research.propose'?65000:15000)});
        guard(ctx);var body;try{body=await r.json();}catch(e){guard(ctx);throw Error('同步服务未返回有效响应');}guard(ctx);
        if(!r.ok||body.error)throw Error((body.error&&body.error.message)||body.message||(typeof body.error==='string'?body.error:'')||('服务响应 '+r.status));return body;
      }catch(e){guard(ctx);throw e;}
    }
    function localList(namespace){
      var rows=readJSON(namespace==='magazine'?'ai-magazine-reading-v1':'ai-learning-v1');
      return(Array.isArray(rows)?rows:[]).filter(function(row){if(!row||typeof row!=='object')return false;var key=namespace==='magazine'?row.url:row.kind+':'+row.url;return typeof key==='string'&&!!cleanMeta(namespace,key,row);});
    }
    function enrich(found,meta){
      ['kind','url','title','at'].forEach(function(k){if(found[k]===undefined||found[k]===null||found[k]==='')if(meta[k]!==undefined)found[k]=meta[k];});
      if(meta.article){if(!found.article||typeof found.article!=='object'||!found.article.title)found.article=meta.article;else if(found.article.publication===meta.article.publication){if(!found.article.publishedAt&&meta.article.publishedAt)found.article.publishedAt=meta.article.publishedAt;if(!found.article.summary&&meta.article.summary)found.article.summary=meta.article.summary;}}
    }
    function storageEvent(key,next){var EventClass=w.StorageEvent||(typeof StorageEvent==='function'?StorageEvent:null);if(EventClass)w.dispatchEvent(new EventClass('storage',{key:key,newValue:next}));}
    function applyRows(rows,ctx){
      guard(ctx);var groups={magazine:localList('magazine'),learning:localList('learning')};
      (Array.isArray(rows)?rows:[]).filter(validRow).forEach(function(row){
        var meta=cleanMeta(row.namespace,row.key,row.metadata);if(!meta)return;
        var k=fieldKey(row);if((state.versions[k]||0)>row.version)return;state.versions[k]=row.version;
        var list=groups[row.namespace],found=list.find(function(x){return(row.namespace==='magazine'?x.url:x.kind+':'+x.url)===row.key;});
        if(!found){found={};enrich(found,meta);list.push(found);}else enrich(found,meta);found[row.field]=row.value;
      });
      pendingEvents().forEach(function(e){var list=groups[e.namespace],row=list.find(function(x){return(e.namespace==='magazine'?x.url:x.kind+':'+x.url)===e.key;});if(!row){row=cleanMeta(e.namespace,e.key,e.metadata);if(row)list.push(row);}if(row)row[e.field]=e.value;});
      Object.keys(groups).forEach(function(ns){guard(ctx);var key=ns==='magazine'?'ai-magazine-reading-v1':'ai-learning-v1',next=JSON.stringify(groups[ns]);if(w.localStorage.getItem(key)!==next){w.localStorage.setItem(key,next);storageEvent(key,next);}});
    }
    function change(namespace,key,field,value,meta){
      if(!allowedField(namespace,field)||typeof value!=='boolean')return false;var clean=cleanMeta(namespace,key,meta);if(!clean)return false;mergeVersions();
      var e={namespace:namespace,key:key,field:field,value:value,baseVersion:state.versions[fieldKey({namespace:namespace,key:key,field:field})]||0,opId:id(),metadata:clean,client:client,origin:origin,sequence:++sequence,createdAt:Date.now()};
      var durable=putEvent(e);persist();status(!durable?'浏览器未允许保存待同步记录；当前操作仅在本页暂存。':current().token?'已保存在本机，正在同步…':'已保存在本机；连接设备后可跨屏同步。');if(current().token)sync();return durable;
    }
    function importLegacy(){
      mergeVersions();var known=new Set(pendingEvents().map(fieldKey));['magazine','learning'].forEach(function(ns){localList(ns).forEach(function(row){['fav',ns==='magazine'?'read':'done'].forEach(function(field){
        var key=ns==='magazine'?row.url:row.kind+':'+row.url,k=fieldKey({namespace:ns,key:key,field:field});
        if(row[field]===true&&!state.versions[k]&&!known.has(k)){putEvent({namespace:ns,key:key,field:field,value:true,baseVersion:0,opId:id(),metadata:cleanMeta(ns,key,row),client:client,origin:origin,sequence:++sequence,createdAt:Date.now()});known.add(k);}
      });});});persist();
    }
    async function sync(){
      var ctx=current();if(!ctx.token)return;if(running&&isCurrent(running)){again=true;return;}running=ctx;again=false;
      async function work(){
        guard(ctx);mergeVersions();var response=await request('sync.pull',null,false,ctx);guard(ctx);connected=true;applyRows(response.rows||[],ctx);
        if(response.research&&w.AI_RESEARCH)w.AI_RESEARCH.applyCloud(response.research);
        var pending=coalesced().slice(0,100);
        if(pending.length){
          var events=pending.map(function(e){return{namespace:e.namespace,key:e.key,field:e.field,value:e.value,baseVersion:e.baseVersion,opId:e.opId,metadata:e.metadata};});
          var pushed=await request('sync.push',{events:events},false,ctx);guard(ctx);
          (pushed.results||[]).forEach(function(result){var event=pending.find(function(e){return e.opId===result.opId;});if(!event)return;if(!validRow(result.row)||fieldKey(result.row)!==fieldKey(event)||!result.conflict&&result.row.value!==event.value)throw Error('同步确认无效，待上传记录仍保留');ack(event,result.conflict?'conflict':'accepted',result.row);});
          rebaseOwnAcknowledged();
          applyRows((pushed.results||[]).filter(function(result){return pending.some(function(e){return e.opId===result.opId;});}).map(function(result){return result.row;}).filter(Boolean),ctx);
        }
        guard(ctx);persist();var currentConflicts=conflicts(),remaining=pendingEvents();
        status(currentConflicts.length?'同步有 '+currentConflicts.length+' 项冲突，已保留云端值；可重试本机选择。':remaining.length?'还有 '+remaining.length+' 项待上传。':'已同步 · '+new Date().toLocaleTimeString('zh-CN',{hour:'2-digit',minute:'2-digit'})+(storageProblem?'；浏览器未允许持久保存连接，请保持页面打开。':''));
        if(remaining.length)again=true;
      }
      try{if(w.navigator&&w.navigator.locks&&w.navigator.locks.request)await w.navigator.locks.request('luohao-cloud-sync-v1',{mode:'exclusive'},work);else await work();}
      catch(e){if(!e.stale&&isCurrent(ctx)){connected=false;status('暂未同步：'+e.message+'。本机记录已保留。');}}
      finally{if(running===ctx){running=null;if(again&&isCurrent(ctx)){again=false;w.setTimeout(function(){if(isCurrent(ctx))sync();},600);}}}
    }

    function open(){var panel=doc.getElementById('cloud-settings');if(!panel)return;panel.showModal();doc.getElementById('cloud-connection').hidden=!!state.token;doc.getElementById('cloud-connected').hidden=!state.token;if(state.token){sync();request('settings.get').then(function(data){var el=doc.getElementById('cloud-model-note');modelConfigs=data.providers||[];modelChoice();el.textContent=modelConfigs.map(function(p){return p.provider+'：'+(p.hasKey?'已设置':'未设置')+' '+(p.model||'');}).join('；')||'尚未设置模型密钥。';}).catch(function(e){status(e.message);});}}
    function modelChoice(){var provider=doc.getElementById('cloud-provider').value,config=modelConfigs.find(function(p){return p.provider===provider;}),field=doc.getElementById('cloud-model');field.value=config&&config.model?config.model:(provider==='deepseek'?'deepseek-flash':'');field.placeholder=provider==='deepseek'?'DeepSeek模型名称':'填写你可用的OpenAI模型名称';}
    async function devices(){var list=doc.getElementById('cloud-devices');try{var result=await request('devices.list');list.replaceChildren();(result.devices||[]).filter(function(d){return!d.revoked;}).forEach(function(d){var row=doc.createElement('p'),label=doc.createElement('span');label.textContent=d.label+(d.current?'（本设备）':'')+' · 最近 '+new Date(d.lastSeenAt).toLocaleString('zh-CN');row.appendChild(label);if(!d.current){var b=doc.createElement('button');b.type='button';b.textContent='撤销连接';b.onclick=async function(){try{await request('devices.revoke',{deviceId:d.deviceId});devices();}catch(e){status(e.message);}};row.appendChild(b);}list.appendChild(row);});}catch(e){status(e.message);}}
    function init(){var panel=doc.getElementById('cloud-settings');if(!panel)return;doc.querySelectorAll('[data-cloud-open]').forEach(function(b){b.addEventListener('click',open);});doc.getElementById('cloud-close').onclick=function(){panel.close();};panel.addEventListener('close',function(){doc.getElementById('cloud-api-key').value='';doc.getElementById('cloud-code').value='';});doc.getElementById('cloud-provider').onchange=modelChoice;doc.getElementById('cloud-devices-refresh').onclick=devices;panel.addEventListener('keydown',function(e){if(e.key==='Escape'){e.preventDefault();panel.close();}});
      doc.getElementById('cloud-connect').onclick=async function(){var secret=doc.getElementById('cloud-code'),button=this;button.disabled=true;try{var type=doc.getElementById('cloud-code-type').value,result=await request(type,type==='bootstrap'||type==='recovery'?{secret:secret.value.trim(),label:doc.getElementById('cloud-device-label').value.trim()}:{code:secret.value.trim(),label:doc.getElementById('cloud-device-label').value.trim()},true);setAuth(result.token);secret.value='';importLegacy();persist();doc.getElementById('cloud-connection').hidden=true;doc.getElementById('cloud-connected').hidden=false;await sync();}catch(e){status(e.message);}finally{button.disabled=false;}};
      doc.getElementById('cloud-sync-now').onclick=sync;
      doc.getElementById('cloud-pair').onclick=async function(){try{var result=await request('pairing.create');doc.getElementById('cloud-pair-code').textContent='配对码：'+result.code+'（有效至 '+new Date(result.expiresAt).toLocaleTimeString('zh-CN')+'，仅用一次）';}catch(e){status(e.message);}};
      doc.getElementById('cloud-disconnect').onclick=function(){setAuth('');persist();if(w.AI_RESEARCH)w.AI_RESEARCH.clearCloud();connected=false;doc.getElementById('cloud-pair-code').textContent='';doc.getElementById('cloud-connection').hidden=false;doc.getElementById('cloud-connected').hidden=true;status('此设备已断开；本机阅读记录仍保留。');};
      doc.getElementById('cloud-conflict-retry').onclick=function(){conflicts().forEach(function(c){var source=c.event;if(source&&change(source.namespace,source.key,source.field,source.value,source.metadata))writeJSON(RESOLVED+c.opId,{at:Date.now()});});persist();sync();};
      doc.getElementById('cloud-model-save').onclick=async function(){var b=this,key=doc.getElementById('cloud-api-key');b.disabled=true;try{var values={provider:doc.getElementById('cloud-provider').value,model:doc.getElementById('cloud-model').value.trim()};if(key.value.trim())values.apiKey=key.value.trim();var result=await request('settings.save',values);modelConfigs=result.providers||[];key.value='';doc.getElementById('cloud-model-note').textContent='密钥已加密保存到服务端；尚未验证真实模型调用。';}catch(e){status(e.message);}finally{b.disabled=false;}};
      doc.getElementById('research-ai-propose').onclick=async function(){if(!state.token){open();return;}var b=this;b.disabled=true;proposal=null;doc.getElementById('research-ai-apply').hidden=true;doc.getElementById('research-ai-preview').textContent='正在分析反馈…';try{var base=w.AI_RESEARCH.state().baseData,result=await request('research.propose',{feedback:doc.getElementById('research-feedback-text').value,provider:doc.getElementById('research-ai-provider').value,baseRevision:base.revision,tasks:base.tasks});proposal=result;doc.getElementById('research-ai-preview').textContent=(result.summary||'任务调整建议')+'\n'+result.patches.map(function(p){var labels={status:'状态',suggestedDate:'建议日期',plannedHours:'预计主动工时',progress:'用户进展'};return p.id+'：'+Object.keys(p).filter(function(k){return k!=='id';}).map(function(k){return (labels[k]||k)+' → '+(p[k]===null?'待定':String(p[k]));}).join('；');}).join('\n');doc.getElementById('research-ai-apply').hidden=!result.patches.length;}catch(e){if(!e.stale)doc.getElementById('research-ai-preview').textContent='未修改任务：'+e.message;}finally{b.disabled=false;}};
      doc.getElementById('research-ai-apply').onclick=async function(){
        if(!proposal)return;this.disabled=true;var ctx=current();
        try{var result=await request('research.apply',{proposalId:proposal.id,expectedRevision:proposal.revision},false,ctx);guard(ctx);if(!result.research)throw Error('服务未返回完整任务状态，请重新同步确认');w.AI_RESEARCH.applyCloud(result.research);proposal=null;this.hidden=true;doc.getElementById('research-ai-preview').textContent='已应用，其他已连接设备联网后同步。任务完成状态不代表实验验收通过。';await sync();guard(ctx);}
        catch(e){if(!e.stale)doc.getElementById('research-ai-preview').textContent='未确认应用：'+e.message;}finally{this.disabled=false;}
      };
      doc.getElementById('research-ai-undo').onclick=async function(){
        this.disabled=true;var ctx=current();
        try{var cloud=w.AI_RESEARCH.state().cloud,result=await request('research.undo',{expectedRevision:cloud?cloud.revision:'0'},false,ctx);guard(ctx);if(!result.research)throw Error('服务未返回完整任务状态，请重新同步确认');w.AI_RESEARCH.applyCloud(result.research);doc.getElementById('research-ai-preview').textContent='已撤销，其他已连接设备联网后同步。';await sync();guard(ctx);}
        catch(e){if(!e.stale)doc.getElementById('research-ai-preview').textContent='未确认撤销：'+e.message;}finally{this.disabled=false;}
      };
      if(current().token){importLegacy();sync();}else status('本机模式；连接设备后可同步收藏、已读和已看。');
    }
    w.AI_CLOUD={change:change,sync:sync,open:open,isConnected:function(){return connected&&!!current().token;}};
    if(doc.readyState==='loading')doc.addEventListener('DOMContentLoaded',init);else init();w.addEventListener('online',sync);w.addEventListener('focus',function(){if(current().token)sync();});w.addEventListener('storage',function(e){if(e.key===AUTH||e.key===null){var before=auth.generation;current();if(before!==auth.generation){if(w.AI_RESEARCH)w.AI_RESEARCH.clearCloud();doc.getElementById('cloud-connection').hidden=!!auth.token;doc.getElementById('cloud-connected').hidden=!auth.token;if(auth.token)sync();else status('此设备已断开；本机阅读记录仍保留。');}}else if(e.key&&e.key.startsWith(EVENT)&&current().token)sync();});w.setInterval(function(){if(current().token&&!doc.hidden)sync();},60000);
  }
  return{fieldKey:fieldKey,validRow:validRow,safeMetadata:safeMetadata,mount:mount};
});
