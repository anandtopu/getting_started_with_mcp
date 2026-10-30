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
Roots, sampling and protocol logging are Deprecated topics. The course will teach
configured path boundaries, direct model providers, and stderr/OpenTelemetry
replacements before analyzing historical exchanges. No Tier 1 application depends
on those deprecated features.

Sources: [current specification](https://modelcontextprotocol.io/specification/2026-07-28),
[official Python SDK](https://py.sdk.modelcontextprotocol.io/),
[official TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk).
