"""Smoke every delivered stdio server with the installed Inspector CLI.

Run: uv run python scripts/inspector_smoke.py
Server capabilities determine which primitive lists apply; unsupported lists are
not an error. This checks protocol stdout as well as Inspector compatibility.
"""

import json
import shutil
import subprocess
import sys

from common.config import ROOT


def main() -> None:
    inspector = ROOT / "node_modules/@modelcontextprotocol/inspector/clients/cli/build/index.js"
    manifest = json.loads((ROOT / "scripts/examples.json").read_text())
    for entry in manifest["servers"]:
        command = [sys.executable, str(ROOT / entry["path"])]
        if entry["path"].endswith(".ts"):
            command = [shutil.which("node"), "--import", "tsx", str(ROOT / entry["path"])]
        for method in entry["lists"]:
            result = subprocess.run(
                [
                    shutil.which("node"),
                    str(inspector),
                    *command,
                    "--protocol-era",
                    "modern",
                    "--method",
                    method,
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
            )
            if result.returncode:
                raise RuntimeError(f"Inspector {entry['path']} {method}: {result.stderr}")
            json.loads(result.stdout)  # Fail if stdout contains diagnostics or non-JSON output.
            print(f"PASS Inspector {entry['path']} {method}")


if __name__ == "__main__":
    main()
