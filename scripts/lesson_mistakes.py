"""Reproduce four common mistakes per lesson, then print the actual returned error.

Run: uv run python scripts/lesson_mistakes.py --module 2 --case 1
These bounded negative examples intentionally catch their expected failures.
"""

import argparse
import asyncio
import json

from mcp import Client

from common.config import ROOT, Settings
from common.data import safe_path
from common.host import Host
from common.notes import notes_server
from common.pagination import all_resources, paged_server
from common.prompts import prompt_server
from common.raw_server import META, VERSION, dispatch
from common.tool_formats import ToolCall
from common.wiki import wiki_server


async def reproduce(module: int, case: int) -> str:
    try:
        if module == 0:
            if case == 1:
                safe_path(ROOT / "data/files", "../issues.db")
            elif case == 2:
                safe_path(ROOT / "data/files", "missing.md").read_text(encoding="utf-8")
            elif case == 3:
                Settings(provider="not-a-provider")
            else:
                Settings(timeout=0)
        elif module == 1:
            params = {"_meta": {META + "protocolVersion": VERSION, META + "clientCapabilities": {}}}
            request = {"jsonrpc": "2.0", "id": 1, "method": "missing/method", "params": params}
            if case == 2:
                request["params"] = []
            elif case == 3:
                params["_meta"][META + "protocolVersion"] = "2099-01-01"
            elif case == 4:
                request["id"] = True
            return json.dumps(dispatch(request)["error"])
        elif module in (2, 3):
            cases = {
                2: [
                    ("create_note", {"title": "Review", "body": "x"}),
                    ("create_note", {"title": "", "body": "x", "confirmed": True}),
                    ("tag_note", {"note_id": 999, "tag": "x", "confirmed": True}),
                    ("missing", {}),
                ],
                3: [
                    ("find_page", {"space": "engineering", "page": "../secret"}),
                    ("find_page", {"space": "engineering", "page": "page-99"}),
                    ("update_bulletin", {"text": "x"}),
                    ("update_bulletin", {"text": "", "confirmed": True}),
                ],
            }
            async with Client(
                notes_server() if module == 2 else wiki_server(), raise_exceptions=False
            ) as client:
                name, arguments = cases[module][case - 1]
                result = await client.call_tool(name, arguments)
                return "\n".join(c.text for c in result.content if c.type == "text")
        elif module == 4:
            cases = [
                ("release_notes", {}),
                ("prepare_meeting", {"customer_id": "999"}),
                ("summarize_incident", {"space": "unknown"}),
                ("prepare_meeting", {"customer_id": "not-a-number"}),
            ]
            async with Client(prompt_server()) as client:
                name, arguments = cases[case - 1]
                try:
                    await client.get_prompt(name, arguments)
                except Exception as error:
                    return str(error)
        elif module == 5:
            async with Client(paged_server()) as client:
                try:
                    if case == 1:
                        await client.list_resources(cursor="invented")
                    elif case == 2:
                        await all_resources(client, max_pages=1)
                    elif case == 3:
                        await client.list_tools()
                    else:
                        from common.wiki import wiki_text

                        wiki_text("engineering", "page-99")
                except Exception as error:
                    return str(error)
        else:

            async def deny(name, arguments):
                return False

            async with Client(notes_server()) as client:
                host = Host({"notes": client}, deny)
                await host.discover()
                calls = [
                    ToolCall("1", "search_notes", {}),
                    ToolCall(
                        "2", "notes__create_note", {"title": "x", "body": "x", "confirmed": True}
                    ),
                    ToolCall("3", "notes__create_note", {"title": "x", "body": "x"}),
                    ToolCall("4", "notes__search_notes", {"query": 17}),
                ]
                return (await host.execute(calls[case - 1])).text
    except Exception as error:
        return str(error)
    raise AssertionError("The expected failure did not occur.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module", type=int, choices=range(7), required=True)
    parser.add_argument("--case", type=int, choices=range(1, 5), required=True)
    args = parser.parse_args()
    print(asyncio.run(reproduce(args.module, args.case)))


if __name__ == "__main__":
    main()
