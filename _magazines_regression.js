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
  ok(pubs.length===6&&['商界','三联生活周刊','第一财经','博客天下','人物','环球人物'].every(n=>pubs.some(p=>p.name===n)),'期刊架完整覆盖六本指定刊物，并使用已核实的正式刊名');
  ok(new Set(pubs.map(p=>p.id)).size===pubs.length,'期刊身份无重复');
  ok(articles.length>=17&&new Set(articles.map(a=>a.url)).size===articles.length,'已核实期刊文章不少于17篇且URL无重复');
  ok(pubs.every(p=>/^https:\/\//.test(p.url)&&p.hosts.includes(new URL(p.url).hostname))&&articles.every(a=>pubs.find(p=>p.id===a.publication)?.hosts.includes(new URL(a.url).hostname)),'期刊与原文链接均属于各自已确认官方渠道');
  const original=['a','b'].flatMap(s=>JSON.parse(fs.readFileSync(path.join(__dirname,'_magazines_sources_'+s+'.json'),'utf8')).magazines.flatMap(p=>p.articles.map(a=>({publication:p.id,title:a.title,url:a.url,publishedAt:a.date??null}))));
  let refreshed=[];const reportFile=path.join(__dirname,'_magazines_refresh.json');
  if(fs.existsSync(reportFile)){const report=JSON.parse(fs.readFileSync(reportFile,'utf8'));refreshed=(report.sources||[]).flatMap(s=>(s.articles||[]).concat(s.retainedArticles||[]).map(a=>({...a,publication:s.publication})));}
  ok(articles.every(a=>original.concat(refreshed).some(e=>e.publication===a.publication&&e.url===a.url&&e.title===a.title&&(e.publishedAt??null)===(a.publishedAt??null))),'每篇标题、原文和发布日期均能对上初始官方核实或最近成功刷新证据');
  const date=s=>typeof s==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(s)&&!isNaN(Date.parse(s))&&new Date(s+'T00:00:00Z').toISOString().slice(0,10)===s;
  const today=new Date().toLocaleDateString('en-CA',{timeZone:'Asia/Shanghai'});
  ok(date(w.MAGAZINES_CHECKED)&&w.MAGAZINES_CHECKED<=today&&(Date.parse(today)-Date.parse(w.MAGAZINES_CHECKED))/86400000<=2,'期刊最近核查日期真实有效且不超过2天，不冒充文章发布日期');
  ok(pubs.every(p=>p.checkedAt===w.MAGAZINES_CHECKED&&['ok','unavailable'].includes(p.status)),'每本刊物有当次核查日期及明确结果状态');
  ok(articles.every(a=>(a.publishedAt===null||date(a.publishedAt)&&a.publishedAt<=today)&&date(a.checkedAt)&&a.checkedAt<=w.MAGAZINES_CHECKED),'期刊文章无非法或未来日期，未披露单篇日期明确留空');
  ok(articles.filter(a=>a.publication==='lifeweek'&&original.some(o=>o.url===a.url)).every(a=>a.publishedAt===null),'三联已核实条目不把期刊出版日冒充单篇发布日期');
  if(articles.length>18)base.events['magazine-more'].click();
  ok(base.elements['magazine-list'].innerHTML.includes('原文未标日期')&&base.elements['magazine-publishers'].innerHTML.includes('官方阅读'),'未披露日期与官方阅读入口均实际渲染');
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
  const escaped=run('window.MAGAZINE_ARTICLES=[{publication:"renwu",title:"<img src=x onerror=alert(1)>",url:"https://boyamedia.com/sys-nd/test.html",summary:"<script>bad</scr"+"ipt>",publishedAt:null}];');
  ok(escaped.elements['magazine-list'].innerHTML.includes('&lt;img')&&!escaped.elements['magazine-list'].innerHTML.includes('<img')&&!escaped.elements['magazine-list'].innerHTML.includes('<script>'),'期刊标题与导读统一转义，不能注入HTML');
  const bad=run('window.MAGAZINE_ARTICLES=[null,{publication:"unknown",title:"bad",url:"https://boyamedia.com/a"},{publication:"renwu",title:"bad",url:"javascript:alert(1)"},{publication:"renwu",title:"bad",url:"https://boyamedia.com.evil.test/a"}];');
  ok(bad.elements['magazine-list'].innerHTML.includes('暂不可用')&&!bad.elements['magazine-list'].innerHTML.includes('href='),'未知刊物、危险协议及伪子域被拦截，空数据仍可浏览刊物入口');
  ok(!!run('window.MAGAZINES=null;window.MAGAZINE_ARTICLES=null;').elements['magazine-list'].innerHTML,'期刊数据缺失不阻断页面脚本');
  const broken=run('',{'ai-magazine-reading-v1':'[null,{},false]','ai-magazine-filters':'{"publication":"bad","mode":null}'});
  ok(broken.elements['magazine-count'].textContent.includes('17')||broken.elements['magazine-list'].innerHTML.includes('mag-article'),'损坏阅读记录和失效筛选值安全回退');
  const blocked=run('',{},true);blocked.events['view-magazines'].click({target:{closest(){return {dataset:{magAction:'fav',magUrl:url}};}}});
  ok(blocked.elements['magazine-storage-note'].textContent.includes('仅在当前页面有效'),'浏览器禁止存储时如实提示，仍可本页操作');
};
