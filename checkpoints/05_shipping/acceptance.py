"""Tier 5 release rehearsal; no publication or model calls.
Run: uv run python checkpoints/05_shipping/acceptance.py [--container]
--container additionally exercises the locally built lumen-notes-course:1.0.0 image.
"""

import argparse
import asyncio
import shutil

from mcp import Client, StdioServerParameters

from common.packaging import artifacts, inspect_artifacts
from common.protocol import SPEC_REVISION
from common.registry import validate_metadata
from scripts.tier5 import run


async def main(container=False, docker_context=None):
    inspect_artifacts(artifacts())
    validate_metadata()
    for module in range(18, 22):
        await run(module)
    if container:
        async with Client(
            StdioServerParameters(
                command=shutil.which("docker"),
                args=[
                    *(["--context", docker_context] if docker_context else []),
                    "run",
                    "--rm",
                    "-i",
                    "--network",
                    "none",
                    "--read-only",
                    "--cap-drop",
                    "ALL",
                    "lumen-notes-course:1.0.0",
                ],
                env={"LUMEN_NOTES_READ_ONLY": "true"},
            ),
            mode=SPEC_REVISION,
            read_timeout_seconds=20,
        ) as client:
            assert [t.name for t in (await client.list_tools()).tools] == ["search_notes"]
            assert not (await client.call_tool("search_notes", {"query": "release"})).is_error
        print("PASS packaged notes container")
    print("PASS Tier 5 shipping checkpoint")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--container", action="store_true")
    parser.add_argument("--docker-context", help="Use an explicitly selected local Docker context")
    args = parser.parse_args()
    asyncio.run(main(args.container, args.docker_context))
