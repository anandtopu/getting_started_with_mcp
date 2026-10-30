"""Exercise and capture modules 14–17 with the real stdio transport.

Run: uv run python scripts/tier4.py [--module 17] [--capture]
Expected: PASS for every selected module. No model credentials needed.
"""

import argparse
import asyncio
import json
import sys

from mcp import Client, StdioServerParameters
from mcp.shared.exceptions import MCPError

from common.config import ROOT
from common.connections import discover
from common.extensions import APP_URI
from common.input_support import decline_unhandled_input
from common.protocol import SPEC_REVISION
from common.report_tasks import TasksClient, task_request

MODULES = ["14_tool_design", "15_agent_frameworks", "16_composition", "17_extensions"]


def connection(index, capture=None):
    path = ROOT / "modules" / MODULES[index - 14] / "python/use_case/server.py"
    args = [str(path)]
    if capture:
        args = [
            str(ROOT / "scripts/wiretap.py"),
            "--capture",
            str(capture),
            "--",
            sys.executable,
            *args,
        ]
    return Client(
        StdioServerParameters(command=sys.executable, args=args, cwd=str(ROOT)),
        mode=SPEC_REVISION,
        extensions=[TasksClient()] if index >= 16 else None,
        elicitation_callback=decline_unhandled_input,
        raise_exceptions=False,
        read_timeout_seconds=10,
    )


async def exercise(client, index):
    await discover(client)
    await client.list_tools()
    if index in {14, 15}:
        assert (await client.call_tool("triage_week", {})).structured_content["total"] == 14
        assert (await client.call_tool("draft_status", {})).structured_content["published"] is False
        assert (await client.call_tool("issue_brief", {"issue_id": -1})).is_error
    if index == 16:
        assert (await client.call_tool("workflow__triage_week", {})).structured_content[
            "total"
        ] == 14
        try:
            await client.call_tool("notes__create_note", {"title": "denied", "body": "fixture"})
        except MCPError:
            pass
        else:
            raise AssertionError("Reader unexpectedly accessed a write tool")
    if index >= 16:
        handle = await client.session.call_tool(
            "quarterly_report", {"ask_details": True}, allow_claimed=True
        )
        async with asyncio.timeout(5):
            while True:
                state = await task_request(client.session, "tasks/get", handle.task_id)
                if state["status"] == "input_required":
                    await task_request(
                        client.session,
                        "tasks/update",
                        handle.task_id,
                        inputResponses={
                            "details-1": {"action": "accept", "content": {"include_details": True}}
                        },
                    )
                elif state["status"] == "completed":
                    assert state["result"]["structuredContent"]["total"] == 400
                    break
                await asyncio.sleep(0.025)
        cancelled = await client.session.call_tool(
            "quarterly_report", {"ask_details": True}, allow_claimed=True
        )
        await task_request(client.session, "tasks/cancel", cancelled.task_id)
        assert (await task_request(client.session, "tasks/get", cancelled.task_id))[
            "status"
        ] == "cancelled"
        result = await client.call_tool("analytics_dashboard", {})
        assert result.structured_content["total"] == 400
        await client.read_resource(APP_URI)


async def run(index, capture=False):
    folder = ROOT / "modules" / MODULES[index - 14] / "wire"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "python_main.jsonl" if capture else None
    async with connection(index, path) as client:
        await exercise(client, index)
    if capture:
        command = f"uv run python scripts/tier4.py --module {index} --capture"
        lines = path.read_text(encoding="utf-8").splitlines()
        header = json.loads(lines[0])
        header["command"] = command
        path.write_text(json.dumps(header) + "\n" + "\n".join(lines[1:]) + "\n", encoding="utf-8")
        (folder / "manifest.json").write_text(
            json.dumps(
                {
                    "command": command,
                    "spec": SPEC_REVISION,
                    "python_sdk": "2.3.0",
                    "files": [path.name],
                    "redactions": [],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    print(f"PASS Module {index:02d}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module", type=int, choices=range(14, 18))
    parser.add_argument("--capture", action="store_true")
    args = parser.parse_args()
    for index in [args.module] if args.module is not None else range(14, 18):
        asyncio.run(run(index, args.capture))


if __name__ == "__main__":
    main()
