"""Return missing prerequisites before more than one replica: shared_store and shared_limiter.
Concepts: shipping; MCP tools/list and tools/call.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
Run: uv run python modules/20_deployment/python/exercises/02_scale.py
Capture the related server: uv run python scripts/tier5.py --module 20 --capture
Expected: Starter extension checks fail until implemented.
"""


def solve(replicas: int, shared_store: bool, shared_limiter: bool):
    return []


def main() -> None:
    print("Run scripts/check_exercise.py --module 20 --exercise 2")


if __name__ == "__main__":
    main()
