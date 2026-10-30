"""Send real JSON lines (including malformed JSON) through the teaching proxy."""

import json
import subprocess
import sys
from pathlib import Path

from common.config import ROOT
from common.raw_server import META, VERSION


def exchange(capture: Path) -> list[dict]:
    meta = {
        META + "protocolVersion": VERSION,
        META + "clientCapabilities": {},
        META + "clientInfo": {"name": "Lumen handwritten client", "version": "1.0"},
    }
    messages = []
    for identifier, method, args in [
        (1, "server/discover", {}),
        (2, "tools/list", {}),
        (3, "tools/call", {"name": "directory_count", "arguments": {}}),
        (4, "missing/method", {}),
        (5, "tools/call", {"name": "wrong"}),
    ]:
        messages.append(
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": identifier,
                    "method": method,
                    "params": {"_meta": meta, **args},
                }
            )
        )
    messages += [
        '{"jsonrpc":"2.0","method":"ping"}',
        "broken JSON",
        "[]",
        json.dumps(
            {
                "jsonrpc": "2.0",
                "id": 6,
                "method": "tools/list",
                "params": {"_meta": {**meta, META + "protocolVersion": "2099-01-01"}},
            }
        ),
    ]
    command = [
        sys.executable,
        str(ROOT / "scripts/wiretap.py"),
        "--capture",
        str(capture),
        "--",
        sys.executable,
        str(ROOT / "common/raw_server.py"),
    ]
    result = subprocess.run(
        command,
        input="\n".join(messages) + "\n",
        capture_output=True,
        text=True,
        timeout=20,
        cwd=ROOT,
        check=True,
    )
    return [json.loads(line) for line in result.stdout.splitlines()]


def main() -> None:
    for response in exchange(ROOT / ".runtime/raw-errors.jsonl"):
        print(json.dumps(response))
