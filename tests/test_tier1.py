"""Meaningful Tier 1 boundaries, state changes, errors and host routing; offline."""

import json
from types import SimpleNamespace

import pytest
from mcp import Client
from mcp.shared.exceptions import MCPError
from mcp_types import PromptReference

from common.config import ROOT, Settings
from common.host import Host
from common.llm import create_tool_model
from common.notes import notes_server
from common.pagination import all_resources, paged_server
from common.prompts import prompt_server
from common.raw_server import META, VERSION, dispatch
from common.rich_tools import rich_server
from common.tool_formats import ToolCall, Turn, provider_tools
from common.wiki import wiki_server


@pytest.mark.anyio
async def test_notes_confirmation_validation_and_idempotency():
    async with Client(notes_server(), raise_exceptions=False) as client:
        bad = await client.call_tool("create_note", {"title": "Review", "body": "x"})
        assert bad.is_error
        assert len((await client.call_tool("search_notes", {})).structured_content["result"]) == 1
        good = await client.call_tool(
            "create_note", {"title": "Review", "body": "x", "confirmed": True}
        )
        assert good.structured_content == {"id": 2, "title": "Review"}
        for _ in range(2):
            result = await client.call_tool(
                "tag_note", {"note_id": 2, "tag": "ship", "confirmed": True}
            )
            assert result.structured_content == {"id": 2, "tags": ["ship"]}
        assert (
            await client.call_tool("create_note", {"title": "", "body": "x", "confirmed": True})
        ).is_error
        assert (
            await client.call_tool("tag_note", {"note_id": 99, "tag": "ship", "confirmed": True})
        ).is_error
    async with Client(notes_server()) as fresh:
        assert len((await fresh.call_tool("search_notes", {})).structured_content["result"]) == 1


@pytest.mark.anyio
async def test_rich_content_and_output_validation():
    async with Client(rich_server(), raise_exceptions=False) as client:
        tools = (await client.list_tools()).tools
        assert tools[0].output_schema["properties"]["open_issues"]["minimum"] == 0
        assert not (await client.call_tool("release_summary", {})).is_error
        assert (await client.call_tool("release_summary", {"open_issues": -1})).is_error
        content = (await client.call_tool("review_assets", {})).content
        assert [item.type for item in content] == ["image", "audio", "resource", "resource_link"]


@pytest.mark.anyio
async def test_wiki_boundary_and_binary():
    import base64

    async with Client(wiki_server()) as client:
        pdf = (await client.read_resource("lumen://contract/1")).contents[0]
        assert base64.b64decode(pdf.blob).startswith(b"%PDF")
        assert pdf.mime_type == "application/pdf"
        with pytest.raises(MCPError):
            await client.read_resource("wiki://engineering/../secret")
        result = await client.read_resource("wiki://index")
        assert result.cache_scope == "private" and result.ttl_ms == 0


@pytest.mark.anyio
async def test_prompt_content_completions_and_invalid_arguments():
    async with Client(prompt_server()) as client:
        result = await client.get_prompt("summarize_incident")
        assert [m.content.type for m in result.messages] == ["text", "resource"]
        for context, expected in [({}, []), ({"space": "engineering"}, ["page-01"])]:
            completion = await client.complete(
                ref=PromptReference(name="summarize_incident"),
                argument={"name": "page", "value": "page-01"},
                context_arguments=context,
            )
            assert completion.completion.values == expected
        with pytest.raises(MCPError):
            await client.get_prompt("prepare_meeting", {"customer_id": "999"})


@pytest.mark.anyio
async def test_pagination_empty_page_bad_cursor_and_bound():
    async with Client(paged_server()) as client:
        assert [r.name for r in await all_resources(client)] == ["Index", "Bulletin"]
        with pytest.raises(RuntimeError, match="budget"):
            await all_resources(client, max_pages=2)
        with pytest.raises(MCPError):
            await client.list_resources(cursor="tampered")

    class Repeating:
        async def list_resources(self, cursor=None):
            return SimpleNamespace(resources=[], next_cursor="again")

    with pytest.raises(RuntimeError, match="Repeated"):
        await all_resources(Repeating())


