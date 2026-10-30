"""Run all delivered examples with deadlines. No external network or model calls.

Run: uv run python scripts/run_all_examples.py [--capture-dir docs/wire]
Expected: one passed foundation server in Phase 2; manifest grows with lessons.
"""

import argparse
import asyncio
import json
import subprocess
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters

from common.config import ROOT
from common.protocol import SPEC_REVISION


async def smoke(capture_dir: Path | None = None) -> int:
    manifest = json.loads((ROOT / "scripts/examples.json").read_text())
    for entry in manifest["servers"]:
        args = [str(ROOT / entry["path"])]
        if capture_dir:
            args = [
                str(ROOT / "scripts/wiretap.py"),
                "--timeout",
                "30",
                "--capture",
                str(capture_dir / (Path(entry["path"]).stem + ".jsonl")),
                "--",
                sys.executable,
                *args,
            ]
        async with (
            asyncio.timeout(30),
            Client(
                StdioServerParameters(command=sys.executable, args=args, cwd=str(ROOT)),
                mode=SPEC_REVISION,
                read_timeout_seconds=10,
            ) as client,
        ):
            assert (await client.list_tools()).tools
            assert (await client.list_resources()).resources
            await client.list_resource_templates()
            assert (await client.list_prompts()).prompts
            await client.read_resource("lumen://dataset/summary")
            await client.get_prompt("explain_dataset")
            result = await client.call_tool(entry["tool"], entry["arguments"])
            assert not result.is_error and result.structured_content == entry["expected"]
        print(f"PASS {entry['path']}")
    for entry in manifest["scripts"]:
        subprocess.run(
            [sys.executable, str(ROOT / entry["path"]), *entry["arguments"]],
            cwd=ROOT,
            check=True,
            timeout=30,
        )
    return len(manifest["servers"]) + len(manifest["scripts"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture-dir", type=Path)
    args = parser.parse_args()
    print(f"Checked {asyncio.run(smoke(args.capture_dir))} delivered examples.")


if __name__ == "__main__":
    main()
