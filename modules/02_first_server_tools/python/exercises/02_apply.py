"""Return an error tool result on denial and a text result after approval.
Run: uv run python modules/02_first_server_tools/python/exercises/02_apply.py
Check: uv run python scripts/check_exercise.py --module 2 --exercise 2
The starter demonstrates a narrower behavior. Extend it to satisfy the checks.
"""


def solve(confirmed: bool):
    # YOUR CODE HERE: Return an error tool result on denial and a text result after approval.
    return {"content": [{"type": "text", "text": "Saved"}], "isError": False}


def main() -> None:
    print(solve(*[False]))


if __name__ == "__main__":
    main()
