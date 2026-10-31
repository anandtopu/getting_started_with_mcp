"""Tier 4 behavior: tool budgets, isolation, native framework calls and extensions."""

import asyncio
import json
from contextvars import ContextVar

import pytest
from mcp import Client
from mcp.shared.exceptions import MCPError

from common.extensions import APP_URI, extension_server
from common.gateway import Gateway, gateway_server
from common.input_support import decline_unhandled_input
from common.protocol import SPEC_REVISION
from common.report_tasks import TasksClient, task_request
from common.tool_design import mirror_server, task_server, triage


@pytest.mark.anyio
async def test_tool_redesign_counts_pagination_and_output():
    async with (
        Client(mirror_server(), mode=SPEC_REVISION) as baseline,
        Client(task_server(), mode=SPEC_REVISION) as redesigned,
    ):
        assert len((await baseline.list_tools()).tools) == 25
        assert len((await redesigned.list_tools()).tools) == 6
        first = (await redesigned.call_tool("search_issues", {"limit": 2})).structured_content
        second = (
            await redesigned.call_tool("search_issues", {"limit": 2, "after": first["next_after"]})
        ).structured_content
        assert [r["id"] for r in first["items"] + second["items"]] == [1, 2, 3, 4]
        concise = await redesigned.call_tool("issue_brief", {"issue_id": 1})
        detailed = await redesigned.call_tool("issue_brief", {"issue_id": 1, "mode": "detailed"})
        assert len(json.dumps(concise.structured_content)) < len(
            json.dumps(detailed.structured_content)
        )
        bad = await redesigned.call_tool("issue_brief", {"issue_id": -1})
        assert bad.is_error and "search_issues" in bad.content[0].text
        assert (await redesigned.call_tool("search_issues", {"limit": 1000})).is_error
        assert triage()["total"] > 0


@pytest.mark.anyio
async def test_gateway_visibility_isolation_and_revocation(tmp_path):
    identity = ContextVar("test_identity", default=("reader", frozenset({"workspace:read"})))
    gateway = Gateway(principal=identity.get)
    server, _, tasks = gateway_server(tmp_path / "tasks.db", gateway)
    try:
        async with Client(server, mode=SPEC_REVISION, raise_exceptions=False) as client:
            names = {t.name for t in (await client.list_tools()).tools}
            assert "notes__search_notes" in names and "notes__create_note" not in names
            assert {"issues", "notes", "wiki", "reports", "analytics", "calendar", "workflow"} <= {
                n.split("__")[0] for n in names
            }
            with pytest.raises(MCPError, match="not available"):
                await client.call_tool(
                    "notes__create_note", {"title": "x", "body": "x", "confirmed": True}
                )
            token = identity.set(("writer", frozenset({"workspace:read", "workspace:write"})))
            try:
                assert "notes__create_note" in {t.name for t in (await client.list_tools()).tools}
                unconfirmed = await client.call_tool(
                    "notes__create_note", {"title": "x", "body": "x"}
                )
                assert unconfirmed.is_error
            finally:
                identity.reset(token)
            assert "notes__create_note" not in {t.name for t in (await client.list_tools()).tools}
            gateway.disabled.add("notes")
            with pytest.raises(MCPError, match="not available"):
                await client.call_tool("notes__search_notes", {})
            assert not (await client.call_tool("workflow__triage_week", {})).is_error
    finally:
        await tasks.close()


@pytest.mark.anyio
async def test_gateway_rate_and_schema(tmp_path):
    gateway = Gateway(rate_limit=1)
    server, _, tasks = gateway_server(tmp_path / "tasks.db", gateway)
    try:
        async with Client(server, mode=SPEC_REVISION, raise_exceptions=False) as client:
            with pytest.raises(MCPError, match="schema"):
                await client.call_tool("workflow__search_issues", {"limit": 100})
            with pytest.raises(MCPError, match="rate limit"):
                await client.call_tool("workflow__search_issues", {})
    finally:
        await tasks.close()


async def wait_state(client, handle, desired):
    async with asyncio.timeout(3):
        while True:
            result = await task_request(client.session, "tasks/get", handle.task_id)
            if result["status"] in desired:
                return result
            await asyncio.sleep(0.025)


