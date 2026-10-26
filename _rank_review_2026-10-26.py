"""October 26 review: read independent official sources before comparing data.

CURRENT_OBSERVED is a fresh transcription of the current official AA table read
with the web tool today, never an assertion generated from rank.js itself.
Transport failures are preserved separately from that independent readable copy.
"""
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parent
DAY='2026-10-26'
NODE='C:/Users/22198/.workbuddy/binaries/node/versions/22.22.2-6/node.exe'
BEIJING=dt.timezone(dt.timedelta(hours=8))
AA='https://artificialanalysis.ai/leaderboards/models'
CHANGELOG='https://artificialanalysis.ai/changelog'
SPARK='https://artificialanalysis.ai/models/comparisons/muse-spark-1-3-vs-muse-spark-1-3-xhigh'
KIMI='https://artificialanalysis.ai/articles/kimi-k3-1-pro-launch-benchmarks'
CURRENT_OBSERVED=[
    ['Claude Opus 5.5 (max with fallback)',58],
    ['Claude Sonnet 5.5 (max with fallback)',56],
    ['Muse Wonder Full (max)',56],
    ['Kimi K3.1 Pro',55],
    ['Claude Fable 5.1 (max with fallback)',53],
    ['GPT-6 Astra (max)',53],
    ['Gemini 4 Argon (high)',53],
    ['Muse Wonder (max)',52],
    ['GPT-6.1 Sol (max)',52],
    ['Grok 4.7 (xhigh)',46],
    ['MiMo-V2.6-Pro',46],
    ['Qwen3.8 Max (0902)',45],
    ['DeepSeek V4.1 Flash 1017 (max)',45],
    ['GLM-5.3 (max)',45],
    ['Ling 3.1 Flash 1019',44],
    ['Step 5 Preview',44],
    ['Claude Haiku 5.5 (max)',43],
    ['MiniMax-M3.1-Flash',43],
]
TOOLS=[
    {'name':'Claude Code','url':'https://code.claude.com/docs/en/overview','finding':'官方概览描述读写项目、运行命令及终端、IDE、桌面、网页入口；未据此更改默认模型、价格或旧成绩。'},
    {'name':'OpenAI Codex','url':'https://learn.chatgpt.com/docs/quickstart?setup=app','finding':'官方quickstart含应用、CLI、IDE和云端工作流；产品与权限依当前账号/环境，不据入口推断某项方案免费。'},
    {'name':'opencode','url':'https://opencode.ai/v2/docs/','finding':'官方V2文档列终端、桌面、网页与供应商配置；迁移页明确V1/V2同用opencode命令，默认不能并排安装，未给网站加入安装指令。'},
    {'name':'Cursor','url':'https://cursor.com/docs','finding':'官方文档列Agent、规则、技能、子代理、hooks、MCP、CLI等工作流；不据文档导航虚构并行上限或新实测成绩。'},
    {'name':'Gemini CLI','url':'https://geminicli.com/docs/','finding':'官方文档提供文件、shell、网页获取、MCP、会话与模型认证配置；没有假定固定免费请求额度。'},
    {'name':'GitHub Copilot','url':'https://docs.github.com/en/copilot/get-started/about-github-copilot','finding':'官方概览描述代码建议、问答、评审及issue/PR任务代理；计划与组织控制分别适用，不重标旧SWE。'},
    {'name':'Google Antigravity','url':'https://antigravity.google/docs/overview','finding':'官方文档包含应用、CLI、IDE扩展、子代理与权限；本轮未取得同环境速度/质量对照。'},
    {'name':'Cline','url':'https://docs.cline.bot/cline-overview','finding':'官方概览列桌面、CLI、编辑器、SDK与模型接入选择，并说明人工审批；没有把开源客户端等同免费模型。'},
    {'name':'Aider','url':'https://aider.chat/docs/','finding':'官方文档提供终端结对编程、模型连接和Git工作流；无新的统一可比SWE/TB成绩。'},
]

def values(source):
    js='let c={window:{}};require("vm").runInNewContext(require("fs").readFileSync(0,"utf8"),c);console.log(JSON.stringify(c.window))'
    return json.loads(subprocess.check_output([NODE,'-e',js],input=source,text=True,encoding='utf-8'))

def transport(url):
    try:
        proc=subprocess.run(['curl.exe','-L','-sS','--compressed','--max-time','16','-A','Mozilla/5.0',
                             '-w','\n@@RESULT@@%{json}',url],capture_output=True,timeout=21)
        body,_,tail=proc.stdout.rpartition(b'\n@@RESULT@@')
        meta=json.loads(tail.decode('utf-8')) if tail else {}
        complete=proc.returncode==0 and meta.get('http_code')==200
        decoded=body.decode('utf-8','replace')
        text=re.sub(r'<(script|style)\b[^>]*>[\s\S]*?</\1>','',decoded,flags=re.I)
        text=re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',text)).strip()
        title=re.search(r'<title[^>]*>(.*?)</title>',decoded,re.I|re.S)
        result={'url':url,'httpStatus':meta.get('http_code',0),'curlExit':proc.returncode,'bytes':len(body),
                'sha256':hashlib.sha256(body).hexdigest(),'finalURL':meta.get('url_effective',url),
                'complete':complete,'error':proc.stderr.decode('utf-8','replace').strip() or None,
                'responseTitle':re.sub(r'\s+',' ',title[1]).strip() if title else None,
                'usableText':bool(complete and len(text)>150 and not re.search(r'just a moment|verify you are human|checking your browser|访问验证|人机验证',text[:1600],re.I))}
    except (subprocess.TimeoutExpired,ValueError) as exc:
        result={'url':url,'complete':False,'usableText':False,'error':str(exc)}
    print(json.dumps({'url':url,'complete':result['complete'],'httpStatus':result.get('httpStatus'),'error':result.get('error')},ensure_ascii=False),flush=True)
    return result

