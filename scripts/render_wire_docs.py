"""Refresh marked README excerpts from actual committed JSONL capture records.

Run after capture: uv run python scripts/render_wire_docs.py
No protocol fields are synthesized or omitted inside an included message.
"""

import json

from common.config import ROOT
from scripts.tier1 import MODULES

SELECTION = [
    ("03_reference_server", ["tools/call"]),
    ("01_jsonrpc", ["server/discover", "missing/method"]),
    ("python_main", ["tools/call"]),
    ("python_main", ["resources/read", "subscriptions/listen"]),
    ("python_main", ["completion/complete"]),
    ("02_pages_and_errors", ["resources/list"]),
    ("notes", ["tools/call"]),
]


def excerpt(index: int) -> str:
    filename, methods = SELECTION[index]
    path = ROOT / "modules" / MODULES[index] / "wire" / f"{filename}.jsonl"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    messages = [row["message"] for row in rows[1:] if isinstance(row["message"], dict)]
    selected = []
    for method in methods:
        requests = [m for m in messages if m.get("method") == method and "id" in m]
        request = requests[0]
        if index == 5:
            request = next(m for m in requests if m.get("params", {}).get("cursor") == "middle")
        if index == 6:
            request = next(m for m in requests if m["params"].get("name") == "create_note")
        selected.append(request)
        reply = next(
            (
                m
                for m in messages
                if m.get("id") == request["id"] and ("result" in m or "error" in m)
            ),
            None,
        )
        if reply:
            selected.append(reply)
    notifications = [
        m
        for m in messages
        if m.get("method", "").startswith("notifications/") and "cancelled" not in m["method"]
    ]
    selected.extend(notifications[:2])
    block = f"Source: [captured {filename}](wire/{filename}.jsonl). "
    block += "Each JSON block below is a complete message copied from that run.\n\n"
    block += "\n\n".join(
        "```json\n" + json.dumps(m, indent=2, ensure_ascii=False) + "\n```" for m in selected
    )
    return block


def main() -> None:
    for index, module in enumerate(MODULES):
        path = ROOT / "modules" / module / "README.md"
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        before, rest = text.split("<!-- wire:start -->", 1)
        _, after = rest.split("<!-- wire:end -->", 1)
        path.write_text(
            before + "<!-- wire:start -->\n\n" + excerpt(index) + "\n\n<!-- wire:end -->" + after,
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
