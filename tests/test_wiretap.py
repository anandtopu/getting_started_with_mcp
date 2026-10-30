"""The proxy must preserve bytes and must not hang on EOF or child failure."""

import json
import os
import subprocess
import sys

from common.config import ROOT


def run_proxy(tmp_path, code, payload=b"", timeout="5", env=None):
    capture = tmp_path / "capture.jsonl"
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/wiretap.py"),
            "--capture",
            str(capture),
            "--timeout",
            timeout,
            "--",
            sys.executable,
            "-c",
            code,
        ],
        input=payload,
        capture_output=True,
        timeout=12,
        env=env,
    )
    return result, capture


def test_bytes_and_redaction(tmp_path):
    secret = "fixture-secret-never-persist"
    payload = (
        json.dumps(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "echo",
                "params": {"text": secret, "api_key": secret},
            }
        )
        + "\r\n"
    ).encode()
    payload += b"not-json\n\xff\n"
    result, capture = run_proxy(
        tmp_path,
        "import sys; sys.stdout.buffer.write(sys.stdin.buffer.read()); sys.stdout.buffer.flush()",
        payload,
        env={**os.environ, "TEST_API_KEY": secret},
    )
    assert result.returncode == 0
    assert result.stdout == payload
    assert secret.encode() not in result.stderr
    assert secret not in capture.read_text()
    records = [json.loads(line) for line in capture.read_text().splitlines()]
    assert {r.get("direction") for r in records} >= {"client->server", "server->client"}


def test_child_exit(tmp_path):
    result, _ = run_proxy(tmp_path, "raise SystemExit(7)")
    assert result.returncode == 7


def test_timeout(tmp_path):
    result, _ = run_proxy(tmp_path, "import time; time.sleep(60)", timeout="0.2")
    assert result.returncode == 124
