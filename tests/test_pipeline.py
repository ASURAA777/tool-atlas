import copy, json, sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from research import validate, valid_url, response_text, sample, read, ROOT
from src.build import auth_groups, gate_group

class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.rows=read(ROOT/'data/research.json')
    def test_dataset_complete_and_valid(self):
        self.assertEqual(sorted(r['id'] for r in self.rows),list(range(1,101)))
        for row in self.rows: validate(row)
    def test_sample_reproducible_stratified(self):
        a=sample(self.rows); b=sample(list(reversed(self.rows)))
        self.assertEqual([r['id'] for r in a],[r['id'] for r in b])
        from collections import Counter
        self.assertEqual(set(Counter(r['category'] for r in a).values()),{2})
        self.assertEqual(len(a),20)
    def test_auth_versions_not_conflated(self):
        self.assertEqual(auth_groups(['OAuth1','OAuth2']),['OAuth1','OAuth2'])
        self.assertEqual(auth_groups(['API key']),['API key'])
        self.assertEqual(auth_groups(['Bearer token']),['Token'])
    def test_bad_evidence_and_verdict_rejected(self):
        r=copy.deepcopy(self.rows[0]); r['claims'][0]['url']='javascript:alert(1)'
        with self.assertRaises(ValueError): validate(r)
        r=copy.deepcopy(self.rows[0]); r['verdict']='guaranteed'
        with self.assertRaises(ValueError): validate(r)
    def test_response_parser_uses_message_only(self):
        value=response_text({'output':[{'type':'web_search_call','text':'ignore me'},{'type':'message','content':[{'type':'output_text','text':'{"ok":true}'}]}]})
        self.assertEqual(value,{'ok':True})
    def test_evidence_url_shape(self):
        self.assertFalse(valid_url('http://example.com'))
        self.assertFalse(valid_url('https://user:password@example.com'))
        self.assertTrue(valid_url('https://docs.example.com/auth'))

if __name__=='__main__': unittest.main()
