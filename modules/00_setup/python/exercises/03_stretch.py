"""Build the two different host envelopes without changing the server entry.
Run: uv run python modules/00_setup/python/exercises/03_stretch.py
Check: uv run python scripts/check_exercise.py --module 0 --exercise 3
The starter demonstrates a narrower behavior. Extend it to satisfy the checks.
"""


def solve(host: str, server: dict):
    # YOUR CODE HERE: Build the two different host envelopes without changing the server entry.
    return {"mcpServers": {"lumen": server}}


def main() -> None:
    print(solve(*["vscode", {"command": "uv", "args": ["run"]}]))


if __name__ == "__main__":
    main()
