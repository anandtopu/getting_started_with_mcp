"""Combine prior scopes and a scope challenge without duplicates.
Run: uv run python modules/11_authorization/python/exercises/01_practice.py
Expected: print one baseline result; run the shared exercise checker for all cases.
"""


def solve(prior: list[str], challenge: list[str]):
    # YOUR CODE HERE: extend this deliberately narrower baseline.
    return sorted(set(prior))


if __name__ == "__main__":
    print(solve(*[["issues:read"], ["issues:write"]]))
