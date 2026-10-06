# Test the guide on another computer

The question is whether someone can reproduce a specified setup using the guide
and an endpoint contract. “The app opened” is a weaker result than “the intended
model completed a verified tool task and resumed successfully.” Score them
separately.

## 1. Freeze the inputs

Record the repository commit before starting. If the guide changes during the
trial, continue with the original commit or start a separately labeled attempt.
Do not silently repair the instructions and count the first attempt as a pass.

Give the installer only:

- The frozen guide and its linked official documentation.
- The client's operating system and permitted installation scope.
- The endpoint contract below, delivered privately if it includes access details.
- The test task, time/request limits and stop conditions.

Record any existing environment instructions or previous knowledge that could
help the installer. A new chat is useful isolation, but does not prove a model
has never seen similar instructions during training.

## 2. Supply an endpoint contract

This example is a template, not an active service or credentials file:

```json
{
  "base_url": "http://127.0.0.1:18000",
  "api_format": "anthropic_messages",
  "served_model": "YOUR_SERVED_MODEL",
  "authentication": "bearer token supplied separately",
  "context_window_tokens": 65536,
  "maximum_output_tokens": 4096,
  "streaming": "must verify",
  "tool_round_trip": "must verify",
  "catalog": "availability must verify",
  "transport": "preconfigured loopback forward",
  "endpoint_expiry": "supply actual lifetime"
}
```

Replace every value with verified facts. Record the source of the context limit:
the runtime's actual configuration is more useful than a model marketing name.
Do not put a real credential in the JSON or publish a private hostname.

If the evaluator supplies a working tunnel, the experiment measures client
setup against that endpoint. It does not measure whether the installer could
create the tunnel. Similarly, a preinstalled client removes installation from
the tested scope. Keep these distinctions in the report.

## 3. Use a disposable project and isolated client configuration

Preserve existing applications, accounts, project files and sessions. Record
versions before making changes. Install Code from its official source if that
is in scope; use a separate configuration directory for the local backend.
Keep normal tool permissions enabled.

Start with one client and one task. Additional panes are convenient for viewing
sessions but do not provide filesystem or credential isolation on their own.
Do not launch several inference servers simply to compare models if the host
cannot safely hold them simultaneously.

Set a finite time budget and generation-request budget, for example thirty
active minutes and forty requests. Those numbers are an experimental choice,
not a capability of the launcher. If claiming an enforced request limit, use
an actual counter/limiter and record its behavior. A passive observer must not
rewrite prompts, repair tool calls or compact history behind the installer's back.

## 4. Run the checks in order

| Check | Evidence needed |
| --- | --- |
| Endpoint | Intended listener reachable; catalog if supported; authentication works |
| Installation | Actual client executable starts and reports its version |
| Routing | Correlated server request reaches the intended runtime/model |
| Text / streaming | A complete reply arrives; stream termination is handled |
| Tool task | Independently checked file output from the task below |
| Error handling | A harmless missing-file error is acknowledged or corrected |
| Restart | Only the test client is restarted, then a new task succeeds |
| Save/reload | A fresh session recovers a saved checkpoint accurately |
| Real compaction | A recorded boundary is crossed and continuity checks pass |
| Desktop | Independently observed UI, model route and tool/workspace behavior |

For a first smoke test, leave compaction and Desktop as `NOT_RUN`. Their success
does not follow from Code's results. An unavailable catalog is not automatically
a failure of a backend that supports Messages but has no catalog route.

### A small verifiable tool task

Create an input JSON containing a newly generated random marker and several
integers. Create a separate protected file and record its hash outside the
agent's expected output.

Ask the model to read the input using a tool, write a JSON containing the exact
marker, count and sum, and explain the result. Compute the expected values
independently with ordinary code. Check the JSON, the protected-file hash and
the actual tool trace. Do not accept the model's assertion that the file exists
as a substitute for reading it.

Repeat after a normal client restart with a different marker and numbers. For
error handling, request a nonexistent file in the disposable project and confirm
that the model does not invent its contents. Preserve the original failed trace
even if a later attempt succeeds.

## 5. Record interventions and results

Classify assistance so another reader can interpret the experiment:

- **Environment:** approving SSH authentication, making an endpoint reachable,
  granting an ordinary installation permission.
- **Documentation:** explaining a missing step or correcting the instructions.
- **Implementation:** writing an adapter, changing a parser or modifying a client.
- **Task assistance:** repairing the model's answer, generated file or tool arguments.

Record all of them, not just the interventions that made the final run succeed.
If a request's outcome is unknown, inspect its evidence before replaying it.

A minimal report can use this template:

```text
Guide commit:
OS and architecture:
Client and runtime versions:
Model identifier/revision and quantization:
Configured context/output limits:
Preinstalled components:
Transport supplied or created during trial:
Permissions and network policy:
Time and request budgets; how enforced:
Checks: PASS / FAIL / BLOCKED / NOT_RUN
Evidence paths and independent verifier:
Interventions and failed attempts:
Unverified features:
```

Keep raw credentials and sensitive request logs private. Publish only deliberately
sanitized examples and measurements; inspect file paths, command lines, screenshots
and Git metadata as well as prose.

## What a successful result supports

“Guide revision X reproduced this client/runtime/model configuration on this
operating system, with these checks passing and these interventions” is a useful
claim. Test another combination as a new experiment if broader coverage matters.

It does not establish that every model with a matching endpoint and context
length will work. Protocol support, tool behavior, token accounting, client
features and model quality all remain relevant.
