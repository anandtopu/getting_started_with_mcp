"""Clear only the resource catalog on its list-change event.
Run: uv run python modules/05_first_client/python/solutions/03_stretch.py
Check: uv run python scripts/check_exercise.py --module 5 --exercise 3 --solution
The starter demonstrates a narrower behavior. Extend it to satisfy the checks.
"""


def solve(cache: dict, method: str):
    return {
        key: value
        for key, value in cache.items()
        if key != "resources" or method != "notifications/resources/list_changed"
    }


def main() -> None:
    print(
        solve(
            *[{"resources": ["old"], "tools": ["search"]}, "notifications/resources/list_changed"]
        )
    )


if __name__ == "__main__":
    main()
