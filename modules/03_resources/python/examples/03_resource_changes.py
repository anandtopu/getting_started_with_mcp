"""Listen before changing a resource, then refetch after invalidation.

Concepts/spec: see ../../README.md, Key APIs and Go deeper.
Run: uv run python modules/03_resources/python/examples/03_resource_changes.py
Expected: resource update notification and Review complete
Inspect/capture: uv run python scripts/tier1.py --module 3 --capture
"""

import asyncio

from common.connections import connection


async def main() -> None:
    async with connection("wiki") as client:
        async with client.listen(
            resources_list_changed=True, resource_subscriptions=["lumen://bulletin"]
        ) as events:
            await client.call_tool(
                "update_bulletin", {"text": "Review complete", "confirmed": True}
            )
            async with asyncio.timeout(5):
                event = await anext(aiter(events))
            print(event)
            print((await client.read_resource("lumen://bulletin")).contents[0].text)


if __name__ == "__main__":
    asyncio.run(main())
