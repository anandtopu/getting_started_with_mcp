"""Exercise actual stdio exchanges and optionally capture Tier 1 traffic.

Run: uv run python scripts/tier1.py --module 3 --capture
Omit --module for all seven modules. No model keys or external requests.
"""

import argparse
import asyncio
import json
import shutil
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters
from mcp_types import PromptReference, ResourceTemplateReference

from common.chat import chat
from common.config import ROOT
from common.connections import connection, discover
from common.protocol import SPEC_REVISION
from common.raw_walkthrough import exchange

MODULES = [
    "00_setup",
    "01_architecture_wire",
    "02_first_server_tools",
    "03_resources",
    "04_prompts",
    "05_first_client",
    "06_building_a_host",
]


def script_client(path: str, capture: Path | None = None) -> Client:
    command = sys.executable
    args = [str(ROOT / path)]
    if path.endswith(".ts"):
        command = shutil.which("node")
        args = ["--import", "tsx", *args]
    if capture:
        args = [str(ROOT / "scripts/wiretap.py"), "--capture", str(capture), "--", command, *args]
        command = sys.executable
    return Client(
        StdioServerParameters(command=command, args=args, cwd=str(ROOT)),
        mode=SPEC_REVISION,
        raise_exceptions=False,
        read_timeout_seconds=10,
    )


async def exercise(client: Client, index: int) -> None:
    await discover(client)
    if index == 2:
        tools = (await client.list_tools()).tools
        names = {t.name for t in tools}
        if "welcome" in names:
            assert not (await client.call_tool("welcome", {"name": "Alex"})).is_error
        elif "release_summary" in names:
            assert (await client.call_tool("release_summary", {})).structured_content[
                "open_issues"
            ] == 3
            assert (await client.call_tool("release_summary", {"open_issues": -1})).is_error
            assert len((await client.call_tool("review_assets", {})).content) == 4
        else:
            assert (
                await client.call_tool("create_note", {"title": "Review", "body": "Check wiki"})
            ).is_error
            note = await client.call_tool(
                "create_note", {"title": "Review", "body": "Check wiki", "confirmed": True}
            )
            assert note.structured_content["id"] == 2
            await client.call_tool("tag_note", {"note_id": 2, "tag": "review", "confirmed": True})
            found = await client.call_tool("search_notes", {"query": "Review"})
            assert found.structured_content["result"][-1]["tags"] == ["review"]
    elif index == 3:
        await client.list_resources()
        await client.list_resource_templates()
        suggestions = await client.complete(
            ref=ResourceTemplateReference(uri="wiki://{space}/{page}"),
            argument={"name": "space", "value": "eng"},
        )
        assert suggestions.completion.values == ["engineering"]
        for uri in ["wiki://index", "wiki://engineering/page-01", "lumen://contract/1"]:
            assert (await client.read_resource(uri)).contents
        await client.call_tool("find_page", {})
        async with client.listen(
            resources_list_changed=True,
            tools_list_changed=True,
            resource_subscriptions=["lumen://bulletin"],
        ) as events:
            assert not (
                await client.call_tool(
                    "update_bulletin", {"text": "Review complete", "confirmed": True}
                )
            ).is_error
            async with asyncio.timeout(5):
                for _ in range(3):
                    await anext(aiter(events))
            assert (await client.read_resource("lumen://bulletin")).contents[
                0
            ].text == "Review complete"
            assert "bulletin_status" in {
                tool.name for tool in (await client.list_tools(cache_mode="refresh")).tools
            }
            assert "lumen://review-receipt" in {
                str(resource.uri)
                for resource in (await client.list_resources(cache_mode="refresh")).resources
            }
    elif index == 4:
        await client.list_prompts()
        for name, args in [
            ("summarize_incident", {"space": "incident_postmortems", "page": "page-01"}),
            ("release_notes", {"issue_ids": "1,2"}),
            ("prepare_meeting", {"customer_id": "1"}),
        ]:
            messages = (await client.get_prompt(name, args)).messages
            assert messages
            if name == "summarize_incident":
                assert [message.content.type for message in messages] == ["text", "resource"]
        result = await client.complete(
            ref=PromptReference(name="summarize_incident"),
            argument={"name": "page", "value": "page-0"},
            context_arguments={"space": "engineering"},
        )
        assert len(result.completion.values) == 8
        limited = await client.complete(
            ref=PromptReference(name="release_notes"), argument={"name": "issue_ids", "value": ""}
        )
        assert len(limited.completion.values) == 100
        assert limited.completion.has_more and limited.completion.total == 400
        async with client.listen(prompts_list_changed=True) as events:
            await client.call_tool("enable_checklist", {"confirmed": True})
            async with asyncio.timeout(5):
                await anext(aiter(events))
            assert "review_checklist" in {
                p.name for p in (await client.list_prompts(cache_mode="refresh")).prompts
            }


