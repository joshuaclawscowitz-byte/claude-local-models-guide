#!/usr/bin/env python3
"""Connect Claude Code to an Anthropic-compatible server. Python 3.9+, no packages."""
import argparse
import contextlib
import ipaddress
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


def endpoint(value):
    url = urllib.parse.urlsplit(value)
    if url.scheme not in ('http', 'https') or not url.hostname:
        raise ValueError('Use an http:// or https:// API root URL.')
    if url.username or url.password or url.query or url.fragment:
        raise ValueError('Keep credentials, query parameters and fragments out of the URL.')
    if url.scheme == 'http':
        try:
            local = ipaddress.ip_address(url.hostname).is_loopback
        except ValueError:
            local = url.hostname == 'localhost'
        if not local:
            raise ValueError('Use HTTPS for a remote endpoint, or an SSH loopback forward.')
    return value.rstrip('/')


def client_environment(base_url, model, config_dir, source=None):
    source = dict(os.environ if source is None else source)
    token = source.get('LOCAL_MODEL_TOKEN', 'local-placeholder')
    env = {k: v for k, v in source.items()
           if not k.startswith('ANTHROPIC_') and k not in (
               'CLAUDE_CODE_OAUTH_TOKEN', 'CLAUDE_CODE_USE_BEDROCK',
               'CLAUDE_CODE_USE_VERTEX', 'CLAUDE_CODE_USE_FOUNDRY')}
    env.update(ANTHROPIC_BASE_URL=base_url, ANTHROPIC_API_KEY='',
               ANTHROPIC_AUTH_TOKEN=token, ANTHROPIC_MODEL=model,
               CLAUDE_CONFIG_DIR=str(Path(config_dir).expanduser()))
    for tier in ('HAIKU', 'SONNET', 'OPUS'):
        env['ANTHROPIC_DEFAULT_' + tier + '_MODEL'] = model
    return env


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # Do not forward credentials to a redirected destination.


def check_model(base_url, model, token):
    request = urllib.request.Request(base_url + '/v1/models', headers={
        'Authorization': 'Bearer ' + token, 'Accept': 'application/json'})
    # Direct connection: do not send local credentials through an inherited proxy.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    with opener.open(request, timeout=5) as response:
        body = response.read(1024 * 1024 + 1)
    if len(body) > 1024 * 1024:
        raise ValueError('Model catalog exceeds the 1 MiB check limit.')
    catalog = json.loads(body)
    if not isinstance(catalog, dict) or not isinstance(catalog.get('data'), list):
        raise ValueError('Expected a model catalog with a data array.')
    if not any(isinstance(item, dict) and item.get('id') == model
               for item in catalog['data']):
        raise ValueError('Requested model alias is absent from the catalog.')


@contextlib.contextmanager
def ssh_forward(target, local_port, remote_port):
    if target.startswith('-') or any(c.isspace() for c in target):
        raise ValueError('Use an SSH alias or user@host without spaces.')
    for port in (local_port, remote_port):
        if not 1 <= port <= 65535:
            raise ValueError('Ports must be between 1 and 65535.')
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', local_port))  # Fail if another listener owns it.
    command = ['ssh', '-N', '-T', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
               '-o', 'ForwardAgent=no', '-o', 'ExitOnForwardFailure=yes',
               '-o', 'ConnectTimeout=8', '-o', 'ServerAliveInterval=15',
               '-o', 'ServerAliveCountMax=2', '-L',
               f'127.0.0.1:{local_port}:127.0.0.1:{remote_port}', target]
    process = subprocess.Popen(command)
    try:
        deadline = time.monotonic() + 15
        while True:
            if process.poll() is not None:
                raise RuntimeError('SSH exited before its forward was ready.')
            try:
                with socket.create_connection(('127.0.0.1', local_port), timeout=.2):
                    break
            except OSError:
                if time.monotonic() >= deadline:
                    raise RuntimeError('Timed out waiting for the SSH listener.')
                time.sleep(.1)
        yield f'http://127.0.0.1:{local_port}'
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    route = parser.add_mutually_exclusive_group()
    route.add_argument('--base-url', default=None, help='Default: http://127.0.0.1:11434')
    route.add_argument('--ssh', metavar='user@model-host', help='Open an owned SSH forward')
    parser.add_argument('--model', required=True, help='Exact alias served by the backend')
    parser.add_argument('--local-port', type=int, default=18000)
    parser.add_argument('--remote-port', type=int, default=8000)
    parser.add_argument('--config-dir', default='~/.config/claude-local')
    parser.add_argument('--claude', default='claude', help='Claude Code executable')
    parser.add_argument('--check', action='store_true', help='Check catalog only; no inference')
    parser.add_argument('claude_args', nargs=argparse.REMAINDER, help='Code arguments after --')
    args = parser.parse_args(argv)
    extra = args.claude_args
    if extra[:1] == ['--']:
        extra = extra[1:]
    executable = shutil.which(args.claude)
    if not args.check and not executable:
        parser.error('Claude Code executable not found; install it or pass --claude.')
    connection = (ssh_forward(args.ssh, args.local_port, args.remote_port) if args.ssh
                  else contextlib.nullcontext(endpoint(args.base_url or 'http://127.0.0.1:11434')))
    with connection as base_url:
        env = client_environment(base_url, args.model, args.config_dir)
        if args.check:
            check_model(base_url, args.model, env['ANTHROPIC_AUTH_TOKEN'])
            print('Endpoint reachable; exact model alias found. No inference requested.')
            return 0
        print('Starting Claude Code with the selected endpoint and model.', flush=True)
        return subprocess.call([executable, '--model', args.model] + extra, env=env)


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
    except urllib.error.HTTPError as exc:
        print(f'Endpoint returned HTTP {exc.code}; check URL and credentials.', file=sys.stderr)
        exc.close()
        raise SystemExit(1)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f'Connection failed: {exc}', file=sys.stderr)
        raise SystemExit(1)
