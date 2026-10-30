"""Generate ready-to-paste host configs with absolute paths for this checkout.

Run: uv run python scripts/host_configs.py --module 2
Output: .runtime/host_configs/02_first_server_tools/{host}.json
No credentials are embedded. Copy the relevant entries into existing host config.
"""

import argparse
import json
import shutil
from pathlib import Path

from common.config import HELP, ROOT
from common.connections import SERVERS
from scripts.tier1 import MODULES


def configurations(index: int) -> dict:
    uv, node = shutil.which("uv"), shutil.which("node")
    if not uv or not node:
        raise RuntimeError(f"Install uv and Node, then reopen the terminal. {HELP}")
    aliases = {
        0: ["files"],
        1: ["raw"],
        2: ["notes"],
        3: ["wiki"],
        4: ["prompts"],
        5: ["notes", "wiki", "prompts"],
        6: ["notes", "wiki", "files"],
    }[index]
    servers = {}
    for alias in aliases:
        if alias == "files":
            servers[alias] = {
                "command": node,
                "args": [
                    str(
                        ROOT / "node_modules/@modelcontextprotocol/server-filesystem/dist/index.js"
                    ),
                    str(ROOT / "data/files"),
                ],
            }
        else:
            servers[alias] = {
                "command": uv,
                "args": [
                    "--directory",
                    str(ROOT),
                    "run",
                    "--frozen",
                    "python",
                    str(ROOT / "modules" / SERVERS[alias]),
                ],
            }
    return {
        host: {
            "servers" if host == "vscode" else "mcpServers": {
                name: {**entry, **({"type": "stdio"} if host == "vscode" else {})}
                for name, entry in servers.items()
            }
        }
        for host in ["claude-desktop", "claude-code", "vscode", "cursor"]
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module", type=int, choices=range(7), default=2)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or ROOT / ".runtime/host_configs" / MODULES[args.module]
    output.mkdir(parents=True, exist_ok=True)
    for host, config in configurations(args.module).items():
        path = output / f"{host}.json"
        path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
        print(path)


if __name__ == "__main__":
    main()
