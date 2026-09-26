"""Synthetic runner fixtures: these results are not Maven execution evidence."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from vesper.workflow import SOURCE, TEST, execute, passing, report, run_demo


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / 'demo'
        for name, content in {
            'pom.xml': '<project/>', 'requirements.md': 'R3: expiry inclusive',
            SOURCE.as_posix(): 'correct source',
            'src/test/java/dev/vesper/ReproducerR3Test.java': 'frozen test',
            'evidence/seeded/Checkout.java.seeded': 'seeded source',
        }.items():
            path = self.project / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        self.mode = 'normal'

    def fake_execute(self, workspace, folder, maven, selector=None, timeout=120):
        folder.mkdir()
        (folder / 'reports').mkdir()
        (folder / 'execution.log').write_text('Synthetic unit-test fixture, not Maven evidence')
        original = 'original' in folder.name
        failed = original and self.mode != 'not_reproduced'
        if self.mode == 'flaky' and 'repeat' in folder.name:
            failed = False
        ids = [TEST] if selector else ['dev.vesper.CheckoutTest#existing', TEST]
        if self.mode == 'missing_test' and 'regression' in folder.name:
            ids = [TEST]
        failure = '<failure type="org.opentest4j.AssertionFailedError" message="expected: &lt;900&gt; but was: &lt;1000&gt;"/>' if failed else ''
        (folder / 'reports/TEST-demo.xml').write_text(
            '<testsuite><testcase>' + failure + '</testcase></testsuite>')
        record = dict(status='execution_failed' if failed else 'passed', exit_code=1 if failed else 0,
                      counts=dict(tests=len(ids), failures=int(failed), errors=0, skipped=0),
                      test_ids=ids, duration_seconds=0, inputs_unchanged=True)
        if self.mode == 'environment_error':
            record.update(status='environment_error', exit_code=None)
        if self.mode == 'compile_error' and original:
            record.update(counts=dict(tests=0, failures=0, errors=0, skipped=0), test_ids=[])
        if self.mode == 'mutated_test' and 'repeat' in folder.name:
            next((workspace / 'src/test').rglob('*.java')).write_text('changed assertion')
        (folder / 'result.json').write_text(json.dumps(record))
        return record

    def workflow(self):
        with patch('vesper.workflow.execute', side_effect=self.fake_execute), patch('vesper.workflow.capture', return_value={'output': 'fixture'}):
            directory = run_demo(self.project, self.root / 'runs', 'fake', evidence_kind='synthetic_fault_injection')
        return directory, json.loads((directory / 'workflow.json').read_text())

    def test_complete_sequence_and_report_keep_approval_pending(self):
        directory, data = self.workflow()
        self.assertEqual('verified_candidate', data['status'])
        self.assertEqual(5, len(data['attempts']))
        self.assertEqual('pending', data['approval'])
        self.assertEqual('correct source', (self.project / SOURCE).read_text())
        self.assertIn('-seeded source', data['diff'])
        self.assertIn('pending review', report(directory).read_text(encoding='utf-8'))

    def test_setup_failure_blocks_before_investigation(self):
        self.mode = 'environment_error'
        _, data = self.workflow()
        self.assertEqual('unresolved', data['investigation'])
        self.assertEqual(1, len(data['attempts']))

    def test_passing_original_is_not_reproduced(self):
        self.mode = 'not_reproduced'
        _, data = self.workflow()
        self.assertEqual('not_reproduced', data['investigation'])
        self.assertEqual('not_attempted', data['repair'])

    def test_inconsistent_original_is_flaky(self):
        self.mode = 'flaky'
        self.assertEqual('flaky', self.workflow()[1]['investigation'])

    def test_compile_error_is_not_a_bug(self):
        self.mode = 'compile_error'
        self.assertEqual('unresolved', self.workflow()[1]['investigation'])

    def test_missing_regression_identity_blocks_verification(self):
        self.mode = 'missing_test'
        self.assertEqual('verification_failed', self.workflow()[1]['repair'])

    def test_changed_reproducer_blocks_candidate(self):
        self.mode = 'mutated_test'
        _, data = self.workflow()
        self.assertEqual('blocked', data['status'])
        self.assertEqual(3, len(data['attempts']))

    def test_duplicate_test_ids_do_not_pass(self):
        self.assertFalse(passing(dict(status='passed', test_ids=[TEST, TEST])))

    def test_real_missing_executable_is_recorded(self):
        result = execute(self.project, self.root / 'attempt', str(self.root / 'missing-maven'))
        self.assertEqual('environment_error', result['status'])
        self.assertTrue((self.root / 'attempt/result.json').is_file())

    def test_attempt_directory_cannot_reuse_stale_reports(self):
        folder = self.root / 'attempt'
        folder.mkdir()
        with self.assertRaises(FileExistsError):
            execute(self.project, folder, 'unused')


if __name__ == '__main__':
    unittest.main()
