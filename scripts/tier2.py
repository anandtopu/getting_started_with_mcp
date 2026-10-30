"""Exercise modules 07Ã¢â‚¬â€œ10. Run: uv run python scripts/tier2.py --capture."""

import argparse
import asyncio
import json

import httpx2 as httpx
from mcp_types import ElicitResult, InputRequiredResult, PromptReference

from common.config import ROOT
from common.connections import discover
from common.protocol import SPEC_REVISION
from scripts.http_lab import http_client, running_server
from scripts.tier1 import script_client

MODULES = [
    "07_real_data",
    "08_server_utilities",
    "09_elicitation_sampling_roots",
    "10_streamable_http",
]


async def exercise(client, index: int) -> None:
    await discover(client)
    names = {t.name for t in (await client.list_tools()).tools}
    if "read_issue" in names:
        assert not (await client.call_tool("read_issue", {"issue_id": 1})).is_error
        args = {"issue": {"title": "Review Lumen"}, "operation_key": "tier2-demo"}
        assert (await client.call_tool("create_issue", args)).is_error
        args["confirmed"] = True
        created = await client.call_tool("create_issue", args)
        assert not created.is_error
        duplicate = await client.call_tool("create_issue", args)
        assert created.structured_content == duplicate.structured_content
        new_id = created.structured_content["id"]
        assert not (
            await client.call_tool(
                "update_issue", {"issue_id": new_id, "status": "closed", "confirmed": True}
            )
        ).is_error
        assert not (
            await client.call_tool("delete_issue", {"issue_id": new_id, "confirmed": True})
        ).is_error
    if "analytics_page" in names:
        result = await client.call_tool("analytics_page", {"limit": 2})
        assert json.loads(result.content[0].text)["truncated"]
        assert (await client.read_resource(str(result.content[1].uri))).contents
    if "project_details" in names:
        assert not (await client.call_tool("project_details", {})).is_error
        assert (await client.call_tool("project_details", {"project_id": 999})).is_error
        assert (await client.call_tool("weather", {"latitude": 0, "longitude": 0})).is_error
    if "quarterly_report" in names:
        progress = []

        async def on_progress(value, total, message):
            progress.append(value)

        assert not (
            await client.call_tool("quarterly_report", {}, progress_callback=on_progress)
        ).is_error
        assert progress == [1, 2, 3, 4]
        task = asyncio.create_task(client.call_tool("quarterly_report", {"delay": 0.5}))
        await asyncio.sleep(0.1)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        async with asyncio.timeout(3):
            while (await client.call_tool("report_status", {})).structured_content["active"]:
                await asyncio.sleep(0.02)
        result = await client.complete(
            ref=PromptReference(name="report_brief"), argument={"name": "quarter", "value": "Q"}
        )
        assert len(result.completion.values) == 4
    if "bulk_close" in names:
        for action in ["decline", "cancel", "accept"]:
            first = await client.session.call_tool(
                "bulk_close", {"issue_ids": [1, 2]}, allow_input_required=True
            )
            assert isinstance(first, InputRequiredResult)
            second = await client.session.call_tool(
                "bulk_close",
                {"issue_ids": [1, 2]},
                input_responses={
                    "decision": ElicitResult(
                        action=action, content={"approve": True} if action == "accept" else None
                    )
                },
                request_state=first.request_state,
                allow_input_required=True,
            )
            assert not second.is_error
        first = await client.session.call_tool("export_report", {}, allow_input_required=True)
        async with httpx.AsyncClient() as browser:
            response = await browser.post(first.input_requests["decision"].params.url)
            assert response.status_code == 200
        result = await client.session.call_tool(
            "export_report",
            {},
            input_responses={"decision": ElicitResult(action="accept")},
            request_state=first.request_state,
            allow_input_required=True,
        )
        assert not result.is_error


