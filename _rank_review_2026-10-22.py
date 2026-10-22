"""Record the October 22 official-source review without rewriting benchmark scores.

Observed rows below were independently read from AA's official leaderboard,
exact-model comparison page and changelog; rank.js is compared against them,
never used as its own score evidence.
Historical SWE results retain their earlier evidence and are not called fresh.
"""
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
NODE = 'C:/Users/22198/.workbuddy/binaries/node/versions/22.22.2-6/node.exe'
DAY = '2026-10-22'
AA = 'https://artificialanalysis.ai/leaderboards/models'
CHANGELOG = 'https://artificialanalysis.ai/changelog'
SPARK = 'https://artificialanalysis.ai/models/comparisons/muse-spark-1-3-vs-muse-spark-1-3-xhigh'
SPARK_OVERSIZED = 'https://artificialanalysis.ai/models/muse-spark-1-3'
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
    ['Step 5 Preview', 44],
    ['Kimi K3 (max)', 44],
    ['Claude Haiku 5.5 (max)', 43],
    ['MiniMax-M3.1-Flash', 43],
]
TOOL_SOURCES = [
    ('Claude Code', 'https://code.claude.com/docs/en/overview', 'Terminal, IDE extensions, desktop and web are explicitly supported.'),
    ('OpenAI Codex', 'https://learn.chatgpt.com/docs/quickstart?setup=app', 'CLI, IDE, local desktop and cloud project workflows; availability depends on account and environment.'),
    ('opencode', 'https://opencode.ai/docs/', 'Open source coding agent with terminal, desktop and IDE extension entry points; configurable models and providers.'),
    ('Cursor', 'https://cursor.com/docs', 'Agent, rules, MCP, subagents, hooks and CLI documentation; no fixed parallel-agent ceiling asserted.'),
    ('Gemini CLI', 'https://geminicli.com/docs/', 'Terminal file, shell, model-selection and MCP workflows; fixed free quota not asserted.'),
    ('GitHub Copilot', 'https://docs.github.com/en/copilot/get-started/about-github-copilot', 'Code suggestions, review, issues and PR agent workflows; plan and organization policies govern features.'),
    ('Google Antigravity', 'https://antigravity.google/docs/overview', 'Official product/workflow documentation; historical throughput is not a fresh cross-product comparison.'),
    ('Cline', 'https://docs.cline.bot/cline-overview', 'Editor, terminal and other app surfaces with configurable model access; client availability does not imply free inference.'),
    ('Aider', 'https://aider.chat/docs/', 'Terminal pair-programming and Git workflow documentation.'),
]


def transport(url):
    proc = subprocess.run(['curl.exe', '-L', '-sS', '--max-time', '12', '-A', 'Mozilla/5.0', '-w', '\n%{http_code}', url], capture_output=True, timeout=16)
    body, _, status = proc.stdout.rpartition(b'\n')
    return {'url': url, 'httpStatus': status.decode(errors='replace'), 'bytes': len(body),
            'sha256': hashlib.sha256(body).hexdigest(), 'exitCode': proc.returncode,
            'error': proc.stderr.decode(errors='replace') if proc.returncode else None}


