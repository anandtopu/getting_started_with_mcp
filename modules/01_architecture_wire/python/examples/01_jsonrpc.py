"""Correlate a request ID and distinguish a notification from an error.

Concepts/spec: see ../../README.md, Key APIs and Go deeper.
Run: uv run python modules/01_architecture_wire/python/examples/01_jsonrpc.py
Expected: id=7, notification None, error -32601
Inspect/capture: uv run python scripts/tier1.py --module 1 --capture
"""

import json

from common.raw_server import META, VERSION, dispatch


def main() -> None:
    meta = {META + "protocolVersion": VERSION, META + "clientCapabilities": {}}
    request = {"jsonrpc": "2.0", "id": 7, "method": "tools/list", "params": {"_meta": meta}}
    print(json.dumps(dispatch(request), indent=2))
    print("Notification response:", dispatch({"jsonrpc": "2.0", "method": "ping"}))
    request["method"] = "missing/method"
    print(json.dumps(dispatch(request)))


if __name__ == "__main__":
    main()