@pytest.mark.anyio
async def test_tasks_real_input_duplicate_update_and_result(tmp_path):
    async with Client(
        extension_server(tmp_path / "tasks.db"),
        mode=SPEC_REVISION,
        extensions=[TasksClient()],
        elicitation_callback=decline_unhandled_input,
    ) as client:
        handle = await client.session.call_tool(
            "quarterly_report", {"ask_details": True}, allow_claimed=True
        )
        state = await wait_state(client, handle, {"input_required"})
        assert "details-1" in state["inputRequests"]
        args = {"details-1": {"action": "accept", "content": {"include_details": True}}}
        await task_request(client.session, "tasks/update", handle.task_id, inputResponses=args)
        await task_request(client.session, "tasks/update", handle.task_id, inputResponses=args)
        completed = await wait_state(client, handle, {"completed"})
        assert completed["result"]["structuredContent"]["total"] == 400
        assert sum(completed["result"]["structuredContent"]["counts"].values()) == 400
        await task_request(client.session, "tasks/cancel", handle.task_id)
        assert (await task_request(client.session, "tasks/get", handle.task_id))[
            "status"
        ] == "completed"


@pytest.mark.anyio
async def test_tasks_cancellation_restart_and_owner(tmp_path):
    path = tmp_path / "tasks.db"
    async with Client(
        extension_server(path), mode=SPEC_REVISION, extensions=[TasksClient()]
    ) as client:
        handle = await client.session.call_tool("quarterly_report", {}, allow_claimed=True)
        await task_request(client.session, "tasks/cancel", handle.task_id)
        assert (await task_request(client.session, "tasks/get", handle.task_id))[
            "status"
        ] == "cancelled"
        completed = await client.call_tool("quarterly_report", {})
        assert completed.structured_content["total"] == 400
        handle2 = await client.session.call_tool("quarterly_report", {}, allow_claimed=True)
    async with Client(
        extension_server(path), mode=SPEC_REVISION, extensions=[TasksClient()]
    ) as client:
        assert (await wait_state(client, handle2, {"completed"}))["result"]["structuredContent"][
            "total"
        ] == 400
    async with Client(
        extension_server(path, principal=lambda: "other-user"),
        mode=SPEC_REVISION,
        extensions=[TasksClient()],
    ) as client:
        with pytest.raises(Exception, match="Unknown or expired task"):
            await task_request(client.session, "tasks/get", handle.task_id)


@pytest.mark.anyio
async def test_extensions_fallback_and_app_resource(tmp_path):
    async with Client(
        extension_server(tmp_path / "tasks.db"), mode=SPEC_REVISION, raise_exceptions=False
    ) as client:
        result = await client.call_tool("quarterly_report", {})
        assert result.structured_content["total"] == 400
        with pytest.raises(MCPError, match="required extension"):
            await client.call_tool("quarterly_report", {"ask_details": True})
        dashboard = await client.call_tool("analytics_dashboard", {})
        assert dashboard.structured_content["total"] == 400
        tool = next(t for t in (await client.list_tools()).tools if t.name == "analytics_dashboard")
        assert tool.meta["ui"]["resourceUri"] == APP_URI
        resource = await client.read_resource(APP_URI)
        assert resource.contents[0].mime_type == "text/html;profile=mcp-app"
        assert "Refresh counts" in resource.contents[0].text


@pytest.mark.anyio
@pytest.mark.parametrize("framework", ["agents", "langgraph", "pydantic"])
async def test_actual_frameworks(framework):
    from common.frameworks import run_framework

    result = await run_framework(framework)
    assert "Week 2026-07-13" in result and "published" in result


@pytest.mark.anyio
async def test_evaluation_reports_real_catalogs_without_claiming_model_accuracy():
    from common.tool_evaluation import EvaluationConfigurationError, evaluate

    result = await evaluate()
    assert result["mirror"]["completed"] == result["task_tools"]["completed"] == 6
    assert result["mirror"]["tools"] == 25 and result["task_tools"]["tools"] == 6
    assert result["mirror"]["catalog_characters"] > result["task_tools"]["catalog_characters"]
    with pytest.raises(EvaluationConfigurationError, match="integer from 1 to 6.*check_env.py"):
        await evaluate(limit=0)


@pytest.mark.anyio
async def test_gateway_upstream_failure_and_context_boundary(tmp_path, monkeypatch):
    from mcp.server import MCPServer

    from common.notes import READ

    incoming = ContextVar("incoming_user_secret", default="absent")
    upstream = MCPServer("boundary")

    @upstream.tool(annotations=READ)
    async def context_probe() -> str:
        return incoming.get()

    gateway = Gateway(factories={"probe": upstream, "workflow": task_server()})
    server, _, tasks = gateway_server(tmp_path / "tasks.db", gateway)
    async with Client(server, mode=SPEC_REVISION) as client:
        token = incoming.set("must-not-forward")
        try:
            result = await client.call_tool("probe__context_probe", {})
            assert result.content[0].text == "absent"
        finally:
            incoming.reset(token)

        async def broken(*args, **kwargs):
            raise RuntimeError("upstream unavailable")

        monkeypatch.setattr(gateway.clients["probe"], "list_tools", broken)
        assert not (await client.call_tool("workflow__triage_week", {})).is_error
        with pytest.raises(MCPError, match="not available"):
            await client.call_tool("probe__context_probe", {})
    await tasks.close()


