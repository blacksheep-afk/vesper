"""Loopback-only workspace for the supported R3 verifier, not a repository host."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
from pathlib import Path
import re
import secrets
import shutil
import threading
import time
from urllib.parse import unquote, urlsplit

from .workflow import run_demo

REPO = Path(__file__).resolve().parents[1]
ASSETS = Path(__file__).with_name('assets')
STAGES = ['01-baseline', '02-original', '03-original-repeat', '04-candidate-reproducer', '05-candidate-regression']
SAVED = 'workflow-20260926-141036-d39fa35f'


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


class Workspace:
    def __init__(self, repo=REPO, maven=None, timeout=300, runner=run_demo):
        self.repo = Path(repo).resolve()
        self.output = self.repo / '.vesper/workspace-runs'
        self.maven = maven or shutil.which('mvn') or 'mvn'
        self.timeout = timeout
        self.runner = runner
        self.token = secrets.token_urlsafe(32)
        self.lock = threading.RLock()
        self.state = dict(active=False, phase='idle', events=[], stages={}, run_id=None, error=None)

    def config(self):
        return dict(token=self.token, project=dict(id='checkout-r3', name='Checkout / discount service',
                    path='demo', requirement='R3', statement='A discount is valid through its expiry date, inclusive.',
                    expected='1,000 cents with a 10% discount on the expiry date must total 900 cents.'),
                    tools=dict(java=bool(shutil.which('java')), maven=bool(shutil.which(self.maven))),
                    scope='Disclosed seeded replay using the existing corrected candidate. No AI repair is generated.')

    def start(self, request):
        if request != {'project': 'checkout-r3', 'requirement_confirmed': True}:
            raise ValueError('Select the supported project and confirm R3 before running.')
        with self.lock:
            if self.state['active']:
                raise RuntimeError('A verification is already running. Wait for its evidence before starting another.')
            self.state = dict(active=True, phase='preparing', events=[], stages={}, run_id=None,
                              started_at=time.time(), error=None)
            self.thread = threading.Thread(target=self._run, name='vesper-verifier', daemon=True)
            self.thread.start()
            return deepcopy(self.state)

    def event(self, kind, **data):
        with self.lock:
            self.state['events'].append(dict(kind=kind, at=time.time(), stage=data.get('stage')))
            if kind == 'run_started':
                self.state['run_id'] = Path(data['run_dir']).name
            elif kind == 'stage_started':
                self.state['phase'] = data['stage']
                self.state['stages'][data['stage']] = dict(status='running')
            elif kind == 'stage_finished':
                self.state['stages'][data['stage']] = data['record']

    def _run(self):
        try:
            folder = self.runner(self.repo / 'demo', self.output, self.maven, self.timeout, on_event=self.event)
            data = read_json(folder / 'workflow.json')
            with self.lock:
                self.state.update(phase=data['status'], result=data, run_id=folder.name)
        except Exception as exc:
            with self.lock:
                self.state.update(phase='error', error=str(exc))
        finally:
            with self.lock:
                self.state.update(active=False, finished_at=time.time())

    def snapshot(self):
        with self.lock:
            state = deepcopy(self.state)
        state['log_tail'] = ''
        if state.get('run_id') and state['phase'] in STAGES:
            log = self.output / state['run_id'] / state['phase'] / 'execution.log'
            if log.is_file():
                with log.open('rb') as stream:
                    stream.seek(max(0, log.stat().st_size - 16000))
                    state['log_tail'] = stream.read(16000).decode('utf-8', errors='replace')
        return state

    def run_folder(self, run_id):
        if not re.fullmatch(r'workflow-[0-9]{8}-[0-9]{6}-[a-f0-9]{8}', run_id):
            raise ValueError('Unknown run identifier')
        roots = [self.output, self.repo / 'evidence/verification-20260926']
        for root in roots:
            folder = (root / run_id).resolve()
            if folder.parent == root.resolve() and (folder / 'workflow.json').is_file():
                return folder
        raise FileNotFoundError('Run evidence is not available yet')

    def evidence(self, run_id):
        folder = self.run_folder(run_id)
        data = read_json(folder / 'workflow.json')
        attempts = {name: read_json(folder / name / 'result.json') for name in data.get('attempts', []) if name in STAGES}
        return dict(run_id=run_id, result=data, stages=attempts,
                    review=read_json(folder / 'review.json') if (folder / 'review.json').is_file() else None,
                    historical=folder.parent != self.output, report=f'/evidence/{run_id}/report.html')

    def history(self):
        files = list(self.output.glob('*/workflow.json'))
        archived = self.repo / 'evidence/verification-20260926' / SAVED / 'workflow.json'
        if archived.is_file():
            files.append(archived)
        items = []
        for path in files:
            try:
                data = read_json(path)
                items.append(dict(run_id=path.parent.name, status=data.get('status'), started_at=data.get('started_at', 0),
                                  historical=path.parent.parent != self.output))
            except (OSError, ValueError):
                continue
        return sorted(items, key=lambda row: row['started_at'], reverse=True)[:20]

    def review(self, run_id, request):
        with self.lock:
            folder = self.run_folder(run_id)
            if folder.parent != self.output:
                raise ValueError('Historical evidence is read-only. Run a fresh verification to record a decision.')
            if self.state['active'] and self.state['run_id'] == run_id:
                raise ValueError('Wait for verification to finish before recording a review.')
            data = read_json(folder / 'workflow.json')
            decision, note = request.get('decision'), request.get('note', '')
            if decision not in ('approved', 'changes_requested') or not isinstance(note, str) or len(note) > 2000:
                raise ValueError('Choose a decision and keep the note under 2,000 characters.')
            if decision == 'approved' and data.get('status') != 'verified_candidate':
                raise ValueError('A blocked candidate cannot be approved here.')
            record = dict(decision=decision, note=note, patch_sha256=data.get('patch_sha256'),
                          recorded_at=datetime.now(timezone.utc).isoformat(), integration='not_performed')
            # Never replace a prior human decision. Re-run to create a new reviewable record.
            with (folder / 'review.json').open('x', encoding='utf-8') as stream:
                json.dump(record, stream, indent=2)
            return record


def handler_for(workspace):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def respond(self, status, body, content_type='application/json; charset=utf-8'):
            if not isinstance(body, bytes):
                body = json.dumps(body).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.send_header('X-Frame-Options', 'DENY')
            self.end_headers()
            self.wfile.write(body)

        def local_request(self, write=False):
            host = f'127.0.0.1:{self.server.server_port}'
            if self.headers.get('Host') != host:
                self.respond(403, {'error': 'Use the printed loopback URL.'})
                return False
            if self.headers.get('Sec-Fetch-Site') == 'cross-site':
                self.respond(403, {'error': 'Cross-site requests are not supported.'})
                return False
            if write and (self.headers.get('Origin') != 'http://' + host or
                          not secrets.compare_digest(self.headers.get('X-Vesper-Token', ''), workspace.token)):
                self.respond(403, {'error': 'Reload the local workspace before starting this action.'})
                return False
            return True

        def do_GET(self):
            if not self.local_request():
                return
            path = unquote(urlsplit(self.path).path)
            try:
                if path == '/api/config':
                    return self.respond(200, workspace.config())
                if path == '/api/state':
                    return self.respond(200, workspace.snapshot())
                if path == '/api/history':
                    return self.respond(200, workspace.history())
                if path.startswith('/api/run/'):
                    return self.respond(200, workspace.evidence(path.removeprefix('/api/run/')))
                static = {'/': 'workspace.html', '/app.js': 'workspace.js', '/app.css': 'workspace.css',
                          '/vesper-mark.svg': 'vesper-mark.svg', '/licenses.txt': 'workspace.js.LEGAL.txt'}
                if path in static:
                    file = ASSETS / static[path]
                    content_type = mimetypes.guess_type(str(file))[0] or 'text/plain'
                elif path.startswith('/evidence/'):
                    run_id, relative = path.removeprefix('/evidence/').split('/', 1)
                    folder = workspace.run_folder(run_id)
                    file = (folder / relative).resolve()
                    if not file.is_relative_to(folder) or file.suffix not in ('.html', '.json', '.log', '.xml', '.md', '.java'):
                        raise ValueError('Only this run’s evidence files are available.')
                    content_type = 'text/html' if file.name == 'report.html' else 'text/plain'
                else:
                    raise FileNotFoundError('Unknown workspace route')
                self.respond(200, file.read_bytes(), content_type + '; charset=utf-8')
            except (OSError, ValueError, KeyError) as exc:
                self.respond(404, {'error': str(exc)})

        def do_POST(self):
            if not self.local_request(write=True):
                return
            try:
                length = int(self.headers.get('Content-Length', 0))
                if not 0 < length <= 8192 or self.headers.get('Content-Type') != 'application/json':
                    raise ValueError('A small JSON request is required.')
                request = json.loads(self.rfile.read(length))
                if not isinstance(request, dict):
                    raise ValueError('Expected a JSON object.')
                path = urlsplit(self.path).path
                if path == '/api/run':
                    return self.respond(202, workspace.start(request))
                if path.startswith('/api/review/'):
                    return self.respond(201, workspace.review(path.removeprefix('/api/review/'), request))
                self.respond(404, {'error': 'Unknown action'})
            except (ValueError, OSError) as exc:
                self.respond(400, {'error': str(exc)})
            except RuntimeError as exc:
                self.respond(409, {'error': str(exc)})
    return Handler


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--maven', default=None)
    parser.add_argument('--timeout', type=int, default=300)
    args = parser.parse_args(argv)
    if not 0 <= args.port <= 65535 or args.timeout <= 0:
        parser.error('Use a valid port and positive timeout.')
    workspace = Workspace(maven=args.maven, timeout=args.timeout)
    server = ThreadingHTTPServer(('127.0.0.1', args.port), handler_for(workspace))
    print(f'Vesper workspace: http://127.0.0.1:{server.server_port}', flush=True)
    print('Runs the supported local Java demo. Ctrl+C stops the workspace; finish active verification first.', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        if workspace.state['active']:
            print('Waiting for the bounded verifier to retain its evidence before exit.', flush=True)
            workspace.thread.join()
    finally:
        server.server_close()
    return 0
