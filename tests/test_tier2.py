"""Phase 4 behavioral boundaries, failure paths, and cleanup; no external services."""

import json
import sqlite3

import httpx2 as httpx
import pytest
from mcp import Client
from mcp.server.mcpserver.exceptions import ToolError
from mcp_types import ElicitResult, InputRequiredResult

from common.analytics import usage_page
from common.chat_v2 import chat
from common.data import data_root, readonly_database
from common.elicitation import make_server as input_server
from common.files_model import summarize_file
from common.input_support import decline_unhandled_input
from common.issues import IssueInput, IssueStore, make_server
from common.llm import FakeModel
from common.rest import fetch_json
from common.rest import make_server as api_server
from common.retry import RetryLedger
from scripts.http_lab import running_server
from scripts.tier2 import exercise_http, run


def test_database_copy_transactions_and_receipts():
    store = IssueStore()
    try:
        created = store.create(IssueInput(title="x'); DROP TABLE issues; --"), "key")
        assert created["id"] == 401
        assert store.create(IssueInput(title=created["title"]), "key") == created
        with pytest.raises(ToolError, match="different"):
            store.create(IssueInput(title="changed"), "key")
        before = store.read(1)
        with pytest.raises(ToolError, match="not found"):
            store.bulk_close([1, 99999])
        assert store.read(1) == before  # first UPDATE rolled back
        assert store.db.execute("SELECT count(*) FROM issues").fetchone()[0] == 401
    finally:
        store.close()
    with pytest.raises(sqlite3.ProgrammingError):
        store.db.execute("SELECT 1")
    with readonly_database("issues.db") as db:
        assert db.execute("SELECT count(*) FROM issues").fetchone()[0] == 400
        with pytest.raises(sqlite3.OperationalError):
            db.execute("DELETE FROM issues")


@pytest.mark.anyio
async def test_crud_validation_and_deleted_receipt():
    async with Client(make_server(), raise_exceptions=False) as client:
        args = {"issue": {"title": ""}, "operation_key": "test", "confirmed": True}
        assert (await client.call_tool("create_issue", args)).is_error
        args["issue"]["title"] = "Review"
        result = await client.call_tool("create_issue", args)
        await client.call_tool(
            "delete_issue", {"issue_id": result.structured_content["id"], "confirmed": True}
        )
        assert (await client.call_tool("create_issue", args)).is_error
        later = await client.call_tool("create_issue", {**args, "operation_key": "later"})
        assert later.structured_content["id"] != result.structured_content["id"]
        assert (await client.call_tool("create_issue", args)).is_error


def test_analytics_complete_pagination_and_bounds():
    rows, offset = [], 0
    while offset is not None:
        page = usage_page(offset=offset, limit=50)
        rows.extend(page["rows"])
        offset = page["next_offset"]
    assert len(rows) == len({row["day"] for row in rows}) == 365
    for arguments in [{"limit": 51}, {"offset": -1}, {"start": "x' OR 1=1"}]:
        with pytest.raises(ToolError):
            usage_page(**arguments)


def test_analytics_execution_deadline(monkeypatch):
    times = iter(range(1000))
    monkeypatch.setattr("common.analytics.time.monotonic", lambda: next(times))
    with pytest.raises(ToolError, match="budget"):
        usage_page(limit=50)


@pytest.mark.anyio
async def test_input_requires_advertised_capability():
    async with Client(input_server(), raise_exceptions=False) as client:
        result = await client.session.call_tool(
            "bulk_close", {"issue_ids": [1]}, allow_input_required=True
        )
        assert result.is_error and "advertise form" in result.content[0].text


@pytest.mark.anyio
async def test_rest_errors_are_bounded_and_network_is_opt_in():
    async with Client(api_server(), raise_exceptions=False) as client:
        assert not (await client.call_tool("project_details", {})).is_error
        assert (await client.call_tool("project_details", {"project_id": 999})).is_error
        assert (await client.call_tool("weather", {"latitude": 0, "longitude": 0})).is_error
    for status, content in [(503, b"down"), (200, b"invalid json"), (200, b"x" * 64001)]:
        transport = httpx.MockTransport(
            lambda request, status=status, content=content: httpx.Response(status, content=content)
        )
        async with httpx.AsyncClient(transport=transport) as client:
            with pytest.raises(ToolError):
                await fetch_json(client, "https://fixture.invalid/")


