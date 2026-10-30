# Tier 4 / Ecosystem

Compose services and negotiate extensions. [Printable one-page PDF](04_tier_4.pdf).

## Tool design

- Descriptions state scope, input constraints, effect and returned evidence.
- Compare catalog size and task success before adding more tools.
- An output schema validates structure; it does not prove factual accuracy.

## Frameworks

- Frameworks own orchestration; MCP owns the external capability boundary.
- The TypeScript track runs Agents SDK, LangChain and LangGraph against one read-only workflow.
- Keep model/runtime versions and approval policy explicit.

## Gateway

- Use fixed upstream aliases and collision-free names. Partition catalogs/caches by principal and scopes.
- Recheck permissions at execution; limit rates and record redacted audit events.
- A failed upstream should not silently expose hidden tools or block unrelated safe reads.

## Tasks

- Advertise io.modelcontextprotocol/tasks before accepting a task handle.
- Poll tasks/get; answer input with tasks/update; cancel with tasks/cancel.
- Persist ownership and expiry. Bound polling. A current Task handle is not the legacy SDK task shape.

## Apps and Skills

- Apps link a tool to a UI resource and a controlled bridge. Enforce browser sandbox/CSP and a narrow tool allowlist.
- Skills are discovered and byte-verified before a separate activation decision. Origin plus URI identifies a skill.

## Checkpoint

- uv run python scripts/tier4.py
- uv run python scripts/gateway_lab.py
- Next: Gateway capstone and shipping modules 18-21.

[Full protocol guide](../docs/PROTOCOL_GUIDE.md) · [Learning path](../LEARNING_PATH.md)
