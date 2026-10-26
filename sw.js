/* Same-origin published snapshots only. No private sites, external API or images. */
const CACHE='luohao-workspace-20261026-v2';
const ROOT=new URL('./',self.location.href).href;
const FILES=['./','./research-data.json','./research-details.json','./manifest.webmanifest','./workspace-icon.svg'].map(x=>new URL(x,ROOT).href);
self.addEventListener('install',event=>{event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(FILES)).then(()=>self.skipWaiting()));});
self.addEventListener('activate',event=>{event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('luohao-workspace-')&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));});
self.addEventListener('fetch',event=>{
  const request=event.request,url=new URL(request.url);
  if(request.method!=='GET'||url.origin!==self.location.origin)return;
  const canonical=new URL(url.pathname,ROOT).href;
  const navigation=request.mode==='navigate'&&(canonical===ROOT||canonical===new URL('index.html',ROOT).href);
  if(!navigation&&!FILES.includes(canonical))return;
  const key=navigation?ROOT:canonical;
  event.respondWith((async()=>{const cache=await caches.open(CACHE);async function fallback(){const saved=await cache.match(key);if(!saved)return null;const headers=new Headers(saved.headers);headers.set('X-Workspace-Snapshot','saved');return new Response(saved.body,{status:saved.status,statusText:saved.statusText,headers});}try{const response=await fetch(request);if(response.ok)await cache.put(key,response.clone());else if(response.status>=500){const saved=await fallback();if(saved)return saved;}return response;}catch(error){const saved=await fallback();if(saved)return saved;throw error;}})());
});
