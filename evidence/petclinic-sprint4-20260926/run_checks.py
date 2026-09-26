import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
workspace = ROOT / sys.argv[1]
attempt = ROOT / 'evidence' / sys.argv[2]
attempt.mkdir(parents=True, exist_ok=False)
jdk = next((ROOT / 'tools').glob('jdk*'))
if not jdk.is_dir():
    jdk = next(p for p in (ROOT / 'tools').glob('jdk*') if p.is_dir())
env = os.environ.copy()
env['JAVA_HOME'] = str(jdk)
env['PATH'] = str(jdk / 'bin') + os.pathsep + env['PATH']
maven = ROOT / 'tools/apache-maven-3.9.9/bin/mvn.cmd'
env['MAVEN_OPTS'] = '-Dmaven.repo.local="' + str(ROOT / 'tools/m2') + '"'
command = [str(maven), '-B', '-DfailIfNoTests=true', *sys.argv[3:]]
def hashes():
    return {str(p.relative_to(workspace)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((workspace / 'src').rglob('*')) if p.is_file()}
before = hashes()
started = time.time()
record = {'command': command, 'workspace': str(workspace), 'started_at': started,
          'source_sha': subprocess.check_output(['git', '-c', 'safe.directory=' + str(workspace), 'rev-parse', 'HEAD'], cwd=workspace, text=True).strip(),
          'input_hashes_before': before, 'python': sys.version}
for name, cmd in [('java', [str(jdk / 'bin/java.exe'), '-version']), ('maven', [str(maven), '-version'])]:
    record[name] = subprocess.run(cmd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout
with (attempt / 'execution.log').open('w', encoding='utf-8') as log:
    process = subprocess.Popen(command, cwd=workspace, env=env, stdout=log, stderr=subprocess.STDOUT)
    try:
        record['exit_code'] = process.wait(timeout=900)
    except subprocess.TimeoutExpired:
        subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'], capture_output=True)
        process.wait()
        record['exit_code'] = None
        record['timeout'] = True
record['duration_seconds'] = round(time.time() - started, 3)
record['input_hashes_after'] = hashes()
record['inputs_unchanged'] = before == record['input_hashes_after']
record['counts'] = dict(tests=0, failures=0, errors=0, skipped=0)
record['cases'] = []
reports = workspace / 'target/surefire-reports'
if reports.exists():
    shutil.copytree(reports, attempt / 'reports')
    for path in sorted(reports.glob('TEST-*.xml')):
        suite = ET.parse(path).getroot()
        for case in suite.findall('testcase'):
            status = next((tag for tag in ('failure', 'error', 'skipped') if case.find(tag) is not None), 'passed')
            entry = dict(id=case.get('classname') + '#' + case.get('name'), status=status)
            if status != 'passed':
                entry['message'] = case.find(status).get('message', '')
            record['cases'].append(entry)
            record['counts']['tests'] += 1
            if status != 'passed': record['counts'][{'failure':'failures','error':'errors','skipped':'skipped'}[status]] += 1
(attempt / 'result.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
print(json.dumps({k:record[k] for k in ('exit_code','duration_seconds','counts','inputs_unchanged')}), flush=True)
sys.exit(0 if record['exit_code'] == 0 else 1)
