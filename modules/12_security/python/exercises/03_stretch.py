"""Reduce an audit event to the approved field set; no arguments or tokens.
Run: uv run python modules/12_security/python/exercises/03_stretch.py
Expected: print one baseline result; run the shared exercise checker for all cases.
"""


def solve(event: dict):
    # YOUR CODE HERE: extend this deliberately narrower baseline.
    return dict(event)


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
