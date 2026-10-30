# Framework compatibility and isolated clients

Verified October 30, 2026. Main servers use official `mcp==2.3.0`, protocol
2026-07-28. Frameworks are optional; their adapters and orchestration are not MCP.

| Framework | Locked version | Native integration | Default evidence |
|---|---|---|---|
| OpenAI Agents | 0.24.0 | `MCPServerStdio`, `Agent`, `Runner` | Full workflow, deterministic Model |
| LangGraph / LangChain | 1.2.18 / 1.4.7 | `MCPAdapter`, `StateGraph` | Full graph, actual tools |
| Strands | 1.62.0 | `MCPClient`, `call_tool_sync` | Actual calls, isolated client |
| Pydantic AI | 2.63.0 | `MCPToolset`, `Agent`, `FunctionModel` | Full workflow, deterministic model |
| Google ADK | 2.13.0 | `McpToolset`, `StdioConnectionParams` | Actual calls, isolated client |
| Claude Agent SDK | 0.2.175 | `ClaudeSDKClient`, `ClaudeAgentOptions` | Actual CLI MCP connection; model opt-in |

```text
uv sync --frozen --all-extras
uv run python scripts/framework_lab.py
uv sync --frozen --project frameworks/strands
uv run python scripts/framework_extras.py strands
uv sync --frozen --project frameworks/adk
uv run python scripts/framework_extras.py adk
```

Strands requires `mcp<2.2`; its lock uses official client 2.1.1. ADK limits
OpenTelemetry to 1.44 while this course uses 1.45.2. Their own environments and
locks prevent a silent downgrade of the server environment. The launcher passes
the main environment's Python to each adapter so it still starts the same server.
These are separate OS processes, not mixed SDK versions in one Python process.

The requested `langchain-mcp-adapters==0.3.2` requires MCP below 2, so the course
uses LangChain's current native `langchain.mcp.MCPAdapter` (beta). It and Pydantic
AI use third-party FastMCP internally. They do not replace the official server SDK.
The Pydantic version uses `MCPToolset`, not the earlier `MCPServerStdio` class.

The first three full workflows are Agents, LangGraph and Pydantic AI. Each calls
`triage_week` and `draft_status` on real synthetic data. The fixture week starts
2026-07-13 and has 14 work items; these are work items, not a fabricated bug type.
Only two read tools are allowed. A draft is never published. Deterministic models
prove orchestration and data plumbing; they do not establish LLM task accuracy.

Claude's default example starts its bundled CLI and connects MCP without a model
query. `--live` requires `LLM_PROVIDER=anthropic`, `LLM_MODEL` and its API key via
common configuration. Built-in tools are disabled and MCP is strictly scoped.
No provider is contacted by the default demos. Optional remote model API examples
use `common.llm.remote_mcp`; see Module 15 for explicit approval and endpoint rules.

Primary API references:
[Agents](https://openai.github.io/openai-agents-python/mcp/),
[LangChain](https://docs.langchain.com/oss/python/langchain/mcp),
[Strands](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/tools/mcp-tools/),
[Pydantic](https://pydantic.dev/docs/ai/mcp/client/),
[ADK](https://adk.dev/tools-custom/mcp-tools/),
[Claude](https://code.claude.com/docs/en/agent-sdk/mcp).
