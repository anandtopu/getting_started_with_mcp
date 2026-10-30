"""Summarize timings without dropping failures; errors remain visible and input order is irrelevant.
Run: uv run python modules/13_testing_observability/python/exercises/03_stretch.py
Expected: print one baseline result; run the shared exercise checker for all cases.
"""


def solve(records: list[dict]):
    # YOUR CODE HERE: extend this deliberately narrower baseline.
    return {"requests": len(records), "errors": 0, "max_ms": 0}


if __name__ == "__main__":
    print(solve(*[[{"ok": True, "ms": 3}, {"ok": False, "ms": 8}]]))
