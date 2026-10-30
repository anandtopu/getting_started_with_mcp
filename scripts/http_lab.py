"""Start bounded loopback test servers and record real HTTP messages and headers."""

import asyncio
import json
import os
import shutil
import socket
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import parse_qs

import httpx2 as httpx
from mcp import Client
from mcp.client.streamable_http import streamable_http_client

from common.config import ROOT
from common.pretty import redact
from common.protocol import SPEC_REVISION


@asynccontextmanager
async def running_server(path: str, extra: tuple[str, ...] = ()):
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    command = (
        [sys.executable] if path.endswith(".py") else [shutil.which("node"), "--import", "tsx"]
    )
    process = await asyncio.create_subprocess_exec(
        *command,
        str(ROOT / path),
        "--port",
        str(port),
        *extra,
        cwd=ROOT,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.PIPE,
    )
    stderr = asyncio.create_task(process.stderr.read())
    try:
        async with asyncio.timeout(15):
            while True:
                if process.returncode is not None:
                    raise RuntimeError((await stderr).decode(errors="replace"))
                try:
                    _, writer = await asyncio.open_connection("127.0.0.1", port)
                    writer.close()
                    await writer.wait_closed()
                    break
                except OSError:
                    await asyncio.sleep(0.05)
        yield f"http://127.0.0.1:{port}/mcp"
    finally:
        if process.returncode is None:
            process.terminate()
        await process.wait()
        await stderr


class CaptureTransport(httpx.AsyncBaseTransport):
    def __init__(self, path: Path | None):
        self.inner = httpx.AsyncHTTPTransport()
        self.path = path
        self.secrets = tuple(
            value
            for key, value in os.environ.items()
            if any(word in key.upper() for word in ("TOKEN", "SECRET", "PASSWORD", "API_KEY"))
        )
        if path:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps(
                    {
                        "capture_version": 1,
                        "transport": "streamable-http",
                        "command": "uv run python scripts/tier2.py --module 10 --capture",
                        "spec": SPEC_REVISION,
                    }
                )
                + "\n",
                encoding="utf-8",
            )

    def record(self, direction: str, message, **metadata) -> None:
        if self.path:
            with self.path.open("a", encoding="utf-8") as stream:
                stream.write(
                    json.dumps(
                        redact(
                            {"direction": direction, "message": message, **metadata}, self.secrets
                        ),
                        ensure_ascii=False,
                    )
                    + "\n"
                )

    async def handle_async_request(self, request):
        body = await request.aread()
        if "application/x-www-form-urlencoded" in request.headers.get("content-type", ""):
            message = {"http_form": parse_qs(body.decode())}
        else:
            message = json.loads(body) if body else None
        self.record(
            "client_to_server",
            message,
            headers=dict(request.headers),
            http_method=request.method,
        )
        response = await self.inner.handle_async_request(request)
        self.record(
            "http_response", None, status=response.status_code, headers=dict(response.headers)
        )
        inner = response.stream
        capture = self
        sse = "text/event-stream" in response.headers.get("content-type", "")

        class RecordedStream(httpx.AsyncByteStream):
            async def __aiter__(self):
                buffer = b""
                async for chunk in inner:
                    buffer += chunk
                    if sse:
                        buffer = buffer.replace(b"\r\n", b"\n")
                        while b"\n\n" in buffer:
                            event, buffer = buffer.split(b"\n\n", 1)
                            data = b"\n".join(
                                line[5:].lstrip()
                                for line in event.splitlines()
                                if line.startswith(b"data:")
                            )
                            if data:
                                capture.record("server_to_client", json.loads(data))
                    yield chunk
                if buffer and not sse:
                    try:
                        message = json.loads(buffer)
                    except ValueError:
                        message = {"http_text": buffer.decode(errors="replace")}
                    if (
                        isinstance(message, dict)
                        and "jsonrpc" not in message
                        and "http_text" not in message
                    ):
                        capture.record("http_body", None, http_json=message)
                        return
                    capture.record("server_to_client", message)

            async def aclose(self):
                await inner.aclose()

        response.stream = RecordedStream()
        return response

    async def aclose(self):
        await self.inner.aclose()


@asynccontextmanager
async def http_client(url: str, capture: Path | None = None):
    async with httpx.AsyncClient(transport=CaptureTransport(capture), timeout=10) as http:
        async with Client(
            streamable_http_client(url, http_client=http),
            mode=SPEC_REVISION,
            raise_exceptions=False,
        ) as client:
            yield client, http
