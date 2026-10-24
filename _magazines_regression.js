const fs=require('fs'),path=require('path'),vm=require('vm');
module.exports=async function({inline,sandbox,ok}){
  function run(inject='',saved={},blocked=false){
    const elements={},events={};
    function el(id){return elements[id]||=( {id,innerHTML:'',textContent:'',value:'',style:{},dataset:{},classList:{add(){},remove(){},toggle(){}},setAttribute(){},getAttribute(){return null;},addEventListener(t,fn){(events[id]||={})[t]=fn;},querySelector(){return null;},querySelectorAll(){return [];},appendChild(){},focus(){}} );}
    const ctx={...sandbox,document:{...sandbox.document,getElementById:el},window:{...sandbox.window,sessionStorage:{getItem(k){return saved[k]||null;},setItem(k,v){saved[k]=v;}},localStorage:{getItem(k){if(blocked)throw Error('storage blocked');return saved[k]||null;},setItem(k,v){if(blocked)throw Error('storage blocked');saved[k]=v;}}}};
    vm.createContext(ctx);vm.runInContext(inline.replace('  var root=document.getElementById("view-magazines");',inject+'\n  var root=document.getElementById("view-magazines");'),ctx);
    return {ctx,elements,events,saved};
  }
  const base=run(),w=base.ctx.window,pubs=w.MAGAZINES,articles=w.MAGAZINE_ARTICLES;
  ok(pubs.length>=19&&['商界','三联生活周刊','第一财经','博客天下','人物','环球人物'].every(n=>pubs.some(p=>p.name===n)),'期刊扩展到至少19本，完整保留原六本指定刊物');
  const baseline=JSON.parse(fs.readFileSync(path.join(__dirname,'_magazines_catalog_baseline.json'),'utf8'));
  ok(baseline.publications.every(p=>pubs.some(x=>x.id===p.id&&x.name===p.name&&x.url===p.url&&JSON.stringify(x.hosts)===JSON.stringify(p.hosts))&&articles.filter(a=>a.publication===p.id).length>=p.minimumArticles),'全部已核实刊物身份和各刊文章基础量未回退');
  ok(new Set(pubs.map(p=>p.id)).size===pubs.length,'期刊身份无重复');
  ok(articles.length>=17&&new Set(articles.map(a=>a.url)).size===articles.length,'已核实期刊文章不少于17篇且URL无重复');
  ok(pubs.every(p=>/^https:\/\//.test(p.url)&&p.hosts.includes(new URL(p.url).hostname))&&articles.every(a=>pubs.find(p=>p.id===a.publication)?.hosts.includes(new URL(a.url).hostname)),'期刊与原文链接均属于各自已确认官方渠道');
  const evidenceFiles=['_magazines_sources_a.json','_magazines_sources_b.json','_magazines_expansion_cn.json','_magazines_expansion_world.json'];
  const sourceData=evidenceFiles.map(f=>JSON.parse(fs.readFileSync(path.join(__dirname,f),'utf8')));
  const original=sourceData.flatMap(d=>d.magazines.flatMap(p=>p.articles.map(a=>({...a,publication:p.id,publishedAt:a.publishedAt??a.date??null}))));
  let refreshed=[];const reportFile=path.join(__dirname,'_magazines_refresh.json');
  if(fs.existsSync(reportFile)){const report=JSON.parse(fs.readFileSync(reportFile,'utf8'));refreshed=(report.sources||[]).flatMap(s=>(s.articles||[]).concat(s.retainedArticles||[]).map(a=>({...a,publication:s.publication})));}
  ok(articles.every(a=>original.concat(refreshed).some(e=>e.publication===a.publication&&e.url===a.url&&e.title===a.title&&(e.publishedAt??null)===(a.publishedAt??null))),'每篇标题、原文和发布日期均能对上初始官方核实或最近成功刷新证据');
  const hotProof=original.concat(refreshed);
  for(const d of sourceData)for(const h of (d.hotLists||[]).concat(d.magazines.flatMap(p=>p.hotLists||[]))){if(Array.isArray(h.items))h.items.forEach(a=>hotProof.push({...a,publication:h.publication,hotRank:a.rank,hotSource:h.sourceUrl,hotCheckedAt:h.asOf}));}
  const hot=articles.filter(a=>a.hotRank),editorial=JSON.parse(fs.readFileSync(path.join(__dirname,'_magazines_editorial.json'),'utf8')).articles;
  ok(['infzm','quanta','sciencenews'].every(p=>hot.some(a=>a.publication===p))&&hot.every(a=>hotProof.some(e=>e.publication===a.publication&&e.url===a.url&&e.hotRank===a.hotRank&&e.hotSource===a.hotSource&&e.hotCheckedAt===a.hotCheckedAt)),'三份官方热榜均有真实条目，排名/来源/核查日期逐条可追溯（条数服从原榜）');
  ok(articles.filter(a=>a.featuredReason).length>=20&&articles.filter(a=>a.featuredReason).every(a=>editorial.some(e=>e.publication===a.publication&&e.url===a.url&&e.title===a.title&&e.reason===a.featuredReason&&e.priority===a.featuredPriority)),'本站精选逐篇具备明确选读理由与独立配置，不冒充官方热度');
  const date=s=>typeof s==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(s)&&!isNaN(Date.parse(s))&&new Date(s+'T00:00:00Z').toISOString().slice(0,10)===s;
  const today=new Date().toLocaleDateString('en-CA',{timeZone:'Asia/Shanghai'});
  ok(date(w.MAGAZINES_CHECKED)&&w.MAGAZINES_CHECKED<=today&&(Date.parse(today)-Date.parse(w.MAGAZINES_CHECKED))/86400000<=2,'期刊最近核查日期真实有效且不超过2天，不冒充文章发布日期');
  ok(pubs.every(p=>p.checkedAt===w.MAGAZINES_CHECKED&&['ok','unavailable'].includes(p.status)),'每本刊物有当次核查日期及明确结果状态');
  ok(articles.every(a=>(a.publishedAt===null||date(a.publishedAt)&&a.publishedAt<=today)&&date(a.checkedAt)&&a.checkedAt<=w.MAGAZINES_CHECKED),'期刊文章无非法或未来日期，未披露单篇日期明确留空');
  ok(articles.filter(a=>a.publication==='lifeweek'&&original.some(o=>o.url===a.url)).every(a=>a.publishedAt===null),'三联已核实条目不把期刊出版日冒充单篇发布日期');
  base.elements['magazine-publication'].value='lifeweek';base.events['magazine-publication'].change();
  ok(base.elements['magazine-list'].innerHTML.includes('原文未标日期')&&base.elements['magazine-publishers'].innerHTML.includes('官方阅读'),'未披露日期与官方阅读入口均实际渲染');
  base.events['magazine-reset'].click();
  if(articles.length>18)base.events['magazine-more'].click();
  const orderedDates=[...base.elements['magazine-list'].innerHTML.matchAll(/<time(?: datetime="([^"]+)")?>/g)].map(m=>m[1]||'');
  ok(orderedDates.every((d,i)=>i===0||orderedDates[i-1]>=d),'期刊文章按明确发布日期倒序，未知日期不伪排序为今天');
  if(articles.length>18)ok((base.elements['magazine-list'].innerHTML.match(/class="mag-article"/g)||[]).length>18,'期刊加载更多实际增加文章而非只改计数');
  base.elements['magazine-query'].value='博客 AI';base.events['magazine-query'].input();
  ok(base.elements['magazine-list'].innerHTML.includes('红果')&&!base.elements['magazine-list'].innerHTML.includes('37万元'),'期刊多词搜索同时匹配刊物与文章导读');
  base.elements['magazine-query'].value='不存在-空列表';base.events['magazine-query'].input();
  ok(base.elements['magazine-list'].innerHTML.includes('重置筛选'),'期刊搜索空态有恢复提示');
  base.events['magazine-reset'].click();
  ok(base.elements['magazine-query'].value===''&&base.elements['magazine-mode'].value==='all'&&base.elements['magazine-category'].value==='all','期刊重置同时恢复所有筛选条件');
  const url=articles[0].url;
  const action=act=>base.events['view-magazines'].click({target:{closest(){return {dataset:{magAction:act,magUrl:url}};}}});
  action('fav');action('read');base.elements['magazine-mode'].value='fav';base.events['magazine-mode'].change();
  ok(base.elements['magazine-list'].innerHTML.includes(articles[0].title)&&base.elements['magazine-count'].textContent.includes('共 1 篇'),'收藏/已读真实存储并支持收藏筛选');
  const reloaded=run('',base.saved);
  ok(reloaded.elements['magazine-mode'].value==='fav'&&reloaded.elements['magazine-list'].innerHTML.includes('已读 ✓'),'重新执行后保留筛选、收藏与已读记录');
  const stored=JSON.parse(base.saved['ai-magazine-reading-v1']).find(x=>x.url===url);
  ok(stored.article.title===articles[0].title&&stored.article.publication===articles[0].publication&&stored.article.publishedAt===articles[0].publishedAt,'期刊收藏保存当时已核实的标题、刊物和单篇日期，供容量滚动后继续阅读');
  const removed=run('window.MAGAZINE_ARTICLES=window.MAGAZINE_ARTICLES.filter(function(a){return a.url!=='+JSON.stringify(url)+';});',{...base.saved});
  ok(removed.elements['magazine-list'].innerHTML.includes(articles[0].title)&&removed.elements['magazine-list'].innerHTML.includes(url)&&removed.elements['magazine-list'].innerHTML.includes('已移出本期列表'),'文章移出当天列表后收藏仍有原文入口，并明确保存信息可能已变化');
  removed.events['magazine-order-hot'].click();
  ok(!removed.elements['magazine-list'].innerHTML.includes('href="'+url+'"'),'历史收藏不借旧快照伪造当前热榜');
  removed.events['magazine-order-featured'].click();
  ok(!removed.elements['magazine-list'].innerHTML.includes('href="'+url+'"'),'历史收藏不凭旧快照冒充本期编辑精选');
  removed.events['magazine-reset'].click();
  ok(!removed.elements['magazine-list'].innerHTML.includes('href="'+url+'"'),'历史收藏不增加当前最新文章数量或回流默认列表');
  const oldURL='https://www.inewsweek.cn/society/2026-10-12/32494.shtml';
  const legacy=run('',{'ai-magazine-reading-v1':JSON.stringify([{url:oldURL,fav:true,read:true,at:1}]),'ai-magazine-filters':'{"mode":"fav"}'});
  const legacyHTML=legacy.elements['magazine-list'].innerHTML;
  ok(legacyHTML.includes('href="'+oldURL+'"')&&legacyHTML.includes('标题未保存')&&legacyHTML.includes('日期未保存')&&!/<time[^>]*datetime=|>2026-10-12<\/time>/.test(legacyHTML),'旧版只有URL的收藏保留官方入口，不从URL猜标题或文章日期');
  legacy.events['view-magazines'].click({target:{closest(){return {dataset:{magAction:'fav',magUrl:oldURL}};}}});
  ok(legacy.elements['magazine-list'].innerHTML.includes('没有匹配')&&!JSON.parse(legacy.saved['ai-magazine-reading-v1']).find(x=>x.url===oldURL).fav,'旧版历史收藏可以正常取消，不产生无法操作的残留卡片');
  const sharedURL='https://boyamedia.com/sys-nd/200.html';
  const shared=run('window.MAGAZINE_ARTICLES=window.MAGAZINE_ARTICLES.filter(function(a){return a.url!=='+JSON.stringify(sharedURL)+';});',{'ai-magazine-reading-v1':JSON.stringify([{url:sharedURL,fav:true,at:1}]),'ai-magazine-filters':'{"mode":"fav"}'});
  ok(shared.elements['magazine-list'].innerHTML.includes('href="'+sharedURL+'"')&&shared.elements['magazine-list'].innerHTML.includes('刊物未保存')&&shared.elements['magazine-list'].innerHTML.includes('日期未保存'),'共用官网域的旧版收藏仍可读，不猜人物或博客天下的具体刊物归属');
  shared.elements['magazine-publication'].value='renwu';shared.events['magazine-publication'].change();
  ok(!shared.elements['magazine-list'].innerHTML.includes('href="'+sharedURL+'"'),'仅有共用域的历史收藏不会被猜归到某一具体刊物筛选');
  const tainted=run('',{'ai-magazine-reading-v1':JSON.stringify([
    {url:'javascript:alert(1)',fav:true},
    {url:'https://www.inewsweek.cn.evil.test/a',fav:true},
    {url:oldURL,fav:true,at:1,article:{publication:'chinanewsweek',title:'<img src=x onerror=alert(1)>',publishedAt:'2099-01-01',summary:'<script>bad</script>',hotRank:1,featuredReason:'伪造精选'}}
  ]),'ai-magazine-filters':'{"mode":"fav"}'});
  ok(tainted.elements['magazine-list'].innerHTML.includes('&lt;img')&&!/<img|<script|javascript:|evil\.test|2099-01-01|伪造精选/.test(tainted.elements['magazine-list'].innerHTML),'本地收藏快照按官方域校验并转义，拒绝未来日期和伪造热榜精选字段');
  const escaped=run('window.MAGAZINE_ARTICLES=[{publication:"renwu",title:"<img src=x onerror=alert(1)>",url:"https://boyamedia.com/sys-nd/test.html",summary:"<script>bad</scr"+"ipt>",publishedAt:null}];');
  ok(escaped.elements['magazine-list'].innerHTML.includes('&lt;img')&&!escaped.elements['magazine-list'].innerHTML.includes('<img')&&!escaped.elements['magazine-list'].innerHTML.includes('<script>'),'期刊标题与导读统一转义，不能注入HTML');
  const bad=run('window.MAGAZINE_ARTICLES=[null,{publication:"unknown",title:"bad",url:"https://boyamedia.com/a"},{publication:"renwu",title:"bad",url:"javascript:alert(1)"},{publication:"renwu",title:"bad",url:"https://boyamedia.com.evil.test/a"}];');
  ok(bad.elements['magazine-list'].innerHTML.includes('暂不可用')&&!bad.elements['magazine-list'].innerHTML.includes('href='),'未知刊物、危险协议及伪子域被拦截，空数据仍可浏览刊物入口');
  ok(!!run('window.MAGAZINES=null;window.MAGAZINE_ARTICLES=null;').elements['magazine-list'].innerHTML,'期刊数据缺失不阻断页面脚本');
  const broken=run('',{'ai-magazine-reading-v1':'[null,{},false]','ai-magazine-filters':'{"publication":"bad","mode":null}'});
  ok(broken.elements['magazine-count'].textContent.includes('17')||broken.elements['magazine-list'].innerHTML.includes('mag-article'),'损坏阅读记录和失效筛选值安全回退');
  const blocked=run('',{},true);blocked.events['view-magazines'].click({target:{closest(){return {dataset:{magAction:'fav',magUrl:url}};}}});
  ok(blocked.elements['magazine-storage-note'].textContent.includes('仅在当前页面有效'),'浏览器禁止存储时如实提示，仍可本页操作');
  base.events['magazine-reset'].click();base.events['magazine-order-hot'].click();
  const hotHTML=base.elements['magazine-list'].innerHTML;
  ok(hotHTML.includes('mag-hot')&&hotHTML.includes('核查')&&!hotHTML.includes('7000家')&&base.elements['magazine-order-note'].textContent.includes('不同刊物分别排名'),'热榜只列有来源名次，展示核查日并声明各刊分别排名');
  base.elements['magazine-publication'].value='shangjie';base.events['magazine-publication'].change();
  ok(base.elements['magazine-list'].innerHTML.includes('没有可核实的官方热榜'),'未公开热榜的刊物给出诚实空态，不造热度');
  base.events['magazine-reset'].click();base.events['magazine-order-featured'].click();
  ok(base.elements['magazine-list'].innerHTML.includes('选读理由')&&base.elements['magazine-order-note'].textContent.includes('不代表原刊热度'),'编辑精选真实筛出有推荐理由文章并标明主观口径');
  const remembered=run('',base.saved);ok(remembered.elements['magazine-heading'].textContent.includes('编辑精选'),'阅读榜单选择重开后恢复');
  base.events['magazine-reset'].click();base.elements['magazine-publication'].value='scientificamerican';base.events['magazine-publication'].change();base.elements['magazine-category'].value='科学新知';base.events['magazine-category'].change();base.elements['magazine-language'].value='en';base.events['magazine-language'].change();
  ok(base.elements['magazine-publication'].value==='scientificamerican'&&base.elements['magazine-list'].innerHTML.includes('英文'),'兼容主题和语言保留所选刊物，不扩大筛选结果');
  base.elements['magazine-language'].value='zh';base.events['magazine-language'].change();
  ok(base.elements['magazine-publication'].value==='all'&&!base.elements['magazine-list'].innerHTML.includes('data-publication="scientificamerican"'),'只在语言不兼容时清除刊物，保留明确筛选条件');
  base.events['magazine-reset'].click();base.events['magazine-more'].click();const loaded=base.elements['magazine-count'].textContent;
  ok(run('',base.saved).elements['magazine-count'].textContent===loaded,'加载更多后的显示数量重开时恢复，长文阅读位置有足够列表高度');
};
