"""Negotiate Apps only when both sides advertise its ID and the client accepts its MIME type.
Run: uv run python modules/17_extensions/python/solutions/01_practice.py
Expected: one sample result; use scripts/check_exercise.py for the full contract.
"""


def solve(client: dict, server: dict):
    key = "io.modelcontextprotocol/ui"
    return key in server and "text/html;profile=mcp-app" in client.get(key, {}).get("mimeTypes", [])


if __name__ == "__main__":
    print(
        solve(
            *[
                {"io.modelcontextprotocol/ui": {"mimeTypes": ["text/html;profile=mcp-app"]}},
                {"io.modelcontextprotocol/ui": {}},
            ]
        )
    )
