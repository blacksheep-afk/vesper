"""Run the supplied Petclinic reproducer unchanged on original and candidate."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
test = Path('src/test/java/org/springframework/samples/petclinic/owner/VesperPetTypeReproductionTests.java')
baseline = json.loads((ROOT / 'evidence/01-upstream-baseline/result.json').read_text())
assert baseline['exit_code'] == 0 and baseline['counts']['tests'] > 0
assert baseline['counts']['failures'] == baseline['counts']['errors'] == 0
assert baseline['inputs_unchanged']
frozen = (ROOT / 'petclinic-sprint3-evidence/VesperPetTypeReproductionTests.java').read_bytes()
shutil.copyfile(ROOT / 'petclinic-sprint3-evidence/VesperPetTypeReproductionTests.java', ROOT / 'original' / test)
assert (ROOT / 'candidate' / test).read_bytes() == frozen

def run(workspace, name, *args):
    if not (ROOT / 'evidence' / name / 'result.json').exists():
        subprocess.run([sys.executable, str(ROOT / 'run_checks.py'), workspace, name, *args], check=False)
    result = json.loads((ROOT / 'evidence' / name / 'result.json').read_text())
    assert result['inputs_unchanged'], 'Source inputs changed during execution'
    assert (ROOT / workspace / test).read_bytes() == frozen, 'Frozen reproducer changed'
    return result

style = run('original', '02-original-format-check', 'clean', 'test', '-Dtest=VesperPetTypeReproductionTests')
flags = []
if style['exit_code'] != 0 and style['counts']['tests'] == 0:
    log = (ROOT / 'evidence/02-original-format-check/execution.log').read_text(encoding='utf-8')
    assert 'Formatting violations' in log or 'formatting violations' in log, 'Unexpected setup failure'
    flags = ['-Dspring-javaformat.validate.skip=true']
for name in ('03-original-reproduction', '04-original-repeat'):
    result = run('original', name, 'clean', 'test', '-Dtest=VesperPetTypeReproductionTests', *flags)
    assert result['exit_code'] != 0 and result['counts'] == dict(tests=2, failures=2, errors=0, skipped=0)
    failures = {c['id'].split('#')[-1]: c['message'] for c in result['cases']}
    assert 'expected: <true> but was: <false>' in failures['existingPetMustRejectMissingType']
    assert 'Status expected:<200> but was:<302>' in failures['editMustRejectClearedType']
targeted = run('candidate', '05-candidate-reproducer-retry', 'clean', 'test', '-Dtest=VesperPetTypeReproductionTests', *flags)
assert targeted['exit_code'] == 0 and targeted['counts'] == dict(tests=2, failures=0, errors=0, skipped=0)
regression = run('candidate', '06-candidate-regression', 'clean', 'verify', *flags)
assert regression['exit_code'] == 0 and regression['counts']['failures'] == regression['counts']['errors'] == 0
before = {c['id']: c['status'] for c in baseline['cases']}
after = {c['id']: c['status'] for c in regression['cases']}
assert all(after.get(k) == v for k, v in before.items()), 'Existing test identity/status changed'
assert set(after) - set(before) == {c['id'] for c in targeted['cases']}
assert len(after) == len(regression['cases']), 'Duplicate test identities'
tests_before = {str(p.relative_to(ROOT / 'original/src/test')): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in (ROOT / 'original/src/test').rglob('*') if p.is_file()}
tests_after = {str(p.relative_to(ROOT / 'candidate/src/test')): hashlib.sha256(p.read_bytes()).hexdigest()
               for p in (ROOT / 'candidate/src/test').rglob('*') if p.is_file()}
assert tests_before == tests_after, 'Tests differ between original and candidate'
manifest = {'status': 'verified_candidate', 'approval': 'pending', 'integration': 'not_performed',
            'test_sha256': hashlib.sha256(frozen).hexdigest(), 'format_flags': flags,
            'test_files_identical': True, 'baseline_test_identities_preserved': True,
            'baseline_counts': baseline['counts'], 'candidate_counts': regression['counts']}
(ROOT / 'evidence/verification.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print(json.dumps(manifest), flush=True)
