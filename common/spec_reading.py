"""Read actual capture structure and prepare a small, redacted conformance report."""

import json
from pathlib import Path

from mcp_types import JSONRPCMessage
from pydantic import TypeAdapter


def messages(path: Path):
    for line in path.read_text(encoding="utf-8").splitlines()[1:]:
        record = json.loads(line)
        message = record.get("message")
        if isinstance(message, dict) and message.get("jsonrpc") == "2.0":
            TypeAdapter(JSONRPCMessage).validate_python(message)
            yield message


def contract_report(path: Path):
    rows = list(messages(path))
    requests = {m["id"]: m for m in rows if "method" in m and "id" in m}
    responses = [m for m in rows if "result" in m or "error" in m]
    missing = [
        m["id"]
        for m in responses
        if m["id"] not in requests
        and not (m["id"] is None and m.get("error", {}).get("code") in {-32700, -32600})
    ]
    if missing:
        raise ValueError("Capture contains an uncorrelated response.")
    return {
        "messages": len(rows),
        "requests": len(requests),
        "methods": sorted({m["method"] for m in requests.values()}),
        "scope": "shape and correlation; not full protocol conformance",
    }


def issue_template(path: Path):
    report = contract_report(path)
    return {
        "spec": "2026-07-28",
        "sdk": "mcp 2.3.0",
        "expected": "Correlated JSON-RPC",
        "observed": report,
        "reproduction": "uv run python scripts/bonus.py --module B3",
        "privacy": "Synthetic capture; inspect before attaching. No issue was submitted.",
    }
