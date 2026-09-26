"""Challenge the actual workflow gate using synthetic Maven results.

No Java, Maven, model, or external service is executed. Only disposable copies
of the supplied demo are modified. The workflow orchestration and parser are real.
"""
import argparse
from contextlib import contextmanager, redirect_stdout
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import types
from unittest.mock import patch
import uuid
import xml.etree.ElementTree as ET

from vesper import workflow

REPO = Path(__file__).resolve().parents[1]
MERGED_REVISION = '0b882ce815bced03a5dd4a5bac70715c79d3140f'
TEST = Path('demo/src/test/java/dev/vesper/ReproducerR3Test.java')
TARGET = ('dev.vesper.ReproducerR3Test', 'expiryDayMustReceiveDiscount_R3')
EXISTING = ('dev.vesper.CheckoutTest', 'syntheticExistingRegressionControl')


@dataclass(frozen=True)
class Scenario:
    name: str
    expected: str
    explanation: str


SCENARIOS = (
    Scenario('valid_control', 'accept', 'Consistent valid evidence; unchanged test and complete synthetic suite.'),
    Scenario('no_target_reports', 'reject', 'Successful command but no targeted XML reports.'),
    Scenario('zero_target_tests', 'reject', 'Targeted report contains no test cases.'),
    Scenario('skipped_target', 'reject', 'The required reproducer is skipped.'),
    Scenario('wrong_target', 'reject', 'Only an unrelated test passes at verification.'),
    Scenario('changed_assertion', 'reject', 'The reproducer expectation changes from 900 to 1000 before verification.'),
    Scenario('dropped_regression', 'reject', 'A baseline test disappears from candidate regression.'),
    Scenario('duplicate_regression', 'reject', 'Duplicate identities replace distinct baseline tests.'),
    Scenario('not_reproduced', 'reject', 'The original targeted test passes; no defect was established.'),
    Scenario('unrelated_failure', 'reject', 'The original fails with an unrelated assertion instead of the accepted expectation.'),
    Scenario('setup_failure', 'reject', 'Original execution fails before tests run.'),
    Scenario('flaky_original', 'reject', 'A repeat original targeted run would pass after the first fails.'),
    Scenario('inconsistent_xml_counts', 'reject', 'XML claims zero tests while containing a passing case.'),
    Scenario('malformed_report', 'reject', 'Targeted XML is truncated; a recorded rejection is required, not a crash.'),
    Scenario('candidate_failure', 'reject', 'The candidate reproducer still fails.'),
    Scenario('regression_failure', 'reject', 'The candidate breaks an existing test.'),
)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def inventory(root):
    return {p.relative_to(root).as_posix(): sha(p) for p in sorted(root.rglob('*')) if p.is_file()}


@contextmanager
def working_directory(path):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def write_suite(folder, cases, wrong_counts=False):
    counts = dict(tests=len(cases), failures=0, errors=0, skipped=0)
    root = ET.Element('testsuite', name='SYNTHETIC_GATE_CHALLENGE')
    for identity, status, message in cases:
        case = ET.SubElement(root, 'testcase', classname=identity[0], name=identity[1])
        if status != 'passed':
            ET.SubElement(case, status, message=message,
                          type='org.opentest4j.AssertionFailedError' if status == 'failure' else 'synthetic')
            counts[{'failure': 'failures', 'error': 'errors', 'skipped': 'skipped'}[status]] += 1
    for key, value in counts.items():
        root.set(key, str(0 if wrong_counts and key == 'tests' else value))
    ET.ElementTree(root).write(folder / 'TEST-synthetic.xml', encoding='utf-8', xml_declaration=True)


