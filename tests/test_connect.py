import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch
import urllib.error


SCRIPT = Path(__file__).resolve().parents[1] / 'examples' / 'connect.py'
spec = importlib.util.spec_from_file_location('connect', SCRIPT)
connect = importlib.util.module_from_spec(spec)
spec.loader.exec_module(connect)


@contextlib.contextmanager
def server(status=200, body=None, headers=None):
    seen = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            seen.append((self.path, self.headers.get('Authorization')))
            self.send_response(status)
            for key, value in (headers or {}).items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(json.dumps(body or {'data': [{'id': 'example-model'}]}).encode())

        def log_message(self, *args):
            pass

    http = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=http.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{http.server_port}', seen
    finally:
        http.shutdown()
        http.server_close()
        thread.join()


class ConnectionTests(unittest.TestCase):
    def test_environment_replaces_inherited_credentials_and_routes(self):
        original = {'PATH': '/bin', 'ANTHROPIC_BASE_URL': 'https://old.invalid',
                    'ANTHROPIC_API_KEY': 'old-example', 'CLAUDE_CODE_OAUTH_TOKEN': 'old-example',
                    'CLAUDE_CODE_USE_VERTEX': '1', 'LOCAL_MODEL_TOKEN': 'test-token'}
        env = connect.client_environment('http://127.0.0.1:8000', 'example-model', '/tmp/config', original)
        self.assertEqual(env['ANTHROPIC_API_KEY'], '')
        self.assertEqual(env['ANTHROPIC_AUTH_TOKEN'], 'test-token')
        self.assertNotIn('CLAUDE_CODE_OAUTH_TOKEN', env)
        self.assertNotIn('CLAUDE_CODE_USE_VERTEX', env)
        self.assertEqual(env['ANTHROPIC_DEFAULT_HAIKU_MODEL'], 'example-model')
        self.assertEqual(original['ANTHROPIC_API_KEY'], 'old-example')

    def test_url_validation(self):
        for url in ('file:///tmp/test', 'http://remote.invalid',
                    'https://user:password@example.invalid', 'https://example.invalid?token=value'):
            with self.assertRaises(ValueError):
                connect.endpoint(url)
        self.assertEqual(connect.endpoint('http://127.0.0.1:8000/'), 'http://127.0.0.1:8000')
        self.assertEqual(connect.endpoint('https://model.example.invalid'), 'https://model.example.invalid')

    def test_catalog_request_has_auth_and_exact_model_match(self):
        with server() as (base, seen):
            connect.check_model(base, 'example-model', 'test-token')
            self.assertEqual(seen, [('/v1/models', 'Bearer test-token')])
            with self.assertRaisesRegex(ValueError, 'absent'):
                connect.check_model(base, 'other-model', 'test-token')

    def test_redirect_never_receives_credentials(self):
        with server() as (destination, seen):
            with server(302, headers={'Location': destination + '/v1/models'}) as (base, _):
                with self.assertRaises(urllib.error.HTTPError) as raised:
                    connect.check_model(base, 'example-model', 'test-token')
                raised.exception.close()
            self.assertEqual(seen, [])

    def test_check_needs_no_cli_and_makes_no_inference_request(self):
        with server() as (base, seen), contextlib.redirect_stdout(io.StringIO()):
            code = connect.main(['--base-url', base, '--model', 'example-model',
                                 '--claude', '/nonexistent/example-client', '--check'])
            self.assertEqual(code, 0)
            self.assertEqual([path for path, _ in seen], ['/v1/models'])

    def test_real_child_receives_configuration_arguments_and_exit_code(self):
        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / 'example-client'
            receipt = Path(directory) / 'receipt.json'
            executable.write_text('#!' + sys.executable + '\n'
                'import os, sys, json\n'
                'from pathlib import Path\n'
                'Path(os.environ["TEST_RECEIPT"]).write_text(json.dumps({\n'
                '"args":sys.argv[1:], "url":os.environ["ANTHROPIC_BASE_URL"],\n'
                '"token":os.environ["ANTHROPIC_AUTH_TOKEN"],\n'
                '"key":os.environ["ANTHROPIC_API_KEY"]}))\n'
                'sys.exit(7)\n')
            executable.chmod(0o700)
            env = {**os.environ, 'TEST_RECEIPT': str(receipt), 'LOCAL_MODEL_TOKEN': 'test-token'}
            run = subprocess.run([sys.executable, str(SCRIPT), '--claude', str(executable),
                '--model', 'example-model', '--base-url', 'http://127.0.0.1:8000',
                '--', '--resume'], env=env, capture_output=True, text=True)
            self.assertEqual(run.returncode, 7, run.stderr)
            data = json.loads(receipt.read_text())
            self.assertEqual(data['args'], ['--model', 'example-model', '--resume'])
            self.assertEqual(data['url'], 'http://127.0.0.1:8000')
            self.assertEqual(data['token'], 'test-token')
            self.assertEqual(data['key'], '')
            self.assertNotIn('test-token', run.stdout + run.stderr)

    def test_ssh_failure_cleans_up_owned_process(self):
        with patch.object(connect.subprocess, 'Popen') as popen:
            child = popen.return_value
            child.poll.return_value = None
            with patch.object(connect.socket, 'create_connection', side_effect=OSError('unavailable')):
                with patch.object(connect.time, 'monotonic', side_effect=[0, 16]):
                    with self.assertRaisesRegex(RuntimeError, 'Timed out'):
                        with connect.ssh_forward('user@model-host', 18000, 8000):
                            self.fail('Should not yield before connection')
            child.terminate.assert_called_once()
            child.wait.assert_called_once()


if __name__ == '__main__':
    unittest.main()