@pytest.mark.parametrize(
    "message, code",
    [
        (None, -32600),
        ([], -32600),
        ({"jsonrpc": "2.0", "id": True, "method": "tools/list"}, -32600),
        ({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": []}, -32602),
    ],
)
def test_raw_invalid_requests(message, code):
    assert dispatch(message)["error"]["code"] == code


def test_raw_notification_and_version_error():
    assert dispatch({"jsonrpc": "2.0", "method": "ping"}) is None
    request = {
        "jsonrpc": "2.0",
        "id": "r1",
        "method": "tools/list",
        "params": {
            "_meta": {META + "protocolVersion": "2099-01-01", META + "clientCapabilities": {}}
        },
    }
    error = dispatch(request)
    assert error["id"] == "r1"
    assert error["error"]["data"] == {"supported": [VERSION], "requested": "2099-01-01"}


@pytest.mark.anyio
async def test_host_approval_cannot_be_supplied_by_model_and_routing():
    approvals = []

    async def approve(name, arguments):
        approvals.append((name, arguments))
        return True

    async with Client(notes_server()) as notes, Client(wiki_server()) as wiki:
        host = Host({"notes": notes, "wiki": wiki}, approve)
        await host.discover()
        assert "notes__create_note" in host.routes and "wiki__find_page" in host.routes
        assert "confirmed" not in host.routes["notes__create_note"][2]["properties"]
        assert (await host.execute(ToolCall("x", "unknown", {}))).error
        assert (
            await host.execute(
                ToolCall("y", "notes__create_note", {"title": "x", "body": "x", "confirmed": True})
            )
        ).error
        assert approvals == []
        call = ToolCall("z", "notes__create_note", {"title": "x", "body": "x"})
        assert not (await host.execute(call)).error
        assert approvals == [(call.name, call.arguments)]


@pytest.mark.anyio
async def test_host_denial_does_not_write_and_loop_preserves_results():
    async def deny(name, arguments):
        return False

    async with Client(notes_server()) as notes:
        host = Host({"notes": notes}, deny)
        call = ToolCall("write-1", "notes__create_note", {"title": "x", "body": "x"})
        model = create_tool_model("demo", Settings(), [Turn(calls=[call]), Turn("Denied")])
        assert await host.run(model) == "Denied"
        assert model.results[1][0].call.id == "write-1" and model.results[1][0].error
        assert len((await notes.call_tool("search_notes", {})).structured_content["result"]) == 1


@pytest.mark.anyio
@pytest.mark.parametrize("mode", ["repeated", "calls", "turns"])
async def test_host_budgets(mode):
    async def approve(name, arguments):
        return True

    call = ToolCall("one", "notes__search_notes", {})
    turns = [Turn(calls=[call]), Turn(calls=[call])]
    async with Client(notes_server()) as notes:
        host = Host(
            {"notes": notes},
            approve,
            max_turns=1 if mode == "turns" else 6,
            max_calls=0 if mode == "calls" else 8,
        )
        with pytest.raises(
            RuntimeError, match={"repeated": "repeated", "calls": "budget", "turns": "budget"}[mode]
        ):
            await host.run(create_tool_model("demo", Settings(), turns))


@pytest.mark.parametrize("provider", ["openai", "anthropic", "gemini", "ollama"])
def test_provider_formats_preserve_schema(provider):
    tool = {
        "name": "notes__search",
        "description": "Find notes",
        "inputSchema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    }
    definitions = json.dumps(provider_tools(provider, [tool]))
    assert "Find notes" in definitions and '"required": ["query"]' in definitions
    assert "confirmed" not in definitions


def test_module_wire_captures_have_real_envelopes_and_notifications():
    messages = []
    for path in (ROOT / "modules").glob("*/wire/*.jsonl"):
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        assert rows[0]["capture_version"] == 1
        messages.extend(row["message"] for row in rows[1:] if isinstance(row["message"], dict))
    methods = {m.get("method") for m in messages}
    assert methods >= {
        "server/discover",
        "completion/complete",
        "subscriptions/listen",
        "notifications/resources/updated",
        "notifications/resources/list_changed",
        "notifications/tools/list_changed",
        "notifications/prompts/list_changed",
    }
    assert any(m.get("result", {}).get("nextCursor") == "middle" for m in messages)
    assert all(
        m["params"]["_meta"][META + "protocolVersion"] == VERSION
        for m in messages
        if "method" in m and "id" in m and m["method"] == "server/discover"
    )


def test_readme_wire_excerpts_match_capture_records():
    import re

    for readme in (ROOT / "modules").glob("*/README.md"):
        text = readme.read_text(encoding="utf-8")
        if "<!-- wire:start -->" not in text:
            continue
        section = text.split("<!-- wire:start -->")[1].split("<!-- wire:end -->")[0]
        captured = [
            json.loads(line)["message"]
            for path in (readme.parent / "wire").glob("*.jsonl")
            for line in path.read_text(encoding="utf-8").splitlines()[1:]
        ]
        for block in re.findall(r"```json\n(.*?)\n```", section, re.S):
            assert json.loads(block) in captured, readme
