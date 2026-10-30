"""Negotiate Apps only when both sides advertise its ID and the client accepts its MIME type.
Run: uv run python modules/17_extensions/python/exercises/01_practice.py
Expected: one sample result; use scripts/check_exercise.py for the full contract.
"""


def solve(client: dict, server: dict):
    # YOUR CODE HERE: extend this narrower working baseline.
    return bool(client)


if __name__ == "__main__":
    print(
        solve(
            *[
                {"io.modelcontextprotocol/ui": {"mimeTypes": ["text/html;profile=mcp-app"]}},
                {"io.modelcontextprotocol/ui": {}},
            ]
        )
    )
