"""Keep only outstanding input-response keys; stale responses are ignored.
Run: uv run python modules/17_extensions/python/solutions/03_stretch.py
Expected: one sample result; use scripts/check_exercise.py for the full contract.
"""


def solve(outstanding: list[str], responses: dict):
    return {key: value for key, value in responses.items() if key in outstanding}


if __name__ == "__main__":
    print(
        solve(*[["details-1"], {"details-1": {"action": "accept"}, "old": {"action": "decline"}}])
    )
