"""Verify the web host against the deployed issues server using a temporary in-memory token.
Run: uv run python scripts/keycloak_check.py --deployed
"""

import asyncio
import json
import os
import tempfile
from pathlib import Path

import httpx2 as httpx

from common.web_chat import make_web_app
from scripts.auth_lab import running_app


async def web_remote_check(token, resource="http://127.0.0.1:8001/mcp"):
    key = "LUMEN_SHIPPING_TEST_TOKEN"
    previous = os.environ.get(key)
    os.environ[key] = token
    try:
        with tempfile.TemporaryDirectory() as folder:
            config = Path(folder) / "host.json"
            config.write_text(
                json.dumps(
                    {
                        "servers": [
                            {
                                "alias": "issues",
                                "profile": "issues",
                                "url": resource,
                                "token_env": key,
                            }
                        ]
                    }
                )
            )
            async with running_app(lambda origin: make_web_app(origin, config)) as origin:
                async with httpx.AsyncClient(base_url=origin, timeout=30) as client:
                    response = await client.post("/api/session", headers={"X-Lumen-Client": "web"})
                    response.raise_for_status()
                    client.headers["X-CSRF-Token"] = response.json()["csrf"]
                    response = await client.post(
                        "/api/chat", json={"prompt": "Read deployed issue"}
                    )
                    response.raise_for_status()
                    async with asyncio.timeout(30):
                        while True:
                            state = (await client.get("/api/state")).json()
                            if state.get("pending"):
                                response = await client.post(
                                    "/api/answer",
                                    json={"id": state["pending"]["id"], "action": "accept"},
                                )
                                response.raise_for_status()
                            if state["status"] in {"complete", "error"}:
                                break
                            await asyncio.sleep(0.1)
                    assert state["status"] == "complete", state
                    results = [e for e in state["events"] if e["type"] == "tool_result"]
                    assert len(results) == 1 and not results[0]["result"].get("isError")
                    assert "access_token" not in json.dumps(state) and token not in json.dumps(
                        state
                    )
                    (await client.post("/api/close")).raise_for_status()
        print("PASS deployed web host: explicit approval -> proxy -> OAuth issues -> result")
    finally:
        if previous is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = previous
