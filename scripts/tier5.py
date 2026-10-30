"""Exercise/capture shipping modules over real transports, with no cloud/model calls.
Run: uv run python scripts/tier5.py [--module 18] [--capture]
"""

import argparse
import asyncio
import json
import sys

from mcp import Client, StdioServerParameters

from common.config import ROOT
from common.connections import discover
from common.production_host import Connection, ProductionHost, ServerConfig
from common.protocol import SPEC_REVISION
from common.tool_formats import ToolCall
from scripts.tier1 import script_client

MODULES = ["18_packaging", "19_registry", "20_deployment", "21_production_hosts"]


async def host_demo(capture=None, *, legacy=False):
    script = str(ROOT / "modules/21_production_hosts/python/use_case/server.py")
    command = [sys.executable, script]
    if capture:
        command = [
            sys.executable,
            str(ROOT / "scripts/wiretap.py"),
            "--capture",
            str(capture),
            "--",
            *command,
        ]
    connection = Connection(
        ServerConfig(alias="notes", profile="notes"),
        lambda *_: None,
        factory=lambda: Client(
            StdioServerParameters(command=command[0], args=command[1:]),
            mode="legacy" if legacy else "auto",
        ),
    )
    await connection.start()
    try:

        async def approve(name, details):
            # Automated approval only for this fixed, non-mutating synthetic check.
            return name == "notes__search_notes" and details["arguments"] == {"query": "release"}

        host = ProductionHost({"notes": connection}, approve, None, lambda *_: None, None)
        await host.discover()
        result = await host.execute(ToolCall("check", "notes__search_notes", {"query": "release"}))
        assert not result.error and "Release handover" in result.text
        return connection.info
    finally:
        await connection.close()


async def run(index, capture=False):
    folder = ROOT / "modules" / MODULES[index - 18] / "wire"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "python_main.jsonl" if capture else None
    paths = [path] if capture else []
    if index == 20:
        from scripts.deployment_lab import run as deployed

        await deployed(path)
    elif index == 21:
        await host_demo(path)
        older = folder / "legacy.jsonl" if capture else None
        info = await host_demo(older, legacy=True)
        assert not info["protocol"].startswith("2026")
        if capture:
            paths.append(older)
    else:
        name = f"modules/{MODULES[index - 18]}/python/use_case/server.py"
        async with script_client(name, path) as client:
            await discover(client)
            assert [t.name for t in (await client.list_tools()).tools] == ["search_notes"]
            assert not (await client.call_tool("search_notes", {"query": "release"})).is_error
    if capture:
        command = f"uv run python scripts/tier5.py --module {index} --capture"
        for recorded in paths:
            rows = recorded.read_text(encoding="utf-8").splitlines()
            header = json.loads(rows[0])
            header["command"] = command
            if recorded.name == "legacy.jsonl":
                header["spec"] = "2025-11-25"
            recorded.write_text(
                json.dumps(header) + "\n" + "\n".join(rows[1:]) + "\n", encoding="utf-8"
            )
        (folder / "manifest.json").write_text(
            json.dumps(
                {
                    "command": command,
                    "spec": SPEC_REVISION,
                    "python_sdk": "2.3.0",
                    "files": [p.name for p in paths],
                    "redactions": ["authorization"],
                },
                indent=2,
            )
            + "\n"
        )
    print(f"PASS Module {index:02d}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module", type=int, choices=range(18, 22))
    parser.add_argument("--capture", action="store_true")
    args = parser.parse_args()
    for index in [args.module] if args.module is not None else range(18, 22):
        asyncio.run(run(index, args.capture))


if __name__ == "__main__":
    main()
