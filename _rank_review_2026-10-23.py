"""Dated October 23 independent official-source review and optional rank update.

OBSERVED is a transcription of the official leaderboard read in this review,
not a score fixture derived from rank.js. Download completeness is recorded
separately and is never inferred from an HTTP status alone.
"""
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
NODE = 'C:/Users/22198/.workbuddy/binaries/node/versions/22.22.2-6/node.exe'
DAY = '2026-10-23'
AA = 'https://artificialanalysis.ai/leaderboards/models'
CHANGELOG = 'https://artificialanalysis.ai/changelog'
SPARK = 'https://artificialanalysis.ai/models/comparisons/muse-spark-1-3-vs-muse-spark-1-3-xhigh'
LING = 'https://artificialanalysis.ai/models/ling-3-1-flash-1019'
OBSERVED = [
    ['Claude Opus 5.5 (max with fallback)', 58],
    ['Claude Sonnet 5.5 (max with fallback)', 56],
    ['Muse Wonder Full (max)', 56],
    ['Claude Fable 5.1 (max with fallback)', 53],
    ['GPT-6 Astra (max)', 53],
    ['Gemini 4 Argon (high)', 53],
    ['GPT-6.1 Sol (max)', 52],
    ['Muse Wonder (max)', 52],
    ['Muse Spark 1.3 (max)', 48],
    ['Grok 4.7 (xhigh)', 46],
    ['MiMo-V2.6-Pro', 46],
    ['Qwen3.8 Max (0902)', 45],
    ['DeepSeek V4.1 Flash 1017 (max)', 45],
    ['GLM-5.3 (max)', 45],
    ['Ling 3.1 Flash 1019', 44],
    ['Step 5 Preview', 44],
    ['Kimi K3 (max)', 44],
    ['Claude Haiku 5.5 (max)', 43],
    ['MiniMax-M3.1-Flash', 43],
]
TOOL_SOURCES = [
    ('Claude Code', 'https://code.claude.com/docs/en/overview', 'Terminal, IDE, desktop and web documentation remain available; no default model or fixed plan price assumed.'),
    ('OpenAI Codex', 'https://learn.chatgpt.com/docs/quickstart?setup=app', 'Official quickstart remains reachable with app, CLI, IDE and cloud project documentation; availability depends on account and environment.'),
    ('opencode', 'https://opencode.ai/v2/docs/', 'V2 supports terminal, desktop and web. Migration guide says V1 and V2 both use the opencode command; installing V2 replaces/conflicts with default V1 installations. No install command added to the site.'),
    ('Cursor', 'https://cursor.com/docs', 'Agent, rules, skills, subagents, hooks, MCP and CLI sections remain available; no fixed parallel-agent ceiling asserted.'),
    ('Gemini CLI', 'https://geminicli.com/docs/', 'File, shell, web fetch, MCP, sessions, model and authentication documentation remain available; no fixed free quota asserted.'),
    ('GitHub Copilot', 'https://docs.github.com/en/copilot/get-started/about-github-copilot', 'Official overview describes code assistance, review and issue/PR task agents; plan and organization controls remain relevant.'),
    ('Google Antigravity', 'https://antigravity.google/docs/overview', 'App, CLI, IDE extensions, subagents and permission documentation remains available; no same-environment new throughput comparison obtained.'),
    ('Cline', 'https://docs.cline.bot/cline-overview', 'Official overview lists desktop, CLI, editor and SDK surfaces, model-access choices and human approval.'),
    ('Aider', 'https://aider.chat/docs/', 'Official terminal pair-programming, model connection and Git workflow documentation remains available.'),
]


def read_rank(source):
    code = 'let s={window:{}};require("vm").runInNewContext(require("fs").readFileSync(0,"utf8"),s);process.stdout.write(JSON.stringify(s.window));'
    return json.loads(subprocess.check_output([NODE, '-e', code], input=source, text=True, encoding='utf-8'))


