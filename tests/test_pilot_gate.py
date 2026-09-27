"""Regression checks for the post-pilot control false rejection."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from experiments.pilot_gate import gate

class PilotControlTests(unittest.TestCase):
    def check_control(self, candidate_ids):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for name in ['original','candidate']:
                project=root/name
                for filename in ['pom.xml','requirements.md','src/main/java/Example.java','src/test/java/ExistingTest.java']:
                    p=project/filename;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('unchanged',encoding='utf-8')
            (root/'candidate/src/test/java/AdditionalTest.java').write_text('new test',encoding='utf-8')
            def execute(workspace,folder,maven,selector,timeout):
                ids=['Existing#test'] if folder.name=='01-baseline' else candidate_ids
                return dict(status='passed',test_ids=ids,inputs_unchanged=True)
            with patch('experiments.pilot_gate.execute',side_effect=execute):
                result,_=gate(root/'original',root/'candidate',None,None,'unused',root/'runs')
            return result['status']

    def test_added_passing_control_test_is_allowed(self):
        self.assertEqual('accepted_no_change',self.check_control(['Existing#test','Additional#test']))

    def test_missing_required_control_identity_is_blocked(self):
        self.assertEqual('blocked',self.check_control(['Additional#test']))
