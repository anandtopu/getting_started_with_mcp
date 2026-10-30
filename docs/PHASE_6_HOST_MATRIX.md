# Phase 6 host compatibility

Checked October 30, 2026. Documentation support and actual test evidence are
separate columns. A stdio configuration does not promise a host implements a
particular Tasks revision or renders an MCP App.

| Host | Verified documentation | Evidence for this course |
|---|---|---|
| Course Python client | Tasks 2026-07-28; Apps resources | Real stdio Tasks create/get/update/cancel, fallback and resource tests |
| Course framework adapters | Six native adapters; three full workflows | Local SDK/CLI connections with deterministic tools |
| Inspector 2.13.0 | Tools/resources discovery | CLI checks of all delivered server entry points; no App UI claim |
| Claude Desktop | MCP Apps SDK documents inline Claude views | Config supplied; desktop rendering is a manual check |
| Claude Code | Local MCP and tool permissions documented | Agent SDK connection tested; no inline App or Tasks support claim |
| VS Code | MCP Apps support documented as Experimental | Config supplied; GUI, setting availability and Tasks revision unverified |
| Cursor | MCP tool connections documented | Config supplied; Apps and Tasks behavior unverified |

Sources: [Apps SDK](https://apps.extensions.modelcontextprotocol.io/api/),
[Claude Code](https://code.claude.com/docs/en/mcp),
[VS Code](https://code.visualstudio.com/docs/agent-customization/mcp-servers),
[Cursor](https://cursor.com/docs/mcp).
The Apps SDK's generic clients link redirected to introductory documentation when
checked; it is not evidence for an individual host's extension support.

The official [extension inventory](https://modelcontextprotocol.io/extensions/overview)
lists Tasks as **Beta, to Core** and Apps as **Stable**. The released Tasks
2026-07-28 specification is the wire contract used here; its versioned release
label is distinct from the inventory's maturity classification.

## Manual App check

1. Generate the current checkout's config with
   `uv run python scripts/host_configs.py --module 17`.
2. Merge the matching config into a host that documents Apps support. Enable its
   feature setting if needed, then restart/reload the server.
3. Ask for `analytics_dashboard`. Confirm 400 synthetic work items and three
   status counts. Select **Refresh counts** and confirm the same result.
4. Confirm the host uses a sandboxed view and enforces the resource's empty
   network/frame CSP allowlists. No external network permission is needed.
5. Close the view. Repeat in a plain client and confirm useful text still works.

Opening the HTML directly is not an MCP host: its bridge needs a parent. The
course tests the official App/AppBridge handshake and messages separately from
host rendering. Report the exact host version and settings when recording a GUI
result; none is claimed by the automated checkpoint.
