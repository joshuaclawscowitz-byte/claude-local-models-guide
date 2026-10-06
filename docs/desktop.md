# Claude Desktop with local models

## Ollama's macOS integration

Ollama publishes a Desktop integration with instructions in its open-source
repository:

- [Claude Desktop guide](https://docs.ollama.com/integrations/claude-desktop)
- [Guide source](https://github.com/ollama/ollama/blob/main/docs/integrations/claude-desktop.mdx)
- [Ollama repository](https://github.com/ollama/ollama)

The documented flow is:

1. Install Ollama and download a supported local model.
2. Open Ollama's **Apps** screen and connect Claude.
3. Follow the setup prompts and restart Claude when requested.
4. Choose models in **Settings → Apps**, then restart Claude to apply them.

Qwen Flash Next is an example of the model you might want to use, not a promise
that a particular release offers that model. Select a model supported by your
installed runtime and hardware. Selecting a cloud model changes where inference
runs.

## Disconnecting

Use Ollama's Apps screen to disconnect Claude and restore the previous
configuration, following its guide. Its documented terminal alternative is:

```sh
ollama launch claude-desktop --restore
```

Use this for an Ollama-managed setup, not as a generic repair for unrelated
Desktop customizations.

## Other backends and custom gateways

Do not assume that Claude Code's environment variables configure Desktop too.
Desktop activation and provider configuration depend on the application version
and integration. Use documented procedures for that combination.

An Anthropic-compatible gateway may translate model names, forward streams and
handle token limits. These capabilities need separate tests; a gateway cannot
make a model reliably use tools merely by changing field names.

This guide does not distribute modified Desktop apps or version-specific binary
patches. Changing an app's identity or signature can affect workspace startup,
updates and keychain trust. Those changes are separate from selecting a local
model and are unnecessary for following the documented Ollama route.
