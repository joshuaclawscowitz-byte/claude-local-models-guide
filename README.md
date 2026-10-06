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

- [Claude Code setup](docs/claude-code.md)
- [Claude Desktop setup](docs/desktop.md)
- [Context, compaction and save/reload](docs/continuity.md)
- [Troubleshooting and verification](docs/verification.md)
- [Upstream references](docs/sources.md)

Examples are templates to adapt, not an installer or a claim of testing every
client/model combination. Start with the upstream integration before adding
custom gateways, app modifications or extra agent interfaces.
