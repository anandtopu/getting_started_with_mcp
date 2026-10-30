# Legacy → current: Tier 1 migration notes

This guide is the only place the course presents old API syntax and protocol
lifecycle examples. The main lessons target **2026-07-28**. This is the Tier 1
portion; later phases will extend HTTP, authorization and utility migrations.

## Connection lifecycle

**Legacy:** a client sent `initialize` with its protocol version and capabilities,
the server returned its selected version and capabilities, and the client sent
`notifications/initialized`. Subsequent requests relied on that negotiated
connection state. Those messages are explained here as historical behavior,
not as a current startup recipe.

**Current:** a client uses `server/discover` to inspect support, and carries the
protocol revision and client capabilities in each request's reserved `_meta`
fields. Server identity can appear in result metadata. Cacheable complete results
carry freshness and scope. [Module 01's real captures](../modules/01_architecture_wire/wire/01_jsonrpc.jsonl)
show that flow. Discovery does not create an implicit protocol session.

For HTTP, old code often depended on `Mcp-Session-Id`. Do not carry that assumption
into the current track. Explicit application handles and subscription lifetimes
remain possible without a protocol-level session handshake.

## Python high-level server

Old, v1-only tutorial syntax:

```python
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

server = FastMCP("Lumen")
```

Current official SDK v2 syntax:

```python
from mcp.server import MCPServer
from mcp_types import TextContent

server = MCPServer("Lumen", version="1.0")
```

Transport settings belong to run methods. The standalone third-party FastMCP
project is a separate package; it is not the official SDK used by this course.

The v2 low-level `Server.run` still accepts a parameter named
`initialization_options`, populated with `create_initialization_options()`.
It describes server identity and capabilities for the SDK's dual-era runner;
its name does not imply that a current client sends the Legacy handshake.
[The pagination capture](../modules/05_first_client/wire/02_pages_and_errors.jsonl)
verifies current per-request behavior through this public v2 API.

## TypeScript package and handlers

The requested older monolithic `@modelcontextprotocol/sdk` package belongs to the
v1 line. This course uses official split v2 `@modelcontextprotocol/server` and
`@modelcontextprotocol/client`. Tool input schemas are `z.object(...)` values.
Current low-level handlers use literal method names, such as
`setRequestHandler('resources/list', handler)`, rather than old runtime schema
tokens. Choose current version negotiation explicitly in the client and serve
stdio with the v2 `serveStdio` entry point.

## Resource change delivery

**Legacy:** `resources/subscribe` and `resources/unsubscribe` managed resource
notifications associated with an established connection.

**Current:** `subscriptions/listen` declares a filter and returns an acknowledged
subscription stream. It can opt into resource updates and tool/resource/prompt
catalog changes. On disconnect, recreate the listener and refetch content;
do not assume missed events can be replayed.

## Later-tier migrations

HTTP+SSE and Dynamic Client Registration are historical compatibility concerns;
the planned current track uses Streamable HTTP and Client ID Metadata Documents.
Roots, sampling and protocol logging are Deprecated topics. Modules 08–09 teach
configured path boundaries, direct model providers, and stderr/OpenTelemetry
replacements before analyzing historical exchanges. No current-track application depends
on those deprecated features.

Sources: [current specification](https://modelcontextprotocol.io/specification/2026-07-28),
[official Python SDK](https://py.sdk.modelcontextprotocol.io/),
[official TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk).

## Phase 4 historical traffic lab — Deprecated, analysis only

The following isolated fixture deliberately uses the older protocol to explain
existing captures. It is not a current-track server. The sampling callback is a
constant fake; no provider is contacted. A root is advisory context, not a filesystem
sandbox. The current alternatives are [configured paths and direct generation](../common/files_model.py).
Old HTTP `Mcp-Session-Id` and `Last-Event-ID` behavior must not be copied into the
current transport: reconnect by reissuing a POST subscription and refetching state.

Run `uv run python scripts/capture_migration.py` to extract these two code blocks
into ignored scratch files, execute them, and refresh the actual messages below.
Exact deprecated API calls stay in this guide; the extraction script is generic.

<!-- migration:server -->
```python
from mcp.server import MCPServer
from mcp.server.mcpserver import Context
from mcp_types import SamplingMessage, TextContent

server = MCPServer("Historical Lumen fixture")


@server.tool()
async def analyze_history(ctx: Context) -> str:
    roots = await ctx.request_context.session.list_roots()
    reply = await ctx.request_context.session.create_message(
        messages=[
            SamplingMessage(
                role="user",
                content=TextContent(type="text", text="Summarize the synthetic fixture."),
            )
        ],
        max_tokens=40,
    )
    return f"Root count: {len(roots.roots)}; fake response: {reply.content.text}"


if __name__ == "__main__":
    server.run()
```

<!-- migration:client -->
```python
import asyncio
import sys
from mcp import Client, StdioServerParameters
from mcp_types import CreateMessageResult, ListRootsResult, Root, TextContent
from common.config import ROOT


async def roots(context):
    return ListRootsResult(roots=[Root(uri=(ROOT / "data/files").as_uri(), name="Fixture")])


async def sample(context, params):
    return CreateMessageResult(
        role="assistant",
        content=TextContent(type="text", text="Historical fake summary"),
        model="fixture",
        stop_reason="endTurn",
    )


async def main():
    params = StdioServerParameters(
        command=sys.executable,
        cwd=str(ROOT),
        args=[
            str(ROOT / "scripts/wiretap.py"),
            "--capture",
            str(ROOT / ".runtime/migration.jsonl"),
            "--",
            sys.executable,
            str(ROOT / ".runtime/migration_server.py"),
        ],
    )
    async with Client(
        params, mode="legacy", list_roots_callback=roots, sampling_callback=sample
    ) as client:
        result = await client.call_tool("analyze_history", {})
        assert not result.is_error


if __name__ == "__main__":
    asyncio.run(main())
```

### Captured historical messages

<!-- migration:wire:start -->

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-11-25",
    "capabilities": {
      "sampling": {},
      "roots": {
        "listChanged": true
      }
    },
    "clientInfo": {
      "name": "mcp",
      "version": "0.1.0"
    }
  }
}
```

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "capabilities": {
      "prompts": {
        "listChanged": false
      },
      "resources": {
        "listChanged": false,
        "subscribe": false
      },
      "tools": {
        "listChanged": false
      }
    },
    "protocolVersion": "2025-11-25",
    "serverInfo": {
      "name": "Historical Lumen fixture",
      "version": ""
    }
  }
}
```

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/initialized"
}
```

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "analyze_history",
    "arguments": {}
  }
}
```

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "roots/list"
}
```

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "roots": [
      {
        "uri": "file:///D:/Learning_Projects/getting_started_with_mcp_prompt/data/files",
        "name": "Fixture"
      }
    ]
  }
}
```

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "sampling/createMessage",
  "params": {
    "messages": [
      {
        "role": "user",
        "content": {
          "type": "text",
          "text": "Summarize the synthetic fixture."
        }
      }
    ],
    "maxTokens": "[REDACTED]"
  }
}
```

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "role": "assistant",
    "content": {
      "type": "text",
      "text": "Historical fake summary"
    },
    "model": "fixture",
    "stopReason": "endTurn"
  }
}
```

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "text": "Root count: 1; fake response: Historical fake summary",
        "type": "text"
      }
    ],
    "isError": false,
    "structuredContent": {
      "result": "Root count: 1; fake response: Historical fake summary"
    }
  }
}
```

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/list"
}
```

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "tools": [
      {
        "description": "",
        "inputSchema": {
          "properties": {},
          "type": "object",
          "title": "analyze_historyArguments"
        },
        "name": "analyze_history",
        "outputSchema": {
          "properties": {
            "result": {
              "title": "Result",
              "type": "string"
            }
          },
          "required": [
            "result"
          ],
          "type": "object",
          "title": "analyze_historyOutput"
        }
      }
    ]
  }
}
```

<!-- migration:wire:end -->

Read the request IDs in both directions. In this old flow the server initiates
separate root and sampling requests while a tool is running. The current input
flow instead returns `input_required` and the host retries with an answer.
Neither old roots nor a model response establishes permission to read a file or
perform a write. Module 09 obtains human consent and enforces its own configured
path boundary.
