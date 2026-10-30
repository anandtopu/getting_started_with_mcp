"""Allow a proposed namespaced tool only if it is both pinned and approved for this host.
Run: uv run python modules/12_security/python/solutions/02_apply.py
Expected: print one baseline result; run the shared exercise checker for all cases.
"""


def solve(name: str, pinned: list[str], allowed: list[str]):
    return name in pinned and name in allowed


if __name__ == "__main__":
    print(solve(*["wiki__read", ["wiki__read"], ["wiki__read"]]))
