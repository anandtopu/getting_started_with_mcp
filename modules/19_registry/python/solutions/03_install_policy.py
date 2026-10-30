"""Allow a reviewed installation only when identity, source and requested permissions are
approved and an exact version is pinned.
Concepts: shipping; MCP tools/list and tools/call.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
Run: uv run python modules/19_registry/python/solutions/03_install_policy.py
Capture the related server: uv run python scripts/tier5.py --module 19 --capture
Expected: All contract cases pass.
"""


def solve(review: dict):
    return all(review.get(k) is True for k in ("identity", "source", "permissions")) and review.get(
        "version"
    ) not in (None, "", "latest", "*")


def main() -> None:
    print("Run scripts/check_exercise.py --module 19 --exercise 3 --solution")


if __name__ == "__main__":
    main()
