const api=require('./reading.js');
module.exports=async function({html,ok}){
  const pubs=[{id:'official',name:'官方期刊',hosts:['official.example']}];
  const data=[{id:'magazines:https://official.example/new',kind:'magazines',url:'https://official.example/new',title:'新文章'},
    {id:'ted:https://www.ted.com/talks/example',kind:'ted',url:'https://www.ted.com/talks/example',title:'演讲标题'}];
  const mags=[{url:'https://official.example/old',fav:true,read:true,at:3,article:{publication:'official',title:'原来保存的标题',publishedAt:'2026-10-01',summary:'保存的独立导读'}},
    {url:'https://official.example/unknown/2026-10-30',fav:true,at:0},
    {url:'https://evil.example/fake',read:true,article:{title:'假文章'}}, {url:'javascript:alert(1)',fav:true}];
  const learning=[{kind:'ted',url:data[1].url,title:'旧标题',fav:true,done:false,at:2},
    {kind:'forum',url:'https://www.bilibili.com/video/BV1xx411c7mD',title:'滚出列表的旧视频',done:true,at:1}];
  const opened=[{kind:'ted',url:data[1].url,title:'演讲标题',openURL:'https://www.youtube.com/watch?v=example',openedAt:10},
    {kind:'magazines',url:mags[0].url,title:'原来保存的标题',openedAt:20},
    {kind:'ted',url:'https://user:secret@example.org',openedAt:30}];
  const before=JSON.stringify({data,mags,learning,opened}),rows=api.collect(data,mags,learning,opened,pubs);
  ok(rows.length===4&&JSON.stringify({data,mags,learning,opened})===before,'阅读中心合并旧收藏、完成和打开记录，不改源数据、不丢移出列表的视频和文章');
  const old=rows.find(r=>r.url===mags[0].url),legacy=rows.find(r=>r.url===mags[1].url);
  ok(old.archived&&old.title==='原来保存的标题'&&old.publishedAt==='2026-10-01'&&old.summary==='保存的独立导读'&&!legacy.publishedAt&&legacy.title.includes('标题未保存'),'归档保留原元数据；只有URL的旧记录不从路径猜标题或日期');
  ok(api.select(rows,'continue','all','').length===1&&api.select(rows,'continue','ted','演讲')[0].openURL.includes('youtube.com')&&!rows.find(r=>r.kind==='ted').done,'继续阅读只收明确打开且未完成的内容，保留实际打开入口，不自动标已看或伪造播放位置');
  ok(api.select(rows,'fav','magazines','官方期刊 原来').length===1&&api.select(rows,'done','all','').length===2&&api.select(rows,'all','all','不存在').length===0,'统一记录的状态、栏目、多词搜索组合筛选实际生效');
  ok(['javascript:alert(1)','https://u:p@example.org/','https://example.org/ bad','https://example.org\\@evil.org'].every(x=>!api.safeURL(x))&&api.safeURL('https://example.org/a?x=1&y=2'),'阅读记录拒绝危险协议、凭据和畸形URL，保留合法原文');
  const catalog=api.catalog({MAGAZINES:pubs,MAGAZINE_ARTICLES:[],TED:[],FORUM_SERIES:[{who:'甲',vids:[{bvid:'BV1xx411c7mD',t:'视频'}]},{who:'乙',vids:[{bvid:'BV1xx411c7mD',t:'视频'}]}]});
  ok(catalog.length===1,'重复归入多个讲坛系列的视频在我的阅读只保留一份稳定身份');
  function fixture(blocked=false){
    const storage={'ai-magazine-reading-v1':JSON.stringify(mags.slice(0,2)),'ai-learning-v1':JSON.stringify(learning),'ai-reading-opened-v1':JSON.stringify(opened),'ai-workspace-opened-v1':JSON.stringify({route:'ted',url:opened[0].openURL,title:'演讲标题',at:10})},events={},windowEvents={},docEvents={},changes=[];
    function element(id){return {id,value:id==='reading-kind'?'all':'',textContent:'',innerHTML:'',hidden:false,addEventListener(t,f){(events[id]||={})[t]=f;},querySelectorAll(){return[];},focus(){this.focused=true;}};}
    const elements={};const doc={getElementById(id){return elements[id]||=(element(id));},querySelectorAll(){return[];},addEventListener(t,f){(docEvents[t]||=[]).push(f);}};
    const w={MAGAZINES:pubs,MAGAZINE_ARTICLES:[],TED:[{url:data[1].url,en:'演讲标题'}],FORUM_SERIES:[],
      localStorage:{getItem(k){return storage[k]??null;},setItem(k,v){if(blocked)throw Error('quota');storage[k]=v;}},
      AI_CLOUD:{change(...args){changes.push(args);}},CustomEvent:class{constructor(type,options){this.type=type;Object.assign(this,options);}},
      addEventListener(t,f){(windowEvents[t]||=[]).push(f);},dispatchEvent(e){(windowEvents[e.type]||[]).forEach(f=>f(e));}};
    const original=JSON.stringify(storage),app=api.mount(w,doc);
    function action(id,name){const attrs={'data-reading-id':id,'data-reading-action':name};events['view-library'].click({target:{closest(){return {getAttribute(k){return attrs[k];},hasAttribute(k){return k in attrs;}};}}});}
    return{storage,original,app,changes,events,elements,w,action};
  }
  const f=fixture();
  ok(JSON.stringify(f.storage)===f.original&&f.app.records().length===4&&f.elements['reading-list'].innerHTML.includes('原来保存的标题')&&f.elements['reading-list'].innerHTML.includes('滚出列表的旧视频'),'打开阅读中心直接识别旧记录，不重写收藏；旧最近打开与新备用观看入口不重复归档');
  const id='ted:'+data[1].url;f.action(id,'done');
  ok(f.app.isDone('ted',data[1].url)&&f.changes.length===1&&f.changes[0][0]==='learning'&&f.changes[0][1]===id&&f.changes[0][2]==='done'&&f.changes[0][3]===true,'在阅读中心标已看复用原learning身份和云change，不另建数据库或新同步命名空间');
  f.action('magazines:'+mags[0].url,'fav');
  ok(f.changes[1][0]==='magazine'&&f.changes[1][1]===mags[0].url&&f.changes[1][2]==='fav'&&f.changes[1][3]===false&&JSON.parse(f.storage['ai-magazine-reading-v1'])[0].read,'取消收藏只改fav，保持已读与原文章快照，两个标记相互独立');
  const remote=JSON.parse(f.storage['ai-learning-v1']);remote[0].done=false;f.storage['ai-learning-v1']=JSON.stringify(remote);f.w.dispatchEvent({type:'storage',key:'ai-learning-v1'});
  ok(!f.app.isDone('ted',data[1].url)&&f.elements['reading-list'].innerHTML.includes('打开过 · 未标完成')&&f.changes.length===2,'原云同步或另一标签页改变记录后刷新中心，读取事件不会反向制造云写入');
  const denied=fixture(true);denied.action(id,'done');
  ok(denied.app.isDone('ted',data[1].url)&&denied.changes.length===0&&denied.elements['reading-storage-note'].textContent.includes('仅本次有效'),'存储配额失败时本次标记留在内存，明确提示未持久保存，不冒称已上传');
  ok(html.includes('id="view-library"')&&html.includes('data-go="library"')&&!html.includes('<script src="reading.js"></script>')&&html.includes('unseenDefault:true')&&html.includes('unreadDefault:true'),'我的阅读有原生路由和手机入口；默认未看规则可迁移旧默认并保留后续明确选择，代码完整内联');
};
