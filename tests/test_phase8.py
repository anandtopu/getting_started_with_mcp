"""Phase 8 integration and adversarial regressions; all identities/data are synthetic."""

import json
import shutil
import sys
import time

import httpx2 as httpx
import pytest
from jsonschema import ValidationError
from mcp import Client, StdioServerParameters
from mcp_types import Request

from common.audit_lab import audit_server
from common.auth_fixture import Authority
from common.auth_tokens import JWTVerifier
from common.config import ROOT
from common.knowledge import Knowledge, knowledge_server
from common.machine_auth import MachineAuthority
from common.ops import make_app
from common.pretty import redact
from common.server_cards import BASE, validate_card
from common.skills_extension import (
    ExtensionResult,
    GetParams,
    ListParams,
    load_skill,
    skills_server,
)
from scripts.auth_lab import rpc, running_app


@pytest.mark.anyio
async def test_explicit_audit_fixture_stdio():
    async with Client(
        StdioServerParameters(
            command=sys.executable,
            args=[str(ROOT / "capstones/02_security_audit/starter/vulnerable_server.py"), "--lab"],
            cwd=str(ROOT),
        ),
        mode="2026-07-28",
        read_timeout_seconds=10,
    ) as client:
        assert len((await client.list_tools()).tools) == 2


@pytest.mark.anyio
async def test_typescript_host_launcher_outside_checkout(tmp_path):
    async with Client(
        StdioServerParameters(
            command=shutil.which("node"),
            args=[str(ROOT / "scripts/launch_ts.cjs"), "notes"],
            cwd=str(tmp_path),
        ),
        mode="2026-07-28",
        read_timeout_seconds=10,
    ) as client:
        assert not (await client.call_tool("search_notes", {"query": "release"})).is_error


@pytest.mark.anyio
async def test_nested_knowledge_resource(tmp_path):
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested/release #1.md").write_text("Nested release evidence", encoding="utf-8")
    async with Client(knowledge_server(tmp_path)) as client:
        result = await client.call_tool("search_knowledge", {"query": "release"})
        uri = result.structured_content["result"][0]["uri"]
        assert uri == "knowledge://notes/nested/release%20%231.md"
        assert (await client.read_resource(uri)).contents[0].text == "Nested release evidence"


def test_knowledge_queries_and_paths(tmp_path):
    (tmp_path / "release.md").write_text("Release deployment checklist")
    (tmp_path / "incident.md").write_text("Incident recovery procedure")
    index = Knowledge(tmp_path)
    try:
        assert index.search("shipping", "text") == []
        assert index.search("shipping", "semantic")[0]["name"] == "release.md"
        assert index.search("unknownxyz", "semantic") == []
        assert index.search('" OR * ; DROP TABLE notes --') == []
        for name in ("../outside", "release.md/../incident.md", "/etc/passwd"):
            with pytest.raises(ValueError, match="Unknown note"):
                index.read(name)
        for query, limit in (("", 1), ("x" * 201, 1), ("release", 21)):
            with pytest.raises(ValueError):
                index.search(query, limit=limit)
    finally:
        index.close()


@pytest.mark.anyio
async def test_audit_repairs():
    async with Client(audit_server()) as client:
        for name, args in [
            ("read_record", {"name": "private"}),
            ("publish_bulletin", {"text": "x", "confirmed": False}),
            ("publish_bulletin", {"text": "x" * 201, "confirmed": True}),
        ]:
            assert (await client.call_tool(name, args)).is_error
        assert not (
            await client.call_tool("publish_bulletin", {"text": "Reviewed", "confirmed": True})
        ).is_error


@pytest.mark.anyio
async def test_skills_unknown_get_cursor_and_digest(monkeypatch):
    from common import skills_extension as skills

    async with Client(skills_server()) as client:
        assert (await load_skill(client))["activated"] is False
        for method, params in [
            ("skills/get", GetParams(uri="skill://unknown/SKILL.md")),
            ("skills/list", ListParams(cursor="unknown")),
        ]:
            with pytest.raises(Exception, match="Unknown skill"):
                await client.session.send_request(
                    Request(method=method, params=params), ExtensionResult
                )
        # The server published a new digest while the registered reader still serves old bytes.
        monkeypatch.setitem(skills.FILES, skills.URI, "tampered content")
        with pytest.raises(ValueError, match="changed"):
            await load_skill(client)


def test_server_card_schema_and_connection_policy():
    card = json.loads((BASE / "server-card.json").read_text())
    assert validate_card(card, "ops.lumen.example")["connected"] is False
    missing = {k: v for k, v in card.items() if k != "name"}
    with pytest.raises(ValidationError):
        validate_card(missing, "ops.lumen.example")
    for url in [
        "http://ops.lumen.example/mcp",
        "https://attacker.invalid/mcp",
        "https://user:password@ops.lumen.example/mcp",
    ]:
        changed = {**card, "remotes": [{"type": "streamable-http", "url": url}]}
        with pytest.raises((ValueError, ValidationError)):
            validate_card(changed, "ops.lumen.example")


