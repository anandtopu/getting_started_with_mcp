"""Generate ready-to-paste host configs with absolute paths for this checkout.

Run: uv run python scripts/host_configs.py --module 2
Output: .runtime/host_configs/02_first_server_tools/{host}.json
No credentials are embedded. Copy the relevant entries into existing host config.
"""

import argparse
import json
import shutil
from copy import deepcopy
from pathlib import Path

from common.config import HELP, ROOT
from common.connections import SERVERS
from scripts.tier1 import MODULES
from scripts.tier2 import MODULES as TIER2_MODULES
from scripts.tier3 import MODULES as TIER3_MODULES
from scripts.tier4 import MODULES as TIER4_MODULES

MODULES = MODULES + TIER2_MODULES + TIER3_MODULES + TIER4_MODULES


def configurations(index: int) -> dict:
    uv, node = shutil.which("uv"), shutil.which("node")
    if not uv or not node:
        raise RuntimeError(f"Install uv and Node, then reopen the terminal. {HELP}")
    if index >= 14:
        entry = {
            "command": uv,
            "args": [
                "--directory",
                str(ROOT),
                "run",
                "--frozen",
                "--extra",
                "http",
                "--extra",
                "auth",
                "python",
                str(ROOT / "modules" / MODULES[index] / "python/use_case/server.py"),
            ],
        }
        return {
            host: {
                "servers" if host == "vscode" else "mcpServers": {
                    "lumen-tier4": {
                        **deepcopy(entry),
                        **({"type": "stdio"} if host == "vscode" else {}),
                    }
                }
            }
            for host in ["claude-desktop", "claude-code", "vscode", "cursor"]
        }
    aliases = {
        0: ["files"],
        1: ["raw"],
        2: ["notes"],
        3: ["wiki"],
        4: ["prompts"],
        5: ["notes", "wiki", "prompts"],
        6: ["notes", "wiki", "files"],
        7: ["issues", "analytics"],
        8: ["reports"],
        9: ["issues"],
        10: ["wiki", "issues"],
        11: ["issues"],
        12: ["notes"],
        13: ["notes"],
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
                    *(["--extra", "http"] if index >= 7 else []),
                    "python",
                    str(ROOT / "modules" / SERVERS[alias]),
                ],
            }
    configs = {
        host: {
            "servers" if host == "vscode" else "mcpServers": {
                name: {**deepcopy(entry), **({"type": "stdio"} if host == "vscode" else {})}
                for name, entry in servers.items()
            }
        }
        for host in ["claude-desktop", "claude-code", "vscode", "cursor"]
    }
    if index in {12, 13}:
        for config in configs.values():
            entries = config.get("servers", config.get("mcpServers"))
            entry = entries.pop("notes")
            entry["args"][-1] = str(ROOT / "modules" / MODULES[index] / "python/use_case/server.py")
            if index == 13:
                entry["args"][4:4] = ["--extra", "observability"]
            entries["lumen-lab" if index == 12 else "lumen-quality"] = entry
    if index in {10, 11}:
        for host in ["claude-code", "vscode", "cursor"]:
            configs[host] = {
                "servers" if host == "vscode" else "mcpServers": {
                    "lumen-remote": {
                        "url": f"http://127.0.0.1:{8001 if index == 11 else 8000}/mcp",
                        **({"type": "http"} if host != "cursor" else {}),
                    }
                }
            }
    if index == 11:
        configs["claude-desktop"] = {"mcpServers": {}}
    return configs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module", type=int, choices=range(18), default=2)
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
