import copy, unittest
from _sync_research import SOURCE_ID, HEADERS, from_connector, validate

class ExportChecks(unittest.TestCase):
    def source(self):
        return dict(spreadsheetId=SOURCE_ID,sheetName='网站数据',sourceUpdatedAt='2026-10-21T08:43:22Z',syncedAt='2026-10-21T09:00:00Z',values=[HEADERS,['T001','2026-10-21','实验资源协调','计划中',1.5,'实验资源']])
    def test_exact_six_fields(self):
        d=from_connector(self.source());self.assertEqual(len(d['tasks'][0]),6);self.assertEqual(d['tasks'][0]['hours'],1.5)
    def test_wrong_file_rejected(self):
        s=self.source();s['spreadsheetId']='private-full-table'
        with self.assertRaises(ValueError):from_connector(s)
    def test_extra_column_rejected(self):
        s=self.source();s['values'][1].append('private evidence')
        with self.assertRaises(ValueError):from_connector(s)
    def test_header_change_rejected(self):
        s=self.source();s['values'][0]=HEADERS[:-1]+['证据路径']
        with self.assertRaises(ValueError):from_connector(s)
    def test_unreviewed_title_rejected(self):
        s=self.source();s['values'][1][2]='详细配方和原始记录'
        with self.assertRaises(ValueError):from_connector(s)
    def test_missing_hours_remain_unknown(self):
        s=self.source();s['values'][1][4]=None;self.assertIsNone(from_connector(s)['tasks'][0]['hours'])
    def test_duplicate_ids_rejected(self):
        s=self.source();s['values'].append(s['values'][1].copy())
        with self.assertRaises(ValueError):from_connector(s)
    def test_invalid_date_rejected(self):
        s=self.source();s['values'][1][1]='2026-02-30'
        with self.assertRaises(ValueError):from_connector(s)
    def test_changed_revision_rejected(self):
        d=from_connector(self.source());d['tasks'][0]['hours']=3
        with self.assertRaises(ValueError):validate(d)
    def test_zero_hours_valid(self):
        s=self.source();s['values'][1][4]=0;self.assertEqual(from_connector(s)['tasks'][0]['hours'],0)
    def test_boolean_hours_rejected(self):
        s=self.source();s['values'][1][4]=True
        with self.assertRaises(ValueError):from_connector(s)

if __name__=='__main__':unittest.main()
