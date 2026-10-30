"""Serve validated structured output and four rich content shapes.

Concepts/spec: see ../../README.md, Key APIs and Go deeper.
Run: uv run python modules/02_first_server_tools/python/examples/02_rich_results.py
Expected: release_summary -> title/open_issues; review_assets -> image/audio/resource/link
Inspect/capture: uv run python scripts/tier1.py --module 2 --capture
"""

from common.rich_tools import rich_server


def main() -> None:
    rich_server().run()


if __name__ == "__main__":
    main()
