"""Run native TypeScript OAuth providers against the local synthetic issuer.
Run: uv run python scripts/ts_auth.py [--enterprise]
"""

import argparse
import asyncio
import json
import shutil

from common.auth_tokens import JWTVerifier
from common.config import ROOT
from common.machine_auth import MachineAuthority
from common.secured_issues import make_app
from scripts.auth_lab import running_app


async def run(enterprise=False):
    authority = MachineAuthority()

    def issuer(url):
        authority.issuer = url
        return authority.app()

    async with running_app(issuer):

        def resource(url):
            authority.resource = url + "/mcp"
            return make_app(
                JWTVerifier(
                    authority.issuer, authority.resource, authority.issuer + "/jwks", authority.jwks
                )
            )

        async with running_app(resource):
            node = shutil.which("node")
            if not node:
                raise RuntimeError("Install Node; run scripts/check_env.py.")
            config = dict(
                issuer=authority.issuer, resource=authority.resource, secret=authority.secret
            )
            if enterprise:
                config["assertion"] = await authority.assertion(
                    authority.issuer, authority.resource
                )
            process = await asyncio.create_subprocess_exec(
                node,
                "--import",
                "tsx",
                "modules/bonus/B4_whats_new/typescript/auth_client.ts",
                cwd=ROOT,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(json.dumps(config).encode()), 30
                )
            except BaseException:
                if process.returncode is None:
                    process.kill()
                    await process.wait()
                raise
            if process.returncode:
                raise RuntimeError(stderr.decode().replace(authority.secret, "[REDACTED]"))
            assert authority.exchanges == 1
            return json.loads(stdout)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--enterprise", action="store_true")
    print(asyncio.run(run(parser.parse_args().enterprise)))
