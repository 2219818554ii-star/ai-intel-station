"""Apply the exact new AA identity from an independently read official bulletin.

The current board and October 23 bulletin were read on October 24. Existing
scores are retained with their prior evidence, not re-certified from rank.js.
"""
import json
import re
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parent
NODE='C:/Users/22198/.workbuddy/binaries/node/versions/22.22.2-6/node.exe'
DAY='2026-10-24'
URL='https://artificialanalysis.ai/articles/kimi-k3-1-pro-launch-benchmarks'
source=(ROOT/'rank.js').read_text(encoding='utf-8')
code='const vm=require("vm"),c={window:{}};vm.runInNewContext(require("fs").readFileSync(0,"utf8"),c);console.log(JSON.stringify(c.window.RANK))'
before=json.loads(subprocess.check_output([NODE,'-e',code],input=source,text=True,encoding='utf-8'))
assert not any(m['name']=='Kimi K3.1 Pro' for m in before['models'])
model={'name':'Kimi K3.1 Pro','vendor':'Moonshot / 月之暗面（中国）','price':'具体API价格与可用性请核对厂商官网','iaa':55,'tb':None,
       't':{k:'—' for k in ['综合','推理','代码','多模态','长上下文','中文','性价比','开源']},
       'note':'10月24日核对AA当前榜与10月23日官方评测公告：智能指数55，1M上下文；公告另列TB4.0为67%，不能填入本页TB2.1列。该公告称权重尚未发布，不能把未来开放计划写成已经开源。价格、产品可用性与主观等级本次不作推断。'}
source=source.replace('    models: [','    models: [\n      '+json.dumps(model,ensure_ascii=False)+',',1)
rows=[list(r) for r in before['tables']['aa']['rows']]
rows.insert(3,['Kimi K3.1 Pro',55])
# Current-board absence cannot erase a previously independently verified model.
# Explicitly identify retained historical rows instead of presenting them as fresh.
for row in rows:
    if row[0] in ('Muse Spark 1.3 (max)','Kimi K3 (max)'):
        row[0]+=' · 10/23历史值'
title='Artificial Analysis 智能指数 · 选录20项（18项当前榜，2项10/23历史值；10/24核查）'
line='      aa: '+json.dumps({'title':title,'unit':'分','rows':rows},ensure_ascii=False)+','
source,count=re.subn(r'^      aa: .*$',lambda _:line,source,count=1,flags=re.M)
assert count==1
for key in ['RANK_UPDATED','RANK_CHECKED']:
    source=re.sub(r'window\.'+key+r' = "[^"]+";',f'window.{key} = "{DAY}";',source,count=1)
note='10月24日实际核对AA当前榜及10月23日官方公告，新增Kimi K3.1 Pro=55。18项来自当前榜；Muse Spark1.3与Kimi K3两条明确保留10/23历史值，不冒称今日在当前榜。现36个模型卡、20项AA选录。TB2.1/SWE仍为原历史口径；工具文档本轮未全量重测，旧型号价格与主观等级未全部复核，保留原核验范围。'
source=re.sub(r'window.RANK_CHECK_NOTE = "[^"\n]*";',lambda _:'window.RANK_CHECK_NOTE = '+json.dumps(note,ensure_ascii=False)+';',source,count=1)
after=json.loads(subprocess.check_output([NODE,'-e',code],input=source,text=True,encoding='utf-8'))
assert [m for m in after['models'] if m['name']!='Kimi K3.1 Pro']==before['models']
assert all(after[k]==before[k] for k in ['tools','combos'])
assert all(after['tables'][k]==before['tables'][k] for k in ['tb','swe','swe_pro'])
report={'checkedAt':DAY,'method':'Independent official web extraction read during current run; prior scores retained only with their separate dated proof.',
        'sources':[{'url':'https://artificialanalysis.ai/leaderboards/models','observedModel':'Kimi K3.1 Pro','score':55,'context':'1M'},
                   {'url':URL,'publishedAt':'2026-10-23','observedModel':'Kimi K3.1 Pro','score':55,'tb4':67,'weights':'not yet published as stated in the October23 bulletin'}],
        'newModel':model,'aaApplied':rows,'preservedHistoricalRows':['Muse Spark 1.3 (max)','Kimi K3 (max)'],
        'previousEvidence':'_rank_review_2026-10-23.json','written':True}
(ROOT/'rank.js').write_text(source,encoding='utf-8')
(ROOT/f'_rank_review_{DAY}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('36 models / 20 AA rows; historic baselines preserved')
