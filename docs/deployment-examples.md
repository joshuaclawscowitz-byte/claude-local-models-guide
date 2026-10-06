# Example deployments and runtime behavior

These are illustrative configurations, not reports from a particular person or
benchmarks. Hostnames, ports and aliases are placeholders. Actual requirements
depend on the exact weights, quantization, serving runtime and client versions.

## Example A: one computer, Ollama and Claude Code

```text
Claude Code → 127.0.0.1:11434 → Ollama → downloaded local model
```

Install the applications using their official instructions and choose a local
model supported by the available hardware. A Qwen coding model is one possible
choice. Then follow [Ollama's Claude Code instructions](https://docs.ollama.com/integrations/claude-code)
or use this repository's launcher after confirming the served alias:

```sh
python3 examples/connect.py \
  --base-url http://127.0.0.1:11434 \
  --model YOUR_SERVED_MODEL --check

python3 examples/connect.py \
  --base-url http://127.0.0.1:11434 \
  --model YOUR_SERVED_MODEL
```

Run these commands from the guide checkout. The check is optional when the
backend has no compatible catalog. A failure to expose a catalog is different
from a failed Messages API. Selecting an Ollama cloud model changes the inference
location even when the client still connects to a local Ollama process.

## Example B: laptop client and separate GPU model server

```text
Laptop: Code → 127.0.0.1:18000
                    ↓ encrypted SSH connection
Server:        127.0.0.1:8000 → compatible runtime → model
```

The laptop handles the terminal and project tools. The other computer handles
inference. For example, a GPU server might use vLLM and serve compatible Qwen
weights under a chosen alias. Qwen Flash Next can be a descriptive example;
`YOUR_SERVED_MODEL` must still be replaced with the exact alias the server accepts.

Use the runtime's model-specific instructions for serving and tool parsing;
[vLLM publishes a Claude Code integration guide](https://docs.vllm.ai/en/latest/serving/integrations/claude_code/).
There is no universal vLLM launch command that selects the correct tool parser,
chat template, memory allocation and context length for every model.

Once the backend and noninteractive SSH authentication are ready:

```sh
python3 examples/connect.py \
  --ssh user@model-host \
  --remote-port 8000 --local-port 18000 \
  --model YOUR_SERVED_MODEL
```

Loopback means something different on each computer. The left side of the
forward is on the laptop; the remote `127.0.0.1:8000` is resolved on the server.
Binding the server to loopback avoids creating an unauthenticated LAN listener.
SSH forwarding transports the API; it does not convert API formats.

The bundled wrapper expects SSH to be ready promptly. It uses an eight-second
connection timeout and a fifteen-second listener readiness deadline. Interactive
login, browser-based reauthentication or a slow connection can exceed these.
It also inherits ordinary SSH configuration, including saved forwards. Review
the chosen SSH profile for conflicting listeners. Do not kill an unrelated
process to take its port.

If authentication needs human interaction, establish an appropriately configured
tunnel separately, then pass its verified loopback URL with `--base-url`. Record
that transport preparation as separate from testing the wrapper's SSH feature.
Do not repeatedly approve stale authentication links for connections that closed.

## Example C: Ollama-managed Desktop on macOS

Use Ollama's Apps interface to connect Claude Desktop, select models and restart
the application as instructed. Follow the separate [Desktop page](desktop.md).
This route is not the Python Code wrapper and is not a verified recipe for
pointing every Desktop release at arbitrary vLLM endpoints.

## What determines speed and memory use?

Measure complete tasks, not just how quickly the first line appears.

| Measurement | What it tells you |
| --- | --- |
| Cold start / model loading | Time before a previously unloaded model can serve a request |
| Queue time | Delay waiting behind other inference requests |
| Time to first token | Delay until generation begins; record whether queue time is included |
| Generation rate | Output tokens per second, with the runtime's counting definition |
| End-to-end task time | Inference, tools, permissions and retries combined |
| Peak memory | Whether the chosen context and concurrency fit the machine |
| Correct completed tasks | Whether speed produced useful work |

A model that chats quickly with a short prompt can behave differently with a
large repository history. Weight storage is only part of memory demand; context
and concurrent requests also consume memory. Quantization may change the memory
and quality tradeoff. A larger advertised context does not establish that the
current runtime was configured to serve it.

For a fair comparison, keep the task, input files, tool permissions and context
budget fixed. Record exact model revision, quantization, runtime version and
hardware class. Separate cold and warm runs, and count failures. Do not present
invented latency numbers as anecdotal measurements.

## A typical failure sequence, explained

As a hypothetical example, suppose short answers work, a longer coding session
hits a context error, and lowering the output allowance gets it moving again.
Later it reaches another context error. This is consistent with history growth:
the smaller output allowance bought room but did not summarize history.

Separately, if the same client later reports connection refused, start with the
listener and tunnel. That is a transport symptom, not proof that the model has
forgotten its instructions. These are examples of how to reason about failures;
they are not a claim about any particular deployment.
