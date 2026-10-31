"""Build and test installed uvx/npx packages. --prepare permits dependency downloads.
Run: uv run python scripts/package_lab.py --prepare (once), then without --prepare.
"""

import argparse
import asyncio
import json

from common.packaging import smoke_packages


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    args = parser.parse_args()
    print(json.dumps(asyncio.run(smoke_packages(offline=not args.prepare)), indent=2))
    print("PASS installed uvx/npx packages and extracted MCPB server outside checkout")


if __name__ == "__main__":
    main()
