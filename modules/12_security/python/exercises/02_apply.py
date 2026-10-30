"""Allow a proposed namespaced tool only if it is both pinned and approved for this host.
Run: uv run python modules/12_security/python/exercises/02_apply.py
Expected: print one baseline result; run the shared exercise checker for all cases.
"""


def solve(name: str, pinned: list[str], allowed: list[str]):
    # YOUR CODE HERE: extend this deliberately narrower baseline.
    return name in pinned


if __name__ == "__main__":
    print(solve(*["wiki__read", ["wiki__read"], ["wiki__read"]]))