async def exercise_http(url: str, capture=None) -> None:
    async with http_client(url, capture) as (client, http):
        await exercise(client, 10)
        assert (await client.read_resource("wiki://engineering/page-01")).contents
        result = await client.call_tool("route_region", {"region": "Hello, Ã¤Â¸â€“Ã§â€¢Å’"})
        assert not result.is_error
        await stream_checks(client)
        await header_checks(http, url)


async def stream_checks(client) -> None:
    for _ in range(2):
        async with client.listen(resource_subscriptions=["workspace://review"]) as events:
            result = await client.call_tool(
                "publish_review", {"text": "Reviewed", "confirmed": True}
            )
            assert not result.is_error
            async with asyncio.timeout(3):
                await anext(aiter(events))
        assert (await client.read_resource("workspace://review")).contents[0].text == "Reviewed"


async def header_checks(http, url: str) -> None:
    request = {
        "jsonrpc": "2.0",
        "id": "headers",
        "method": "tools/call",
        "params": {
            "name": "route_region",
            "arguments": {"region": "east"},
            "_meta": {
                "io.modelcontextprotocol/protocolVersion": SPEC_REVISION,
                "io.modelcontextprotocol/clientCapabilities": {},
                "io.modelcontextprotocol/clientInfo": {"name": "header-lab", "version": "1"},
            },
        },
    }
    headers = {
        "Accept": "application/json, text/event-stream",
        "MCP-Protocol-Version": SPEC_REVISION,
        "Mcp-Method": "tools/call",
        "Mcp-Name": "route_region",
        "Mcp-Param-Region": "east",
    }
    for extra, status in [
        ({"Origin": "https://evil.example"}, 403),
        ({"Host": "evil.example"}, 421),
        ({"Mcp-Method": "resources/read"}, 400),
        ({"Mcp-Name": "wrong"}, 400),
        ({"Mcp-Param-Region": "west"}, 400),
    ]:
        response = await http.post(url, json=request, headers={**headers, **extra})
        assert response.status_code == status, (extra, response.status_code, response.text)
    assert (await http.get(url)).status_code == 405
    assert (await http.get(url, headers={"Origin": "https://evil.example"})).status_code == 403
    preflight = await http.options(
        url,
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Mcp-Method, Mcp-Param-Region",
        },
    )
    assert preflight.headers["access-control-allow-origin"] == "http://localhost:3000"


async def run(index: int, capture: bool = False) -> None:
    folder = ROOT / "modules" / MODULES[index - 7] / "wire"
    folder.mkdir(parents=True, exist_ok=True)
    if index == 10:
        for language, suffix in [("python", "py"), ("typescript", "ts")]:
            path = f"modules/{MODULES[3]}/{language}/examples/01_http_server.{suffix}"
            async with running_server(path) as url:
                await exercise_http(url, folder / f"{language}_http.jsonl" if capture else None)
        path = f"modules/{MODULES[3]}/python/examples/01_http_server.py"
        async with running_server(path, ("--json",)) as url:
            async with http_client(url, folder / "python_json.jsonl" if capture else None) as (
                client,
                http,
            ):
                await discover(client)
                assert (await client.list_tools()).tools
    else:
        path = f"modules/{MODULES[index - 7]}/python/use_case/server.py"
        async with script_client(
            path, folder / "python_main.jsonl" if capture else None, index == 9
        ) as client:
            await exercise(client, index)
    if capture:
        (folder / "manifest.json").write_text(
            json.dumps(
                {
                    "command": f"uv run python scripts/tier2.py --module {index} --capture",
                    "spec": SPEC_REVISION,
                    "python_sdk": "2.3.0",
                    "typescript_sdk": "2.4.0",
                    "files": sorted(p.name for p in folder.glob("*.jsonl")),
                },
                indent=2,
            )
            + "\n"
        )
    print(f"PASS Module {index:02d}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module", type=int, choices=range(7, 11))
    parser.add_argument("--capture", action="store_true")
    args = parser.parse_args()
    for index in range(7, 11) if args.module is None else [args.module]:
        asyncio.run(run(index, args.capture))


if __name__ == "__main__":
    main()
