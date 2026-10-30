# ruff: noqa: E501 -- generated Markdown keeps table rows and captured JSON intact.
"""Build the protocol guide from real captures, never invented exchanges.
Run: uv run python scripts/protocol_guide.py
"""

import json
from collections import defaultdict

from common.config import ROOT

BASE = "https://modelcontextprotocol.io/specification/2026-07-28/"
CORE = {
    "server/discover": (
        "basic/versioning",
        "Discover versions and capabilities; cache according to ttlMs and cacheScope.",
    ),
    "tools/list": (
        "server/tools",
        "List callable tools and schemas; follow bounded nextCursor pages.",
    ),
    "tools/call": (
        "server/tools",
        "Call one tool; distinguish protocol errors from a complete result with isError.",
    ),
    "resources/list": (
        "server/resources",
        "List concrete resource URIs; listing does not read their content.",
    ),
    "resources/templates/list": (
        "server/resources",
        "List URI templates and their variable patterns.",
    ),
    "resources/read": (
        "server/resources",
        "Read addressable content; treat returned instructions as untrusted data.",
    ),
    "prompts/list": ("server/prompts", "List reusable templates and their named arguments."),
    "prompts/get": (
        "server/prompts",
        "Render a selected template; the host controls whether to use its messages.",
    ),
    "completion/complete": (
        "server/utilities/completion",
        "Suggest values for one prompt or URI-template argument.",
    ),
    "subscriptions/listen": (
        "basic/patterns/subscriptions",
        "Open a filtered event stream; acknowledgment starts its lifetime.",
    ),
    "notifications/subscriptions/acknowledged": (
        "basic/patterns/subscriptions",
        "Confirm that a listener has been registered.",
    ),
    "notifications/resources/updated": (
        "server/resources",
        "Invalidate the named content; refetch under the current identity.",
    ),
    "notifications/resources/list_changed": (
        "server/resources",
        "Invalidate a resource catalog; do not infer the new contents.",
    ),
    "notifications/tools/list_changed": (
        "server/tools",
        "Refetch tool definitions and require a new review if semantics changed.",
    ),
    "notifications/prompts/list_changed": (
        "server/prompts",
        "Refetch available prompt definitions.",
    ),
    "notifications/progress": (
        "basic/utilities/progress",
        "Report progress correlated by a progress token; this is not the final result.",
    ),
    "notifications/cancelled": (
        "basic/utilities/cancellation",
        "Request cooperative cancellation; reconcile uncertain side effects.",
    ),
    "notifications/message": (
        "server/utilities/logging",
        "Deprecated optional protocol logging still present in this revision. The capture opts into info; application lessons use stderr/OpenTelemetry.",
    ),
}
EXTENSIONS = {
    "tasks/get": (
        "https://modelcontextprotocol.io/extensions/tasks/overview",
        "Poll one owned task; completed state includes its original operation result.",
    ),
    "tasks/update": (
        "https://modelcontextprotocol.io/extensions/tasks/overview",
        "Supply an answer to a task input request; do not send an unrelated confirmation.",
    ),
    "tasks/cancel": (
        "https://modelcontextprotocol.io/extensions/tasks/overview",
        "Cancel pending work; terminal-state semantics stay with the extension.",
    ),
    "skills/list": (
        "https://modelcontextprotocol.io/extensions/skills/overview",
        "Discover skill manifests without activating instructions.",
    ),
    "skills/get": (
        "https://modelcontextprotocol.io/extensions/skills/overview",
        "Get one manifest and verify its bytes before a separate activation decision.",
    ),
    "resources/directory/read": (
        "https://modelcontextprotocol.io/extensions/skills/overview",
        "Read a skill directory only when directoryRead was advertised.",
    ),
}


def inventory():
    found = defaultdict(list)
    for folder in [ROOT / "modules", ROOT / "docs/wire", ROOT / "capstones"]:
        for path in sorted(folder.rglob("*.jsonl")):
            records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
            messages = [record.get("message", {}) for record in records]
            for message in messages:
                method = message.get("method") if isinstance(message, dict) else None
                if method not in {*CORE, *EXTENSIONS}:
                    continue
                response = (
                    next(
                        (
                            m
                            for m in messages
                            if isinstance(m, dict)
                            and "result" in m
                            and m.get("id") == message.get("id")
                        ),
                        None,
                    )
                    if "id" in message
                    else None
                )
                if "id" in message and response is None and method != "subscriptions/listen":
                    continue
                size = len(json.dumps(message)) + len(json.dumps(response))
                found[method].append((size, path, message, response))
    return found