async def run(index: int, capture: bool = False) -> None:
    folder = ROOT / "modules" / MODULES[index] / "wire"

    def target(name):
        return folder / f"{name}.jsonl" if capture else None

    async with asyncio.timeout(90):
        if index == 0:
            async with connection("files", target("03_reference_server")) as client:
                await client.list_tools()
                result = await client.call_tool("list_allowed_directories", {})
                assert not result.is_error
                await client.call_tool("list_directory", {"path": str(ROOT / "data/files")})
        elif index == 1:
            responses = await asyncio.to_thread(
                exchange, target("01_jsonrpc") or ROOT / ".runtime/raw-errors.jsonl"
            )
            assert {r["error"]["code"] for r in responses if "error" in r} >= {
                -32600,
                -32601,
                -32602,
                -32700,
                -32022,
            }
            async with connection("raw", target("03_wiretap_client")) as client:
                await client.list_tools()
                await client.call_tool("directory_count", {})
        elif index in (2, 3, 4):
            for language, suffix in [("python", "py"), ("typescript", "ts")]:
                paths = [f"modules/{MODULES[index]}/{language}/use_case/main.{suffix}"]
                if index == 2:
                    paths += [
                        f"modules/{MODULES[index]}/{language}/examples/{name}.{suffix}"
                        for name in ["01_hello_server", "02_rich_results"]
                    ]
                for path in paths:
                    async with script_client(
                        path, target(f"{language}_{Path(path).stem}")
                    ) as client:
                        await exercise(client, index)
        elif index == 5:
            from common.pagination import all_resources

            path = "modules/05_first_client/python/use_case/paged_server.py"
            async with script_client(path, target("02_pages_and_errors")) as client:
                assert len(await all_resources(client)) == 2
                try:
                    await client.list_resources(cursor="invalid")
                except Exception:
                    pass  # Expected protocol error is retained in the wire capture.
                else:
                    raise AssertionError("Invalid cursor was accepted")
            for alias, primitive in [("notes", 2), ("wiki", 3), ("prompts", 4)]:
                async with connection(alias, target(alias)) as client:
                    await exercise(client, primitive)
        else:
            await chat(
                "Run the documented fixture", demo=True, capture_dir=folder if capture else None
            )
    if capture:
        import importlib.metadata

        manifest = {
            "command": f"uv run python scripts/tier1.py --module {index} --capture",
            "spec": SPEC_REVISION,
            "python_sdk": importlib.metadata.version("mcp"),
            "typescript_sdk": "2.4.0",
            "filesystem": "2.1.0",
            "files": sorted(p.name for p in folder.glob("*.jsonl")),
        }
        (folder / "manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
        )
    print(f"PASS Module {index:02d}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module", type=int, choices=range(7))
    parser.add_argument("--capture", action="store_true")
    args = parser.parse_args()
    for index in range(7) if args.module is None else [args.module]:
        asyncio.run(run(index, args.capture))


if __name__ == "__main__":
    main()
