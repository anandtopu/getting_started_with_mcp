"""Run a real stdio client; reproduce and diagnose stdout corruption.

Run: uv run python modules/13_testing_observability/python/examples/02_inspector_stdout.py
Expected: PASS with the measured checks below.
"""

import asyncio
import json
import subprocess
import sys

from common.quality import validate_stdout
from scripts.tier3 import run


async def main() -> None:
    await run(13)
    # The broken child is isolated; the invalid line never reaches a normal server.
    broken = subprocess.run(
        [sys.executable, "-c", "print('debug startup')"],
        capture_output=True,
        text=True,
        timeout=3,
        check=True,
    )
    try:
        validate_stdout(broken.stdout)
    except ValueError as error:
        print(str(error))
    else:
        raise AssertionError("Expected corrupted stdout rejection")
    assert validate_stdout(json.dumps({"jsonrpc": "2.0", "id": 1, "result": {}})) == 1
    print("PASS stdio smoke and corruption diagnostic; see Inspector commands in README")


if __name__ == "__main__":
    asyncio.run(main())
