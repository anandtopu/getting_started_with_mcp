"""Make the name field required and reject empty names in a tool input schema.
Run: uv run python modules/02_first_server_tools/python/solutions/01_practice.py
Check: uv run python scripts/check_exercise.py --module 2 --exercise 1 --solution
The starter demonstrates a narrower behavior. Extend it to satisfy the checks.
"""


def solve():
    return {
        "type": "object",
        "properties": {"name": {"type": "string", "minLength": 1}},
        "required": ["name"],
    }


def main() -> None:
    print(solve(*[]))


if __name__ == "__main__":
    main()
