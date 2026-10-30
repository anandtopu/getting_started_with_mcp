"""Keep source text in an embedded resource with its URI and MIME type.
Run: uv run python modules/04_prompts/python/exercises/02_apply.py
Check: uv run python scripts/check_exercise.py --module 4 --exercise 2
The starter demonstrates a narrower behavior. Extend it to satisfy the checks.
"""


def solve(uri: str, source: str):
    # YOUR CODE HERE: Keep source text in an embedded resource with its URI and MIME type.
    return {"role": "user", "content": {"type": "text", "text": source}}


def main() -> None:
    print(solve(*["wiki://engineering/page-01", "# Review"]))


if __name__ == "__main__":
    main()
