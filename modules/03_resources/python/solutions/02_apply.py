"""Choose text for text/* and blob for binary MIME types.
Run: uv run python modules/03_resources/python/solutions/02_apply.py
Check: uv run python scripts/check_exercise.py --module 3 --exercise 2 --solution
The starter demonstrates a narrower behavior. Extend it to satisfy the checks.
"""


def solve(mime: str):
    return "text" if mime.startswith("text/") else "blob"


def main() -> None:
    print(solve(*["text/markdown"]))


if __name__ == "__main__":
    main()
