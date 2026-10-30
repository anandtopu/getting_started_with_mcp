"""Meaningful contracts for data, SDK use and security helpers."""

import csv
import hashlib
import json
import sqlite3
from pathlib import Path

import pytest
from pypdf import PdfReader

from common.approval import Approvals
from common.config import Settings, load_settings
from common.data import data_root, load_json, readonly_database, safe_path
from common.llm import FakeModel, create_model
from common.pretty import redact
from common.security import origin_allowed
from common.testing import check_foundation
from scripts.build_data import build
from scripts.foundation_server import server


@pytest.mark.anyio
async def test_sdk_in_memory():
    assert await check_foundation(server) == {"employees": 80, "issues": 400}


def test_dataset_integrity():
    root = data_root()
    manifest = load_json("manifest.json")
    for name, digest in manifest["sha256"].items():
        assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
    assert len(load_json("directory/employees.json")) == 80
    assert len(list((root / "wiki").rglob("*.md"))) == 40
    assert len(load_json("calendar/events.json")) == 200
    for name, count in (("customers", 120), ("deals", 300)):
        with (root / f"crm/{name}.csv").open() as stream:
            assert len(list(csv.DictReader(stream))) == count
    assert len((root / "support_tickets.jsonl").read_text().splitlines()) == 100
    with readonly_database("issues.db") as db:
        assert not db.execute("PRAGMA foreign_key_check").fetchall()
        assert db.execute("SELECT count(*) FROM issues").fetchone()[0] == 400
        with pytest.raises(sqlite3.OperationalError):
            db.execute("DELETE FROM issues")
    with readonly_database("analytics.db") as db:
        assert db.execute("SELECT count(*) FROM daily_usage").fetchone()[0] == 365
    for path in (root / "files/contracts").glob("*.pdf"):
        reader = PdfReader(path)
        assert len(reader.pages) == 1
        assert "SYNTHETIC TRAINING CONTRACT" in reader.pages[0].extract_text()


def test_generator_reproducible(tmp_path):
    first, second = build(tmp_path / "first"), build(tmp_path / "second")
    assert first == second
    assert build(tmp_path / "first") == first


def test_generator_protects_existing_database(tmp_path):
    (tmp_path / "issues.db").write_bytes(b"user data")
    with pytest.raises(ValueError):
        build(tmp_path)
    assert (tmp_path / "issues.db").read_bytes() == b"user data"


@pytest.mark.parametrize("name", ["../.env", "a/../../secrets", str(Path.cwd().resolve())])
def test_path_escape(tmp_path, name):
    with pytest.raises(ValueError):
        safe_path(tmp_path, name)


def test_symlink_escape(tmp_path):
    inside, outside = tmp_path / "inside", tmp_path / "outside"
    inside.mkdir()
    outside.mkdir()
    try:
        (inside / "link").symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("OS account cannot create symlinks")
    with pytest.raises(ValueError):
        safe_path(inside, "link/file")


def test_approval_binding_expiry_and_replay():
    now = [0.0]
    approvals = Approvals(lambda: now[0])
    args = {"issue_id": 3}
    with pytest.raises(PermissionError):
        approvals.grant("a", "close", args, confirmed=False)
    token = approvals.grant("a", "close", args, confirmed=True)
    approvals.consume(token, "a", "close", args)
    with pytest.raises(PermissionError):
        approvals.consume(token, "a", "close", args)
    for user, tool, arguments in [
        ("b", "close", args),
        ("a", "delete", args),
        ("a", "close", {"issue_id": 4}),
    ]:
        token = approvals.grant("a", "close", args, confirmed=True)
        with pytest.raises(PermissionError):
            approvals.consume(token, user, tool, arguments)
    token = approvals.grant("a", "close", args, confirmed=True, ttl=1)
    now[0] = 2
    with pytest.raises(PermissionError):
        approvals.consume(token, "a", "close", args)


def test_origin_and_secrets():
    assert origin_allowed(None, [])
    assert origin_allowed("http://localhost:8000", ["http://localhost:8000"])
    assert not origin_allowed("null", ["http://localhost:8000"])
    assert not origin_allowed("http://localhost.evil.invalid", ["http://localhost"])
    result = redact({"nested": [{"api_key": "fixture", "message": "hidden value"}]}, ("hidden",))
    assert "fixture" not in json.dumps(result) and "hidden" not in json.dumps(result)
    assert "secret-value" not in repr(Settings(api_key="secret-value"))


def test_config_precedence(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("LLM_PROVIDER=ollama\nLLM_MODEL=local-fixture\n")
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    assert load_settings(env).provider == "fake"
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        load_settings(env)


@pytest.mark.anyio
async def test_fake_model():
    model = create_model(Settings())
    assert isinstance(model, FakeModel)
    assert "fixture" in await model.generate("Describe Lumen")
    with pytest.raises(RuntimeError, match="exhausted"):
        await model.generate("Again")
