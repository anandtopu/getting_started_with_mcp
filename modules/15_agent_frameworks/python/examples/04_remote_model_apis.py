"""Inspect remote MCP request bodies; --live needs a deployed server and model credentials.
Run: uv run python modules/15_agent_frameworks/python/examples/04_remote_model_apis.py
Wire: uv run python scripts/tier4.py --module 15 --capture
Expected: PASS and real synthetic Lumen results.
Spec: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
"""

import argparse
import asyncio
import json

from common.llm import remote_mcp
from common.remote_models import request_body


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--url", default="https://mcp.lumen.example/mcp")
    args = parser.parse_args()
    if args.live:
        print(await remote_mcp(args.url))
    else:
        for provider in ["openai", "anthropic", "gemini"]:
            print(
                provider,
                json.dumps(request_body(provider, "select-via-LLM_MODEL", args.url), indent=2),
            )
        print("PASS request construction only; no provider or illustrative endpoint was contacted.")


if __name__ == "__main__":
    asyncio.run(main())
