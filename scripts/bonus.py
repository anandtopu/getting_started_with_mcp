"""Finite bonus checks; native SDK builds are a separate explicit command.
Run: uv run python scripts/bonus.py --module B4 --capture
"""

import argparse
import asyncio
import json

from mcp import Client

from common.config import ROOT
from common.skills_extension import load_skill, skills_server
from common.spec_reading import contract_report, issue_template


async def run(module, capture=False):
    if module == "B3":
        source = ROOT / "modules/01_architecture_wire/wire/01_jsonrpc.jsonl"
        report = contract_report(source)
        assert report["requests"] > 0
        assert issue_template(source)["spec"] == "2026-07-28"
        if capture:
            from scripts.tier1 import script_client

            path = ROOT / "modules/bonus/B3_spec_contributing/wire/main.jsonl"
            async with script_client(
                "modules/01_architecture_wire/python/examples/02_raw_server.py", path
            ) as client:
                await client.list_tools()
                await client.call_tool("directory_count", {})
        print(report)
    elif module == "B4":
        from common.machine_auth import run as auth
        from common.server_cards import BASE, validate_card

        async with Client(skills_server()) as client:
            assert await load_skill(client) == {"verified_files": 2, "activated": False}
        assert not validate_card(
            json.loads((BASE / "server-card.json").read_text()), "ops.lumen.example"
        )["connected"]
        folder = ROOT / "modules/bonus/B4_whats_new/wire"
        for enterprise in (False, True):
            await auth(
                enterprise,
                folder / ("enterprise.jsonl" if enterprise else "machine.jsonl")
                if capture
                else None,
            )
        if capture:
            from scripts.tier1 import script_client

            async with script_client(
                "modules/bonus/B4_whats_new/python/use_case/server.py", folder / "skills.jsonl"
            ) as client:
                await load_skill(client)
    else:
        raise ValueError("Use B3 or B4; B1 and B2 have their own language runners.")
    print(f"PASS bonus {module}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module", choices=["B3", "B4"], required=True)
    parser.add_argument("--capture", action="store_true")
    args = parser.parse_args()
    asyncio.run(run(args.module, args.capture))
