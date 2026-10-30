"""Match the exact issuer recorded before redirect; missing or changed issuer fails.
Run: uv run python modules/11_authorization/python/exercises/02_apply.py
Expected: print one baseline result; run the shared exercise checker for all cases.
"""


def solve(expected: str, returned: str | None):
    # YOUR CODE HERE: extend this deliberately narrower baseline.
    return returned is not None


if __name__ == "__main__":
    print(solve(*["https://auth.example", "https://auth.example"]))
