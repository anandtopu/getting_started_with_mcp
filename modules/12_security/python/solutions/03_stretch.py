"""Reduce an audit event to the approved field set; no arguments or tokens.
Run: uv run python modules/12_security/python/solutions/03_stretch.py
Expected: print one baseline result; run the shared exercise checker for all cases.
"""


def solve(event: dict):
    return {key: event[key] for key in ("event", "principal", "allowed") if key in event}


if __name__ == "__main__":
    print(
        solve(
            *[
                {
                    "event": "read",
                    "principal": "learner",
                    "allowed": False,
                    "token": "fake",
                    "arguments": {"salary": 1},
                }
            ]
        )
    )
