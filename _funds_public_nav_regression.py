"""Reject unsafe/stale evidence and preserve account/cash/archive boundaries."""
import copy
import datetime as dt
import json
import unittest
from _funds_public_nav import ROOT, TZ, CODES, now, digest, parse_nav, read_values, apply_report

class PublicNAVTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=(ROOT/'funds.js').read_text(encoding='utf8')
        cls.before=read_values(cls.source)
        cls.fixture=json.loads((ROOT/'_funds_snapshot_2026-10-15.json').read_text(encoding='utf8'))
        cls.day=now()[:10]

    def report(self,changed=False,nav_day=None):
        rows=[]
        for code in CODES:
            old=next(h for h in self.before['FUNDS_HOLD'] if h['code']==code)
            date=nav_day or old['navDate']
            raw={'x':int(dt.datetime.fromisoformat(date).replace(tzinfo=TZ).timestamp()*1000),'y':old['unit']+(0.01 if changed else 0),'equityReturn':old['dayPct']*100}
            body='var fS_code="'+code+'";var fS_name="Official test fund";var Data_netWorthTrend='+json.dumps([raw])+';'
            rows.append({'code':code,'url':'https://fund.eastmoney.com/pingzhongdata/'+code+'.js','httpStatus':'200','curlExit':0,'complete':True,'checkedAtTime':now(),'completedAt':now(),'sha256':digest(body),'bytes':len(body.encode()),'rawBody':body,**parse_nav(body,code,self.day)})
        return {'schema':2,'sourceSHA256':digest(self.source),'checkedAt':now(),'observations':rows}

    def apply(self,report):return apply_report(self.source,report,self.fixture,self.day)

    def test_changed_nav_preserves_every_nonpublic_field(self):
        source,proof=self.apply(self.report(changed=True))
        after=read_values(source)
        self.assertTrue(proof['publicNAVChanged'])
        self.assertEqual(after['FUNDS_CASH'],self.before['FUNDS_CASH'])
        self.assertEqual(after['FUNDS_STOCKS'],self.before['FUNDS_STOCKS'])
        for a,b in zip(self.before['FUNDS_HOLD'],after['FUNDS_HOLD']):
            self.assertEqual({k:v for k,v in a.items() if k not in ('unit','dayPct','navDate')},{k:v for k,v in b.items() if k not in ('unit','dayPct','navDate')})
        self.assertTrue(all('rawBody' not in r for r in proof['observations']))

    def test_unchanged_nav_never_rolls_content_or_application_date(self):
        source,proof=self.apply(self.report())
        after=read_values(source)
        self.assertFalse(proof['publicNAVChanged'])
        for key in self.before:
            if key not in ('FUNDS_CHECKED','FUNDS_CHECK_NOTE'):self.assertEqual(after[key],self.before[key],key)

    def test_incomplete_or_tampered_sources_fail_before_write(self):
        changes=[lambda r:r.update(complete=False),lambda r:r.update(curlExit=28),lambda r:r.update(httpStatus='412'),lambda r:r.update(url='https://other.example/feed'),lambda r:r.update(rawBody=r['rawBody']+' '),lambda r:r['nav'].update(unit=99),lambda r:r.update(checkedAtTime=self.day+'T23:59:59+08:00')]
        for change in changes:
            report=self.report();change(report['observations'][0])
            with self.subTest(change=repr(change)),self.assertRaises(ValueError):self.apply(report)

    def test_identity_future_missing_return_and_date_regression_rejected(self):
        body='var fS_code="012920";var fS_name="Test";var Data_netWorthTrend=[{"x":1794844800000,"y":1,"equityReturn":2}];'
        with self.assertRaises(ValueError):parse_nav(body,'016452',self.day)
        with self.assertRaises(ValueError):parse_nav(body,'012920','2026-01-01')
        with self.assertRaises(ValueError):parse_nav(body.replace(',"equityReturn":2',''),'012920','2027-01-01')
        with self.assertRaises(ValueError):self.apply(self.report(nav_day='2026-01-01'))

    def test_legacy_stale_and_missing_identity_rejected(self):
        with self.assertRaises(ValueError):self.apply({'nav':{},'astk':{},'ustk':{}})
        report=self.report();report['sourceSHA256']='0'*64
        with self.assertRaises(ValueError):self.apply(report)
        report=self.report();report['observations'].pop()
        with self.assertRaises(ValueError):self.apply(report)

    def test_snapshot_drift_is_not_accepted_as_a_new_baseline(self):
        fixture=copy.deepcopy(self.fixture);fixture['funds'][0]['amt']+=1
        with self.assertRaises(ValueError):apply_report(self.source,self.report(changed=True),fixture,self.day)

if __name__=='__main__':unittest.main()
