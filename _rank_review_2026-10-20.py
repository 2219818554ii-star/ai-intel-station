"""Record the October 20 official-source review without rewriting benchmark scores.

Observed rows below were independently read from AA's official leaderboard and
changelog; rank.js is compared against them, never used as its own score evidence.
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
DAY = '2026-10-20'
AA = 'https://artificialanalysis.ai/leaderboards/models'
CHANGELOG = 'https://artificialanalysis.ai/changelog'
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
    ('Claude Code', 'https://code.claude.com/docs/en/overview', 'Terminal, IDE extensions, desktop and web are explicitly supported; old no-GUI claim removed.'),
    ('OpenAI Codex', 'https://learn.chatgpt.com/docs/quickstart?setup=app', 'CLI, IDE, local desktop and cloud project workflows; availability depends on account and environment.'),
    ('opencode', 'https://opencode.ai/docs/', 'Terminal coding agent with configurable models and providers; unverified star-count and universal-best claims removed.'),
    ('Cursor', 'https://cursor.com/docs', 'Agent, rules, MCP and CLI documentation; unverified fixed parallel-agent ceiling removed.'),
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
    urls = [AA, CHANGELOG, 'https://www.tbench.ai/leaderboard', 'https://www.swebench.com/'] + [x[1] for x in TOOL_SOURCES]
    with ThreadPoolExecutor(max_workers=4) as pool:
        transports = list(pool.map(transport, urls))
    report = {
        'checkedAt': DAY, 'checkedAtTimestamp': now.isoformat(),
        'scope': 'Official AA selected model rows and tool documentation; preserve historical TB/SWE and account-independent metadata.',
        'sources': [
            {'url': AA, 'method': 'Official web extraction read 2026-10-20', 'usable': True, 'observedRows': OBSERVED},
            {'url': CHANGELOG, 'method': 'Official dated changelog read 2026-10-20', 'findings': [
                {'date': '2026-10-18', 'model': 'DeepSeek V4.1 Flash 1017 (max)', 'iaa': 45},
                {'date': '2026-10-19', 'model': 'MiniMax-M3.1-Flash', 'iaa': 43},
                {'date': '2026-09-10', 'model': 'DeepSeek V4.1 Flash (max)', 'iaa': 39}]},
            {'url': 'https://www.tbench.ai/leaderboard', 'finding': 'Redirects to official Terminal-Bench4.0 homepage; no same-version TB2.1 new scores written.'},
            {'url': 'https://www.swebench.com/', 'finding': 'Verified500 and BashOnly mini-SWE-agent are different views; no current comparable numeric results obtained.'},
        ],
        'modelAdditions': [
            {'name': 'DeepSeek V4.1 Flash 1017 (max)', 'iaa': 45, 'evaluationAnnouncedAt': '2026-10-18', 'source': AA, 'otherGrades': 'unverified; blank', 'tb': None},
            {'name': 'MiniMax-M3.1-Flash', 'iaa': 43, 'evaluationAnnouncedAt': '2026-10-19', 'source': AA, 'otherGrades': 'unverified; blank', 'tb': None},
        ],
        'aaApplied': OBSERVED, 'sweApplied': historical['sweApplied'],
        'toolsReview': [{'name': name, 'url': url, 'checkedAt': DAY, 'method': 'Official web extraction', 'finding': finding} for name, url, finding in TOOL_SOURCES],
        'transportObservations': transports,
        'limits': [
            'Transport HTTP success is separate from the official web extraction used for semantic verification.',
            'Tool benchmark scores retain old model/harness pairings; none are presented as fresh scores.',
            'Subscription prices, defaults, request quotas, star counts and unverifiable strongest/fastest claims removed from tools/combos instead of guessed.',
            'Existing full model price fields and subjective grades were not fully reverified; global note preserves this limit.',
            'AA selection contains represented model versions, not every model or every reasoning effort.',
        ],
    }
    (ROOT / '_rank_review_2026-10-20.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'models': len(rank['models']), 'aaRows': len(OBSERVED), 'toolSources': len(TOOL_SOURCES), 'report': '_rank_review_2026-10-20.json', 'historicalScoresPreserved': True}, ensure_ascii=False))
