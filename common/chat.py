"""Lumen Chat v1 terminal checkpoint: two built services and one reference server."""

import argparse
import asyncio
import json
from contextlib import AsyncExitStack

from common.config import ROOT, Settings
from common.connections import connection
from common.host import Host
from common.llm import create_tool_model
from common.tool_formats import ToolCall, Turn


async def chat(prompt: str, demo: bool = False, capture_dir=None) -> None:
    async def approve(name: str, arguments: dict) -> bool:
        print(f"Requested tool: {name}\nArguments: {json.dumps(arguments, ensure_ascii=True)}")
        if demo:
            # These exact fixture actions are shown in README before the learner runs --demo.
            expected = {
                "notes__search_notes": {"query": "release"},
                "wiki__find_page": {"space": "engineering", "page": "page-01"},
                "files__list_allowed_directories": {},
                "notes__create_note": {"title": "Reviewed handover", "body": "Check the wiki."},
            }
            return name in expected and arguments == expected[name]
        answer = await asyncio.to_thread(input, "Approve this exact call? [y/N] ")
        return answer.strip().lower() == "y"

    turns = [
        Turn(
            calls=[
                ToolCall("read-1", "notes__search_notes", {"query": "release"}),
                ToolCall("read-2", "wiki__find_page", {"space": "engineering", "page": "page-01"}),
                ToolCall("read-3", "files__list_allowed_directories", {}),
            ]
        ),
        Turn(
            calls=[
                ToolCall(
                    "write-1",
                    "notes__create_note",
                    {"title": "Reviewed handover", "body": "Check the wiki."},
                )
            ]
        ),
        Turn("Fixture complete: checked three servers and created one approved ephemeral note."),
    ]
    model = create_tool_model(prompt, Settings() if demo else None, turns=turns if demo else None)
    async with AsyncExitStack() as stack:
        clients = {}
        for alias in ["notes", "wiki", "files"]:
            capture = capture_dir / f"{alias}.jsonl" if capture_dir else None
            clients[alias] = await stack.enter_async_context(connection(alias, capture))
        host = Host(clients, approve)
        print(await host.run(model))
        for reply in host.audit:
            print(f"{reply.call.id}: {'error' if reply.error else 'complete'}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--demo", action="store_true", help="Run only the documented fixed fixture."
    )
    parser.add_argument("--capture", action="store_true")
    parser.add_argument("--prompt", default="Find release context and prepare a handover note.")
    args = parser.parse_args()
    try:
        asyncio.run(chat(args.prompt, args.demo, ROOT / ".runtime/chat" if args.capture else None))
    except (RuntimeError, ValueError) as error:
        parser.exit(1, f"{error}\n")
