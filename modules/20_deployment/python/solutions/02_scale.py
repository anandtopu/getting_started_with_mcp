"""Return missing prerequisites before more than one replica: shared_store and shared_limiter.
Concepts: shipping; MCP tools/list and tools/call.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
Run: uv run python modules/20_deployment/python/solutions/02_scale.py
Capture the related server: uv run python scripts/tier5.py --module 20 --capture
Expected: All contract cases pass.
"""


def solve(replicas: int, shared_store: bool, shared_limiter: bool):
    return (
        []
        if replicas <= 1
        else [
            name
            for name, enabled in [
                ("shared_store", shared_store),
                ("shared_limiter", shared_limiter),
            ]
            if not enabled
        ]
    )


def main() -> None:
    print("Run scripts/check_exercise.py --module 20 --exercise 2 --solution")


if __name__ == "__main__":
    main()
