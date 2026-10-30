"""Local ASGI API and bounded external HTTP wrapper; external calls are opt in."""

import asyncio

import httpx2 as httpx
from fastapi import FastAPI, HTTPException
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

mock_api = FastAPI(title="Lumen internal API fixture")


@mock_api.get("/projects/{project_id}")
async def project(project_id: int) -> dict:
    if project_id not in range(1, 6):
        raise HTTPException(404, "Unknown project")
    return {"id": project_id, "name": f"Lumen project {project_id}", "service": "local fixture"}


async def fetch_json(client: httpx.AsyncClient, url: str, params: dict | None = None) -> dict:
    try:
        async with asyncio.timeout(5), client.stream("GET", url, params=params) as response:
            response.raise_for_status()
            body = bytearray()
            async for chunk in response.aiter_bytes():
                body.extend(chunk)
                if len(body) > 64000:
                    raise ToolError("API response exceeds 64 KB; request less data.")
            import json

            result = json.loads(body)
            if not isinstance(result, dict):
                raise ValueError("Expected an object")
            return result
    except (httpx.HTTPError, TimeoutError, ValueError):
        raise ToolError("API request failed; check the project or try again later.") from None


def make_server() -> MCPServer:
    server = MCPServer("Lumen API wrapper")

    @server.tool()
    async def project_details(project_id: int = 1) -> dict:
        """Call the local FastAPI mock without using the external network."""
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=mock_api), base_url="http://fixture", timeout=3
        ) as client:
            return await fetch_json(client, f"/projects/{project_id}")

    @server.tool()
    async def weather(latitude: float, longitude: float, allow_network: bool = False) -> dict:
        """Opt in to an Open-Meteo request for these coordinates; no API key is required."""
        if not allow_network:
            raise ToolError("External network is off; explicitly set allow_network=true.")
        if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
            raise ToolError("Coordinates are outside their allowed range.")
        async with httpx.AsyncClient(timeout=3, follow_redirects=False) as client:
            return await fetch_json(
                client,
                "https://api.open-meteo.com/v1/forecast",
                {"latitude": latitude, "longitude": longitude, "current": "temperature_2m"},
            )

    return server
