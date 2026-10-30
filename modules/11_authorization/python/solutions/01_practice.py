"""Combine prior scopes and a scope challenge without duplicates.
Run: uv run python modules/11_authorization/python/solutions/01_practice.py
Expected: print one baseline result; run the shared exercise checker for all cases.
"""


def solve(prior: list[str], challenge: list[str]):
    return sorted(set(prior) | set(challenge))


if __name__ == "__main__":
    print(solve(*[["issues:read"], ["issues:write"]]))
