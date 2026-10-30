"""Check local runtimes without contacting a model.

Concepts/spec: see ../../README.md, Key APIs and Go deeper.
Run: uv run python modules/00_setup/python/examples/02_environment.py
Expected: Python/Node/uv versions, optional services may be absent
Inspect/capture: uv run python scripts/tier1.py --module 0 --capture
"""

from scripts.check_env import main

if __name__ == "__main__":
    main()