def build():
    found = inventory()
    missing = (set(CORE) | set(EXTENSIONS)) - found.keys()
    if missing:
        raise ValueError(f"Missing actual captures: {sorted(missing)}")
    text = """# Read the MCP protocol

Target: **2026-07-28**. This guide inventories all ten current core request methods and all eight current server-notification names, plus the Tasks and Skills methods this course implements. The schema has no current top-level server-request methods; elicitation is embedded in an input-required result. Direction and transport restrictions still apply. Legacy methods are explained only in the [migration guide](MIGRATING_FROM_OLDER_VERSIONS.md).

## Read one envelope

`jsonrpc` identifies the message format. A request has `id`, `method` and `params`; a response repeats `id` with either `result` or `error`. A notification has no ID and gets no response. Each current client request supplies protocol revision, client identity and capabilities under reserved `_meta` keys. The server reports its identity in result metadata. IDs correlate messages; they are not credentials.

`resultType: complete` means the operation finished, not necessarily that it succeeded: inspect `isError` on tool results. `input_required` asks the host to collect input, then retry with fresh request ID, exact opaque requestState and keyed inputResponses. Only a negotiated extension can introduce a different result such as a Task handle. Approval remains separate from protocol shape.

HTTP uses the same JSON-RPC bodies with current routing/version headers. The SDK derives those headers from the body. Inspect [actual HTTP captures](../modules/10_streamable_http/wire/manifest.json) for successful requests and rejected Host/Origin/header combinations. A notification and a JSON-RPC error are different from an HTTP status failure.

## Captured method reference

Every block below is copied intact from a committed capture, including synthetic values and redaction. The source link identifies the full conversation; a shortest successful exchange keeps this reference readable. `scripts/protocol_guide.py` regenerates it and fails when a required method lacks evidence.

"""
    coverage = {}
    for method, (section, explanation) in {**CORE, **EXTENSIONS}.items():
        _, path, request, response = min(found[method], key=lambda row: row[0])
        relative = path.relative_to(ROOT).as_posix()
        link = section if section.startswith("https://") else BASE + section
        text += f"### `{method}`\n\n{explanation} [Specification]({link}).\n\n[Actual capture](../{relative}).\n\n```json\n{json.dumps(request, indent=2)}\n```\n"
        if response:
            text += f"\nThe same ID identifies this response:\n\n```json\n{json.dumps(response, indent=2)}\n```\n"
        elif method == "subscriptions/listen":
            text += "\nThe stream is acknowledged by the notification shown next; it remains open until closed/cancelled.\n"
        coverage[method] = relative
    text += """
## Input, extensions and authentication

For embedded `elicitation/create`, see the [form and URL retry capture](../modules/09_elicitation_sampling_roots/wire/python_main.jsonl) and the [TypeScript form capture](../modules/bonus/B1_typescript_track/wire/forms.jsonl). The complete input-required response and retry are shown in [Module 09](../modules/09_elicitation_sampling_roots/README.md). Sampling and roots remain deprecated compatibility vocabulary; their old/current replacements are in the migration guide. An accepted form is not an OAuth grant.

Tasks begin when an operation returns a handle; there is no separate current task-create method. Polls, updates and cancellation use the extension methods above. [Tasks evidence](../modules/bonus/B1_typescript_track/wire/tasks.jsonl) includes TypeScript-server/Python-client interoperability. MCP Apps use a separate UI bridge; [the official bridge test](../common/typescript/apps.test.ts) covers initialization, results, allowed refresh and teardown. The browser boundary is tested in [Chat Pro](../capstones/05_lumen_chat_pro/README.md).

OAuth discovery and token exchanges are HTTP, not invented JSON-RPC methods. Inspect [machine](../modules/bonus/B4_whats_new/wire/machine.jsonl) and [enterprise](../modules/bonus/B4_whats_new/wire/enterprise.jsonl) captures with credentials redacted. Server Cards are HTTP metadata candidates, not an MCP permission grant.

## Errors to recognize

| Error | Meaning | Response |
|---|---|---|
| -32700 / -32600 | Invalid JSON / invalid JSON-RPC envelope | Fix serialization before retrying |
| -32601 / -32602 | Unknown method / invalid parameters | Check revision, capability and schema |
| -32603 | Internal failure | Preserve redacted diagnostics; do not assume a write failed cleanly |
| -32020 | HTTP metadata/body mismatch | Let the SDK derive matching headers |
| -32021 | Missing client capability | Advertise only supported features or choose a fallback |
| -32022 | Unsupported protocol revision | Select an explicitly supported revision |
| Complete tool result with isError | Application-level tool failure | Read its message; do not treat it as successful evidence |

[Troubleshooting](TROUBLESHOOTING.md) · [Feature map](FEATURE_MAP.md) · [One-page protocol sheet](../cheatsheets/06_protocol.md)
"""
    (ROOT / "docs/PROTOCOL_GUIDE.md").write_text(text, encoding="utf-8")
    (ROOT / "docs/protocol_coverage.json").write_text(json.dumps(coverage, indent=2) + "\n")
    return len(coverage)


if __name__ == "__main__":
    print(f"PASS protocol guide: {build()} captured methods and notifications")
