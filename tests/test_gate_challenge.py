"""Test experiment bookkeeping, not fabricated Java outcomes."""
import json
from pathlib import Path
import tempfile
import unittest

from experiments.gate_challenge import REPO, SCENARIOS, inventory, run_case, summarize


class GateChallengeTests(unittest.TestCase):
    def test_case_identifiers_and_expected_labels_are_valid(self):
        self.assertEqual(len(SCENARIOS), len({s.name for s in SCENARIOS}))
        self.assertEqual({'accept', 'reject'}, {s.expected for s in SCENARIOS})

    def test_control_runs_actual_workflow_in_copy_and_records_provenance(self):
        before = inventory(REPO / 'demo')
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / 'control'
            record = run_case(SCENARIOS[0], folder)
            self.assertEqual('accept', record['observed'])
            self.assertTrue(record['synthetic'])
            self.assertTrue(record['executor_calls'])
            self.assertEqual(record, json.loads((folder / 'result.json').read_text()))
            self.assertEqual([], record['changed_demo_files'])
        self.assertEqual(before, inventory(REPO / 'demo'))

    def test_changed_assertion_fixture_actually_changes_only_the_copy(self):
        before = inventory(REPO / 'demo')
        scenario = next(s for s in SCENARIOS if s.name == 'changed_assertion')
        with tempfile.TemporaryDirectory() as temp:
            result = run_case(scenario, Path(temp) / 'mutation')
            self.assertEqual(1, len(result['injected_mutations']))
            self.assertTrue(result['injected_mutations'][0].replace('\\', '/').endswith('src/test/java/dev/vesper/ReproducerR3Test.java'))
            self.assertEqual('reject', result['observed'])
        self.assertEqual(before, inventory(REPO / 'demo'))

    def test_every_known_adversarial_case_is_rejected_without_crashing(self):
        with tempfile.TemporaryDirectory() as temp:
            for scenario in SCENARIOS[1:]:
                with self.subTest(case=scenario.name):
                    result = run_case(scenario, Path(temp) / scenario.name)
                    self.assertEqual('reject', result['observed'])
                    self.assertIsNone(result['crash'])

    def test_existing_case_output_cannot_be_reused(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(FileExistsError):
                run_case(SCENARIOS[0], Path(temp))

    def test_crashes_are_not_counted_as_controlled_rejections(self):
        records = [
            dict(expected='reject', observed='accept', conforms=False),
            dict(expected='reject', observed='crash', conforms=False),
            dict(expected='accept', observed='reject', conforms=False),
            dict(expected='reject', observed='reject', conforms=True),
        ]
        self.assertEqual(dict(cases=4, conforming=1, false_acceptances=1, false_rejections=1, crashes=1), summarize(records))


if __name__ == '__main__':
    unittest.main()
