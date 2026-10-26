"""Dated primary-source correction: API aliases are not AA effort snapshots.

CURRENT_OBSERVED and OFFICIAL_FLASH are independent transcriptions from the
official AA current board and DeepSeek API docs read with the web tool today.
They are not generated from rank.js. Transport evidence remains separate.
"""
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parent
DAY='2026-10-27'
NODE='C:/Users/22198/.workbuddy/binaries/node/versions/22.22.2-6/node.exe'
BEIJING=dt.timezone(dt.timedelta(hours=8))
AA='https://artificialanalysis.ai/leaderboards/models'
DOCS='https://api-docs.deepseek.com/'
PRICING='https://api-docs.deepseek.com/quick_start/pricing/'
THINKING='https://api-docs.deepseek.com/guides/thinking_mode/'
CURRENT_OBSERVED=[
 ['Claude Opus 5.5 (max with fallback)',58],['Claude Sonnet 5.5 (max with fallback)',56],
 ['Muse Wonder Full (max)',56],['Kimi K3.1 Pro',55],['Claude Fable 5.1 (max with fallback)',53],
 ['GPT-6 Astra (max)',53],['Gemini 4 Argon (high)',53],['Muse Wonder (max)',52],
 ['GPT-6.1 Sol (max)',52],['Grok 4.7 (xhigh)',46],['MiMo-V2.6-Pro',46],
 ['Qwen3.8 Max (0902)',45],['DeepSeek V4.1 Flash 1017 (max)',45],['GLM-5.3 (max)',45],
 ['Ling 3.1 Flash 1019',44],['Step 5 Preview',44],['Claude Haiku 5.5 (max)',43],['MiniMax-M3.1-Flash',43]
]
OFFICIAL_FLASH={
 'apiModel':'deepseek-flash','servedVersion':'DeepSeek-V4.1-Flash-1017','context':'1M',
 'legacyAliases':['deepseek-v4-flash','deepseek-v4-flash-vision-exp'],
 'legacyModelState':'Original corresponding models retired; aliases now served by Flash 1017 and billed at Flash rates.',
 'usdPerMillionTokens':{'offPeak':{'inputCacheMiss':0.15,'inputCacheHit':0.003,'output':0.6},
                       'peak':{'inputCacheMiss':0.3,'inputCacheHit':0.006,'output':1.2}},
 'defaultThinking':True,'defaultEffort':'high','explicitNonThinking':{'thinking':{'type':'disabled'}},
 'boundary':'AA 45 is the fixed 1017/max evaluation, not a score for every API effort or a benchmark of this workspace JSON task adjustment.'
}

def values(source):
 code='let c={window:{}};require("vm").runInNewContext(require("fs").readFileSync(0,"utf8"),c);console.log(JSON.stringify(c.window))'
 return json.loads(subprocess.check_output([NODE,'-e',code],input=source,text=True,encoding='utf-8'))

