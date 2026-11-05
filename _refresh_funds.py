"""Fetch complete public NAV evidence only; never writes funds.js or stock quotes."""
import concurrent.futures
import json
from _funds_public_nav import ROOT, CODES, collect, digest, now

if __name__ == '__main__':
    checked = now()
    source = (ROOT / 'funds.js').read_text(encoding='utf8')
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(lambda c: collect(c, checked[:10]), CODES))
    report = {'schema': 2, 'checkedAt': checked, 'sourceSHA256': digest(source), 'observations': rows,
              'source': 'Eastmoney Tiantian Fund published NAV feed; complete identity-checked responses',
              'unchangedScope': 'Account, cash, stock quotes, performance and other historical profiles.'}
    (ROOT / 'funds_refresh_tmp.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    complete = sum(not row.get('error') for row in rows)
    print('Complete public NAV evidence: %d/4. funds.js unchanged.' % complete)
    raise SystemExit(0 if complete == 4 else 1)
