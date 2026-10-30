"""Finite bonus/capstone acceptance and real cross-language wire capture.
Run: uv run python scripts/phase8.py [--capture]
Native compiler builds and package installs have separate explicit commands.
"""

import argparse
import asyncio
import json
import shutil
import sys

from mcp import Client, StdioServerParameters
from mcp_types import Request

from common.config import ROOT
from common.input_support import decline_unhandled_input
from common.report_tasks import TaskHandle, TasksClient, task_request
from common.skills_extension import ExtensionResult, GetParams, load_skill
from scripts.bonus import run as bonus
from scripts.capstones import run as capstone

B1 = ROOT / "modules/bonus/B1_typescript_track"
B4 = ROOT / "modules/bonus/B4_whats_new"


def client(path, capture, *, tasks=False, log_level=None):
    command = [sys.executable, str(ROOT / path)]
    if str(path).endswith(".ts"):
        command = [shutil.which("node"), "--import", "tsx", str(ROOT / path)]
    if capture:
        command = [
            sys.executable,
            str(ROOT / "scripts/wiretap.py"),
            "--capture",
            str(capture),
            "--",
            *command,
        ]
    return Client(
        StdioServerParameters(command=command[0], args=command[1:], cwd=str(ROOT)),
        mode="2026-07-28",
        extensions=[TasksClient()] if tasks else None,
        elicitation_callback=decline_unhandled_input,
        read_timeout_seconds=10,
        log_level=log_level,
    )


async def typescript(capture=False):
    folder = B1 / "wire"
    for profile, filename in [
        ("notes", "server.ts"),
        ("forms", "forms_server.ts"),
        ("tasks", "tasks_server.ts"),
    ]:
        async with client(
            B1 / "typescript" / filename,
            folder / f"{profile}.jsonl" if capture else None,
            tasks=profile == "tasks",
        ) as peer:
            await peer.list_tools()
            if profile == "notes":
                assert not (await peer.call_tool("search_notes", {"query": "release"})).is_error
                assert (
                    await peer.call_tool("create_note", {"title": "Review", "body": "Pending"})
                ).is_error
            elif profile == "forms":
                result = await peer.call_tool("review_bulletin", {"text": "Reviewed release"})
                assert result.structured_content == {"published": False}
            else:
                handle = await peer.session.call_tool(
                    "quarterly_report", {"ask_details": True}, allow_claimed=True
                )
                assert isinstance(handle, TaskHandle)
                await task_request(
                    peer.session,
                    "tasks/update",
                    handle.task_id,
                    inputResponses={
                        "details": {"action": "accept", "content": {"include_details": True}}
                    },
                )
                assert (await task_request(peer.session, "tasks/get", handle.task_id))[
                    "status"
                ] == "completed"
                other = await peer.session.call_tool("quarterly_report", {}, allow_claimed=True)
                await task_request(peer.session, "tasks/cancel", other.task_id)
                assert (await task_request(peer.session, "tasks/get", other.task_id))[
                    "status"
                ] == "cancelled"
    async with client(
        B4 / "typescript/skills_server.ts", B4 / "wire/typescript_skills.jsonl" if capture else None
    ) as peer:
        assert (await load_skill(peer))["activated"] is False
        directory = await peer.session.send_request(
            Request(
                method="resources/directory/read",
                params=GetParams(uri="skill://incident-review/references"),
            ),
            ExtensionResult,
        )
        assert directory.model_dump(by_alias=True)
    async with client(
        "scripts/reference_notifications.py",
        ROOT / "docs/wire/logging_reference.jsonl" if capture else None,
        log_level="info",
    ) as peer:
        assert not (await peer.call_tool("inspect_logging", {})).is_error
    print("PASS TypeScript/Python interop: notes, form retries, Tasks, Skills, notifications")


def excerpts():
    for folder in sorted((ROOT / "modules/bonus").glob("B*")):
        readme = folder / "README.md"
        records = []
        for path in sorted((folder / "wire").glob("*.jsonl")):
            if path.stem in {"java", "enterprise", "machine"}:
                continue
            for line in path.read_text().splitlines()[1:]:
                message = json.loads(line).get("message")
                if message and "jsonrpc" in message and len(json.dumps(message)) < 2500:
                    records.append((path, message))
            if len(records) >= 2:
                break
        block = "\n".join(
            f"Captured from [{p.name}](wire/{p.name}); "
            f"{m.get('method', 'correlated response')}.\n\n"
            f"```json\n{json.dumps(m, indent=2)}\n```\n"
            for p, m in records[:2]
        )
        text = readme.read_text(encoding="utf-8")
        before, _, remainder = text.partition("<!-- bonus-wire:start -->")
        _, marker, after = remainder.partition("<!-- bonus-wire:end -->")
        if marker:
            readme.write_text(
                before + "<!-- bonus-wire:start -->\n" + block + "<!-- bonus-wire:end -->" + after,
                encoding="utf-8",
            )


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", action="store_true")
    args = parser.parse_args()
    for name in ["B3", "B4"]:
        await bonus(name, args.capture)
    await typescript(args.capture)
    for project in range(1, 6):
        await capstone(project, args.capture)
    if args.capture:
        excerpts()
    print("PASS Phase 8 local contracts")


if __name__ == "__main__":
    asyncio.run(main())
