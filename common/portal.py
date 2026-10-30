"""Loopback approval page. A URL acknowledgement alone never grants permission."""

import asyncio
import socket
import time
from contextlib import asynccontextmanager

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, PlainTextResponse
from starlette.routing import Route

from common.retry import RetryLedger


@asynccontextmanager
async def approval_portal(ledger: RetryLedger):
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    origin = f"http://127.0.0.1:{port}"

    async def page(request: Request):
        if request.headers.get("host") != f"127.0.0.1:{port}":
            return PlainTextResponse("Invalid host", status_code=421)
        if request.headers.get("origin") not in (None, origin):
            return PlainTextResponse("Invalid origin", status_code=403)
        pending = ledger.pending.get(request.path_params["token"])
        if pending is None or pending.expires <= time.monotonic():
            return PlainTextResponse("Expired approval", status_code=410)
        if request.method == "POST":
            pending.approved = True
            return PlainTextResponse("Approved. Return to Lumen Chat and retry.")
        return HTMLResponse(
            "<h1>Lumen fixture export</h1><p>Allow exporting the synthetic report?</p>"
            '<form method="post"><button>Approve this export</button></form>',
            headers={
                "Referrer-Policy": "no-referrer",
                "Cache-Control": "no-store",
                "Content-Security-Policy": "default-src 'none'; form-action 'self'",
            },
        )

    app = Starlette(routes=[Route("/approve/{token}", page, methods=["GET", "POST"])])
    server = uvicorn.Server(uvicorn.Config(app, log_level="error", access_log=False))
    task = asyncio.create_task(server.serve(sockets=[sock]))
    try:
        async with asyncio.timeout(5):
            while not server.started:
                if task.done():
                    await task
                await asyncio.sleep(0.01)
        yield origin
    finally:
        server.should_exit = True
        await task
        sock.close()
