# Tier 2 checkpoint: Lumen Workspace v4 and Chat v2

Run from the repository root:

```text
uv sync --frozen --extra http --extra host
npm ci
uv run python -m common.chat_v2 --demo
uv run python scripts/tier2.py
```

The fixed demo reads release notes, finds the engineering wiki page, reads two
usage rows, confirms closing synthetic issues 1 and 2, and produces four report
progress events. It ends with `Tier 2 fixture complete`. It changes only a
disposable database copy and never contacts a model provider.

For the HTTP route, keep this running in one terminal:

```text
uv run python modules/10_streamable_http/python/examples/01_http_server.py
```

In a second terminal:

```text
uv run python -m common.chat_v2 --demo --http http://127.0.0.1:8000/mcp
```

Wiki and reports now use HTTP. The other services remain local stdio services.
You can substitute the TypeScript server on the same port:

```text
npm exec tsx -- modules/10_streamable_http/typescript/examples/01_http_server.ts
```

Before moving on, demonstrate each of these outcomes:

- A denied or cancelled form leaves the issue unchanged.
- Changing arguments, replaying state, or submitting a string instead of a boolean fails.
- Accepting a URL without completing its browser action does not authorize the export.
- An analytics page is bounded and provides a resource link when more rows exist.
- Cancelling the report returns active work to zero.
- An untrusted Origin gets 403 and mismatched mirrored headers get 400.
- Reissuing a subscription refetches current state rather than claiming missed-event replay.
- Retrying an issue creation with its original key does not create another issue.

`tests/test_tier2.py` verifies these boundaries, and the transport checks run
against both languages. For manual input, omit `--demo`; the host asks before
every tool call and handles forms separately from model tool arguments. Live
providers need their configured model and key. Phase 5 adds authentication and
security topics; this checkpoint is a loopback learning service.
