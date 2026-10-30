"""Run the SDK-free JSON-RPC dispatcher; read common/raw_server.py first.

Concepts/spec: see ../../README.md, Key APIs and Go deeper.
Run: uv run python modules/01_architecture_wire/python/examples/02_raw_server.py
Expected: waits for one JSON request per line; protocol output only
Inspect/capture: uv run python scripts/tier1.py --module 1 --capture
"""

from common.raw_server import main

if __name__ == "__main__":
    main()
