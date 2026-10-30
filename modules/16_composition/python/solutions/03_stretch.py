"""Partition catalog keys by principal, distinct scopes and policy revision.
Run: uv run python modules/16_composition/python/solutions/03_stretch.py
Expected: one sample result; use scripts/check_exercise.py for the full contract.
"""


def solve(principal: str, scopes: list[str], revision: int):
    return [principal, sorted(set(scopes)), revision]


if __name__ == "__main__":
    print(solve(*["alex", ["write", "read", "read"], 2]))
