# Claude Code and Claude Desktop with local models

A general guide to connecting Claude Code and Claude Desktop to local models.
**Qwen Flash Next is an example**; use the exact model identifier served by your
chosen backend. No particular computer, account or project is required.

Claude Code is the coding client. Changing its model to Qwen does not turn it
into the separate Qwen Code product.

## Choose a setup

| Setup | Starting point |
| --- | --- |
| Claude Code with Ollama | [Ollama's Code guide](https://docs.ollama.com/integrations/claude-code) — managed launch or manual environment variables |
| Claude Desktop with Ollama on macOS | [Ollama's Desktop guide](https://docs.ollama.com/integrations/claude-desktop) — connect through Ollama's Apps screen |
| Claude Code with another compatible server | [Manual endpoint setup](docs/claude-code.md) — for a server implementing the Anthropic Messages API |

Ollama's implementation and documentation are open source: [repository](https://github.com/ollama/ollama),
[Desktop guide source](https://github.com/ollama/ollama/blob/main/docs/integrations/claude-desktop.mdx).

## How it works

```text
Claude Code → Anthropic-compatible API → local model
```

For a model hosted on another computer:

```text
Claude Code → local SSH forward → remote model server
```

The basic Code setup selects the endpoint, its authentication and the served
model. Tools and streaming must also be compatible. A similar-looking JSON API
alone does not guarantee that every agent feature will work.

## Guides

- [Detailed architecture: client, API, runtime, tools and Python launcher](docs/how-it-works.md)
- [Example deployments and runtime behavior](docs/deployment-examples.md)
- [Runnable Python launcher: local endpoint or SSH](examples/README.md)
- [Claude Code setup](docs/claude-code.md)
- [Claude Desktop setup](docs/desktop.md)
- [Context, compaction and save/reload](docs/continuity.md)
- [Troubleshooting and verification](docs/verification.md)
- [Reproduce the setup on another computer](docs/reproducibility.md)
- [Upstream references](docs/sources.md)

## What this repository provides

| Included | Scope |
| --- | --- |
| Python launcher | Starts installed Claude Code against a selected compatible endpoint; optional owned SSH forward |
| Offline tests | Exercise the wrapper with a mock API and disposable child process |
| Code and Desktop documentation | Explains their different configuration paths and links to upstream instructions |
| Continuity and evaluation procedures | Describes how to check tool use, restart, checkpoints and real compaction |

The launcher is not a model server, Desktop patch, automatic compactor or
network sandbox. Passing its offline tests does not qualify a live model.
Deployment stories and token budgets in this guide are explicitly illustrative;
they do not disclose a person's infrastructure or report unmeasured performance.

For a first read, start with **Detailed architecture**, choose an example
deployment, run the connection check, and then verify one small tool task.
Treat long-context operation and Desktop as separate checks. For comparisons,
pin the Git revision so changing instructions cannot silently change the trial.

Examples are templates to adapt, not an installer or a claim of testing every
client/model combination. Start with the upstream integration before adding
custom gateways, app modifications or extra agent interfaces.
