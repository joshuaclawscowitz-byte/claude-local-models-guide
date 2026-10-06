# Upstream references

| Source | Use |
| --- | --- |
| [Ollama repository](https://github.com/ollama/ollama) | Open-source runtime and integrations |
| [Ollama: Claude Code](https://docs.ollama.com/integrations/claude-code) | Managed launch and manual API configuration |
| [Ollama: Claude Desktop](https://docs.ollama.com/integrations/claude-desktop) | macOS setup, model selection and restoration |
| [Desktop guide source](https://github.com/ollama/ollama/blob/main/docs/integrations/claude-desktop.mdx) | Open-source documentation for the Desktop method |
| [vLLM repository](https://github.com/vllm-project/vllm) | Alternative model-serving backend |
| [vLLM: Claude Code integration](https://docs.vllm.ai/en/stable/serving/integrations/claude_code/) | Anthropic-compatible serving configuration |
| [Anthropic: LLM gateways](https://code.claude.com/docs/en/llm-gateway) | Gateway contract and support boundaries |
| [Anthropic: tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview) | Structured client tool calls and results |
| [Claude Code: model configuration](https://code.claude.com/docs/en/model-config) | Model selection and effort controls |
| [Ollama: Anthropic compatibility](https://docs.ollama.com/api/anthropic-compatibility) | Supported protocol subset and limitations |

The architecture, evaluation and deployment explanations were checked against
the linked documentation on 2026-10-06. Upstream pages are living documents;
record versions and recheck them before treating an example as an installation
contract. Deployment examples are illustrative, not benchmark results.

Anthropic's gateway documentation states that routing Claude Code to non-Claude
models is unsupported by Anthropic. Third-party integration documentation does
not change that support boundary. Consult current upstream instructions for the
versions you install.
