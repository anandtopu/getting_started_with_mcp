"""Refresh marked README excerpts from actual committed JSONL capture records.

Run after capture: uv run python scripts/render_wire_docs.py
No protocol fields are synthesized or omitted inside an included message.
"""

import json

from common.config import ROOT
from scripts.tier1 import MODULES
from scripts.tier2 import MODULES as TIER2_MODULES
from scripts.tier3 import MODULES as TIER3_MODULES
from scripts.tier4 import MODULES as TIER4_MODULES
from scripts.tier5 import MODULES as TIER5_MODULES

MODULES = MODULES + TIER2_MODULES + TIER3_MODULES + TIER4_MODULES + TIER5_MODULES

SELECTION = [
    ("03_reference_server", ["tools/call"]),
    ("01_jsonrpc", ["server/discover", "missing/method"]),
    ("python_main", ["tools/call"]),
    ("python_main", ["resources/read", "subscriptions/listen"]),
    ("python_main", ["completion/complete"]),
    ("02_pages_and_errors", ["resources/list"]),
    ("notes", ["tools/call"]),
    ("python_main", ["tools/call", "resources/read"]),
    ("python_main", ["tools/call"]),
    ("python_main", ["tools/call"]),
    ("python_http", ["subscriptions/listen", "tools/call"]),
    ("python_http", ["server/discover", "tools/call"]),
    ("python_main", ["resources/read", "tools/call"]),
    ("python_main", ["tools/call"]),
]
SELECTION += [("python_main", ["tools/call"])] * 3
SELECTION += [("python_main", ["tools/call", "tasks/get", "tasks/update", "tasks/cancel"])]

SELECTION += [("python_main", ["tools/call"])] * 4


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
        if index == 9:
            request = next(m for m in requests if m["params"].get("name") == "bulk_close")
        if index == 10 and method == "tools/call":
            request = next(m for m in requests if m["params"].get("name") == "route_region")
        if index == 11 and method == "tools/call":
            request = next(m for m in requests if m["id"] != "auth-check")
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
    if index == 17:
        for state in ["input_required", "completed"]:
            reply = next(m for m in messages if m.get("result", {}).get("status") == state)
            request = next(m for m in messages if m.get("id") == reply["id"] and "method" in m)
            if request not in selected:
                selected.extend([request, reply])
    notifications = [
        m
        for m in messages
        if m.get("method", "").startswith("notifications/") and "cancelled" not in m["method"]
    ]
    selected.extend(notifications[:2])
    if index == 9:
        retry = next(
            m
            for m in messages
            if m.get("method") == "tools/call" and m.get("params", {}).get("inputResponses")
        )
        selected.append(retry)
        selected.append(next(m for m in messages if m.get("id") == retry["id"] and "result" in m))
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
