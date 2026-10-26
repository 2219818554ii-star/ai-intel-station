"""Native research export checks: no network, private-source reads or writes."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
import _sync_research_details as export

ROOT=Path(__file__).resolve().parent

class NativeResearchExportChecks(unittest.TestCase):
    def setUp(self):
        self.summary=json.loads((ROOT/'research-data.json').read_text(encoding='utf-8'))
        self.bundle=json.loads((ROOT/'research-details.json').read_text(encoding='utf-8'))

    def test_valid_exact_coverage_and_same_release(self):
        self.assertIs(export.validate_bundle(self.bundle,self.summary),self.bundle)
        self.assertEqual({t['id'] for t in self.summary['tasks']},{t['id'] for t in self.bundle['tasks']})
        self.assertEqual(len(self.bundle['tasks']),136)
        self.assertEqual(len(self.bundle['records']),5)
        self.assertEqual(export.digest(self.bundle['tasks'],self.bundle['records']),export.APPROVED_RELEASE_DIGESTS[self.bundle['sourceReleaseId']])

    def test_changed_body_cannot_self_certify_by_recomputing_its_digest(self):
        self.bundle['tasks'][0]['steps']='Unreviewed replacement'
        self.bundle['contentDigest']=export.digest(self.bundle['tasks'],self.bundle['records'])
        with self.assertRaises(ValueError):export.validate_bundle(self.bundle,self.summary)

    def test_summary_or_release_mismatch_fails_closed(self):
        for key,value in [('summaryRevision','0'*16),('sourceReleaseId','0'*20),('contentDigest','0'*64)]:
            b=deepcopy(self.bundle);b[key]=value
            with self.assertRaises(ValueError):export.validate_bundle(b,self.summary)

    def test_unknown_fields_and_private_paths_are_not_silently_exported(self):
        variants=[]
        for field,value in [('evidence','private'),('credentials','not-for-public')]:
            b=deepcopy(self.bundle);b['tasks'][0][field]=value;variants.append(b)
        for value in ['https://private.example/record','file:///local-record','X:/private/record','password API_KEY=example','contact@example.org','13800000000']:
            b=deepcopy(self.bundle);b['tasks'][0]['progress']=value;variants.append(b)
        for b in variants:
            with self.assertRaises(ValueError):export.validate_bundle(b,self.summary)

    def test_task_coverage_and_record_association(self):
        variants=[]
        b=deepcopy(self.bundle);b['tasks'].pop();variants.append(b)
        b=deepcopy(self.bundle);b['tasks'][1]['id']=b['tasks'][0]['id'];variants.append(b)
        b=deepcopy(self.bundle);b['records'][0]['taskIds']=['T99999'];variants.append(b)
        b=deepcopy(self.bundle);b['records'].append(deepcopy(b['records'][0]));variants.append(b)
        for b in variants:
            with self.assertRaises(ValueError):export.validate_bundle(b,self.summary)

    def test_unknown_actual_hours_stay_null_and_explicit_zero_stays_zero(self):
        self.assertTrue(all(r[k] is None for r in self.bundle['records'] for k in ['start','end','activeHours','waitingHours','travelHours','breakMinutes']))
        self.assertIsNone(export.actual(None));self.assertEqual(export.actual(0),0)
        for invalid in [-1,True,float('inf'),25]:
            with self.assertRaises(ValueError):export.actual(invalid,24)

    def test_private_columns_and_raw_measurements_are_absent(self):
        self.assertTrue(all(set(t)==set(export.TASK_KEYS) for t in self.bundle['tasks']))
        self.assertTrue(all(set(r)==set(export.RECORD_KEYS) for r in self.bundle['records']))
        text=json.dumps(self.bundle,ensure_ascii=False)
        self.assertNotIn('spreadsheetId',text);self.assertNotIn('evidence',text);self.assertNotIn('ocv-data',text)

    def test_unreviewed_original_release_is_rejected(self):
        with self.assertRaises(ValueError):export.make_bundle({'schemaVersion':1,'releaseId':'0'*20},{'schemaVersion':1,'releaseId':'0'*20},self.summary)

if __name__=='__main__':unittest.main()
