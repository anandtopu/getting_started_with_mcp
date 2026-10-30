# Connect Tier 1 servers to a host

Run commands from the repository root after `uv sync` and `npm ci`:

```text
uv run python scripts/host_configs.py --module 0
```

The generator writes four ready-to-paste files under `.runtime/host_configs/00_setup`.
It resolves executable and project paths on your own machine, including Windows
backslashes escaped correctly for JSON. Copy the relevant entries into your
existing configuration, preserving other servers. Modules 02–06 use the same
command with their module number. No secrets are copied into the configuration.

| Host | Location and envelope | How to verify |
|---|---|---|
| Claude Desktop | Open Settings → Developer → Edit Config. The file is `claude_desktop_config.json`; its outer key is `mcpServers`. Windows normally stores it under `%APPDATA%\Claude`; macOS under `~/Library/Application Support/Claude`. | Restart the app, find the filesystem tools, and ask it to list the allowed folder. |
| Claude Code | Project `.mcp.json`, with outer key `mcpServers`. Review the project's server trust request. | Open `/mcp`, inspect the enabled server, then request the directory listing. |
| VS Code | Project `.vscode/mcp.json`, with outer key `servers`; each local entry has `type: stdio`. | Use the MCP server start controls, select its tools in chat, and request the listing. |
| Cursor | Project `.cursor/mcp.json` or user `~/.cursor/mcp.json`, with outer key `mcpServers`. | Enable the server in MCP settings, then request the listing in an agent chat. |

For module 00, use **two** available hosts. Type: “List files in the allowed Lumen
folder. Do not modify files.” Approve read operations only. Then request one
Markdown specification from the listing. Compare the path, tool name and returned
content across both hosts. The reference server is restricted to `data/files`;
its write tools still exist, so the host's approval decision matters.

The committed `host_configs/*.json` files are examples generated on the capture
machine. Regenerate them before use elsewhere. Avoid relative working-directory
assumptions: desktop applications do not necessarily start in your checkout.
If an executable is missing, reopen the terminal after installation and run
`uv run python scripts/check_env.py`. If the host cannot find a server, inspect
its server log; protocol stdout must contain JSON messages only.

## Compatibility and evidence

Configuration formats were checked on **2026-10-30** against the official sources
below. The course's Python and TypeScript clients are pinned to revision
2026-07-28; real stdio captures prove discovery, per-request metadata, tools,
resources, prompts, completions and subscriptions. The official filesystem server
2.1.0 was also tested with that revision.

| Surface | Verified here | Not claimed |
|---|---|---|
| Four host configuration envelopes | JSON generation, absolute path resolution, official documentation | A live UI session in each host, account availability, or identical feature presentation |
| Python SDK 2.3 / TypeScript SDK 2.4 | Offline contracts and real current-revision stdio exchanges | Every host's feature/revision support |
| Prompt pickers and completion UI | Protocol messages and SDK behavior | The same slash-command syntax or completion interface across hosts |
| Subscriptions | Resource and catalog events in both SDK tracks | Every third-party host exposes subscriptions to the user |
| Raw teaching server | Current-revision client and Inspector | Compatibility with hosts that only implement an older revision |

Use the supplied Inspector and clients as the reproducible baseline. A host may
hide prompts, ignore rich content, or use a compatibility revision. Inspect its
wire traffic before diagnosing that as a server implementation failure. SDK-based
services can use the SDK's supported compatibility behavior; the raw teaching
server deliberately supports only the current revision.

## Official sources

Module 10 includes HTTP URL configurations for Claude Code, VS Code and Cursor.
Start the loopback server first, then generate them with
`uv run python scripts/host_configs.py --module 10`. Claude Desktop retains its
stdio reference entries; no desktop remote account or UI behavior is assumed.
The course's current-only endpoint requires a host that supports MCP 2026-07-28.
The supplied SDK clients and Inspector's modern mode are the verified baseline.
Form/URL input and progress are exercised by Lumen Chat v2. Configuration syntax
was checked against the sources below on October 30, 2026; GUI use was not tested.

- [Claude Desktop local server setup](https://modelcontextprotocol.io/docs/2026-07-28/develop/connect-local-servers)
- [Claude Code MCP configuration](https://code.claude.com/docs/en/mcp)
- [VS Code MCP servers](https://code.visualstudio.com/docs/agent-customization/mcp-servers)
- [Cursor MCP configuration](https://cursor.com/docs/mcp)
- [Official filesystem server](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem)

## Feature support snapshot: 2026-10-30

| Host | Documented evidence | Revision/extension boundary |
|---|---|---|
| Claude Desktop | Local stdio configuration with `mcpServers` | Exact current revision and Tasks UI not established by the local setup page; manual GUI check |
| Claude Code | stdio/HTTP; form and URL input; current v2 runtime | Documentation identifies 2026-07-28 runtime and version/flag conditions. Tasks require the documented CLI/SDK version and surface; desktop/VS Code are excluded from that Tasks statement |
| VS Code | `servers` configuration with explicit stdio/HTTP type | Configuration page does not establish current revision or every extension; inspect connection before use |
| Cursor | Tools, prompts, resources, elicitation and Apps listed | Exact wire revision and Tasks support not established by the overview |

Sources: [Desktop](https://modelcontextprotocol.io/docs/2026-07-28/develop/connect-local-servers), [Claude Code](https://code.claude.com/docs/en/mcp), [VS Code](https://code.visualstudio.com/docs/agent-customization/mcp-servers), [Cursor](https://cursor.com/docs/mcp). These are documentation checks, not four executed GUI sessions. Conditional support must not be read as universal support across versions and accounts.

B1 adds [native TypeScript launch configurations](../modules/bonus/B1_typescript_track/host_configs/vscode.json); B2's configurations require building the selected native executable first. Replace the generated absolute checkout paths on another machine. [Lumen Chat Pro](../capstones/05_lumen_chat_pro/README.md) and Inspector remain the locally tested UI/protocol baselines.
