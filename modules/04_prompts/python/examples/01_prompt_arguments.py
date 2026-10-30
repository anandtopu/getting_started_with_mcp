"""List prompt arguments and explicitly choose a release workflow.

Concepts/spec: see ../../README.md, Key APIs and Go deeper.
Run: uv run python modules/04_prompts/python/examples/01_prompt_arguments.py
Expected: three prompts, a draft instruction containing real synthetic issue rows
Inspect/capture: uv run python scripts/tier1.py --module 4 --capture
"""

import asyncio

from mcp import Client

from common.prompts import prompt_server


async def main() -> None:
    async with Client(prompt_server()) as client:
        print([p.name for p in (await client.list_prompts()).prompts])
        print((await client.get_prompt("release_notes", {"issue_ids": "1,2"})).messages)


if __name__ == "__main__":
    asyncio.run(main())