def main():
    now=dt.datetime.now(BEIJING)
    assert now.date().isoformat()==DAY,'Use a new dated review for a new day.'
    source=(ROOT/'rank.js').read_text(encoding='utf-8');before=values(source)
    observed=dict(CURRENT_OBSERVED)
    current_rows=[r for r in before['RANK']['tables']['aa']['rows'] if '历史值' not in r[0]]
    assert len(current_rows)==18
    assert all(observed.get(name)==score for name,score in current_rows),'A real score change requires separate review before mutation.'
    historical=[r for r in before['RANK']['tables']['aa']['rows'] if '历史值' in r[0]]
    assert historical==[['Muse Spark 1.3 (max) · 10/23历史值',48],['Kimi K3 (max) · 10/23历史值',44]]
    urls=[AA,CHANGELOG,SPARK,KIMI,'https://opencode.ai/v2/docs/migrate-v1/',
          'https://www.tbench.ai/leaderboard','https://www.swebench.com/']+[x['url'] for x in TOOLS]
    with ThreadPoolExecutor(max_workers=4) as pool:network=list(pool.map(transport,urls))
    report={'checkedAt':DAY,'attemptedAt':now.isoformat(),'completedAt':dt.datetime.now(BEIJING).isoformat(),
            'independentOfficialWebRead':True,'method':'Official primary pages independently read with the web tool during this run; current table transcribed above before comparing rank.js. Curl completeness is recorded separately, not inferred from HTTP200.',
            'officialObservations':[{'url':AA,'filter':'Status:Current','observedSelectedRows':CURRENT_OBSERVED},
                {'url':CHANGELOG,'latestDisplayedDatedSection':'2026-10-23','finding':'Latest visible model additions remain Kimi K3.1 Pro and Nemotron3.5 Bolt E4B 4GB(Reasoning); no changed selected score found.'},
                {'url':SPARK,'finding':'Exact comparison still shows max48 versus xhigh45; historical row kept with original date and not promoted to the current board.'},
                {'url':KIMI,'publishedAt':'2026-10-23','finding':'AA bulletin still gives K3.1Pro55, K3(max)44 and TB4.0=67%; its weights statement is as of the bulletin, not a newly verified release.'},
                {'url':'https://www.tbench.ai/leaderboard','finding':'Official endpoint redirects toTB4.0; no new same-basis TB2.1 source obtained.'},
                {'url':'https://www.swebench.com/','finding':'Official site separates Verified/BashOnly and other tracks; no same-tool/model/environment update obtained for retained historic entries.'}],
            'tools':TOOLS,'transport':network,'aaScoresChanged':False,'modelCardsChanged':False,
            'historicalLabelsAndDatesPreserved':True,'contentUpdatedAt':before['RANK_UPDATED'],
            'aaApplied':before['RANK']['tables']['aa']['rows'],
            'scopeLimitation':'Existing model prices, subjective grades, historical model-card scores and old TB/SWE pairings were not re-measured; no availability or speed claim inferred from documentation reachability.'}
    source=re.sub(r'window\.RANK_CHECKED = "[^"]+";',f'window.RANK_CHECKED = "{DAY}";',source,count=1)
    note='10月26日实际重查AA当前榜、精确型号/推理档位及官方公告：18项当前选录分数均未变；2项历史记录仍保留10/23日期，内容更新日保持10/24。9个工具官方文档入口与公开说明已重查，网络不完整请求另行保留。TB2.1/SWE旧同口径成绩、旧型号价格与主观等级未全部复核，不把文档可达性写成性能重测。'
    source=re.sub(r'window\.RANK_CHECK_NOTE = "[^"\n]*";',lambda _:'window.RANK_CHECK_NOTE = '+json.dumps(note,ensure_ascii=False)+';',source,count=1)
    after=values(source)
    assert after['RANK_UPDATED']==before['RANK_UPDATED']=='2026-10-24'
    assert after['RANK']==before['RANK'],'Only check metadata may change when selected content is unchanged.'
    report['protectedComparison']='Entire RANK object including all36 model cards, tools, combinations,20 AA rows and historic TB/SWE tables equal before/after; RANK_UPDATED preserved.'
    (ROOT/'rank.js').write_text(source,encoding='utf-8')
    (ROOT/f'_rank_review_{DAY}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'contentUpdatedAt':after['RANK_UPDATED'],'checkedAt':DAY,'currentScoresUnchanged':18,'toolsOfficiallyRead':len(TOOLS),'completeDownloads':sum(x['complete'] for x in network),'downloadAttempts':len(network)},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
