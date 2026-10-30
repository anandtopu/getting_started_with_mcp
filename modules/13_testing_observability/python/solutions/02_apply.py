"""Score exact tool name AND arguments; empty evaluations return zero.
Run: uv run python modules/13_testing_observability/python/solutions/02_apply.py
Expected: print one baseline result; run the shared exercise checker for all cases.
"""


def solve(actual: list[dict], expected: list[dict]):
    return sum(a == e for a, e in zip(actual, expected, strict=True))


if __name__ == "__main__":
    print(
        solve(
            *[
                [{"name": "read", "arguments": {"id": 1}}],
                [{"name": "read", "arguments": {"id": 1}}],
            ]
        )
    )
