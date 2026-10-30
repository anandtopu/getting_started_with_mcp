"""Runnable policy exercise. See the bonus README for the contract."""


def solve(names: list[str], limit: int) -> list[str]:
    if not 1 <= limit <= 20:
        raise ValueError("Choose 1-20 names")
    return sorted(set(names))[:limit]