def transport(url):
 try:
  proc=subprocess.run(['curl.exe','-L','-sS','--compressed','--max-time','14','-A','Mozilla/5.0','-w','\n@@RESULT@@%{json}',url],capture_output=True,timeout=19)
  body,_,tail=proc.stdout.rpartition(b'\n@@RESULT@@');meta=json.loads(tail.decode()) if tail else {}
  complete=proc.returncode==0 and meta.get('http_code')==200
  text=body.decode('utf-8','replace');clean=re.sub(r'<(script|style)\b[^>]*>[\s\S]*?</\1>','',text,flags=re.I);clean=re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',clean))
  result={'url':url,'finalURL':meta.get('url_effective',url),'httpStatus':meta.get('http_code',0),'curlExit':proc.returncode,'complete':complete,'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest(),'usableText':bool(complete and len(clean)>150 and not re.search(r'just a moment|verify you are human|checking your browser',clean[:1800],re.I)),'error':proc.stderr.decode('utf-8','replace').strip() or None}
 except (subprocess.TimeoutExpired,ValueError) as error:result={'url':url,'complete':False,'usableText':False,'error':str(error)}
 print(json.dumps({'url':url,'complete':result['complete'],'httpStatus':result.get('httpStatus'),'error':result.get('error')},ensure_ascii=False),flush=True)
 return result

def main():
 now=dt.datetime.now(BEIJING);assert now.date().isoformat()==DAY,'A new day requires a new independently dated review.'
 source=(ROOT/'rank.js').read_text(encoding='utf-8');before=values(source);rank=before['RANK']
 observed=dict(CURRENT_OBSERVED);current=[r for r in rank['tables']['aa']['rows'] if '历史值' not in r[0]]
 assert len(current)==18 and all(observed.get(name)==score for name,score in current),'A changed official score needs separate review.'
 assert [r for r in rank['tables']['aa']['rows'] if '历史值'in r[0]]==[['Muse Spark 1.3 (max) · 10/23历史值',48],['Kimi K3 (max) · 10/23历史值',44]]
 targets={m['name']:m for m in rank['models'] if m['name'] in ('DeepSeek V4.1 Flash 1017 (max)','DeepSeek V4.1-Flash')};assert len(targets)==2
 original=json.loads(json.dumps(targets));updated=json.loads(json.dumps(targets))
 updated['DeepSeek V4.1 Flash 1017 (max)']['price']='API每百万token（错峰/高峰）：输入未命中$0.15/$0.30、命中$0.003/$0.006；输出$0.60/$1.20'
 updated['DeepSeek V4.1 Flash 1017 (max)']['note']='10月27日核对DeepSeek官方API：调用名deepseek-flash当前指向V4.1-Flash-1017，1M上下文，支持思考与非思考；默认思考high，也可显式关闭。AA45仍是1017的max档评测，不能套给本站JSON任务调整的非思考调用。需要本人API Key与账户额度；官方文档api-docs.deepseek.com，控制台platform.deepseek.com。价格依峰谷和缓存命中区分，本次未重测TB2.1或专项等级。'
 updated['DeepSeek V4.1-Flash']['price']='旧版历史快照；现行Flash API按量付费，价格见1017卡'
 updated['DeepSeek V4.1-Flash']['note']='本卡保留旧版V4.1 Flash的AA max=39历史值，不代表当前官方API版本。10月27日官方文档说明deepseek-v4-flash与deepseek-v4-flash-vision-exp所对应原型号已退役，兼容请求由V4.1-Flash-1017承接并按Flash价格计费；新接入使用deepseek-flash。旧39分及专项等级保持原记录，不因兼容别名改成45分；原“限时预览”不再作为现行API状态。'
 assert original!=updated,'Do not roll the content date for an unchanged card.'
 urls=[AA,'https://artificialanalysis.ai/changelog',DOCS,PRICING,THINKING,'https://platform.deepseek.com/api_keys']
 with ThreadPoolExecutor(max_workers=4) as pool:network=list(pool.map(transport,urls))
 for name,card in updated.items():
  pattern=r'      \{name:"'+re.escape(name)+r'"[\s\S]*?(?=\n      \{name:)'
  source,count=re.subn(pattern,lambda _: '      '+json.dumps(card,ensure_ascii=False)+',',source,count=1)
  assert count==1,('Card mutation must match exactly once',name)
 source=source.replace('2项10/23历史值；10/24核查','2项10/23历史值；10/27核查',1)
 for key in ('RANK_UPDATED','RANK_CHECKED'):source=re.sub(r'window\.'+key+r' = "[^"]+";',f'window.{key} = "{DAY}";',source,count=1)
 note='10月27日真实核对AA当前榜：18项当前选录分数未变，2条10/23历史值及全部旧TB/SWE分数保留。实质内容修正为两张DeepSeek Flash卡：现行调用别名、退役兼容型号、已核实峰谷/缓存价格，以及AA max快照与本站非思考JSON任务调用的区别。未声称价格核查等同模型实调或国内全网可达，其他旧型号价格与主观等级未全部复核。'
 source=re.sub(r'window\.RANK_CHECK_NOTE = "[^"\n]*";',lambda _:'window.RANK_CHECK_NOTE = '+json.dumps(note,ensure_ascii=False)+';',source,count=1)
 after=values(source);after_rank=after['RANK']
 assert [m for m in after_rank['models'] if m['name']not in updated]==[m for m in rank['models'] if m['name']not in updated]
 assert all(after_rank[k]==rank[k] for k in ('tools','combos'))
 assert all(after_rank['tables'][k]==rank['tables'][k] for k in ('tb','swe','swe_pro'))
 assert after_rank['tables']['aa']['rows']==rank['tables']['aa']['rows']
 assert all(after_rank['models'][i][k]==model[k] for i,model in enumerate(rank['models']) for k in model if k not in ('price','note'))
 report={'checkedAt':DAY,'attemptedAt':now.isoformat(),'completedAt':dt.datetime.now(BEIJING).isoformat(),'independentOfficialWebRead':True,'method':'Independently read the official AA current board and DeepSeek first-call/pricing/thinking docs with the web tool before comparing source data. Readable official web extraction and direct transport completeness are distinct evidence.','officialObservations':[{'url':AA,'filter':'Status:Current','observedSelectedRows':CURRENT_OBSERVED,'finding':'All18 selected current scores unchanged; two explicit10/23 historical rows remain historical.'},{'url':'https://artificialanalysis.ai/changelog','latestDisplayedDatedSection':'2026-10-23','finding':'No newer selected-model score change found.'},{'url':DOCS,'finding':'Current rolling API model name and retired compatibility aliases are distinct from fixed benchmark snapshots.'},{'url':PRICING,'observedFlash':OFFICIAL_FLASH},{'url':THINKING,'finding':'Thinking enabled by default at high effort; explicitly disabled for non-thinking. AA max is a different setting.'},{'url':'https://platform.deepseek.com/api_keys','finding':'Official key-console entry linked by API docs; web fetch403 is access limitation, not a dead-link finding or a login/balance validation.'}],'transport':network,'aaScoresChanged':False,'modelCardsChanged':True,'modelCardChanges':[{'name':name,'before':original[name],'after':updated[name],'changedFields':['price','note']} for name in updated],'aaApplied':after_rank['tables']['aa']['rows'],'contentUpdatedAt':DAY,'previousContentUpdatedAt':before['RANK_UPDATED'],'previousEvidence':'_rank_review_2026-10-26.json','preservedHistoricalRows':['Muse Spark 1.3 (max) · 10/23历史值','Kimi K3 (max) · 10/23历史值'],'protectedComparison':'All model identities, scores, TB values and subjective grades unchanged; other34 cards, tools, combinations and historical TB/SWE tables unchanged. Only two Flash price/note fields and independently rechecked AA title change.','scopeLimitation':'No model API inference call, key/login validation, balance access, nationwide-network availability promise, new performance measurement or unverified weight-release claim. Existing subjective grades and unrelated prices are not recertified.','written':True}
 (ROOT/'rank.js').write_text(source,encoding='utf-8');(ROOT/f'_rank_review_{DAY}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'modelCardsCorrected':2,'aaCurrentScoresUnchanged':18,'aaHistoricalRowsPreserved':2,'contentUpdatedAt':DAY,'completeDownloads':sum(r['complete']for r in network),'downloadAttempts':len(network)},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
