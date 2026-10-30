"""Shipping boundaries: archives, metadata, retries, approval binding and browser requests."""

import asyncio
import json
import shutil
import sys
import tarfile
from types import SimpleNamespace

import httpx2 as httpx
import pytest
from mcp_types import Tool

from common.deployment import Operations, public_url
from common.packaging import artifacts, inspect_artifacts, run
from common.production_host import Connection, ServerConfig, load_host_config
from common.registry import fixture_transport, list_registry, validate_metadata, version_url
from common.web_chat import Session, make_web_app


def test_artifacts_and_sdist_rebuild(tmp_path):
    paths = artifacts()
    inventory = inspect_artifacts(paths)
    assert "package/dist/cli.cjs" in inventory["npm"]
    assert "manifest.json" in inventory["bundle"]
    with tarfile.open(paths["sdist"]) as source:
        source.extractall(tmp_path, filter="data")
    project = next(tmp_path.glob("*/pyproject.toml")).parent
    run(
        [
            shutil.which("uv"),
            "build",
            str(project),
            "--wheel",
            "--no-build-isolation",
            "--python",
            sys.executable,
            "--out-dir",
            str(tmp_path / "rebuilt"),
        ],
        cwd=tmp_path,
    )
    assert list((tmp_path / "rebuilt").glob("*.whl"))


def test_archive_rejects_environment_files(tmp_path):
    import zipfile

    path = tmp_path / "secret.whl"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("pkg/.env.production", "fixture-only")
    with pytest.raises(ValueError, match="Unexpected"):
        inspect_artifacts({"wheel": path})


def test_registry_identity_mismatch():
    from jsonschema import ValidationError

    with pytest.raises(ValidationError):
        validate_metadata({})
    document = validate_metadata()
    document["version"] = "2.0.0"
    with pytest.raises(ValueError, match="identity/version"):
        validate_metadata(document)
    assert "io.github.a%2Fnotes" in version_url("io.github.a/notes", "1.0.0")


@pytest.mark.anyio
async def test_registry_pagination_and_cycle():
    assert len(await list_registry(fixture_transport())) == 1
    cycle = httpx.MockTransport(
        lambda _: httpx.Response(200, json={"servers": [], "metadata": {"nextCursor": "same"}})
    )
    with pytest.raises(ValueError, match="repeated"):
        await list_registry(cycle)


@pytest.mark.parametrize(
    "url",
    [
        "http://outside.example/mcp",
        "https://u:p@host/mcp",
        "http://localhost.evil/mcp",
        "https://host/mcp?token=x",
    ],
)
def test_public_url_rejection(url):
    with pytest.raises(ValueError):
        public_url(url)


def test_rate_budget_and_bounded_subjects():
    now = [1.0]
    limiter = Operations(None, None, limit=2, clock=lambda: now[0])
    assert [limiter.allow("alex") for _ in range(3)] == [True, True, False]
    for i in range(999):
        assert limiter.allow(str(i))
    assert not limiter.allow("overflow")
    now[0] = 62
    assert limiter.allow("overflow") and len(limiter.windows) == 1


def test_config_rejects_duplicates_and_untrusted_endpoints(tmp_path):
    path = tmp_path / "host.json"
    path.write_text(json.dumps({"servers": [{"alias": "notes", "profile": "notes"}] * 2}))
    with pytest.raises(ValueError, match="unique aliases"):
        load_host_config(path)
    path.write_text(
        json.dumps(
            {
                "servers": [
                    {"alias": "notes", "profile": "notes", "url": "http://remote.example/mcp"}
                ]
            }
        )
    )
    with pytest.raises(ValueError, match="HTTPS"):
        load_host_config(path)


@pytest.mark.anyio
async def test_actual_connection_refresh_and_reconnect():
    c = await Connection(ServerConfig(alias="notes", profile="notes"), lambda *_: None).start()
    try:
        tool = next(t for t in await c.tools() if t.name == "search_notes")
        stale = tool.model_copy(update={"description": "Different meaning"})
        with pytest.raises(PermissionError, match="changed after review"):
            await c.checked_call(stale, {"query": "release"})
        assert not (await c.checked_call(tool, {"query": "release"})).is_error
        await c.restart()
        assert c.info["generation"] == 2
        assert not (await c.checked_call(tool, {"query": "release"})).is_error
    finally:
        await c.close()


@pytest.mark.anyio
@pytest.mark.parametrize("safe", [True, False])
async def test_transport_retry_is_local_read_policy(monkeypatch, safe):
    c = Connection(ServerConfig(alias="notes", profile="notes"), lambda *_: None)
    tool = Tool(name="search_notes" if safe else "create_note", input_schema={"type": "object"})
    calls, restarts = [], []

    async def tools():
        return [tool]

    async def invoke(action):
        calls.append(action)
        if len(calls) == 1:
            raise ConnectionError("response lost")
        return "fixture result"

    async def restart():
        restarts.append(True)

    monkeypatch.setattr(c, "tools", tools)
    monkeypatch.setattr(c, "invoke", invoke)
    monkeypatch.setattr(c, "restart", restart)
    if safe:
        assert await c.checked_call(tool, {}) == "fixture result"
        assert len(calls) == 2 and len(restarts) == 1
    else:
        with pytest.raises(RuntimeError, match="Outcome unknown"):
            await c.checked_call(tool, {})
        assert len(calls) == 1 and not restarts


@pytest.mark.anyio
async def test_decision_cannot_be_replayed_or_misbound():
    session = Session(SimpleNamespace(servers=[]))
    task = asyncio.create_task(session.question("approval", {"tool": "notes__create_note"}))
    await asyncio.sleep(0)
    with pytest.raises(ValueError, match="expired"):
        session.answer("different-question", "accept", {})
    question = session.pending["id"]
    session.answer(question, "decline", {})
    with pytest.raises(ValueError, match="already answered"):
        session.answer(question, "accept", {})
    assert (await task)["action"] == "decline"
    assert session.pending is None


@pytest.mark.anyio
async def test_browser_boundary_and_capacity(monkeypatch):
    async def start(self):
        await asyncio.sleep(0.01)

    monkeypatch.setattr(Session, "start", start)
    app = make_web_app()
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app), base_url="http://127.0.0.1:8766"
    ) as http:
        assert (await http.get("/api/state")).status_code == 401
        assert (await http.post("/api/session")).status_code == 403
        assert (
            await http.post("/api/session", headers={"Origin": "https://evil.example"})
        ).status_code == 403
        assert (await http.get("/", headers={"Host": "evil.example"})).status_code == 421
        responses = await asyncio.gather(
            *[http.post("/api/session", headers={"X-Lumen-Client": "web"}) for _ in range(6)]
        )
        assert sorted(r.status_code for r in responses) == [200, 200, 200, 200, 429, 429]
        assert (await http.post("/api/cancel")).status_code == 403
        bootstrap = await http.post("/api/session", headers={"X-Lumen-Client": "web"})
        http.headers["X-CSRF-Token"] = bootstrap.json()["csrf"]
        assert (await http.post("/api/app-call", json={"name": "delete_issue"})).status_code == 403
        assert (await http.post("/api/close")).status_code == 200


@pytest.mark.anyio
async def test_legacy_real_transport():
    from scripts.tier5 import host_demo

    info = await host_demo(legacy=True)
    assert info["protocol"] == "2025-11-25"


@pytest.mark.anyio
async def test_web_host_uses_authenticated_remote_transport():
    from scripts.auth_lab import auth_stack
    from scripts.shipping_check import web_remote_check

    async with auth_stack() as authority:
        await web_remote_check(authority.token(), authority.resource)
