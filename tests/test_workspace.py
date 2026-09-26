"""Workspace transport and review checks. Runner fixtures are synthetic."""
import http.client
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import tempfile
import threading
import unittest

from vesper.workspace import Workspace, handler_for

RUN = 'workflow-20260926-000000-aabbccdd'


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Workspace(Path(self.temp.name))

    def saved(self, status='verified_candidate'):
        folder = self.workspace.output / RUN
        folder.mkdir(parents=True)
        (folder / 'workflow.json').write_text(json.dumps(dict(status=status, attempts=[], patch_sha256='fixture-hash')), encoding='utf-8')
        return folder

    def test_rejects_unconfirmed_or_arbitrary_project(self):
        for request in ({'project':'anything','requirement_confirmed':True},
                        {'project':'checkout-r3','requirement_confirmed':False},
                        {'project':'checkout-r3','requirement_confirmed':True,'command':'arbitrary'}):
            with self.assertRaises(ValueError):
                self.workspace.start(request)
        self.assertFalse(self.workspace.state['active'])

    def test_one_real_worker_at_a_time_and_observed_stages(self):
        entered, release = threading.Event(), threading.Event()
        folder = self.saved()
        def fixture(project, output, maven, timeout, on_event):
            on_event('run_started', run_dir=str(folder))
            on_event('stage_started', stage='01-baseline')
            entered.set()
            release.wait(5)
            on_event('stage_finished', stage='01-baseline', record={'status':'passed','counts':{'tests':1}})
            return folder
        self.workspace.runner = fixture
        self.workspace.start({'project':'checkout-r3','requirement_confirmed':True})
        self.addCleanup(lambda: (release.set(), self.workspace.thread.join(5)))
        self.assertTrue(entered.wait(3))
        self.assertEqual('running', self.workspace.snapshot()['stages']['01-baseline']['status'])
        with self.assertRaises(RuntimeError):
            self.workspace.start({'project':'checkout-r3','requirement_confirmed':True})
        release.set(); self.workspace.thread.join(5)
        self.assertFalse(self.workspace.state['active'])
        self.assertEqual('passed',self.workspace.snapshot()['stages']['01-baseline']['status'])

    def test_review_is_separate_bound_and_not_overwritten(self):
        folder=self.saved()
        before=(folder/'workflow.json').read_bytes()
        review=self.workspace.review(RUN,{'decision':'approved','note':'Synthetic test decision'})
        self.assertEqual('fixture-hash',review['patch_sha256'])
        self.assertEqual('not_performed',review['integration'])
        self.assertEqual(before,(folder/'workflow.json').read_bytes())
        with self.assertRaises(FileExistsError):
            self.workspace.review(RUN,{'decision':'changes_requested'})

    def test_blocked_candidate_cannot_be_approved(self):
        self.saved('blocked')
        with self.assertRaises(ValueError):
            self.workspace.review(RUN,{'decision':'approved'})
        self.assertEqual('changes_requested', self.workspace.review(RUN,{'decision':'changes_requested'})['decision'])

    def test_history_cannot_resolve_outside_evidence(self):
        with self.assertRaises(ValueError):
            self.workspace.run_folder('../../demo')


class WorkspaceHttpTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace=Workspace(Path(self.temp.name))
        self.server=ThreadingHTTPServer(('127.0.0.1',0),handler_for(self.workspace))
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start()
        self.addCleanup(self.stop)
        self.host=f'127.0.0.1:{self.server.server_port}'

    def stop(self):
        self.server.shutdown(); self.server.server_close(); self.thread.join(3)

    def request(self, method, path, body=None, headers=None):
        connection=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=3)
        try:
            connection.request(method,path,body=body,headers=headers or {})
            response=connection.getresponse()
            return response.status,response.read()
        finally:
            connection.close()

    def test_local_state_is_readable_but_foreign_host_is_rejected(self):
        self.assertEqual(200,self.request('GET','/api/state')[0])
        self.assertEqual(403,self.request('GET','/api/state',headers={'Host':'attacker.example'})[0])
        self.assertEqual(403,self.request('GET','/api/config',headers={'Sec-Fetch-Site':'cross-site'})[0])

    def test_execution_requires_origin_token_and_valid_scope(self):
        body=json.dumps({'project':'checkout-r3','requirement_confirmed':True})
        self.assertEqual(403,self.request('POST','/api/run',body,{'Content-Type':'application/json'})[0])
        headers={'Content-Type':'application/json','Origin':'http://'+self.host,'X-Vesper-Token':self.workspace.token}
        self.assertEqual(400,self.request('POST','/api/run',json.dumps({'project':'unknown'}),headers)[0])
        self.assertFalse(self.workspace.state['active'])

    def test_evidence_route_rejects_path_escape(self):
        folder=self.workspace.output/RUN; folder.mkdir(parents=True)
        (folder/'workflow.json').write_text('{}')
        self.assertEqual(404,self.request('GET',f'/evidence/{RUN}/../../outside.json')[0])

    def test_runner_exception_is_a_failure_not_a_verified_result(self):
        def broken(*args,**kwargs):
            raise OSError('fixture tool unavailable')
        self.workspace.runner=broken
        self.workspace.start({'project':'checkout-r3','requirement_confirmed':True})
        self.workspace.thread.join(3)
        state=self.workspace.snapshot()
        self.assertFalse(state['active'])
        self.assertEqual('error',state['phase'])
        self.assertIn('fixture tool unavailable',state['error'])
