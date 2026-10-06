# Verification and troubleshooting

These are checks to perform on your own setup, not claims that a particular
machine or model combination has passed them.

For an independent installation attempt, use the [reproducibility procedure](reproducibility.md).
Keep setup failures distinct from model/task failures.

## Verify the complete path

1. Check the configured endpoint and, where available, its model catalog.
2. Inspect server logs to confirm the intended model receives requests.
3. In a disposable folder, ask the agent to write a unique phrase to a file,
   read it back and report the result. Inspect the file independently.
4. Exercise one harmless failed tool call and check that the agent reports or
   corrects it rather than claiming success.
5. Test streaming and longer responses for truncation.
6. Check session reload and a real compaction boundary independently.

## Connection refused

`ECONNREFUSED` means the connection was refused at the destination. Check the
exact host and port, local listener, tunnel process and remote service before
changing model settings. If the server works remotely but the forwarded local
port has no listener, investigate the tunnel.

SSH keepalives help detect a broken connection. A supervisor can restart a
failed tunnel with bounded retries; that is different from replaying a model
request or tool action whose outcome may be unknown.

## Context-length errors

Compare input plus reserved output with the server's configured window. Reduce
unnecessary input, use compaction or start a fresh chat with a checkpoint.
Reducing output alone postpones the boundary and can truncate answers.

## Tool call failed or answer stops at a promise

Inspect the tool name, required arguments, returned error and model stop reason.
A missing argument, a failed workspace, a normal end-of-turn and an exhausted
output allowance are different faults. Correct the observed fault; do not
assume all unfinished answers have the same cause.

For example, distinguish a complete response ending with `end_turn`, one stopped
at `max_tokens`, and one requesting `tool_use`. Then inspect the corresponding
client trace. A missing required argument is a tool-call failure even if the
HTTP request succeeded. A promise followed by a normal end of turn can be a
model behavior problem; a tool request that never reaches the tool points to
another boundary. A stream that never terminates needs transport/event tracing.
These protocol fields are described in [Ollama's compatibility reference](https://docs.ollama.com/api/anthropic-compatibility).

## A focused diagnostic table

| Symptom | First evidence to inspect | Avoid assuming |
| --- | --- | --- |
| `401` or `403` | Credential source and required header scheme | A dummy token authenticates every backend |
| Model not found | Exact requested alias and served catalog/configuration | The friendly display name is an API identifier |
| Connection refused | Exact listener, port and owned tunnel process | A context or reasoning setting will repair networking |
| Repeated SSH browser checks | Whether the pending connection still exists; auth timeout | Approval of an old link revives a closed connection |
| Address already in use | Listener owner and inherited SSH forwards | It is safe to terminate whichever process has the port |
| Tools work once then fail | Full call/result pairing and next request | Initial text generation established tool compatibility |
| “I will…” with no action | Actual response blocks and stop reason | The model performed the promised action |
| Auto mode unavailable | Installed client's support and any separate classifier route | Ordinary local chat implies permission-classifier support |
| Effort choice has no effect | Environment, client settings and runtime's supported controls | Identically named effort levels mean the same behavior across models |
| Restart loses connection | Tunnel lifetime and launch environment | The model service must have crashed |

Claude Code's [model configuration documentation](https://code.claude.com/docs/en/model-config)
describes effort controls, but a replacement backend still has to implement the
corresponding behavior. The Python launcher retains variables outside its
explicit cleanup list; an inherited effort setting is one example to inspect.

## Logs that help without exposing secrets

Prefer request IDs, timestamps, route labels, model aliases, status codes, token
counts and stop reasons. Keep full prompt/tool content private when necessary
for diagnosis. Do not publish authorization headers, environment dumps, login
links, private paths or raw session transcripts. Reproduce a fault with a small
synthetic input when possible, and preserve the original evidence privately.

## Workspace or keychain problems

For an unmodified application, follow its supported repair instructions.
For a modified application, compare its signature and required entitlements
with the original and inspect the relevant logs. Re-signing can change the
identity used for keychain permissions. Avoid blanket access grants and never
share passwords or keychain secrets in diagnostic reports.
