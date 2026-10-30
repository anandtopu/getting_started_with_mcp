"""Return only aggregate status, duration_ms, and request_id; omit token, arguments, and
unknown fields.
Concepts: shipping; MCP tools/list and tools/call.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
Run: uv run python modules/20_deployment/python/solutions/03_log_redaction.py
Capture the related server: uv run python scripts/tier5.py --module 20 --capture
Expected: All contract cases pass.
"""


def solve(event: dict):
    return {key: event[key] for key in ("status", "duration_ms", "request_id") if key in event}


def main() -> None:
    print("Run scripts/check_exercise.py --module 20 --exercise 3 --solution")


if __name__ == "__main__":
    main()
