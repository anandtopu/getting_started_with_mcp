"""Build and exercise the same real stdio contract in four official native SDKs.
Run: uv run python scripts/native_sdks.py --language go --build --capture
Build resolves dependencies; subsequent contract runs are offline. Java is legacy interoperability.
"""

import argparse
import asyncio
import json
import os
import shutil
import subprocess
import sys

from mcp import Client, StdioServerParameters

from common.config import ROOT

BASE = ROOT / "modules/bonus/B2_other_sdks"
OUT = ROOT / ".runtime/phase8"


def dotnet():
    local = OUT / "dotnet" / ("dotnet.exe" if os.name == "nt" else "dotnet")
    return str(local) if local.exists() else shutil.which("dotnet") or "dotnet"


def command(language):
    suffix = ".exe" if os.name == "nt" else ""
    return {
        "go": [str(OUT / ("lumen-go" + suffix))],
        "csharp": [dotnet(), str(OUT / "csharp/Notes.dll")],
        "rust": [str(BASE / "rust/target/debug" / ("lumen-notes-course" + suffix))],
        "java": ["java", "-jar", str(BASE / "java/target/notes-1.0.0.jar")],
    }[language]


def build(language):
    OUT.mkdir(parents=True, exist_ok=True)
    commands = {
        "go": [["go", "test", "./..."], ["go", "build", "-o", command("go")[0], "."]],
        "csharp": [
            [dotnet(), "restore", "Notes.csproj", "--locked-mode"],
            [dotnet(), "build", "Notes.csproj", "--no-restore", "-o", str(OUT / "csharp")],
        ],
        "rust": [["cargo", "build", "--locked"]],
        "java": [[shutil.which("mvn") or "mvn", "-q", "package"]],
    }
    for args in commands[language]:
        subprocess.run(args, cwd=BASE / language, check=True, timeout=300)


def body(result):
    if result.structured_content is not None:
        return result.structured_content
    return json.loads(next(c.text for c in result.content if c.type == "text"))


async def contract(language, capture=False):
    args = command(language)
    if capture:
        args = [
            sys.executable,
            str(ROOT / "scripts/wiretap.py"),
            "--capture",
            str(BASE / "wire" / f"{language}.jsonl"),
            "--",
            *args,
        ]
    async with Client(
        StdioServerParameters(command=args[0], args=args[1:], cwd=str(ROOT)),
        mode="legacy" if language == "java" else "2026-07-28",
        read_timeout_seconds=20,
    ) as client:
        tools = {t.name for t in (await client.list_tools()).tools}
        assert {"search_notes", "create_note", "tag_note"} <= tools
        assert (await client.list_resources()).resources
        prompts = (await client.list_prompts()).prompts
        assert prompts
        assert (await client.get_prompt("review_notes")).messages
        found = await client.call_tool("search_notes", {"query": "release"})
        assert body(found)["result"][0]["title"] == "Release handover"
        assert (
            await client.call_tool(
                "create_note", {"title": "Review", "body": "Check wiki", "confirmed": False}
            )
        ).is_error
        created = await client.call_tool(
            "create_note", {"title": "Review", "body": "Check wiki", "confirmed": True}
        )
        assert body(created)["id"] == 2
        for _ in range(2):
            tagged = await client.call_tool(
                "tag_note", {"note_id": 2, "tag": "reviewed", "confirmed": True}
            )
            assert body(tagged)["tags"] == ["reviewed"]
        assert (await client.read_resource("lumen://notes/help")).contents
        assert (await client.call_tool("search_notes", {"query": "x" * 101})).is_error
    print(f"PASS native {language}: search, approval, create, idempotent tag, resource, bounds")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--language", choices=["go", "csharp", "rust", "java"], required=True)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--capture", action="store_true")
    args = parser.parse_args()
    if args.build:
        build(args.language)
    asyncio.run(contract(args.language, args.capture))


if __name__ == "__main__":
    main()
