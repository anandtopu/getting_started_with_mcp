"""Exercise the repaired server inside the Compose isolation boundary.

Run: docker compose -f deployment/security/compose.yaml build
Then: uv run python scripts/container_check.py
"""

import asyncio

from mcp import Client, StdioServerParameters

from common.config import ROOT
from common.protocol import SPEC_REVISION
from scripts.tier3 import exercise


async def main():
    async with asyncio.timeout(60):
        async with Client(
            StdioServerParameters(
                command="docker",
                args=[
                    "compose",
                    "-f",
                    "deployment/security/compose.yaml",
                    "run",
                    "--rm",
                    "-T",
                    "repaired-lab",
                ],
                cwd=str(ROOT),
            ),
            mode=SPEC_REVISION,
            raise_exceptions=False,
        ) as client:
            await exercise(client, 12)
    print("PASS repaired lab: unprivileged, read-only container with network disabled")


if __name__ == "__main__":
    asyncio.run(main())
