"""Launch allow-listed lesson servers; callers own their async context lifetime."""

import shutil
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters
from mcp_types import DiscoverResult

from common.config import HELP, ROOT
from common.protocol import SPEC_REVISION

SERVERS = {
    "notes": "02_first_server_tools/python/use_case/main.py",
    "wiki": "03_resources/python/use_case/main.py",
    "prompts": "04_prompts/python/use_case/main.py",
    "raw": "01_architecture_wire/python/examples/02_raw_server.py",
}


async def discover(client: Client) -> DiscoverResult:
    """A pinned Python client skips probing; explicitly fetch real capabilities."""
    result = DiscoverResult.model_validate(await client.session.send_discover(SPEC_REVISION))
    client.session.adopt(result)
    return result


def connection(alias: str, capture: Path | None = None) -> Client:
    if alias == "files":
        command = shutil.which("node")
        script = ROOT / "node_modules/@modelcontextprotocol/server-filesystem/dist/index.js"
        if not command or not script.exists():
            raise RuntimeError(f"Run npm ci to install the local filesystem server. {HELP}")
        args = [str(script), str(ROOT / "data/files")]
    else:
        command = sys.executable
        args = [str(ROOT / "modules" / SERVERS[alias])]
    if capture:
        args = [str(ROOT / "scripts/wiretap.py"), "--capture", str(capture), "--", command, *args]
        command = sys.executable
    return Client(
        StdioServerParameters(command=command, args=args, cwd=str(ROOT)),
        mode=SPEC_REVISION,
        read_timeout_seconds=10,
        raise_exceptions=False,
    )
