"""Exercise the native TypeScript authorization-code client with the local issuer.

Run: uv run python scripts/ts_oauth.py
Expected: a successful read, rejected issuer mix-up and rejected write scope.
"""

import asyncio
import json
import shutil

from common.config import ROOT
from scripts.auth_lab import auth_stack


async def run():
    node = shutil.which("node")
    if not node:
        raise RuntimeError("Install Node; run uv run python scripts/check_env.py.")
    async with auth_stack() as authority:
        process = await asyncio.create_subprocess_exec(
            node,
            "--import",
            "tsx",
            "modules/11_authorization/typescript/oauth_client.ts",
            cwd=ROOT,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            output, _ = await asyncio.wait_for(
                process.communicate(
                    json.dumps(
                        {
                            "issuer": authority.issuer,
                            "resource": authority.resource,
                        }
                    ).encode()
                ),
                30,
            )
        except BaseException:
            if process.returncode is None:
                process.kill()
                await process.wait()
            raise
        if process.returncode:
            raise RuntimeError("Native OAuth fixture failed; run its targeted regression test.")
        return json.loads(output)


if __name__ == "__main__":
    print(asyncio.run(run()))
