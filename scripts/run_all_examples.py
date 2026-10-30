"""Run all delivered examples with deadlines. No external network or model calls.

Run: uv run python scripts/run_all_examples.py [--capture-dir docs/wire]
Expected: a PASS line for every delivered server and runnable client example.
"""

import argparse
import asyncio
import json
import subprocess
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters

from common.config import ROOT
from common.protocol import SPEC_REVISION
from scripts.tier1 import exercise, script_client


async def check_lesson_server(entry: dict, capture_dir: Path | None) -> None:
    path = entry["path"]
    capture = capture_dir / (path.replace("/", "_") + ".jsonl") if capture_dir else None
    if entry["kind"] == "phase8":
        async with asyncio.timeout(30), script_client(path, capture) as client:
            from common.connections import discover

            await discover(client)
            for method in entry["lists"]:
                await getattr(
                    client,
                    {
                        "tools/list": "list_tools",
                        "resources/list": "list_resources",
                        "prompts/list": "list_prompts",
                    }[method],
                )()
        return
    if entry["kind"] == "tier5":
        async with script_client(path, capture) as client:
            from common.connections import discover

            await discover(client)
            assert (await client.list_tools()).tools
            assert not (await client.call_tool("search_notes", {"query": "release"})).is_error
        return
    if entry["kind"] == "auth":
        from scripts.auth_lab import auth_stack, exercise_auth

        async with auth_stack() as authority:
            await exercise_auth(authority, capture)
        return
    if entry["kind"] == "http":
        from scripts.http_lab import running_server
        from scripts.tier2 import exercise_http

        async with running_server(path) as url:
            await exercise_http(url, capture)
        return
    if entry["kind"] == "tier4":
        from scripts.tier4 import connection
        from scripts.tier4 import exercise as exercise_tier4

        async with connection(entry["module"], capture) as client:
            await exercise_tier4(client, entry["module"])
        return
    async with (
        asyncio.timeout(30),
        script_client(path, capture, entry.get("module") == 9) as client,
    ):
        if entry["kind"] == "raw":
            assert (await client.list_tools()).tools[0].name == "directory_count"
            assert not (await client.call_tool("directory_count", {})).is_error
        elif entry["kind"] == "paged":
            from common.pagination import all_resources

            assert len(await all_resources(client)) == 2
        elif entry["kind"] == "tier3":
            from scripts.tier3 import exercise as exercise_tier3

            await exercise_tier3(client, entry["module"])
        elif entry["kind"] == "tier2":
            from scripts.tier2 import exercise as exercise_tier2

            await exercise_tier2(client, entry["module"])
        else:
            await exercise(client, entry["module"])


async def smoke(capture_dir: Path | None = None) -> int:
    manifest = json.loads((ROOT / "scripts/examples.json").read_text())
    for entry in manifest["servers"]:
        if entry.get("kind") != "foundation":
            await check_lesson_server(entry, capture_dir)
            print(f"PASS {entry['path']}")
            continue
        args = [str(ROOT / entry["path"])]
        if capture_dir:
            args = [
                str(ROOT / "scripts/wiretap.py"),
                "--timeout",
                "30",
                "--capture",
                str(capture_dir / (Path(entry["path"]).stem + ".jsonl")),
                "--",
                sys.executable,
                *args,
            ]
        async with (
            asyncio.timeout(30),
            Client(
                StdioServerParameters(command=sys.executable, args=args, cwd=str(ROOT)),
                mode=SPEC_REVISION,
                read_timeout_seconds=10,
            ) as client,
        ):
            assert (await client.list_tools()).tools
            assert (await client.list_resources()).resources
            await client.list_resource_templates()
            assert (await client.list_prompts()).prompts
            await client.read_resource("lumen://dataset/summary")
            await client.get_prompt("explain_dataset")
            result = await client.call_tool(entry["tool"], entry["arguments"])
            assert not result.is_error and result.structured_content == entry["expected"]
        print(f"PASS {entry['path']}")
    for entry in manifest["scripts"]:
        import shutil

        command = [sys.executable]
        if entry["path"].endswith(".ts"):
            command = [shutil.which("node"), "--import", "tsx"]
        result = subprocess.run(
            [*command, str(ROOT / entry["path"]), *entry["arguments"]],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=entry.get("timeout", 30),
        )
        if result.returncode:
            raise RuntimeError(f"Failed {entry['path']}\n{result.stdout}\n{result.stderr}")
        print(f"PASS {entry['path']}")
    return len(manifest["servers"]) + len(manifest["scripts"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture-dir", type=Path)
    args = parser.parse_args()
    print(f"Checked {asyncio.run(smoke(args.capture_dir))} delivered examples.")


if __name__ == "__main__":
    main()
