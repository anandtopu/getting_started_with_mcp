"""Convert a MCP definition to Anthropic input_schema without losing its description.
Run: uv run python modules/06_building_a_host/python/solutions/01_practice.py
Check: uv run python scripts/check_exercise.py --module 6 --exercise 1 --solution
The starter demonstrates a narrower behavior. Extend it to satisfy the checks.
"""


def solve(tool: dict):
    return {
        "name": tool["name"],
        "description": tool.get("description", ""),
        "input_schema": tool["inputSchema"],
    }


def main() -> None:
    print(
        solve(*[{"name": "search", "description": "Find notes", "inputSchema": {"type": "object"}}])
    )


if __name__ == "__main__":
    main()
