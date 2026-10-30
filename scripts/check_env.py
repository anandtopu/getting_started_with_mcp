"""Check prerequisites without installing anything or contacting a model.

Run: uv run python scripts/check_env.py [--strict]
Expected: required Python/Node/uv/npm checks and optional Docker/Ollama status.
"""

import argparse
import importlib.metadata
import os
import shutil
import subprocess
import sys


def check() -> bool:
    ok = (3, 12) <= sys.version_info[:2] < (3, 15)
    print(f"{'OK' if ok else 'MISSING'} Python {sys.version.split()[0]} (need 3.12-3.14)")
    for command in ("uv", "node", "npm", "npx", "ollama", "docker"):
        path = shutil.which(
            command + ".cmd" if os.name == "nt" and command in {"npm", "npx"} else command
        )
        required = command in {"uv", "node", "npm", "npx"}
        valid = path is not None
        version = "not installed"
        if path:
            try:
                result = subprocess.run(
                    [path, "--version"], capture_output=True, text=True, timeout=5, check=False
                )
                version = (
                    result.stdout.strip().splitlines()[0] if result.stdout.strip() else "unknown"
                )
                valid = result.returncode == 0
                if command == "node":
                    valid = valid and version.lstrip("v").split(".")[0] in {"24", "26"}
            except (OSError, subprocess.TimeoutExpired):
                valid, version = False, "could not run"
        print(f"{'OK' if valid else 'MISSING' if required else 'OPTIONAL'} {command}: {version}")
        if required:
            ok &= valid
    for package in ("mcp", "pydantic", "pypdf"):
        try:
            print(f"OK {package} {importlib.metadata.version(package)}")
        except importlib.metadata.PackageNotFoundError:
            print(f"MISSING {package}: run uv sync")
            ok = False
    for key in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY"):
        print(f"OPTIONAL {key}: {'set' if os.environ.get(key) else 'not set'}")
    print("Keys and model services are unnecessary for the default offline tests.")
    return ok


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    ok = check()
    if args.strict and not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
