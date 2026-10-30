"""Offer page completions only when prior context names a valid space.
Run: uv run python modules/04_prompts/python/solutions/03_stretch.py
Check: uv run python scripts/check_exercise.py --module 4 --exercise 3 --solution
The starter demonstrates a narrower behavior. Extend it to satisfy the checks.
"""


def solve(prefix: str, context: dict):
    from common.wiki import SPACES

    return (
        [f"page-{i:02d}" for i in range(1, 9) if f"page-{i:02d}".startswith(prefix)]
        if context.get("space") in SPACES
        else []
    )


def main() -> None:
    print(solve(*["page-01", {"space": "engineering"}]))


if __name__ == "__main__":
    main()
