"""Experimental supplied-snapshot gate for the live pilot, not a general project API."""
import hashlib
import json
from pathlib import Path
import shutil
import time
import uuid
import xml.etree.ElementTree as ET
from vesper.workflow import execute, inventory, passing, snapshot


def gate(original, candidate, test_file, expectation, maven, output):
    original, candidate, output = map(lambda p: Path(p).resolve(), (original,candidate,output))
    run = output / ('gate-' + uuid.uuid4().hex[:10]); run.mkdir(parents=True)
    start = time.perf_counter()
    record = dict(status='blocked', explanation='Incomplete', attempts=[], gate_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    before = inventory(candidate)
    record['original_inputs'] = inventory(original); record['candidate_inputs'] = before
    def attempt(name, workspace, selector=None):
        value = execute(workspace, run/name, maven, selector, 180)
        record['attempts'].append(dict(name=name, **value))
        return value
    try:
        for key,value in record['original_inputs'].items():
            if key == 'pom.xml' or key == 'requirements.md' or key.startswith('src/test/'):
                if before.get(key) != value:
                    raise ValueError('Frozen build, requirements or existing test changed: '+key)
        for label,source in [('baseline',original),('original',original),('candidate',candidate)]:
            snapshot(source,run/label)
        baseline=attempt('01-baseline',run/'baseline')
        if not passing(baseline): raise ValueError('Original ordinary baseline did not pass')
        if test_file is None:
            final=attempt('02-control',run/'candidate')
            if not passing(final,baseline['test_ids']): raise ValueError('Control regression failed')
            if any(before.get(k)!=v for k,v in record['original_inputs'].items() if k.startswith('src/main/')):
                raise ValueError('Unnecessary production change on control')
            record.update(status='accepted_no_change',explanation='No repair claimed; original and candidate ordinary tests pass and production is unchanged.')
        else:
            for name in ['original','candidate']:
                dest=run/name/'src/test/java/dev/vesper/AcceptedTest.java'
                dest.write_bytes(Path(test_file).read_bytes())
            frozen={name:inventory(run/name) for name in ['original','candidate']}
            target='dev.vesper.AcceptedTest#requirement'
            for label in ['02-original','03-repeat']:
                result=attempt(label,run/'original',target)
                if result.get('exit_code')!=1 or result.get('counts')!=dict(tests=1,failures=1,errors=0,skipped=0) or result.get('test_ids')!=[target] or not result.get('inputs_unchanged'):
                    raise ValueError('Expected original assertion was not reproduced twice')
                failures=[f for p in (run/label/'reports').glob('TEST-*.xml') for f in ET.parse(p).getroot().iter('failure')]
                if len(failures)!=1 or failures[0].get('type')!='org.opentest4j.AssertionFailedError' or expectation not in failures[0].get('message',''):
                    raise ValueError('Original failure does not match accepted expectation')
            result=attempt('04-candidate',run/'candidate',target)
            if not passing(result,[target]): raise ValueError('Accepted candidate reproducer did not pass')
            final=attempt('05-regression',run/'candidate')
            # Added tests may strengthen the suite; every frozen baseline identity must execute.
            expected=set(baseline['test_ids'])|{target}
            if not passing(final) or not expected.issubset(final.get('test_ids',[])):
                raise ValueError('Required regression identities did not pass')
            if any(inventory(run/name)!=value for name,value in frozen.items()):
                raise ValueError('Snapshot inputs changed during verification')
            record.update(status='verified_candidate',explanation='Accepted assertion failed twice on original and passed unchanged on candidate; required regression identities passed.')
        if inventory(candidate)!=before: raise ValueError('Candidate changed during gate evaluation')
    except (OSError,ValueError,ET.ParseError) as exc:
        record.update(status='blocked',explanation=str(exc))
    record['duration_seconds']=round(time.perf_counter()-start,3)
    (run/'gate.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    return record,run
