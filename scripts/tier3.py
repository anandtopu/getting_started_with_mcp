"""Check modules 11-13. Run: uv run python scripts/tier3.py --capture."""

import argparse
import asyncio
import json
from contextlib import nullcontext

from common.config import ROOT
from common.connections import discover
from common.defenses import ReviewedHost, catalog, catalog_fingerprint
from common.protocol import SPEC_REVISION
from common.tool_formats import ToolCall
from scripts.auth_lab import auth_stack, exercise_auth
from scripts.tier1 import script_client

MODULES = ["11_authorization", "12_security", "13_testing_observability"]


async def exercise(client, index: int):
    await discover(client)
    if index == 12:
        assert (await client.read_resource("lab://poisoned-wiki")).contents
        assert not (await client.call_tool("fixture_salary", {"employee_id": 1})).is_error
        assert (await client.call_tool("fixture_salary", {"employee_id": 2})).is_error
        assert (
            await client.call_tool("project_summary", {"project": "https://evil.example"})
        ).is_error

        async def approve(name, args):
            return name == "lab__read_lab_page"

        host = ReviewedHost(
            {"lab": client},
            approve,
            {"lab": catalog_fingerprint(await catalog(client))},
            {"lab__read_lab_page"},
        )
        await host.discover()
        page = await host.execute(ToolCall("page", "lab__read_lab_page", {}))
        assert not page.error and "untrusted" in page.text
        for name in ["files__read_file", "lab__fixture_salary", "mail__send"]:
            assert (await host.execute(ToolCall(name, name, {}))).error
    else:
        assert (await client.list_tools()).tools
        assert not (await client.call_tool("search_notes", {})).is_error
        assert (await client.call_tool("create_note", {"title": "", "body": "x"})).is_error


async def run(index: int, capture: bool = False):
    folder = ROOT / "modules" / MODULES[index - 11] / "wire"
    folder.mkdir(parents=True, exist_ok=True)
    if index == 11:
        async with auth_stack() as authority:
            await exercise_auth(authority, folder / "python_http.jsonl" if capture else None)
    else:
        path = f"modules/{MODULES[index - 11]}/python/use_case/server.py"
        span = nullcontext()
        tracing = None
        if capture and index == 13:
            from opentelemetry import trace

            from common.quality import configure_traces

            tracing, _ = configure_traces()
            span = trace.get_tracer("lumen.capture").start_as_current_span("wire-quality")
        try:
            with span:
                async with script_client(
                    path, folder / "python_main.jsonl" if capture else None
                ) as client:
                    await exercise(client, index)
        finally:
            if tracing:
                tracing.force_flush()
                tracing.shutdown()
    if capture:
        for path in folder.glob("*.jsonl"):
            lines = path.read_text(encoding="utf-8").splitlines()
            header = json.loads(lines[0])
            header["command"] = f"uv run python scripts/tier3.py --module {index} --capture"
            path.write_text(
                json.dumps(header) + "\n" + "\n".join(lines[1:]) + "\n", encoding="utf-8"
            )
        (folder / "manifest.json").write_text(
            json.dumps(
                {
                    "command": f"uv run python scripts/tier3.py --module {index} --capture",
                    "spec": SPEC_REVISION,
                    "python_sdk": "2.3.0",
                    "files": sorted(p.name for p in folder.glob("*.jsonl")),
                    "redactions": ["Authorization headers and credential fields"],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    print(f"PASS Module {index:02d}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module", type=int, choices=range(11, 14))
    parser.add_argument("--capture", action="store_true")
    args = parser.parse_args()
    for index in range(11, 14) if args.module is None else [args.module]:
        asyncio.run(run(index, args.capture))


if __name__ == "__main__":
    main()
