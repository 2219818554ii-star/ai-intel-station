/* One reading shelf over the existing magazine/learning records. No private data in the build. */
(function(root,factory){
  var api=factory();if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&root.document)root.AI_READING=api.mount(root,root.document);
})(typeof window==='undefined'?null:window,function(){
  'use strict';
  var KEYS={magazine:'ai-magazine-reading-v1',learning:'ai-learning-v1',opened:'ai-reading-opened-v1'};
  var LABELS={magazines:'期刊文章',ted:'TED',forum:'成长讲坛',learn:'AI 学习'};
  function array(x){return Array.isArray(x)?x.filter(function(r){return r&&typeof r==='object'&&!Array.isArray(r);}):[];}
  function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
  function safeURL(s){try{var u=new URL(s);return typeof s==='string'&&s.length<=2100&&!/[\s<>"'\\]/.test(s)&&!u.username&&!u.password&&['http:','https:'].includes(u.protocol)?s:'';}catch(e){return '';}}
  function stamp(n){return Number.isFinite(n)&&n>0?n:0;}
  function catalog(w,doc){
    var rows=[],seen=new Set(),pubs=array(w.MAGAZINES);
    function add(kind,url,title,extra){if(!safeURL(url)||!title||seen.has(kind+':'+url))return;seen.add(kind+':'+url);rows.push(Object.assign({id:kind+':'+url,kind:kind,url:url,title:String(title).slice(0,600)},extra||{}));}
    array(w.MAGAZINE_ARTICLES).forEach(function(a){var p=pubs.find(function(p){return p.id===a.publication;});if(p)add('magazines',a.url,a.title,{publication:p.id,source:p.name,publishedAt:a.publishedAt,summary:a.summary,article:{publication:p.id,title:a.title,publishedAt:a.publishedAt,summary:a.summary}});});
    array(w.TED).forEach(function(t){add('ted',t.url,t.en||t.zh,{source:t.sp});});
    array(w.FORUM_SERIES).forEach(function(s){array(s.vids).forEach(function(v){if(/^BV[0-9A-Za-z]{10}$/.test(v.bvid||''))add('forum','https://www.bilibili.com/video/'+v.bvid,v.t,{source:s.who});});});
    if(doc&&doc.querySelectorAll)Array.from(doc.querySelectorAll('#view-learn .rsrc-item')).forEach(function(card){var a=card.querySelector('a.rsrc');if(a)add('learn',a.href,a.textContent.trim());});
    return rows;
  }
  function collect(data,magazines,learning,opened,pubs){
    var map=new Map(data.map(function(r){return[r.id,Object.assign({},r,{fav:false,done:false,at:0,openedAt:0})];}));
    function row(kind,url,title){var id=kind+':'+url;if(!LABELS[kind]||!safeURL(url))return null;
      if(kind==='magazines'){var u=new URL(url);if(u.protocol!=='https:'||!array(pubs).some(function(p){return Array.isArray(p.hosts)&&p.hosts.includes(u.hostname.toLowerCase());}))return null;}
      if(!map.has(id))map.set(id,{id:id,kind:kind,url:url,title:String(title||'旧记录（标题未保存）').slice(0,600),fav:false,done:false,at:0,openedAt:0,archived:true});
      return map.get(id);
    }
    array(magazines).forEach(function(r){var item=row('magazines',r.url,r.article&&r.article.title);if(!item)return;item.fav=r.fav===true;item.done=r.read===true;item.at=stamp(r.at);if(item.archived&&r.article){item.article=r.article;item.summary=typeof r.article.summary==='string'?r.article.summary:'';item.publishedAt=r.article.publishedAt;item.publication=r.article.publication;var p=array(pubs).find(function(p){return p.id===item.publication;});if(p)item.source=p.name;}});
    array(learning).forEach(function(r){var item=row(r.kind,r.url,r.title);if(!item)return;item.fav=r.fav===true;item.done=r.done===true;item.at=stamp(r.at);});
    array(opened).forEach(function(r){var item=row(r.kind,r.url,r.title);if(!item||!stamp(r.openedAt))return;if(r.openedAt>=item.openedAt){item.openedAt=r.openedAt;item.openURL=safeURL(r.openURL)||item.url;}});
    return Array.from(map.values()).filter(function(r){return r.fav||r.done||r.openedAt;}).sort(function(a,b){return Math.max(b.at,b.openedAt)-Math.max(a.at,a.openedAt)||a.title.localeCompare(b.title);});
  }
  function select(rows,mode,kind,query){var terms=String(query||'').toLowerCase().trim().split(/\s+/).filter(Boolean);return rows.filter(function(r){return(kind==='all'||r.kind===kind)&&(mode==='all'||mode==='fav'&&r.fav||mode==='done'&&r.done||mode==='continue'&&r.openedAt>0&&!r.done)&&terms.every(function(t){return[r.title,r.source,r.summary].join(' ').toLowerCase().includes(t);});}).sort(function(a,b){return mode==='continue'?b.openedAt-a.openedAt:Math.max(b.at,b.openedAt)-Math.max(a.at,a.openedAt);});}
  function mount(w,doc){
    var root=doc.getElementById('view-library');if(!root)return null;
    var list=doc.getElementById('reading-list'),query=doc.getElementById('reading-query'),kind=doc.getElementById('reading-kind'),more=doc.getElementById('reading-more'),notice=doc.getElementById('reading-storage-note');
    var memory={},volatile=new Set(),problem=false,saved=w.AI_SESSION?w.AI_SESSION.read('ai-reading-shelf'):{},mode=['all','continue','fav','done'].includes(saved.mode)?saved.mode:'all',limit=Number.isInteger(saved.limit)&&saved.limit>=24&&saved.limit<=5000?saved.limit:24,visible=[],data=catalog(w,doc);
    query.value=typeof saved.query==='string'?saved.query.slice(0,200):'';kind.value=LABELS[saved.kind]?saved.kind:'all';
    function read(key){if(volatile.has(key))return memory[key]||[];try{var raw=w.localStorage.getItem(key);return raw===null?(memory[key]||[]):JSON.parse(raw);}catch(e){problem=true;return memory[key]||[];}}
    function write(key,rows){memory[key]=rows;try{w.localStorage.setItem(key,JSON.stringify(rows));volatile.delete(key);return true;}catch(e){problem=true;volatile.add(key);return false;}}
    function opened(){var rows=array(read(KEYS.opened)),legacy;try{legacy=JSON.parse(w.localStorage.getItem('ai-workspace-opened-v1')||'null');}catch(e){}
      if(legacy&&LABELS[legacy.route]&&stamp(legacy.at)&&safeURL(legacy.url)&&!rows.some(function(r){return r.kind===legacy.route&&(r.url===legacy.url||r.openURL===legacy.url);}))rows.push({kind:legacy.route,url:legacy.url,title:legacy.title,openedAt:legacy.at});return rows;
    }
    function records(){return collect(data,read(KEYS.magazine),read(KEYS.learning),opened(),w.MAGAZINES);}
    function notify(key){if(w.dispatchEvent&&w.CustomEvent)w.dispatchEvent(new w.CustomEvent('reading-records-changed',{detail:{key:key}}));}
    function seen(kind,url){var rows=array(read(kind==='magazines'?KEYS.magazine:KEYS.learning));return rows.some(function(r){return r.url===url&&(kind==='magazines'||r.kind===kind)&&(kind==='magazines'?r.read===true:r.done===true);});}
    function toggle(id,action){
      var item=records().find(function(r){return r.id===id;});if(!item||!['fav','done'].includes(action))return false;
      var mag=item.kind==='magazines',key=mag?KEYS.magazine:KEYS.learning,rows=array(read(key)),row=rows.find(function(r){return r.url===item.url&&(mag||r.kind===item.kind);});
      if(!row){row=mag?{url:item.url,fav:false,read:false}:{kind:item.kind,url:item.url,title:item.title,fav:false,done:false};rows.push(row);}
      var field=action==='done'&&mag?'read':action;row[field]=!item[action];row.at=Date.now();if(mag&&item.article)row.article=item.article;
      var saved=write(key,rows);if(saved&&w.AI_CLOUD)w.AI_CLOUD.change(mag?'magazine':'learning',mag?item.url:item.kind+':'+item.url,field,row[field],row);notify(key);return true;
    }
    function remember(item,href){
      if(!item||!safeURL(item.url)||!safeURL(href))return;
      var rows=opened().filter(function(r){return !(r.kind===item.kind&&r.url===item.url);});rows.unshift({kind:item.kind,url:item.url,title:item.title,openURL:href,openedAt:Date.now()});write(KEYS.opened,rows.slice(0,200));render();
    }
    function render(){
      if(w.AI_SESSION)w.AI_SESSION.write('ai-reading-shelf',{mode:mode,kind:kind.value,query:query.value.slice(0,200),limit:limit});
      var rows=records();visible=select(rows,mode,kind.value||'all',query.value);
      Array.from(root.querySelectorAll('[data-reading-mode]')).forEach(function(b){var m=b.getAttribute('data-reading-mode'),n=select(rows,m,'all','').length;b.setAttribute('aria-pressed',String(m===mode));b.textContent=({all:'全部记录',continue:'继续阅读',fav:'我的收藏',done:'已读 / 已看'})[m]+' · '+n;});
      doc.getElementById('reading-count').textContent='共 '+visible.length+' 项 · 已显示 '+Math.min(limit,visible.length)+' 项';
      list.innerHTML=visible.slice(0,limit).map(function(r){var doneLabel=r.kind==='magazines'?'已读':'已看';return '<article class="reading-item" data-reading-id="'+esc(r.id)+'"><div class="reading-item-meta"><span>'+esc(LABELS[r.kind])+(r.source?' · '+esc(r.source):'')+'</span><span>'+(r.done?doneLabel:(r.openedAt?'打开过 · 未标完成':'未标完成'))+(r.fav?' · 已收藏':'')+'</span></div><h3><a href="'+esc(r.openURL||r.url)+'" data-reading-open="'+esc(r.id)+'" target="_blank" rel="noopener noreferrer">'+esc(r.title)+'</a></h3>'+(r.archived?'<p class="reading-archive">已移出当前列表，保留原入口；原文信息可能变化。</p>':'')+(r.summary?'<p class="reading-summary">'+esc(r.summary)+'</p>':'')+'<div class="reading-actions"><a class="top-btn" href="'+esc(r.openURL||r.url)+'" data-reading-open="'+esc(r.id)+'" target="_blank" rel="noopener noreferrer">'+(r.done?'再看一次 ↗':r.openedAt?'继续打开 ↗':'打开原文 ↗')+'</a><button type="button" class="top-btn" data-reading-action="fav" data-reading-id="'+esc(r.id)+'" aria-label="'+(r.fav?'取消收藏：':'收藏：')+esc(r.title)+'" aria-pressed="'+r.fav+'">'+(r.fav?'已收藏':'收藏')+'</button><button type="button" class="top-btn" data-reading-action="done" data-reading-id="'+esc(r.id)+'" aria-label="'+(r.done?'标为未完成：':'标为'+doneLabel+'：')+esc(r.title)+'" aria-pressed="'+r.done+'">'+(r.done?doneLabel+' ✓':'标记'+doneLabel)+'</button></div></article>';}).join('')||'<div class="reading-empty"><p>'+(rows.length?'这个筛选下没有记录，可以切换其他状态。':'还没有阅读记录。在期刊、TED、讲坛或AI学习中收藏、标记完成或打开内容，就会汇集在这里。')+'</p><button type="button" class="top-btn" data-go="magazines">找一篇文章</button> <button type="button" class="top-btn" data-go="ted">挑一个视频</button></div>';
      more.hidden=visible.length<=limit;
      notice.textContent=problem?'浏览器暂时无法保存，新的操作仅本次有效。请保留当前页面。':'收藏、已读和已看沿用原记录，连接设备后可同步；最近打开保存在这台设备。外站的阅读位置和播放进度以原站为准。';
    }
    root.addEventListener('click',function(e){var b=e.target.closest&&e.target.closest('[data-reading-mode],[data-reading-action]');if(!b)return;
      if(b.hasAttribute('data-reading-mode')){mode=b.getAttribute('data-reading-mode');limit=24;render();return;}
      var id=b.getAttribute('data-reading-id'),action=b.getAttribute('data-reading-action'),before=visible.findIndex(function(r){return r.id===id;});
      if(toggle(id,action)){render();var buttons=Array.from(list.querySelectorAll('[data-reading-action="'+action+'"]')),focus=buttons.find(function(x){return x.getAttribute('data-reading-id')===id;})||buttons[Math.min(Math.max(before,0),buttons.length-1)]||doc.getElementById('reading-heading');if(focus)focus.focus({preventScroll:true});}
    });
    query.addEventListener('input',function(){limit=24;render();});kind.addEventListener('change',function(){limit=24;render();});
    more.addEventListener('click',function(){var before=limit;limit+=24;render();var a=list.querySelectorAll('h3 a')[before];if(a)a.focus();});
    doc.getElementById('reading-reset').addEventListener('click',function(){mode='all';query.value='';kind.value='all';limit=24;render();});
    doc.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[href]');if(!a||!safeURL(a.href))return;
      var id=a.getAttribute('data-reading-open'),item=id&&(records().find(function(r){return r.id===id;})||data.find(function(r){return r.id===id;}));
      if(!item){var view=a.closest('#view-magazines,#view-ted,#view-forum,#view-learn');if(!view)return;var card=a.closest('article,.rsrc-item');if(!card)return;var canonical=card.querySelector(view.id==='view-magazines'?'h4 a':view.id==='view-learn'?'a.rsrc':view.id==='view-ted'?'a.top-btn':"a[href*='bilibili.com/video/']");if(!canonical)return;item=data.find(function(r){return r.kind===view.id.slice(5)&&r.url===canonical.href;});}
      if(item)remember(item,a.href);
    });
    w.addEventListener('storage',function(e){if(e.key===null||Object.values(KEYS).includes(e.key)||e.key==='ai-workspace-opened-v1')render();});
    w.addEventListener('reading-records-changed',render);
    w.addEventListener('workspace:route',function(e){if(e.detail&&e.detail.tab==='library')render();});
    render();return{records:records,isDone:seen,notify:notify,render:render};
  }
  return{catalog:catalog,collect:collect,select:select,safeURL:safeURL,mount:mount};
});
