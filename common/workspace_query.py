"""A CLI client can answer a fixed question without a language model."""

import argparse
import asyncio

from common.connections import connection


async def query(text: str, space: str, page: str, watch_once: bool = False) -> None:
    async with connection("notes") as notes, connection("wiki") as wiki:
        print(
            (await notes.call_tool("search_notes", {"query": text})).model_dump_json(by_alias=True)
        )
        print((await wiki.read_resource(f"wiki://{space}/{page}")).contents[0].text)
        if watch_once:
            cache = {"lumen://bulletin": await wiki.read_resource("lumen://bulletin")}
            async with wiki.listen(resource_subscriptions=["lumen://bulletin"]) as events:
                await wiki.call_tool(
                    "update_bulletin", {"text": "CLI review complete", "confirmed": True}
                )
                async with asyncio.timeout(5):
                    event = await anext(aiter(events))
                cache.pop(str(event.uri), None)
                cache["lumen://bulletin"] = await wiki.read_resource("lumen://bulletin")
                print("Refetched:", cache["lumen://bulletin"].contents[0].text)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", default="release")
    parser.add_argument("--space", default="engineering")
    parser.add_argument("--page", default="page-01")
    parser.add_argument("--watch-once", action="store_true")
    parser.add_argument(
        "--confirm-demo-write",
        action="store_true",
        help="Approve the fixed in-memory CLI review bulletin update.",
    )
    args = parser.parse_args()
    if args.watch_once and not args.confirm_demo_write:
        parser.exit(1, "Review the demo write, then add --confirm-demo-write to approve it.\n")
    asyncio.run(query(args.query, args.space, args.page, args.watch_once))
