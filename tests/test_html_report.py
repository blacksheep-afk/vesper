"""Evidence presentation must escape input and preserve blocked states."""
import json
from pathlib import Path
import tempfile
import unittest
from vesper.html_report import render_html

class HtmlReportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def render(self, **values):
        data = dict(status='blocked', explanation='No usable evidence', attempts=[])
        data.update(values)
        (self.root / 'workflow.json').write_text(json.dumps(data), encoding='utf-8')
        return render_html(self.root).read_text(encoding='utf-8')

    def test_escape_recorded_input(self):
        html = self.render(explanation='<script>alert(1)</script>', diff='<img onerror=alert(1)>')
        self.assertNotIn('<script>alert(1)</script>', html)
        self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt;', html)
        self.assertIn('&lt;img onerror=alert(1)&gt;', html)

    def test_blocked_run_does_not_invent_execution(self):
        html = self.render()
        self.assertIn('Verification blocked', html)
        self.assertEqual(5, html.count('>Not run<'))
        self.assertIn('No confirmed failure', html)
        self.assertNotIn('>900¢<', html)

    def test_synthetic_success_retains_disclosure(self):
        html = self.render(status='verified_candidate', evidence_kind='synthetic_fault_injection')
        self.assertIn('Synthetic challenge · no Java executed', html)
        self.assertIn('Pending review', html)
        self.assertIn('not performed', html)

    def test_attempt_path_cannot_escape_run(self):
        with self.assertRaises(ValueError):
            self.render(attempts=['../outside'])

    def test_no_remote_dependencies(self):
        html = self.render()
        self.assertNotIn('src="http', html)
        self.assertNotIn('href="http', html)
        self.assertIn('prefers-reduced-motion', html)