def test_retry_ledger_expiry_binding_replay_and_bound(monkeypatch):
    clock = [100.0]
    monkeypatch.setattr("common.retry.time.monotonic", lambda: clock[0])
    ledger = RetryLedger(ttl=5)
    token = ledger.issue("close", {"ids": [1]})
    with pytest.raises(ToolError, match="Arguments changed"):
        ledger.take(token, "close", {"ids": [2]})
    with pytest.raises(ToolError, match="already used"):
        ledger.take(token, "close", {"ids": [1]})
    token = ledger.issue("close", {})
    clock[0] = 106
    with pytest.raises(ToolError, match="expired"):
        ledger.take(token, "close", {})
    for _ in range(100):
        ledger.issue("close", {})
    with pytest.raises(ToolError, match="Too many"):
        ledger.issue("close", {})


@pytest.mark.anyio
@pytest.mark.parametrize(
    "action,content,expected_error",
    [
        ("decline", None, False),
        ("cancel", None, False),
        ("accept", {"approve": "yes"}, True),
        ("accept", {"approve": False}, False),
        ("accept", {"approve": True, "extra": "bad"}, True),
    ],
)
async def test_form_denials_and_bad_input_never_write(action, content, expected_error):
    async with Client(
        input_server(), raise_exceptions=False, elicitation_callback=decline_unhandled_input
    ) as client:
        before = (await client.call_tool("read_issue", {"issue_id": 1})).structured_content
        first = await client.session.call_tool(
            "bulk_close", {"issue_ids": [1]}, allow_input_required=True
        )
        assert isinstance(first, InputRequiredResult)
        result = await client.session.call_tool(
            "bulk_close",
            {"issue_ids": [1]},
            input_responses={"decision": ElicitResult(action=action, content=content)},
            request_state=first.request_state,
            allow_input_required=True,
        )
        assert result.is_error == expected_error
        assert (await client.call_tool("read_issue", {"issue_id": 1})).structured_content == before


@pytest.mark.anyio
async def test_url_ack_is_not_authorization_and_replay_fails():
    async with Client(
        input_server(), raise_exceptions=False, elicitation_callback=decline_unhandled_input
    ) as client:
        first = await client.session.call_tool("export_report", {}, allow_input_required=True)
        params = dict(
            input_responses={"decision": ElicitResult(action="accept")},
            request_state=first.request_state,
            allow_input_required=True,
        )
        result = await client.session.call_tool("export_report", {}, **params)
        assert result.is_error and "browser approval" in result.content[0].text
        assert (await client.session.call_tool("export_report", {}, **params)).is_error
        first = await client.session.call_tool("export_report", {}, allow_input_required=True)
        async with httpx.AsyncClient() as browser:
            response = await browser.post(
                first.input_requests["decision"].params.url,
                headers={"Origin": "https://evil.example"},
            )
            assert response.status_code == 403


@pytest.mark.anyio
async def test_direct_generation_requires_consent_and_safe_path():
    model = FakeModel()
    root = data_root() / "wiki"
    with pytest.raises(PermissionError):
        await summarize_file(root, "engineering/page-01.md", model)
    with pytest.raises(ValueError):
        await summarize_file(root, "../issues.db", model, True)
    assert model.prompts == []
    assert "fixture" in await summarize_file(root, "engineering/page-01.md", model, True)
    assert len(model.prompts) == 1


@pytest.mark.anyio
async def test_progress_cancel_stdio():
    await run(8)


@pytest.mark.anyio
@pytest.mark.parametrize("language,suffix", [("python", "py"), ("typescript", "ts")])
async def test_http_transport_and_remote_host(language, suffix):
    path = f"modules/10_streamable_http/{language}/examples/01_http_server.{suffix}"
    async with running_server(path) as url:
        await exercise_http(url)
        await chat(demo=True, http_url=url)


def test_http_captures_include_real_headers_and_both_response_types():
    for path in (data_root().parent / "modules/10_streamable_http/wire").glob("*.jsonl"):
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        if path.stem == "python_json":
            assert any(
                r.get("status") == 200
                and r.get("headers", {}).get("content-type") == "application/json"
                for r in rows
            )
            continue
        assert {r.get("status") for r in rows} >= {200, 400, 403, 405, 421}
        assert any(
            "text/event-stream" in r.get("headers", {}).get("content-type", "") for r in rows
        )
        assert any(
            "application/json" in r.get("headers", {}).get("content-type", "")
            for r in rows
            if r.get("direction") == "http_response"
        )
