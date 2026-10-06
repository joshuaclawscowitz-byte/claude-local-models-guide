# Verification and troubleshooting

These are checks to perform on your own setup, not claims that a particular
machine or model combination has passed them.

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

## Workspace or keychain problems

For an unmodified application, follow its supported repair instructions.
For a modified application, compare its signature and required entitlements
with the original and inspect the relevant logs. Re-signing can change the
identity used for keychain permissions. Avoid blanket access grants and never
share passwords or keychain secrets in diagnostic reports.
