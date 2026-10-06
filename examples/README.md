# Runnable Python connection example

[`connect.py`](connect.py) uses Python 3.9+ and the standard library. Install
Claude Code separately. An existing model server must support Anthropic
Messages requests; this script does not install or start a model.

## Same-computer endpoint

Replace `YOUR_SERVED_MODEL` with your server's actual model alias. Qwen Flash
Next is an example model, not a hard-coded requirement.

```sh
python3 examples/connect.py --model YOUR_SERVED_MODEL --check
python3 examples/connect.py --model YOUR_SERVED_MODEL
```

The default URL is `http://127.0.0.1:11434`, the conventional local Ollama port.
For another compatible server:

```sh
python3 examples/connect.py \
  --base-url http://127.0.0.1:8000 \
  --model YOUR_SERVED_MODEL
```

The optional `--check` requests only `/v1/models` and requires an exact model
match. Some compatible servers do not expose a catalog; skip that check for
those servers. It never makes a model inference request or starts Claude Code.
Starting Code normally may make requests according to the client's behavior.

## Another computer over SSH

```sh
python3 examples/connect.py \
  --ssh user@model-host \
  --remote-port 8000 --local-port 18000 \
  --model YOUR_SERVED_MODEL --check

python3 examples/connect.py \
  --ssh user@model-host \
  --remote-port 8000 --local-port 18000 \
  --model YOUR_SERVED_MODEL
```

Replace `user@model-host` with your SSH alias or destination. SSH authentication
and host-key trust must already be configured. The remote model listener stays
on remote loopback; the local forward binds only to local loopback. The script
owns that SSH process and terminates it when Code exits or the wrapper is
interrupted. It does not retry model requests or supervise tunnel reconnection.
An abrupt process kill can prevent normal cleanup.

## Credentials and other arguments

If the backend requires bearer authentication, set `LOCAL_MODEL_TOKEN` in your
environment through your preferred secret manager. The script otherwise uses
the dummy value `local-placeholder`, suitable only for servers that ignore API
authentication behind a local connection. No real credential belongs in source
code or a shared command example.

The script replaces inherited Anthropic connection credentials, selects a
separate `~/.config/claude-local` client configuration, and points the default
Haiku/Sonnet/Opus aliases at the same selected local model. It supports bearer
authentication; adapt the code if your server specifically needs another scheme.

Additional Code arguments follow `--`:

```sh
python3 examples/connect.py --model YOUR_SERVED_MODEL -- --resume
```

Use `--claude /path/to/claude` for a specific executable and `--config-dir` to
select another client configuration directory. Existing settings, plugins,
MCP servers and explicit client options can change behavior. This launcher is
not a network sandbox or a guarantee that the entire client stays offline.
It leaves the client's permission system in place; verify the supported mode
on your installed version before using tools.

## What the Python code actually does

The key connection is in `client_environment()`:

```python
env.update(
    ANTHROPIC_BASE_URL=base_url,
    ANTHROPIC_API_KEY='',
    ANTHROPIC_AUTH_TOKEN=token,
    ANTHROPIC_MODEL=model,
    CLAUDE_CONFIG_DIR=str(Path(config_dir).expanduser()),
)
```

`subprocess.call()` starts the installed Code client with that environment.
Code itself then makes the Anthropic-format HTTP requests. The Python catalog
check independently exercises HTTP through `urllib.request`; it rejects
redirects to avoid forwarding credentials to an unexpected destination.

This is a **Claude Code** launcher. Desktop uses a different provider setup;
follow the [Ollama Desktop route](../docs/desktop.md) for that application.

## Offline tests

```sh
python3 -m unittest discover -s tests -v
```

Tests use a loopback mock HTTP server and a disposable client executable. They
check authentication, model selection, redirect refusal, child arguments/exit
status and SSH failure cleanup. No real model, SSH host or installed Claude
client is contacted. They do not establish live model/tool compatibility.
