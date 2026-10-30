"""Run: uv run python -m common.chat_v2 --demo. Expected: Tier 2 fixture complete."""

import argparse
import asyncio
from contextlib import AsyncExitStack

from mcp import Client
from mcp_types import ElicitResult

from common.config import Settings
from common.connections import connection
from common.host_v2 import HostV2
from common.llm import create_tool_model
from common.protocol import SPEC_REVISION
from common.tool_formats import ToolCall, Turn


async def chat(demo: bool = False, http_url: str | None = None) -> None:
    expected = {
        "notes__search_notes": {"query": "release"},
        "wiki__find_page": {"space": "engineering", "page": "page-01"},
        "analytics__analytics_page": {"limit": 2},
        "issues__bulk_close": {"issue_ids": [1, 2]},
        "reports__quarterly_report": {"quarter": "Q1"},
    }

    async def approve(name, arguments):
        print(f"Tool: {name} {arguments}")
        if demo:
            return expected.get(name) == arguments
        return (await asyncio.to_thread(input, "Approve this call? [y/N] ")).lower() == "y"

    async def ask(params):
        print(params.message)
        if demo:
            # Only this published fixture question can be answered automatically.
            if params.mode != "form" or params.message != "Close these synthetic issues: [1, 2]?":
                return ElicitResult(action="decline")
            return ElicitResult(action="accept", content={"approve": True})
        if params.mode == "url":
            print(f"Open in your browser: {params.url}")
            accepted = await asyncio.to_thread(
                input, "Completed browser approval? [y/decline/cancel] "
            )
            action = {"y": "accept", "cancel": "cancel"}.get(accepted.lower(), "decline")
            return ElicitResult(action=action)
        accepted = await asyncio.to_thread(input, "Submit approve=true? [y/decline/cancel] ")
        if accepted.lower() == "cancel":
            return ElicitResult(action="cancel")
        if accepted.lower() != "y":
            return ElicitResult(action="decline")
        return ElicitResult(action="accept", content={"approve": True})

    async def progress(value, total, message):
        print(f"Progress {value}/{total}: {message}")

    turns = [
        Turn(calls=[ToolCall(str(i), name, args)])
        for i, (name, args) in enumerate(expected.items())
    ]
    turns.append(Turn("Tier 2 fixture complete: context, confirmation, and progress checked."))
    model = create_tool_model(
        "Review Lumen issues with wiki and usage context, then report.",
        Settings() if demo else None,
        turns=turns if demo else None,
    )
    async with AsyncExitStack() as stack:
        remote = (
            await stack.enter_async_context(
                Client(http_url, mode=SPEC_REVISION, raise_exceptions=False)
            )
            if http_url
            else None
        )
        clients = {}
        for name in ["notes", "wiki", "analytics", "issues", "reports"]:
            clients[name] = (
                remote
                if remote and name in {"wiki", "reports"}
                else (await stack.enter_async_context(connection(name)))
            )
        host = HostV2(clients, approve, ask, progress)
        print(await host.run(model))
        if demo and any(reply.error for reply in host.audit):
            failures = [reply.call.name + ": " + reply.text for reply in host.audit if reply.error]
            raise RuntimeError("Checkpoint failed: " + "; ".join(failures))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--http", help="Use a running lesson HTTP endpoint for wiki and reports")
    args = parser.parse_args()
    asyncio.run(chat(args.demo, args.http))


if __name__ == "__main__":
    main()