class SyntheticMaven:
    def __init__(self, scenario, workspace):
        self.scenario = scenario
        self.workspace = workspace
        self.calls = []
        self.original_attempts = 0
        self.mutations = []

    def __call__(self, args, project, timeout, label):
        reports = Path(next(x.split('=', 1)[1] for x in args if x.startswith('-Dvesper.reportsDirectory=')))
        self.calls.append({'stage': label, 'args': args, 'project': str(project), 'synthetic': True})
        return self.emit(reports, label, self.workspace / TEST)

    def popen(self, command, cwd, stdout, stderr, start_new_session=False):
        """Fake only the process boundary; repaired execute() and classify() run."""
        reports = Path(next(x.split('=', 1)[1] for x in command if x.startswith('-Dvesper.reportsDirectory=')))
        phase = {'01-baseline': 'baseline', '02-original': 'reproduce',
                 '03-original-repeat': 'reproduce', '04-candidate-reproducer': 'verify',
                 '05-candidate-regression': 'regress_fix'}[reports.parent.name]
        self.calls.append({'stage': phase, 'args': command, 'project': str(cwd), 'synthetic': True})
        code, output, duration = self.emit(reports, phase, Path(cwd) / TEST.relative_to('demo'))
        stdout.write(output)
        stdout.flush()
        if code is None:
            raise OSError('SYNTHETIC Maven setup failure')
        return types.SimpleNamespace(wait=lambda timeout=None: code)

    def emit(self, reports, label, test):
        name = self.scenario.name
        passed = (TARGET, 'passed', '')
        existing = (EXISTING, 'passed', '')
        failed = (TARGET, 'failure', 'expected: <900> but was: <1000>')
        cases, code = [passed, existing], 0
        if label == 'reproduce':
            self.original_attempts += 1
            cases, code = [failed], 1
            if name == 'not_reproduced' or (name == 'flaky_original' and self.original_attempts > 1):
                cases, code = [passed], 0
            elif name == 'unrelated_failure':
                cases = [(TARGET, 'failure', 'Unrelated assertion: expected: <1> but was: <2>')]
            elif name == 'setup_failure':
                return None, 'SYNTHETIC setup failure; Maven was not executed', 0.0
        elif label == 'regress_bug':
            cases, code = [failed, existing], 1
            if name == 'not_reproduced':
                cases, code = [passed, existing], 0
        elif label == 'verify':
            cases = [passed]
            if name == 'no_target_reports':
                return 0, 'SYNTHETIC success with absent reports', 0.0
            if name == 'zero_target_tests':
                cases = []
            elif name == 'skipped_target':
                cases = [(TARGET, 'skipped', 'Synthetic skip')]
            elif name == 'wrong_target':
                cases = [existing]
            elif name == 'changed_assertion':
                original = test.read_bytes()
                changed = original.replace(b'900L,', b'1000L,')
                if original == changed:
                    raise ValueError('Fixture no longer contains the expected assertion')
                test.write_bytes(changed)
                self.mutations.append(str(test.relative_to(self.workspace)))
            elif name == 'malformed_report':
                (reports / 'TEST-synthetic.xml').write_text('<testsuite><testcase>')
                return 0, 'SYNTHETIC truncated XML', 0.0
            elif name == 'candidate_failure':
                cases, code = [failed], 1
        elif label == 'regress_fix':
            if name == 'dropped_regression':
                cases = [passed]
            elif name == 'duplicate_regression':
                cases = [passed, passed]
            elif name == 'regression_failure':
                cases, code = [passed, (EXISTING, 'failure', 'Synthetic regression')], 1
        write_suite(reports, cases, wrong_counts=name == 'inconsistent_xml_counts' and label == 'verify')
        return code, 'SYNTHETIC fixture: Java/Maven were not executed', 0.0


