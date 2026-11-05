"""Apply complete current-day public NAV evidence; account/cash fields are frozen."""
import json
from _funds_public_nav import ROOT, apply_report, now

if __name__ == '__main__':
    day = now()[:10]
    source = (ROOT / 'funds.js').read_text(encoding='utf8')
    report = json.loads((ROOT / 'funds_refresh_tmp.json').read_text(encoding='utf8'))
    fixture = json.loads((ROOT / '_funds_snapshot_2026-10-15.json').read_text(encoding='utf8'))
    updated, clean = apply_report(source, report, fixture, day)
    (ROOT / ('_funds_review_' + day + '.json')).write_text(json.dumps(clean, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    (ROOT / 'funds.js').write_text(updated, encoding='utf8')
    print('Public NAV changed: %s. Account, cash and historical profiles verified unchanged.' % clean['publicNAVChanged'])
