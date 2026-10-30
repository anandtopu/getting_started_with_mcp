"""Repository-wide checks on delivered code and documentation."""

import ast
import json
import runpy

import pytest
from mcp import Client

from common.config import ROOT
from scripts.check_course import validate
from scripts.check_links import check
from scripts.run_all_examples import smoke


@pytest.mark.anyio
async def test_actual_server_stdout(tmp_path):
    await smoke(tmp_path)
    for path in tmp_path.glob("*.jsonl"):
        records = [json.loads(line) for line in path.read_text().splitlines()]
        if records[0]["transport"] == "streamable-http":
            assert any(record.get("status") == 200 for record in records)
            messages = [
                record["message"]
                for record in records[1:]
                if record["message"] and "http_text" not in record["message"]
            ]
        else:
            messages = [record["message"] for record in records[1:]]
        assert all(message.get("jsonrpc") == "2.0" for message in messages), path


@pytest.mark.anyio
async def test_isolated_security_fixture():
    namespace = runpy.run_path(str(ROOT / "data/security/vulnerable_server.py"))
    async with Client(namespace["server"]) as client:
        result = await client.call_tool("fixture_salary", {"employee_id": 1})
        assert result.structured_content["synthetic"] is True
        assert result.structured_content["salary"] == 100000


def test_links_and_course():
    assert check() == []
    assert validate() == []
    assert validate(release=True)  # Do not call an incomplete course a release.


def test_no_legacy_imports_or_stdout_in_servers():
    banned = ["mcp.server." + "fastmcp", "mcp." + "types"]
    manifest = json.loads((ROOT / "scripts/examples.json").read_text())
    servers = {ROOT / entry["path"] for entry in manifest["servers"]}
    servers.add(ROOT / "data/security/vulnerable_server.py")
    paths = [
        *ROOT.joinpath("common").rglob("*.py"),
        *ROOT.joinpath("scripts").glob("*.py"),
        *ROOT.joinpath("modules").rglob("*.py"),
        ROOT / "data/security/vulnerable_server.py",
    ]
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert node.module not in banned, path
            if isinstance(node, ast.Import):
                assert not any(alias.name in banned for alias in node.names), path
            if path in servers and isinstance(node, ast.Call):
                assert not (isinstance(node.func, ast.Name) and node.func.id == "print"), path


def test_capture_is_real_jsonrpc():
    path = ROOT / "docs/wire/foundation_server.jsonl"
    records = [json.loads(line) for line in path.read_text().splitlines()]
    assert records[0]["transport"] == "stdio"
    messages = [record["message"] for record in records[1:]]
    assert all(message.get("jsonrpc") == "2.0" for message in messages)
    methods = {message.get("method") for message in messages}
    assert methods >= {"tools/list", "tools/call", "resources/list", "prompts/list"}
    assert all(
        message["result"]["resultType"] == "complete" for message in messages if "result" in message
    )
