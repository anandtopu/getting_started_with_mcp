"""Summarize timings without dropping failures; errors remain visible and input order is irrelevant.
Run: uv run python modules/13_testing_observability/python/solutions/03_stretch.py
Expected: print one baseline result; run the shared exercise checker for all cases.
"""


def solve(records: list[dict]):
    return {
        "requests": len(records),
        "errors": sum(not row["ok"] for row in records),
        "max_ms": max((row["ms"] for row in records), default=0),
    }


if __name__ == "__main__":
    print(solve(*[[{"ok": True, "ms": 3}, {"ok": False, "ms": 8}]]))
