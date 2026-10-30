"""An SDK-free teaching server implementing a deliberately small current MCP surface."""

import json
import sys

VERSION = "2026-07-28"
META = "io.modelcontextprotocol/"
TOOL = {
    "name": "directory_count",
    "description": "Count the synthetic employee sample.",
    "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    "annotations": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
}


def dispatch(message: object) -> dict | None:
    identifier = message.get("id") if isinstance(message, dict) else None

    def error(code: int, text: str, data: dict | None = None) -> dict:
        detail = {"code": code, "message": text}
        if data is not None:
            detail["data"] = data
        return {"jsonrpc": "2.0", "id": identifier, "error": detail}

    if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
        return error(-32600, "Invalid Request")
    if not isinstance(message.get("method"), str):
        return error(-32600, "Invalid Request")
    if "id" not in message:
        return None  # Notifications never get a response.
    if isinstance(identifier, bool) or not isinstance(identifier, (int, str)):
        identifier = None
        return error(-32600, "Invalid request ID")
    params = message.get("params", {})
    if not isinstance(params, dict) or not isinstance(params.get("_meta", {}), dict):
        return error(-32602, "Invalid Params")
    meta = params.get("_meta", {})
    if meta.get(META + "protocolVersion") != VERSION:
        return error(
            -32022,
            "Unsupported protocol version",
            {"supported": [VERSION], "requested": str(meta.get(META + "protocolVersion"))},
        )
    if not isinstance(meta.get(META + "clientCapabilities"), dict):
        return error(-32602, "Client capabilities must be an object")
    method = message["method"]
    result = {
        "resultType": "complete",
        "_meta": {META + "serverInfo": {"name": "Lumen raw directory", "version": "1.0"}},
    }
    if method in {"server/discover", "tools/list"}:
        result.update(ttlMs=0, cacheScope="private")
    if method == "server/discover":
        result.update(supportedVersions=[VERSION], capabilities={"tools": {}})
    elif method == "tools/list":
        result["tools"] = [TOOL]
    elif method == "tools/call":
        if params.get("name") != TOOL["name"] or params.get("arguments", {}) != {}:
            return error(-32602, "Unknown tool or invalid arguments")
        result.update(content=[{"type": "text", "text": "80 synthetic employees"}], isError=False)
    else:
        return error(-32601, "Method not found")
    return {"jsonrpc": "2.0", "id": identifier, "result": result}


def main() -> None:
    for line in sys.stdin:
        try:
            result = dispatch(json.loads(line))
        except ValueError:
            result = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Parse error"},
            }
        if result is not None:
            sys.stdout.write(json.dumps(result) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
