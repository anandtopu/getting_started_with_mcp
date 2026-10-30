"""Build Python wheel/sdist, npm tarball and validated MCPB.
Concepts: shipping; MCP tools/list and tools/call.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
Run: uv run python modules/18_packaging/python/examples/01_build_artifacts.py
Capture the related server: uv run python scripts/tier5.py --module 18 --capture
Expected: wheel, sdist, npm, bundle inventories
"""

from common.packaging import artifacts, inspect_artifacts


def main() -> None:
    # KEY IDEA: inspect exactly what will be distributed.
    for kind, names in inspect_artifacts(artifacts()).items():
        print(f"{kind}: {len(names)} packaged files")


if __name__ == "__main__":
    main()
