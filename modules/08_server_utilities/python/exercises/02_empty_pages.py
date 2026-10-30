"""Flatten resource pages, preserving values after an empty page.
Run: uv run python modules/08_server_utilities/python/exercises/02_empty_pages.py
Expected: prints the first fixture result; check all cases with scripts/check_exercise.py.
"""


def solve(pages: list[list[str]]) -> object:
    # YOUR CODE HERE: Flatten resource pages, preserving values after an empty page.
    return pages[0] if pages else []


if __name__ == "__main__":
    print(solve(*[[["a"], [], ["b"]]]))
