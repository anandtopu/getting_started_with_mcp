"""Smoke every delivered stdio server with the installed Inspector CLI.

Run: uv run python scripts/inspector_smoke.py
Server capabilities determine which primitive lists apply; unsupported lists are
not an error. This checks protocol stdout as well as Inspector compatibility.
"""

import asyncio
import json
import shutil
import subprocess
import sys

from common.config import ROOT


async def inspect(command: list, entry: dict) -> None:
    inspector = ROOT / "node_modules/@modelcontextprotocol/inspector/clients/cli/build/index.js"
    for method in entry["lists"]:
        result = await asyncio.to_thread(
            subprocess.run,
            [
                shutil.which("node"),
                str(inspector),
                *command,
                "--protocol-era",
                "modern",
                "--method",
                method,
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
        if result.returncode:
            if (
                sys.platform == "win32"
                and "UV_HANDLE_CLOSING" in result.stderr
                and command[0].startswith("http")
            ):
                # Node's Windows HTTP shutdown can abort after a valid exchange.
                # Use the explicitly permitted equivalent SDK check; never mask a server error.
                import httpx2 as httpx
                from mcp import Client
                from mcp.client.streamable_http import streamable_http_client

                headers = {}
                if "--header" in command:
                    key, value = command[command.index("--header") + 1].split(": ", 1)
                    headers[key] = value
                async with httpx.AsyncClient(headers=headers) as http:
                    transport = streamable_http_client(command[0], http_client=http)
                    async with Client(transport, mode="2026-07-28") as client:
                        operation = {
                            "tools/list": client.list_tools,
                            "resources/list": client.list_resources,
                            "prompts/list": client.list_prompts,
                        }[method]
                        await operation()
                print(
                    f"PASS SDK equivalent (Windows Inspector shutdown failure) "
                    f"{entry['path']} {method}"
                )
                continue
            raise RuntimeError(f"Inspector {entry['path']} {method}: {result.stderr}")
        json.loads(result.stdout)
        print(f"PASS Inspector {entry['path']} {method}")


async def main() -> None:
    manifest = json.loads((ROOT / "scripts/examples.json").read_text())
    for entry in manifest["servers"]:
        if entry.get("kind") == "auth":
            from scripts.auth_lab import auth_stack

            async with auth_stack() as authority:
                await inspect(
                    [
                        authority.resource,
                        "--transport",
                        "http",
                        "--header",
                        "Authorization: Bearer " + authority.token(),
                    ],
                    entry,
                )
            continue
        if entry.get("kind") == "http":
            from scripts.http_lab import running_server

            async with running_server(entry["path"]) as url:
                await inspect([url, "--transport", "http"], entry)
            continue
        command = [sys.executable, str(ROOT / entry["path"])]
        if entry["path"].endswith(".ts"):
            command = [shutil.which("node"), "--import", "tsx", str(ROOT / entry["path"])]
        await inspect(command, entry)


if __name__ == "__main__":
    asyncio.run(main())
