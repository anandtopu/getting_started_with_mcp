"""Exercise a bounded per-principal request window with a deterministic clock.
Concepts: shipping; MCP tools/list and tools/call.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
Run: uv run python modules/20_deployment/python/examples/02_rate_budget.py
Capture the related server: uv run python scripts/tier5.py --module 20 --capture
Expected: PASS per-principal budget and expiry
"""

from common.deployment import Operations


def main() -> None:
    now = [0.0]
    limiter = Operations(None, None, limit=2, clock=lambda: now[0])
    # KEY IDEA: use a verified subject, not a caller-supplied user header.
    assert [limiter.allow("verified-alex") for _ in range(3)] == [True, True, False]
    assert limiter.allow("verified-sam")
    now[0] = 61
    assert limiter.allow("verified-alex")
    print("PASS per-principal budget and expiry")


if __name__ == "__main__":
    main()
