"""Finite capstone acceptance; no model keys, cloud accounts or permanent writes.
Run: uv run python scripts/capstones.py [--project 1] [--capture]
"""

import argparse
import asyncio
import tempfile
from pathlib import Path

from mcp import Client
from mcp.shared.exceptions import MCPError
from mcp_types import PromptReference

from common.audit_lab import audit_server
from common.config import ROOT
from common.gateway import Gateway, gateway_server
from common.knowledge import Knowledge, knowledge_server
from common.ops import make_server
from common.report_tasks import TasksClient, task_request

NAMES = [
    "01_personal_knowledge",
    "02_security_audit",
    "03_lumen_gateway",
    "04_lumen_ops",
    "05_lumen_chat_pro",
]


async def knowledge():
    folder = ROOT / "capstones/01_personal_knowledge/notes"
    index = Knowledge(folder)
    try:
        assert index.search("shipping", "text") == []
        assert index.search("shipping", "semantic")[0]["name"] == "release.md"
        assert index.search("unknownxyz", "semantic") == []
    finally:
        index.close()
    async with Client(knowledge_server(folder)) as client:
        assert not (await client.call_tool("search_knowledge", {"query": "release"})).is_error
        assert (await client.read_resource("knowledge://notes/release.md")).contents
        assert (await client.get_prompt("summarize_note", {"name": "release.md"})).messages
        completion = await client.complete(
            PromptReference(name="summarize_note"), {"name": "name", "value": "rel"}
        )
        assert completion.completion.values == ["release.md"]


async def audit():
    for repaired in (False, True):
        async with Client(audit_server(repaired=repaired)) as client:
            read = await client.call_tool("read_record", {"name": "private"})
            write = await client.call_tool("publish_bulletin", {"text": "Unreviewed"})
            assert bool(read.is_error) == repaired
            assert bool(write.is_error) == repaired
            assert not (await client.call_tool("read_record", {"name": "public"})).is_error


async def gateway(path):
    from common.notes import notes_server

    identity = ["reader", frozenset({"workspace:read"})]
    gw = Gateway({"notes": notes_server()}, principal=lambda: tuple(identity), rate_limit=3)
    server, _, _ = gateway_server(path, gw)
    async with Client(server) as client:
        assert "notes__create_note" not in {t.name for t in (await client.list_tools()).tools}
        try:
            await client.call_tool(
                "notes__create_note",
                {
                    "title": "x",
                    "body": "y",
                    "confirmed": True,
                },
            )
        except MCPError as error:
            assert "not available" in str(error)
        else:
            raise AssertionError("Reader invoked a hidden write")
        identity[:] = ["writer", frozenset({"workspace:read", "workspace:write"})]
        assert "notes__create_note" in {t.name for t in (await client.list_tools()).tools}
        assert not (await client.call_tool("notes__search_notes", {"query": "release"})).is_error
        gw.disabled.add("notes")
        try:
            await client.call_tool("notes__search_notes", {})
        except MCPError as error:
            assert "not available" in str(error)
        else:
            raise AssertionError("Disabled route remained callable")


async def ops(path):
    from common.input_support import decline_unhandled_input
    from common.report_tasks import TaskHandle

    async with Client(
        make_server(path), extensions=[TasksClient()], elicitation_callback=decline_unhandled_input
    ) as client:
        tools = {t.name for t in (await client.list_tools()).tools}
        assert {"bulk_close", "analytics_dashboard", "quarterly_report", "read_issue"} <= tools
        assert not (await client.call_tool("analytics_dashboard", {})).is_error
        handle = await client.session.call_tool(
            "quarterly_report", {"quarter": "Q1"}, allow_claimed=True
        )
        assert isinstance(handle, TaskHandle)
        for _ in range(20):
            result = await task_request(client.session, "tasks/get", handle.task_id)
            if result.get("status") == "completed":
                break
            await asyncio.sleep(0.03)
        else:
            raise AssertionError("Report did not complete within the polling budget")


async def run(project, capture=False):
    with tempfile.TemporaryDirectory(prefix="lumen-capstone-") as temporary:
        path = Path(temporary) / "reports.db"
        if project == 1:
            await knowledge()
        elif project == 2:
            await audit()
        elif project == 3:
            await gateway(path)
        elif project == 4:
            await ops(path)
        else:
            from scripts.tier5 import host_demo

            await host_demo()
        if capture and project < 5:
            from scripts.tier1 import script_client

            folder = ROOT / "capstones" / NAMES[project - 1]
            async with script_client(
                str(folder / "solution/server.py"), folder / "wire/main.jsonl"
            ) as client:
                await client.list_tools()
                if project == 1:
                    await client.call_tool(
                        "search_knowledge", {"query": "shipping", "mode": "semantic"}
                    )
                    await client.read_resource("knowledge://notes/release.md")
                    await client.get_prompt("summarize_note", {"name": "release.md"})
                elif project == 2:
                    await client.call_tool("read_record", {"name": "private"})
                elif project == 3:
                    await client.call_tool("notes__search_notes", {"query": "release"})
                else:
                    await client.call_tool("analytics_dashboard", {})
        elif capture:
            from scripts.tier5 import host_demo

            await host_demo(ROOT / "capstones" / NAMES[4] / "wire/main.jsonl")
    print(f"PASS capstone {project}: {NAMES[project - 1]}")


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=int, choices=range(1, 6))
    parser.add_argument("--capture", action="store_true")
    args = parser.parse_args()
    for project in [args.project] if args.project else range(1, 6):
        await run(project, args.capture)


if __name__ == "__main__":
    asyncio.run(main())