if __name__ == '__main__':
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
    if now.date().isoformat() != DAY:
        raise RuntimeError('Dated review fixture: perform a new source review instead of rolling its date.')
    code = 'let s={window:{}};require("vm").runInNewContext(require("fs").readFileSync("rank.js","utf8"),s);process.stdout.write(JSON.stringify(s.window));'
    values = json.loads(subprocess.check_output([NODE, '-e', code], cwd=ROOT))
    rank = values['RANK']
    assert rank['tables']['aa']['rows'] == OBSERVED, 'AA values or version identities differ from independently observed rows'
    historical = json.loads((ROOT / '_rank_review_2026-10-19.json').read_text(encoding='utf-8'))
    assert rank['tables']['swe']['rows'] == historical['sweApplied']['verified']
    assert rank['tables']['swe_pro']['rows'] == historical['sweApplied']['pro']
    for name, score in [('DeepSeek V4.1-Flash', 39), ('MiniMax M3', 29)]:
        assert next(m for m in rank['models'] if m['name'] == name)['iaa'] == score, 'Old model overwritten by a different version'
    urls = [AA, CHANGELOG, SPARK, SPARK_OVERSIZED, 'https://www.tbench.ai/leaderboard', 'https://www.swebench.com/', 'https://opencode.ai/v2/docs/'] + [x[1] for x in TOOL_SOURCES]
    with ThreadPoolExecutor(max_workers=4) as pool:
        transports = list(pool.map(transport, urls))
    report = {
        'checkedAt': DAY, 'checkedAtTimestamp': now.isoformat(),
        'scope': 'Official AA selected model rows and tool documentation; preserve historical TB/SWE and account-independent metadata.',
        'sources': [
            {'url': AA, 'method': 'Official web extraction read 2026-10-22', 'usable': True,
             'observedRows': [r for r in OBSERVED if r[0] != 'Muse Spark 1.3 (max)'],
             'finding': 'Seventeen selected exact model/effort rows are visible in the Current table; Muse Spark 1.3 was not present in this view and required independent exact-model confirmation.'},
            {'url': SPARK, 'method': 'Official comparison table read 2026-10-22', 'usable': True,
             'observedRows': [['Muse Spark 1.3 (max)', 48], ['Muse Spark 1.3 (xhigh)', 45]],
             'finding': 'The official comparison distinguishes Max48 from Xhigh45. Only the existing Max48 selection is retained; an absent Current-table row alone is not retirement or score-change evidence.'},
            {'url': SPARK_OVERSIZED, 'method': 'Official model page attempted 2026-10-22', 'usable': False,
             'error': 'Web extractor rejected content exceeding 4 MiB; official exact-model comparison above supplied the score evidence. This is not a dead-link determination.'},
            {'url': CHANGELOG, 'method': 'Official dated changelog read 2026-10-22', 'findings': [
                {'date': '2026-10-18', 'model': 'DeepSeek V4.1 Flash 1017 (max)', 'iaa': 45},
                {'date': '2026-10-19', 'model': 'MiniMax-M3.1-Flash', 'iaa': 43},
                {'date': '2026-09-10', 'model': 'DeepSeek V4.1 Flash (max)', 'iaa': 39}]},
            {'url': 'https://www.tbench.ai/leaderboard', 'finding': 'Redirects to official Terminal-Bench4.0 homepage; no same-version TB2.1 new scores written.'},
            {'url': 'https://www.swebench.com/', 'finding': 'Verified500 and BashOnly mini-SWE-agent are different views; no current comparable numeric results obtained.'},
        ],
        'modelAdditions': [],
        'contentChanges': [],
        'comparison': 'All 18 selected exact model/effort scores are corroborated: 17 by the official Current table and Muse Spark1.3 Max48 by the official comparison page. Scores match October20 content; no numeric score or model addition written.',
        'lastSuccessfulContentUpdate': values['RANK_UPDATED'],
        'changelogReview': 'Latest visible October21 entries add LithosAI/Makora performance results for DeepSeek1017 and DigitalOcean results for Beam1.0. Provider performance announcements are not new intelligence scores or new model identities.',
        'aaApplied': OBSERVED, 'sweApplied': historical['sweApplied'],
        'toolsReview': [{'name': name, 'url': url, 'checkedAt': DAY, 'method': 'Official web extraction', 'finding': finding} for name, url, finding in TOOL_SOURCES],
        'additionalToolObservation': {'name': 'OpenCode', 'url': 'https://opencode.ai/v2/docs/', 'checkedAt': DAY,
            'finding': 'V1 documentation now points to separate V2 documentation. V1 and V2 share the opencode command and default installations can conflict. Existing generic model/provider description remains accurate; no version-specific install command is published in rank.js.'},
        'transportObservations': transports,
        'limits': [
            'Transport HTTP success is separate from the official web extraction used for semantic verification.',
            'Tool benchmark scores retain old model/harness pairings; none are presented as fresh scores.',
            'Subscription prices, defaults, quotas and star counts were not refreshed; tool descriptions continue to defer to official account and plan availability.',
            'Existing full model price fields and subjective grades were not fully reverified; global note preserves this limit.',
            'AA selection contains represented model versions, not every model or every reasoning effort.',
        ],
    }
    (ROOT / '_rank_review_2026-10-22.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'models': len(rank['models']), 'aaRows': len(OBSERVED), 'toolSources': len(TOOL_SOURCES), 'report': '_rank_review_2026-10-22.json', 'historicalScoresPreserved': True}, ensure_ascii=False))