def run_case(scenario, folder, runner=None):
    runner = runner or workflow
    folder.mkdir(parents=True, exist_ok=False)
    workspace = folder / 'workspace'
    shutil.copytree(REPO / 'demo', workspace / 'demo', ignore=shutil.ignore_patterns('target'))
    before = inventory(workspace / 'demo')
    executor = SyntheticMaven(scenario, workspace)
    console = io.StringIO()
    started = time.perf_counter()
    crash, code = None, None
    with working_directory(workspace), redirect_stdout(console):
        try:
            if hasattr(runner, 'run_demo'):
                with patch.object(runner.subprocess, 'Popen', side_effect=executor.popen), patch.object(
                        runner, 'capture', return_value={'exit_code': 0, 'output': 'SYNTHETIC tool version'}):
                    result_dir = runner.run_demo(workspace / 'demo', workspace / '.vesper/runs', 'synthetic-maven', 1)
                result = json.loads((result_dir / 'workflow.json').read_text(encoding='utf-8'))
                code = 0 if result['status'] == 'verified_candidate' else 1
            else:
                with patch.object(runner, '_mvn', side_effect=executor):
                    code = runner.run_workflow(1)
        except Exception as exc:
            crash = type(exc).__name__ + ': ' + str(exc)
    after = inventory(workspace / 'demo')
    observed = 'crash' if crash else ('accept' if code == 0 else 'reject')
    record = dict(case=scenario.name, expected=scenario.expected, observed=observed,
                  conforms=observed == scenario.expected, explanation=scenario.explanation,
                  exit_code=code, crash=crash, synthetic=True,
                  elapsed_seconds=round(time.perf_counter() - started, 6),
                  original_targeted_attempts=executor.original_attempts,
                  injected_mutations=executor.mutations,
                  changed_demo_files=sorted(k for k in before.keys() | after.keys() if before.get(k) != after.get(k)),
                  input_hashes=before, final_hashes=after, executor_calls=executor.calls)
    (folder / 'console.txt').write_text(console.getvalue(), encoding='utf-8')
    (folder / 'result.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    return record


def summarize(records):
    return dict(cases=len(records), conforming=sum(r['conforms'] for r in records),
                false_acceptances=sum(r['expected'] == 'reject' and r['observed'] == 'accept' for r in records),
                false_rejections=sum(r['expected'] == 'accept' and r['observed'] == 'reject' for r in records),
                crashes=sum(r['observed'] == 'crash' for r in records))


def load_runner(selection):
    if selection == 'current':
        return workflow, (REPO / 'vesper/workflow.py').read_bytes()
    source = subprocess.check_output(['git', 'show', MERGED_REVISION + ':vesper/workflow.py'], cwd=REPO)
    module = types.ModuleType('vesper._merged_challenge_reference')
    exec(compile(source, 'merged-reference-workflow.py', 'exec'), module.__dict__)
    return module, source


def run(output, selection='current'):
    output = Path(output).resolve()
    if output == REPO / 'demo' or REPO / 'demo' in output.parents:
        raise ValueError('Experiment output must be outside the accepted demo')
    run_dir = output / ('gate-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8])
    run_dir.mkdir(parents=True, exist_ok=False)
    accepted_before = inventory(REPO / 'demo')
    runner, runner_bytes = load_runner(selection)
    records = [run_case(s, run_dir / s.name, runner) for s in SCENARIOS]
    if inventory(REPO / 'demo') != accepted_before:
        raise RuntimeError('Accepted demo changed during experiment')
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip()
    summary = summarize(records)
    data = dict(experiment='gate-qualification-v1', evidence_kind='synthetic_fault_injection',
                generated_at=datetime.now(timezone.utc).isoformat(), source_revision=revision,
                runner=selection, reference_revision=MERGED_REVISION if selection == 'merged' else None,
                workflow_sha256=hashlib.sha256(runner_bytes).hexdigest(), harness_sha256=sha(Path(__file__)),
                python=sys.version, accepted_demo_unchanged=True, summary=summary, cases=records,
                agent_comparison='NOT_RUN', java_maven_execution='NOT_RUN')
    (run_dir / 'results.json').write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    lines = ['# Gate qualification result', '',
             '**Synthetic fault injection. No agent session, Java execution or productivity measurement.**', '',
             f'Repository revision: `{revision}`. Workflow bytes: `{data["workflow_sha256"]}`.', '',
             'The actual workflow and XML parser ran; process execution and version capture used labeled fixtures.',
             f'Runner selection: `{selection}`. The merged reference is pinned, not an alternative candidate implementation.',
             'One fixture baseline has two synthetic identities; these are not the real Java suite totals.', '',
             f'Conforming cases: {summary["conforming"]}/{summary["cases"]}; false acceptances: {summary["false_acceptances"]}; '
             f'false rejections: {summary["false_rejections"]}; crashes: {summary["crashes"]}.', '',
             '| Case | Expected | Observed | Result |', '| --- | --- | --- | --- |']
    lines += [f'| [{r["case"]}]({r["case"]}/result.json) | {r["expected"]} | {r["observed"]} | {"PASS" if r["conforms"] else "FAIL"} |' for r in records]
    lines += ['', 'A crash blocks acceptance but is reported separately from a controlled rejection.',
              'The flaky fixture passes on a second original attempt; each case records how many attempts the runner requested.',
              'Accepted repository source stayed unchanged; mutations occurred only in per-case copies.', '',
              'This measures mechanical gate behavior, not how often Codex makes mistakes or whether Vesper saves time.',
              'These known challenge cases are development checks, not an unseen effectiveness benchmark.']
    (run_dir / 'report.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return run_dir, data


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='.vesper/experiments')
    parser.add_argument('--runner', choices=['current', 'merged'], default='current',
                        help='Compare current code with the pinned pre-repair merged workflow')
    args = parser.parse_args(argv)
    directory, data = run(args.output, args.runner)
    print(directory / 'report.md')
    print(json.dumps(data['summary']))
    return 0 if data['summary']['conforming'] == data['summary']['cases'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
