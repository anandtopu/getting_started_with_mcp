# Tier 1 / Foundations

Read the wire; build a useful local server. [Printable one-page PDF](01_tier_1.pdf).

## Mental model

- Host = UI, model and permissions. Client = one protocol peer. Server = capabilities and allowed data.
- Tools perform operations; resources expose content; prompts provide templates. The host chooses what enters model context.

## First run

- uv sync; npm ci
- uv run python scripts/check_env.py
- uv run python scripts/foundation_server.py (waits for protocol input)
- npm run inspector -- uv run python scripts/foundation_server.py

## Current exchange

- Target 2026-07-28. Discover support with server/discover. Every request carries revision and client capabilities in reserved _meta keys.
- Match response IDs to request IDs. Notifications have no ID and no response.
- A complete tool result may still have isError=true.

## Useful primitives

- tools/list -> tools/call
- resources/list or resources/templates/list -> resources/read
- prompts/list -> prompts/get; completion/complete suggests an argument value.

## Security habits

- Keep stdout exclusively for JSON-RPC; log to stderr.
- Validate argument shape and bounds at runtime. Tool annotations are hints, not authorization.
- Require a separate review before a write; never let a model grant its own permission.

## Checkpoint

- uv run python scripts/tier1.py
- Explain the request, response, resource URI and approval boundary.
- Next: modules 07-10; details in docs/PROTOCOL_GUIDE.md.

[Full protocol guide](../docs/PROTOCOL_GUIDE.md) · [Learning path](../LEARNING_PATH.md)
