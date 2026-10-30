"""Request context-sensitive completions and refresh a changed prompt catalog.

Concepts/spec: see ../../README.md, Key APIs and Go deeper.
Run: uv run python modules/04_prompts/python/examples/03_prompt_completion.py
Expected: eight page suggestions and review_checklist after catalog change
Inspect/capture: uv run python scripts/tier1.py --module 4 --capture
"""

import asyncio

from mcp_types import PromptReference

from common.connections import connection


async def main() -> None:
    async with connection("prompts") as client:
        result = await client.complete(
            ref=PromptReference(name="summarize_incident"),
            argument={"name": "page", "value": "page-0"},
            context_arguments={"space": "engineering"},
        )
        print(result.completion.values)
        limited = await client.complete(
            ref=PromptReference(name="release_notes"), argument={"name": "issue_ids", "value": ""}
        )
        print(
            "Suggestions/total/has_more:",
            len(limited.completion.values),
            limited.completion.total,
            limited.completion.has_more,
        )
        async with client.listen(prompts_list_changed=True) as events:
            await client.call_tool("enable_checklist", {"confirmed": True})
            async with asyncio.timeout(5):
                print(await anext(aiter(events)))
            print([p.name for p in (await client.list_prompts(cache_mode="refresh")).prompts])


if __name__ == "__main__":
    asyncio.run(main())
