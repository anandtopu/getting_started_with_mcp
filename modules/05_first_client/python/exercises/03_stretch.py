"""Clear only the resource catalog on its list-change event.
Run: uv run python modules/05_first_client/python/exercises/03_stretch.py
Check: uv run python scripts/check_exercise.py --module 5 --exercise 3
The starter demonstrates a narrower behavior. Extend it to satisfy the checks.
"""


def solve(cache: dict, method: str):
    # YOUR CODE HERE: Clear only the resource catalog on its list-change event.
    return dict(cache)


def main() -> None:
    print(
        solve(
            *[{"resources": ["old"], "tools": ["search"]}, "notifications/resources/list_changed"]
        )
    )


if __name__ == "__main__":
    main()