@pytest.mark.anyio
async def test_tasks_invalid_input_expiry_and_failure(tmp_path, monkeypatch):
    import common.report_tasks as tasks_module

    path = tmp_path / "task.db"
    async with Client(
        extension_server(path),
        mode=SPEC_REVISION,
        extensions=[TasksClient()],
        elicitation_callback=decline_unhandled_input,
    ) as client:
        handle = await client.session.call_tool(
            "quarterly_report", {"ask_details": True}, allow_claimed=True
        )
        await wait_state(client, handle, {"input_required"})
        with pytest.raises(MCPError, match="boolean"):
            await task_request(
                client.session,
                "tasks/update",
                handle.task_id,
                inputResponses={
                    "details-1": {"action": "accept", "content": {"include_details": "yes"}}
                },
            )
        await task_request(
            client.session,
            "tasks/update",
            handle.task_id,
            inputResponses={"unknown": {"action": "accept"}},
        )
        assert (await task_request(client.session, "tasks/get", handle.task_id))[
            "status"
        ] == "input_required"
        await task_request(
            client.session,
            "tasks/update",
            handle.task_id,
            inputResponses={"details-1": {"action": "decline"}},
        )
        assert (await task_request(client.session, "tasks/get", handle.task_id))[
            "status"
        ] == "cancelled"

        def broken(*args):
            raise RuntimeError("private computation detail")

        monkeypatch.setattr(tasks_module, "report", broken)
        handle = await client.session.call_tool("quarterly_report", {}, allow_claimed=True)
        state = await wait_state(client, handle, {"failed"})
        assert state["error"] == {"code": -32603, "message": "Report computation failed."}
        import sqlite3

        with sqlite3.connect(path) as connection:
            connection.execute("UPDATE tasks SET expires=0 WHERE id=?", (handle.task_id,))
        with pytest.raises(MCPError, match="expired"):
            await task_request(client.session, "tasks/get", handle.task_id)


@pytest.mark.parametrize("provider", ["openai", "anthropic", "gemini"])
def test_remote_mcp_requests_require_allowlists_and_safe_endpoint(provider):
    from common.remote_models import remote_url, request_body

    body = request_body(provider, "configured-model", "https://mcp.lumen.example/mcp")
    serialized = json.dumps(body)
    assert "triage_week" in serialized and "draft_status" in serialized
    assert "create_note" not in serialized
    if provider == "openai":
        assert body["tools"][0]["require_approval"] == "always"
    for address in [
        "http://mcp.example/mcp",
        "https://127.0.0.1/mcp",
        "https://user:password@host.example/mcp",
        "https://host.example/?secret=x",
    ]:
        with pytest.raises(ValueError):
            remote_url(address)
    with pytest.raises(ValueError, match="illustrative"):
        remote_url("https://mcp.lumen.example/mcp", live=True)


def test_remote_tool_configs_match_installed_provider_schemas():
    from anthropic.types.beta.beta_mcp_toolset_param import BetaMCPToolsetParam
    from google.genai._gaos.types.interactions.createmodelinteraction import CreateModelInteraction
    from openai.types.responses.tool_param import Mcp
    from pydantic import TypeAdapter

    from common.remote_models import request_body

    for provider, model in [("openai", Mcp), ("anthropic", BetaMCPToolsetParam)]:
        tool = request_body(provider, "configured-model", "https://lumen.example/mcp")["tools"][0]
        validated = TypeAdapter(model).validate_python(tool)
        assert validated["type"] == tool["type"]
    # This is the installed generated request model, not a live provider call.
    body = request_body("gemini", "configured-model", "https://lumen.example/mcp")
    validated = CreateModelInteraction.model_validate(body)
    assert validated.tools[0].allowed_tools[0].tools == ["draft_status", "triage_week"]
    assert validated.generation_config.max_output_tokens == 512


@pytest.mark.anyio
async def test_task_tool_error_is_completed_and_bad_arguments_are_rejected(tmp_path, monkeypatch):
    import common.report_tasks as task_module

    async with Client(
        extension_server(tmp_path / "task.db"), mode=SPEC_REVISION, extensions=[TasksClient()]
    ) as client:
        with pytest.raises(MCPError, match="boolean"):
            await client.call_tool("quarterly_report", {"ask_details": "yes"})
        monkeypatch.setattr(
            task_module,
            "report",
            lambda *args: {
                "resultType": "complete",
                "isError": True,
                "content": [{"type": "text", "text": "Report input cannot be processed."}],
            },
        )
        handle = await client.session.call_tool("quarterly_report", {}, allow_claimed=True)
        state = await wait_state(client, handle, {"completed", "failed"})
        assert state["status"] == "completed" and state["result"]["isError"]
