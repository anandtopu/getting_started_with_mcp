"""Embed retrieved source content in a multi-message incident prompt.

Concepts/spec: see ../../README.md, Key APIs and Go deeper.
Run: uv run python modules/04_prompts/python/examples/02_embedded_context.py
Expected: user text, user resource, customer meeting context
Inspect/capture: uv run python scripts/tier1.py --module 4 --capture
"""

import asyncio

from mcp import Client

from common.prompts import prompt_server


async def main() -> None:
    async with Client(prompt_server()) as client:
        result = await client.get_prompt(
            "summarize_incident", {"space": "incident_postmortems", "page": "page-01"}
        )
        for message in result.messages:
            print(message.role, message.content.type)
        print((await client.get_prompt("prepare_meeting", {"customer_id": "1"})).messages)


if __name__ == "__main__":
    asyncio.run(main())
