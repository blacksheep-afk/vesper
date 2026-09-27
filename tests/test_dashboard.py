import json
from pathlib import Path
import tempfile
import unittest

from vesper.dashboard import saved_events
from vesper.web_server import create_web_ui_files


class DashboardTests(unittest.TestCase):
    def test_failed_saved_run_is_not_reported_as_passed(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / 'result.json').write_text(json.dumps({'stages': [
                {'stage': 'regress_bug', 'exit_code': 1},
                {'stage': 'verify', 'status': 'verified'},
                {'stage': 'regress_fix', 'status': 'failed'}], 'total_duration_seconds': 1.25}))
            events = saved_events(folder)
            self.assertEqual(events[0][1]['status'], 'failed')
            self.assertEqual(events[-1][1]['status'], 'failed')

    def test_assets_are_validated_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / 'index.html').write_text('existing')
            with self.assertRaises(FileNotFoundError):
                create_web_ui_files(folder)
            for name in ('styles.css', 'app.js'):
                (folder / name).write_text('custom')
            create_web_ui_files(folder)
            self.assertEqual((folder / 'styles.css').read_text(), 'custom')
