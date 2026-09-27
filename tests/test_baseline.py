import tempfile
import unittest
from pathlib import Path
from vesper.baseline import classify, run

class BaselineTests(unittest.TestCase):
    def result(self, body=None, code=0):
        with tempfile.TemporaryDirectory() as temp:
            if body is not None:
                Path(temp, "TEST-demo.xml").write_text(body)
            return classify(temp, code)["status"]

    def suite(self, case="<testcase classname='Demo' name='works'/>", tests=1, skipped=0, failures=0):
        return f"<testsuite tests='{tests}' skipped='{skipped}' failures='{failures}' errors='0'>{case}</testsuite>"

    def test_real_pass(self): self.assertEqual("passed", self.result(self.suite()))
    def test_nonzero_exit_not_pass(self): self.assertEqual("execution_failed", self.result(self.suite(), 1))
    def test_missing_reports(self): self.assertEqual("missing_reports", self.result())
    def test_zero_tests(self): self.assertEqual("zero_tests", self.result(self.suite("", tests=0)))
    def test_skipped_only(self): self.assertEqual("skipped_tests", self.result(self.suite("<testcase classname='Demo' name='works'><skipped/></testcase>", skipped=1)))
    def test_failure_even_with_zero_exit(self): self.assertEqual("tests_failed", self.result(self.suite("<testcase classname='Demo' name='works'><failure/></testcase>", failures=1)))
    def test_malformed_report(self): self.assertEqual("invalid_report", self.result("<broken"))
    def test_misleading_counts(self): self.assertEqual("invalid_report", self.result(self.suite("")))
    def test_missing_test_identity(self): self.assertEqual('invalid_report', self.result(self.suite('<testcase/>')))
    def test_duplicate_test_identity(self):
        case = "<testcase classname='Demo' name='works'/>"
        self.assertEqual('invalid_report', self.result(self.suite(case + case, tests=2)))
    def test_old_report_outside_fresh_directory_is_ignored(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); (root/'TEST-old.xml').write_text(self.suite()); (root/'fresh').mkdir()
            self.assertEqual('missing_reports', classify(root/'fresh',0)['status'])
    def test_missing_executable_records_environment_error(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); (root/'pom.xml').write_text('<project/>')
            self.assertEqual(1, run(root, root/'runs', str(root/'nonexistent-maven')))
            import json
            result=json.loads(next((root/'runs').glob('*/result.json')).read_text())
            self.assertEqual('environment_error', result['status'])

if __name__ == '__main__': unittest.main()
