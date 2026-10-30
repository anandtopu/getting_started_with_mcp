"""A deterministic multi-server command-line query; no model required.

Concepts/spec: see ../../README.md, Key APIs and Go deeper.
Run: uv run python modules/05_first_client/python/examples/03_cli_and_changes.py
Expected: matching notes plus a wiki page; --help lists query arguments
Inspect/capture: uv run python scripts/tier1.py --module 5 --capture
"""

from common.workspace_query import main

if __name__ == "__main__":
    main()
