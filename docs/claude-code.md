# Claude Code with a local model

## Requirements

Install Claude Code and run a model server that implements the Anthropic
Messages API, including tool calls and streaming. An OpenAI-compatible chat
endpoint alone is insufficient unless an adapter supplies the missing protocol.
[Ollama](https://docs.ollama.com/integrations/claude-code) and
[vLLM](https://docs.vllm.ai/en/stable/serving/integrations/claude_code/)
publish integration instructions.

Qwen Flash Next is one example model family. The CLI needs the actual alias
configured by your server, which can differ from the model's display name.

## Option 1: Ollama launcher

Follow [Ollama's Code guide](https://docs.ollama.com/integrations/claude-code).
Its launcher entry point is:

```sh
ollama launch claude
```

Choose a downloaded local model if you want local inference. Ollama also offers
cloud models; those run remotely.

## Option 2: direct endpoint configuration

For a runnable Python version with optional SSH forwarding and a connectivity
check, see [the Python connection example](../examples/README.md).

For local Ollama, replace `YOUR_SERVED_MODEL` with the installed model identifier:

```sh
ANTHROPIC_BASE_URL=http://127.0.0.1:11434 \
ANTHROPIC_AUTH_TOKEN=ollama \
ANTHROPIC_API_KEY='' \
CLAUDE_CONFIG_DIR="$HOME/.config/claude-local" \
claude --model YOUR_SERVED_MODEL
```

`ollama` is a placeholder accepted by local Ollama, not an Anthropic credential.
For another backend, use its URL and authentication requirements. Use the API
root; the client normally adds `/v1/messages`. Check `/status` and inspect
settings that may override the environment.

An isolated configuration directory helps keep local and other accounts apart.
Check the installed CLI's help for supported permission modes and choose its
ordinary permission-prompt mode while validating a new backend. Do not assume
an auto-mode classifier supports your local model just because basic chat works.

## Model on another computer

Keep the remote inference listener bound to loopback and use SSH forwarding.
The ports below are examples; substitute your server's actual listening port.

```sh
ssh -N -T \
  -o BatchMode=yes -o StrictHostKeyChecking=yes -o ForwardAgent=no \
  -o ExitOnForwardFailure=yes -o ServerAliveInterval=15 \
  -o ServerAliveCountMax=2 \
  -L 127.0.0.1:18000:127.0.0.1:8000 user@model-host
```

SSH authentication and the host key must already be configured. Leave the tunnel
running and set `ANTHROPIC_BASE_URL=http://127.0.0.1:18000` in the client command.
Use the backend's credentials; an SSH tunnel does not change its HTTP protocol.

Where supported, a catalog request can check connectivity without generating text:

```sh
curl --fail --max-time 5 http://127.0.0.1:18000/v1/models
```

A catalog response is only a connectivity check. Follow it with the bounded
[tool and continuity checks](verification.md).

## Optional extensions

Some clients select additional model aliases for small tasks or subagents.
Consult the installed version's configuration reference and map them deliberately.
Check server logs to confirm the requests go where intended.

A gateway can translate protocol details or add context handling, but it adds
another process to operate and test. App renaming, re-signing and keychain
changes are not needed to configure the ordinary Claude Code CLI endpoint.