def transport(url):
    p = subprocess.run(['curl.exe', '-L', '-sS', '--max-time', '16', '-A', 'Mozilla/5.0', '-w', '\n%{http_code}', url], capture_output=True, timeout=21)
    body, _, status = p.stdout.rpartition(b'\n')
    complete = p.returncode == 0 and status == b'200'
    return {'url': url, 'httpStatus': status.decode(errors='replace'), 'bytes': len(body),
            'sha256': hashlib.sha256(body).hexdigest(), 'exitCode': p.returncode,
            'complete': complete, 'error': p.stderr.decode(errors='replace') if p.returncode else None}


if __name__ == '__main__':
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
    assert now.date().isoformat() == DAY, 'New date requires a new source review.'
    source = (ROOT / 'rank.js').read_text(encoding='utf-8')
    before = read_rank(source)
    old_rows = [r for r in OBSERVED if r[0] != 'Ling 3.1 Flash 1019']
    historical = json.loads((ROOT / '_rank_review_2026-10-19.json').read_text(encoding='utf-8'))
    assert before['RANK']['tables']['aa']['rows'] in (old_rows, OBSERVED)
    assert before['RANK']['tables']['swe']['rows'] == historical['sweApplied']['verified']
    assert before['RANK']['tables']['swe_pro']['rows'] == historical['sweApplied']['pro']
    urls = [AA, CHANGELOG, SPARK, LING, 'https://huggingface.co/inclusionAI/Ling-3.1-flash',
            'https://opencode.ai/v2/docs/migrate-v1/', 'https://www.tbench.ai/leaderboard', 'https://www.swebench.com/'] + [x[1] for x in TOOL_SOURCES]
    with ThreadPoolExecutor(max_workers=4) as pool:
        transports = list(pool.map(transport, urls))
    report = {
        'checkedAt': DAY, 'checkedAtTimestamp': now.isoformat(),
        'scope': 'Current AA exact model/version/effort selections, nine official tool documents, TB/SWE availability; no account data involved.',
        'sources': [
            {'url': AA, 'method': 'Official web extraction independently read October 23', 'usable': True,
             'observedRows': [r for r in OBSERVED if r[0] != 'Muse Spark 1.3 (max)'],
             'newObservation': {'model': 'Ling 3.1 Flash 1019', 'creator': 'InclusionAI', 'intelligenceIndex': 44, 'contextWindow': '1.05M'},
             'finding': 'All eighteen visible exact selections, including new Ling1019, match the row values transcribed here. Muse Spark Max requires the separate exact-model comparison.'},
            {'url': CHANGELOG, 'method': 'Official dated changelog read October 23', 'usable': True,
             'newObservation': {'evaluationPublishedAt': '2026-10-22', 'model': 'Ling 3.1 Flash 1019', 'intelligenceIndex': 44},
             'finding': 'October22 explicitly announces new language-model evaluation Ling3.1 Flash1019=44; October21 provider endpoints are not new intelligence scores.'},
            {'url': SPARK, 'method': 'Official comparison table read October 23', 'usable': True,
             'observedRows': [['Muse Spark 1.3 (max)', 48], ['Muse Spark 1.3 (xhigh)', 45]]},
            {'url': LING, 'method': 'Official single-model web extraction attempted October 23', 'usable': False,
             'error': 'Extractor rejected more than4MiB. New exact identity and score are independently supported by the current table and dated changelog; no dead-link judgment.'},
            {'url': 'https://huggingface.co/inclusionAI/Ling-3.1-flash', 'method': 'Official creator model card read October23', 'usable': True,
             'finding': 'The creator card is named Ling-3.1-flash and identifies MIT weights,560B/25B and1M context. It does not establish that the separate1019checkpoint is currently downloadable; these weight/API availability claims are deliberately not copied to the new exact-version row.'},
            {'url': 'https://www.tbench.ai/leaderboard', 'finding': 'Redirects to official TB4.0 page; no independently comparable TB2.1 refresh obtained.'},
            {'url': 'https://www.swebench.com/', 'finding': 'Official Verified/BashOnly and other benchmark views remain distinct; no current same-harness new scores obtained.'},
        ],
        'aaApplied': OBSERVED, 'sweApplied': historical['sweApplied'],
        'modelAdditions': [{'name': 'Ling 3.1 Flash 1019', 'iaa': 44, 'tb': None, 'specialtyGrades': {},
                            'scoreSource': AA, 'evaluationDateSource': CHANGELOG, 'evaluationPublishedAt': '2026-10-22'}],
        'contentChanges': ['Added the newly evaluated exact Ling3.1 Flash1019 model to model cards and AA selections; existing eighteen selected version/effort values preserved.'],
        'previousSuccessfulContentUpdate': before['RANK_UPDATED'],
        'lastSuccessfulContentUpdate': DAY if '--write' in sys.argv else before['RANK_UPDATED'],
        'toolsReview': [{'name': n, 'url': u, 'checkedAt': DAY, 'method': 'Official web extraction', 'finding': f} for n, u, f in TOOL_SOURCES],
        'transportObservations': transports,
        'limits': ['HTTP status alone is not complete-download or semantic proof; curl completeness and errors are recorded separately.',
                   'New1019API/weights availability, token pricing, specialty grades andTB2.1score were not verified; none guessed.',
                   'Historical tool model/harness scores, full older-model prices and subjective grades were not remeasured.'],
    }
    if '--write' in sys.argv:
        if not any(m['name'] == 'Ling 3.1 Flash 1019' for m in before['RANK']['models']):
            marker = '      {name:"MiMo V2.6 Pro"'
            assert source.count(marker) == 1
            addition = '      {name:"Ling 3.1 Flash 1019", vendor:"InclusionAI（中国）", price:"API/权重开放与价格待核实", iaa:44, tb:null,\n       t:{},\n       note:"10月23日核对AA官方当前榜与10月22日评测更新：1019独立版本智能指数44、上下文1.05M。旧Ling3.1模型卡不能证明1019权重已开放；本次未核实该版本API开放、价格、TB2.1及专项分级，均不猜填。"},\n'
            source = source.replace(marker, addition + marker, 1)
        import re
        source = re.sub(r'window.RANK_UPDATED = "[^"]+";', f'window.RANK_UPDATED = "{DAY}";', source, count=1)
        source = re.sub(r'window.RANK_CHECKED = "[^"]+";', f'window.RANK_CHECKED = "{DAY}";', source, count=1)
        source = source.replace('当前模型选录18项（保留版本与推理档位，2026-10-20核对）', '当前模型选录19项（保留版本与推理档位，2026-10-23核对）', 1)
        if before['RANK']['tables']['aa']['rows'] == old_rows:
            source = source.replace('["Step 5 Preview", 44]', '["Ling 3.1 Flash 1019", 44], ["Step 5 Preview", 44]', 1)
        note = '10月23日实核AA官方当前榜与10月22日评测公告，新收录Ling3.1 Flash1019=44；现19个选录型号，原18个型号与推理档位分数不变，Muse Spark1.3 max48仍由精确对比页复核。9个工具官方文档入口已复核。新型号的API/权重开放与价格待核实。TB2.1及SWE保留原历史日期与成绩；旧工具成绩未重测，全体旧型号价格与主观等级未全部复核。'
        source = re.sub(r'window.RANK_CHECK_NOTE = "[^"\n]*";', 'window.RANK_CHECK_NOTE = ' + json.dumps(note, ensure_ascii=False) + ';', source, count=1)
        after = read_rank(source)
        assert after['RANK']['tables']['aa']['rows'] == OBSERVED
        assert [m for m in after['RANK']['models'] if m['name'] != 'Ling 3.1 Flash 1019'] == [m for m in before['RANK']['models'] if m['name'] != 'Ling 3.1 Flash 1019']
        for k in ('tools', 'combos'):
            assert after['RANK'][k] == before['RANK'][k]
        for k in ('tb', 'swe', 'swe_pro'):
            assert after['RANK']['tables'][k] == before['RANK']['tables'][k]
        (ROOT / 'rank.js').write_text(source, encoding='utf-8')
        report['written'] = True
    (ROOT / '_rank_review_2026-10-23.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'aaRows': len(OBSERVED), 'newModel': 'Ling 3.1 Flash 1019', 'score': 44, 'report': '_rank_review_2026-10-23.json', 'written': report.get('written', False)}))
