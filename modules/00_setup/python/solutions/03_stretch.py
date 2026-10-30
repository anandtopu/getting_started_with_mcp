"""Build the two different host envelopes without changing the server entry.
Run: uv run python modules/00_setup/python/solutions/03_stretch.py
Check: uv run python scripts/check_exercise.py --module 0 --exercise 3 --solution
The starter demonstrates a narrower behavior. Extend it to satisfy the checks.
"""


def solve(host: str, server: dict):
    return {"servers" if host == "vscode" else "mcpServers": {"lumen": server}}


def main() -> None:
    print(solve(*["vscode", {"command": "uv", "args": ["run"]}]))


if __name__ == "__main__":
    main()
