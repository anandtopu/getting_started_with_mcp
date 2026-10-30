"""Compare a fixture authorization flaw with the repaired server.

Run: uv run python modules/12_security/python/examples/03_defense_lab.py
Expected: PASS with the measured checks below.
"""

import asyncio
import runpy

from mcp import Client

from common.config import ROOT
from common.defenses import make_server


async def main() -> None:
    vulnerable = runpy.run_path(str(ROOT / "data/security/vulnerable_server.py"))["server"]
    async with Client(vulnerable) as client:
        assert (await client.call_tool("fixture_salary", {"employee_id": 2})).structured_content[
            "salary"
        ]
    async with Client(make_server(), raise_exceptions=False) as client:
        assert (await client.call_tool("fixture_salary", {"employee_id": 2})).is_error
        assert not (await client.call_tool("fixture_salary", {"employee_id": 1})).is_error
    print("PASS reproduced synthetic leak; repair denies another employee")


if __name__ == "__main__":
    asyncio.run(main())
