"""Sequential evidence workflow for the disclosed checkout R3 demonstration."""
import argparse
import difflib
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid
import xml.etree.ElementTree as ET

from .baseline import capture, classify

SOURCE = Path('src/main/java/dev/vesper/Checkout.java')
TEST = 'dev.vesper.ReproducerR3Test#expiryDayMustReceiveDiscount_R3'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def inventory(root):
    return {p.relative_to(root).as_posix(): digest(p)
            for p in sorted(Path(root).rglob('*')) if p.is_file()
            and 'target' not in p.relative_to(root).parts}


def snapshot(source, destination):
    # Only the trusted demo's build and source inputs; no historical outputs.
    inputs = [source / 'pom.xml', source / 'requirements.md']
    inputs += list((source / 'src').rglob('*'))
    if any(p.is_symlink() or (hasattr(p, 'is_junction') and p.is_junction()) for p in [source, source / 'src', *inputs]):
        raise ValueError('Linked demo inputs are not supported')
    destination.mkdir()
    for p in inputs:
        if p.is_file():
            target = destination / p.relative_to(source)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, target)


def execute(workspace, folder, maven, selector=None, timeout=120):
    folder.mkdir()
    reports = folder / 'reports'
    reports.mkdir()
    command = [maven, '-B', 'clean', 'test', '-Dvesper.reportsDirectory=' + str(reports),
               '-DfailIfNoTests=true', '-Dsurefire.failIfNoSpecifiedTests=true']
    if selector:
        command.append('-Dtest=' + selector)
    record = {'command': command, 'workspace': str(workspace), 'started_at': time.time()}
    before = inventory(workspace)
    try:
        with (folder / 'execution.log').open('w', encoding='utf-8') as log:
            process = subprocess.Popen(command, cwd=workspace, stdout=log, stderr=subprocess.STDOUT,
                                       start_new_session=os.name != 'nt')
            try:
                code = process.wait(timeout=timeout)
            except (subprocess.TimeoutExpired, KeyboardInterrupt) as exc:
                if os.name == 'nt':
                    subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    import signal
                    os.killpg(process.pid, signal.SIGKILL)
                process.wait()
                record.update(status='timeout' if isinstance(exc, subprocess.TimeoutExpired) else 'interrupted', exit_code=None)
            else:
                record.update(classify(reports, code), exit_code=code)
    except OSError as exc:
        record.update(status='environment_error', exit_code=None, error=str(exc))
    record['inputs_unchanged'] = before == inventory(workspace)
    if not record['inputs_unchanged']:
        record['status'] = 'inputs_changed'
    record['duration_seconds'] = round(time.time() - record['started_at'], 3)
    (folder / 'result.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
    return record


def passing(record, expected=None):
    ids = record.get('test_ids', [])
    return (record['status'] == 'passed' and bool(ids) and len(ids) == len(set(ids))
            and (expected is None or set(ids) == set(expected)))


def r3_failure(record, folder):
    if (record['status'] != 'execution_failed' or record.get('exit_code') != 1
            or record.get('counts') != dict(tests=1, failures=1, errors=0, skipped=0)
            or record.get('test_ids') != [TEST]):
        return False
    for path in (folder / 'reports').glob('TEST-*.xml'):
        for case in ET.parse(path).getroot().findall('testcase'):
            failure = case.find('failure')
            if failure is not None:
                message = failure.get('message', '')
                return ('expected: <900> but was: <1000>' in message
                        and failure.get('type') == 'org.opentest4j.AssertionFailedError')
    return False


def report(run_dir):
    run_dir = Path(run_dir).resolve()
    data = json.loads((run_dir / 'workflow.json').read_text(encoding='utf-8'))
    lines = ['# Vesper evidence report', '', '**Disclosed seeded demonstration — not an organic finding.**', '',
             'Requirement R3: discounts remain valid on the expiry date.',
             'Input: 1000 cents, 10% discount, checkout and expiry 2026-09-25. Expected: 900 cents.', '',
             f"Workflow: **{data['status']}**", f"Investigation: **{data['investigation']}**",
             f"Candidate: **{data['repair']}**", 'Human decision: **pending review**',
             'Integration: **not performed by this workflow**',
             f"Elapsed: {data['duration_seconds']} seconds (this invocation only).", '',
             'The expected result is specified by demo/requirements.md. This replay does not record a new human approval.', '',
             '| Stage | Execution status | Tests / failures / errors / skipped | Seconds | Evidence |',
             '| --- | --- | --- | --- | --- |']
    for name in data['attempts']:
        item = json.loads((run_dir / name / 'result.json').read_text(encoding='utf-8'))
        counts = item.get('counts', {})
        tally = ' / '.join(str(counts.get(k, '—')) for k in ('tests', 'failures', 'errors', 'skipped'))
        lines.append(f"| {name} | {item['status']} | {tally} | {item['duration_seconds']} | [record]({name}/result.json), [log]({name}/execution.log) |")
    lines += ['', '## Findings and unresolved work', '', data['explanation'], '',
              'A passing reproducer means not reproduced. Setup failures do not demonstrate an application bug.', '',
              '## Candidate patch', '', '```diff', data.get('diff', '(No patch prepared.)').rstrip(), '```', '',
              '## Provenance and limits', '', '[Run metadata, versions and input hashes](workflow.json).',
              '[Original snapshot](original/) · [Candidate snapshot](candidate/) · [Baseline snapshot](baseline/)', '',
              'The candidate is the existing corrected demo source; this command does not generate an AI repair.',
              'This workflow supports the supplied Maven demo and its R3 test only. It does not prove general correctness.',
              'No productivity improvement, Bob usage or Bobcoin consumption has been measured here.',
              'Bob session screenshots must be captured from actual Bob sessions.']
    destination = run_dir / 'report.md'
    destination.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return destination


def run_demo(project, output, maven, timeout=120):
    project, output = Path(project).resolve(), Path(output).resolve()
    if timeout <= 0:
        raise ValueError('Timeout must be positive')
    # Do not recursively include run output in input snapshots.
    if output == project or project in output.parents and 'src' in output.relative_to(project).parts:
        raise ValueError('Output must not replace the demo or be inside source inputs')
    run_dir = output / ('workflow-' + time.strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:8])
    run_dir.mkdir(parents=True)
    data = dict(schema_version=1, mode='disclosed-r3-replay', status='blocked', investigation='unresolved',
                repair='not_attempted', approval='pending', integration='not_performed',
                started_at=time.time(), python=sys.version, attempts=[], explanation='Workflow did not complete.')

    def attempt(name, workspace, selector=None):
        result = execute(workspace, run_dir / name, maven, selector, timeout)
        data['attempts'].append(name)
        return result

    try:
        data['input_hashes'] = inventory(project / 'src')
        data['requirement_sha256'] = digest(project / 'requirements.md')
        data['java'] = capture(['java', '-version'], project)
        data['maven'] = capture([maven, '-version'], project)
        for name in ('baseline', 'original', 'candidate'):
            snapshot(project, run_dir / name)
        seed = project / 'evidence/seeded/Checkout.java.seeded'
        if seed.is_symlink():
            raise ValueError('Linked seed input is not supported')
        shutil.copy2(seed, run_dir / 'original' / SOURCE)
        data['seed_sha256'] = digest(seed)
        original, candidate = run_dir / 'original', run_dir / 'candidate'
        original_inputs, candidate_inputs = inventory(original), inventory(candidate)
        changed = {k for k in original_inputs.keys() | candidate_inputs.keys()
                   if original_inputs.get(k) != candidate_inputs.get(k)}
        if changed != {SOURCE.as_posix()}:
            raise ValueError('Only Checkout.java may differ; reproducer and build inputs must be identical')
        data['snapshots'] = {name: inventory(run_dir / name) for name in ('baseline', 'original', 'candidate')}
        data['diff'] = ''.join(difflib.unified_diff((original / SOURCE).read_text(encoding='utf-8').splitlines(True),
                              (candidate / SOURCE).read_text(encoding='utf-8').splitlines(True),
                              fromfile='original/' + SOURCE.as_posix(), tofile='candidate/' + SOURCE.as_posix()))
        baseline = attempt('01-baseline', run_dir / 'baseline')
        if not passing(baseline) or TEST not in baseline.get('test_ids', []):
            data['explanation'] = 'Baseline blocked: require a passing nonempty suite including the R3 test. Inspect its execution record.'
            return run_dir
        results = []
        for name in ('02-original', '03-original-repeat'):
            result = attempt(name, original, TEST)
            results.append((r3_failure(result, run_dir / name), passing(result, [TEST])))
        if not all(failed for failed, passed in results):
            if all(passed for failed, passed in results):
                data['investigation'] = 'not_reproduced'
            elif any(failed for failed, passed in results) and any(passed for failed, passed in results):
                data['investigation'] = 'flaky'
            data['explanation'] = 'The original attempts did not both show the expected R3 assertion failure. No bug or verified repair is claimed.'
            return run_dir
        data['investigation'] = 'reproduced'
        data['repair'] = 'verification_failed'
        if inventory(original) != original_inputs or inventory(candidate) != candidate_inputs:
            raise ValueError('Frozen inputs changed during reproduction')
        targeted = attempt('04-candidate-reproducer', candidate, TEST)
        if not passing(targeted, [TEST]):
            data['explanation'] = 'R3 was reproduced, but the unchanged candidate reproducer did not pass.'
            return run_dir
        regression = attempt('05-candidate-regression', candidate)
        if not passing(regression, baseline['test_ids']):
            data['explanation'] = 'R3 was reproduced, but candidate regression failed or the executed test identities changed.'
            return run_dir
        if inventory(original) != original_inputs or inventory(candidate) != candidate_inputs:
            raise ValueError('Frozen inputs changed during verification')
        data.update(status='verified_candidate', repair='regression_passed',
                    explanation='One disclosed R3 defect reproduced twice: expected 900 cents, observed 1000. The unchanged reproducer and the full baseline test set passed on the candidate. Review the patch and evidence; no approval or integration is inferred.')
    except (OSError, ValueError, ET.ParseError) as exc:
        data['explanation'] = 'Workflow blocked: ' + str(exc)
    except KeyboardInterrupt:
        data['explanation'] = 'Workflow interrupted; incomplete evidence is not verification.'
    finally:
        data['duration_seconds'] = round(time.time() - data['started_at'], 3)
        (run_dir / 'workflow.json').write_text(json.dumps(data, indent=2), encoding='utf-8')
        report(run_dir)
    return run_dir


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='action', required=True)
    commands.add_parser('baseline', help='Run the existing baseline checker (baseline --help for options)')
    demo = commands.add_parser('workflow', help='Replay the disclosed R3 demonstration in isolated copies')
    demo.add_argument('--project', default='demo')
    demo.add_argument('--output', default='.vesper/runs')
    demo.add_argument('--maven', default=shutil.which('mvn') or 'mvn')
    demo.add_argument('--timeout', type=int, default=120)
    render = commands.add_parser('report', help='Regenerate Markdown from a saved workflow run')
    render.add_argument('run_dir')
    args = parser.parse_args(argv)
    try:
        if args.action == 'report':
            print(report(args.run_dir))
            return 0
        folder = run_demo(args.project, args.output, args.maven, args.timeout)
        print(folder / 'report.md')
        data = json.loads((folder / 'workflow.json').read_text(encoding='utf-8'))
        print(data['status'] + ': ' + data['explanation'])
        return 0 if data['status'] == 'verified_candidate' else 1
    except (OSError, ValueError) as exc:
        print(str(exc))
        return 2
