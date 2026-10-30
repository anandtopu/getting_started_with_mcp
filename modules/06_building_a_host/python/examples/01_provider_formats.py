"""Translate one MCP tool into four provider schema envelopes.

Concepts/spec: see ../../README.md, Key APIs and Go deeper.
Run: uv run python modules/06_building_a_host/python/examples/01_provider_formats.py
Expected: input_schema, parameters, parameters_json_schema, function.parameters
Inspect/capture: uv run python scripts/tier1.py --module 6 --capture
"""

import json

from common.tool_formats import provider_tools


def main() -> None:
    tool = {
        "name": "notes__search_notes",
        "description": "Find Lumen notes by text.",
        "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}}},
    }
    for provider in ["anthropic", "openai", "gemini", "ollama"]:
        print(provider, json.dumps(provider_tools(provider, [tool])))


if __name__ == "__main__":
    main()