@pytest.mark.anyio
async def test_machine_assertion_wrong_resource_and_replay():
    authority = MachineAuthority()
    authority.issuer, authority.resource = "https://issuer.example", "https://ops.example/mcp"
    assertion = await authority.assertion(authority.issuer, authority.resource)
    data = dict(
        client_id="lumen-machine",
        client_secret=authority.secret,
        grant_type="urn:ietf:params:oauth:grant-type:jwt-bearer",
        assertion=assertion,
        resource=authority.resource,
        scope="issues:read",
    )
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(authority.app()), base_url=authority.issuer
    ) as client:
        assert (
            await client.post("/token", data={**data, "resource": "https://other.example"})
        ).status_code == 400
        assert (await client.post("/token", data=data)).status_code == 200
        assert (await client.post("/token", data=data)).status_code == 400
        assert (
            await client.post("/token", data={**data, "assertion": "corrupt"})
        ).status_code == 400
    assert redact({"assertion": assertion, "client_secret": authority.secret}) == {
        "assertion": "[REDACTED]",
        "client_secret": "[REDACTED]",
    }


@pytest.mark.anyio
async def test_ops_http_authorization_and_task_owner(tmp_path):
    authority = Authority("https://issuer.lumen.example", "")

    def app(url):
        authority.resource = url + "/mcp"
        verifier = JWTVerifier(
            authority.issuer, authority.resource, authority.issuer + "/jwks", authority.jwks
        )
        return make_app(verifier, tmp_path / "tasks.db")

    async with running_app(app):
        headers = {
            "MCP-Protocol-Version": "2026-07-28",
            "Accept": "application/json, text/event-stream",
            "Mcp-Method": "tools/call",
            "Mcp-Name": "read_issue",
        }
        async with httpx.AsyncClient(headers=headers, timeout=5) as client:
            for token in [
                "corrupt",
                authority.token(aud="https://wrong.example"),
                authority.token(exp=int(time.time()) - 5),
            ]:
                assert (
                    await client.post(
                        authority.resource, json=rpc(), headers={"Authorization": "Bearer " + token}
                    )
                ).status_code == 401
            reader = {"Authorization": "Bearer " + authority.token()}
            response = await client.post(authority.resource, json=rpc(), headers=reader)
            assert response.status_code == 200, response.text
            assert not response.json()["result"].get("isError"), response.text
            assert (
                await client.post(
                    authority.resource, json=rpc("bulk_close", {"issue_ids": [1]}), headers=reader
                )
            ).status_code == 403
            assert (
                await client.post(
                    authority.resource,
                    json=rpc(),
                    headers={**reader, "Origin": "https://evil.example"},
                )
            ).status_code == 403
            request = rpc("quarterly_report", {"quarter": "Q1"})
            request["params"]["_meta"]["io.modelcontextprotocol/clientCapabilities"] = {
                "extensions": {"io.modelcontextprotocol/tasks": {}}
            }
            handle = (
                await client.post(
                    authority.resource,
                    json=request,
                    headers={**reader, "Mcp-Name": "quarterly_report"},
                )
            ).json()["result"]
            assert handle["resultType"] == "task"
            confirm = rpc("bulk_close", {"issue_ids": [1]})
            confirm["params"]["_meta"]["io.modelcontextprotocol/clientCapabilities"] = {
                "elicitation": {"form": {}}
            }
            writer = {
                "Authorization": "Bearer " + authority.token("issues:read issues:write"),
                "Mcp-Name": "bulk_close",
            }
            pending = (await client.post(authority.resource, json=confirm, headers=writer)).json()[
                "result"
            ]
            assert pending["resultType"] == "input_required", pending
            confirm["params"].update(
                requestState=pending["requestState"],
                inputResponses={"decision": {"action": "accept", "content": {"approve": True}}},
            )
            done = (await client.post(authority.resource, json=confirm, headers=writer)).json()[
                "result"
            ]
            assert not done.get("isError"), done
            request.update(method="tasks/get")
            request["params"] = {"taskId": handle["taskId"], "_meta": request["params"]["_meta"]}
            other = {"Authorization": "Bearer " + authority.token(sub="different-user")}
            denied = (
                await client.post(
                    authority.resource,
                    json=request,
                    headers={**other, "Mcp-Method": "tasks/get", "Mcp-Name": handle["taskId"]},
                )
            ).json()
            assert denied["error"]["code"] == -32602
            owned = (
                await client.post(
                    authority.resource,
                    json=request,
                    headers={**reader, "Mcp-Method": "tasks/get", "Mcp-Name": handle["taskId"]},
                )
            ).json()
            assert owned["result"]["status"] in {"working", "completed"}, owned


def test_capstone_registry_metadata():
    from jsonschema import Draft7Validator, FormatChecker

    schema = json.loads((ROOT / "distribution/registry/server.schema.json").read_text())
    Draft7Validator(schema, format_checker=FormatChecker()).validate(
        json.loads((ROOT / "capstones/04_lumen_ops/server.json").read_text())
    )
