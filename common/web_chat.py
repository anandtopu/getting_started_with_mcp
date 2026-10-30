"""Local, single-user Lumen Chat v4 web host. No credentials are sent to the browser.
Run: uv run python -m common.web_chat --port 8766
"""

import argparse
import asyncio
import os
import secrets
import time
from contextlib import asynccontextmanager
from urllib.parse import urlsplit

from dotenv import dotenv_values
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from jsonschema import Draft202012Validator, ValidationError
from pydantic import BaseModel, ConfigDict, Field

from common.config import ROOT, Settings
from common.llm import create_tool_model
from common.production_host import Connection, ProductionHost, load_host_config
from common.tool_formats import ToolCall, Turn

UI = ROOT / "common/web_ui"
CONFIG = ROOT / "modules/21_production_hosts/host_configs/lumen-chat.json"
KEYS = {"openai": "OPENAI_API_KEY", "anthropic": "ANTHROPIC_API_KEY", "gemini": "GEMINI_API_KEY"}


def settings_for(provider, model=""):
    values = {**dotenv_values(ROOT / ".env"), **os.environ}
    if provider == "fake":
        return Settings()
    if provider not in {*KEYS, "ollama"}:
        raise ValueError("Choose a supported provider.")
    selected = (
        model
        or values.get(provider.upper() + "_MODEL")
        or (values.get("LLM_MODEL") if values.get("LLM_PROVIDER") == provider else None)
    )
    key = values.get(KEYS.get(provider, ""), "")
    if not selected or selected == "fixture" or (provider in KEYS and not key):
        raise ValueError("Configure the selected provider's model and key on the server first.")
    return Settings(
        provider=provider,
        model=selected,
        api_key=key,
        ollama_host=values.get("OLLAMA_HOST", "http://127.0.0.1:11434"),
        max_tokens=512,
    )


def fixture_turns(prompt):
    text = prompt.casefold()
    if "deployed" in text:
        actions = [("issues__read_issue", {"issue_id": 1})]
    elif "report" in text:
        actions = [("gateway__quarterly_report", {"quarter": "Q1", "ask_details": True})]
    elif "dashboard" in text:
        actions = [("gateway__analytics_dashboard", {})]
    elif "close" in text:
        actions = [("issues__bulk_close", {"issue_ids": [1, 2]})]
    elif "note" in text:
        actions = [
            (
                "notes__create_note",
                {"title": "Release follow-up", "body": "Review the synthetic release checklist."},
            )
        ]
    else:
        actions = [
            ("gateway__workflow__triage_week", {"week_start": "2026-07-13"}),
            ("gateway__workflow__draft_status", {"week_start": "2026-07-13"}),
        ]
    return [
        *[Turn(calls=[ToolCall(str(i), name, args)]) for i, (name, args) in enumerate(actions)],
        Turn("Workflow complete. Review the tool evidence below; no model service was contacted."),
    ]


class Session:
    def __init__(self, config):
        self.config, self.csrf = config, secrets.token_urlsafe(32)
        self.expires = time.monotonic() + 1800
        self.connections, self.events = {}, []
        self.pending, self.response, self.run = None, None, None
        self.status, self.app, self.app_html = "ready", None, ""
        self.app_connection, self.app_tool = None, None

    def emit(self, kind, value):
        self.events.append({"type": kind, **value})
        self.events = self.events[-120:]

    async def start(self):
        try:
            for config in self.config.servers:
                self.connections[config.alias] = await Connection(config, self.emit).start()
        except BaseException:
            await self.close()
            raise

    async def question(self, kind, data):
        if self.response and not self.response.done():
            raise RuntimeError("Another decision is already pending.")
        self.response = asyncio.get_running_loop().create_future()
        self.pending = {"id": secrets.token_urlsafe(16), "kind": kind, **data}
        self.status = "waiting"
        try:
            # Human deliberation has its own generous bound, outside network deadlines.
            async with asyncio.timeout(120):
                return await self.response
        finally:
            self.pending, self.response = None, None
            self.status = "running"

    async def approve(self, name, details):
        answer = await self.question("approval", {"tool": name, **details})
        return answer["action"] == "accept"

    async def ask(self, params):
        if params.get("mode", "form") != "form":
            self.emit(
                "error",
                {
                    "message": "URL input is not opened automatically. "
                    "Use a configured trusted flow."
                },
            )
            return {"action": "decline"}
        schema = params.get("requestedSchema", {})
        if schema.get("type") != "object" or len(schema.get("properties", {})) > 8:
            raise ValueError("Unsupported input form.")
        if any(
            field.get("type") not in {"boolean", "string", "number", "integer"}
            for field in schema.get("properties", {}).values()
        ):
            raise ValueError("This host accepts small scalar forms only.")
        return await self.question(
            "input", {"message": params.get("message", "User input required"), "schema": schema}
        )

    def answer(self, question_id, action, content):
        if not self.pending or self.pending["id"] != question_id or not self.response:
            raise ValueError("Decision expired or was already answered.")
        if action not in {"accept", "decline", "cancel"}:
            raise ValueError("Choose accept, decline or cancel.")
        if self.pending["kind"] == "input" and action == "accept":
            Draft202012Validator(self.pending["schema"]).validate(content)
        if self.response.done():
            raise ValueError("Decision was already answered.")
        self.response.set_result(
            {"action": action, **({"content": content} if action == "accept" else {})}
        )

    def show_app(self, connection, tool, html, result):
        self.app_connection, self.app_tool, self.app_html = connection, tool, html
        self.app = {"id": secrets.token_urlsafe(16), "result": result, "title": "Lumen analytics"}

    async def chat(self, prompt, settings):
        self.status = "running"
        self.emit("user", {"text": prompt})
        try:
            host = ProductionHost(
                self.connections, self.approve, self.ask, self.emit, self.show_app
            )
            model = create_tool_model(
                prompt,
                settings,
                turns=fixture_turns(prompt) if settings.provider == "fake" else None,
            )
            async with asyncio.timeout(240):
                result = await host.run(model)
            self.emit("assistant", {"text": result})
            self.status = "complete"
        except asyncio.CancelledError:
            self.status = "cancelled"
            self.emit(
                "cancelled",
                {
                    "message": "Operation stopped. "
                    "Confirm any uncertain remote outcome before retrying."
                },
            )
        except Exception:
            self.status = "error"
            self.emit(
                "error",
                {
                    "message": "The workflow could not finish. "
                    "Check configuration and connection status."
                },
            )
        finally:
            self.pending = None

    async def cancel(self):
        if self.run and not self.run.done():
            self.run.cancel()
            await asyncio.gather(self.run, return_exceptions=True)

    async def close(self):
        await self.cancel()
        for connection in self.connections.values():
            await connection.close()
        self.connections.clear()

    def snapshot(self):
        return {
            "status": self.status,
            "events": self.events,
            "pending": self.pending,
            "connections": [c.info for c in self.connections.values()],
            "app": self.app,
        }


class Message(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prompt: str = Field(min_length=1, max_length=3000)
    provider: str = "fake"
    model: str = Field(default="", max_length=100)


class Answer(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(max_length=100)
    action: str
    content: dict = Field(default_factory=dict)


class WebBoundary:
    def __init__(self, app, origin):
        self.app, self.origin = app, origin
        self.host = urlsplit(origin).netloc.encode()

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        headers = dict(scope["headers"])
        if headers.get(b"host") != self.host:
            return await Response(status_code=421)(scope, receive, send)
        if (
            headers.get(b"origin") not in {None, self.origin.encode()}
            or headers.get(b"sec-fetch-site") == b"cross-site"
        ):
            return await Response(status_code=403)(scope, receive, send)
        body = b""
        while True:
            event = await receive()
            if event["type"] == "http.disconnect":
                return
            body += event.get("body", b"")
            if len(body) > 64000:
                return await Response(status_code=413)(scope, receive, send)
            if not event.get("more_body"):
                break
        delivered = False

        async def replay():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": body, "more_body": False}
            return await receive()

        async def secure(message):
            if message["type"] == "http.response.start":
                extra = [
                    (b"x-content-type-options", b"nosniff"),
                    (b"referrer-policy", b"no-referrer"),
                    (b"cache-control", b"no-store"),
                ]
                if not scope["path"].startswith("/api/app-view/"):
                    extra.append(
                        (
                            b"content-security-policy",
                            b"default-src 'self'; script-src 'self'; style-src 'self'; "
                            b"frame-src 'self'; object-src 'none'; base-uri 'none'; "
                            b"frame-ancestors 'none'",
                        )
                    )
                message["headers"] = [*message.get("headers", []), *extra]
            await send(message)

        await self.app(scope, replay, secure)


def make_web_app(origin="http://127.0.0.1:8766", config_path=CONFIG):
    sessions = {}
    config = load_host_config(config_path)

    @asynccontextmanager
    async def lifespan(app):
        yield
        for session in sessions.values():
            await session.close()

    app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
    app.state.sessions = sessions

    def session_for(request, mutation=False):
        value = sessions.get(request.cookies.get("lumen_session"))
        if value is None or value.expires <= time.monotonic():
            raise HTTPException(401, "Session expired. Reload to reconnect.")
        if mutation and not secrets.compare_digest(
            request.headers.get("x-csrf-token", ""), value.csrf
        ):
            raise HTTPException(403, "Request verification failed.")
        return value

    @app.get("/")
    async def index():
        return FileResponse(UI / "index.html")

    @app.post("/api/session")
    async def create_session(request: Request):
        if request.headers.get("x-lumen-client") != "web":
            raise HTTPException(403, "Use the local web interface.")
        old = request.cookies.get("lumen_session")
        if old in sessions and sessions[old].expires > time.monotonic():
            return {"csrf": sessions[old].csrf, **sessions[old].snapshot()}
        for sid, old_session in list(sessions.items()):
            if old_session.expires <= time.monotonic():
                removed = sessions.pop(sid, None)
                if removed:
                    await removed.close()
        if len(sessions) >= 4:
            raise HTTPException(429, "Close an existing session or wait for expiry.")
        session = Session(config)
        sid = secrets.token_urlsafe(32)
        sessions[sid] = session
        try:
            await session.start()
        except BaseException:
            sessions.pop(sid, None)
            raise
        response = JSONResponse({"csrf": session.csrf, **session.snapshot()})
        response.set_cookie(
            "lumen_session",
            sid,
            httponly=True,
            samesite="strict",
            max_age=1800,
            secure=origin.startswith("https:"),
        )
        return response

    @app.get("/api/state")
    async def state(request: Request):
        return session_for(request).snapshot()

    @app.post("/api/chat", status_code=202)
    async def chat(request: Request, message: Message):
        session = session_for(request, True)
        if session.run and not session.run.done():
            raise HTTPException(409, "Finish or cancel the current workflow first.")
        try:
            settings = settings_for(message.provider, message.model)
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from None
        session.run = asyncio.create_task(session.chat(message.prompt, settings))
        return {"accepted": True}

    @app.post("/api/answer")
    async def answer(request: Request, answer: Answer):
        try:
            session_for(request, True).answer(answer.id, answer.action, answer.content)
        except (ValueError, ValidationError) as exc:
            raise HTTPException(400, "Answer is invalid, expired or already used.") from exc
        return {"accepted": True}

    @app.post("/api/cancel")
    async def cancel(request: Request):
        await session_for(request, True).cancel()
        return {"cancelled": True}

    @app.post("/api/reconnect")
    async def reconnect(request: Request):
        session = session_for(request, True)
        if session.run and not session.run.done():
            raise HTTPException(409, "Cancel the workflow before reconnecting.")
        for connection in session.connections.values():
            await connection.restart()
        session.emit("info", {"message": "Reconnected. Ephemeral server data may have reset."})
        return {"connected": True}

    @app.get("/api/app-view/{app_id}")
    async def app_view(request: Request, app_id: str):
        session = session_for(request)
        if not session.app or session.app["id"] != app_id:
            raise HTTPException(404)
        return HTMLResponse(
            session.app_html,
            headers={
                "Content-Security-Policy": "default-src 'none'; script-src 'unsafe-inline'; "
                "style-src 'unsafe-inline'; "
                "img-src data:; connect-src 'none'; frame-src 'none'; form-action 'none'; "
                "base-uri 'none'; sandbox allow-scripts"
            },
        )

    @app.post("/api/app-call")
    async def app_call(request: Request):
        session = session_for(request, True)
        body = await request.json()
        if (
            not session.app
            or body != {"name": "analytics_dashboard", "arguments": {}}
            or session.app_tool.name != "analytics_dashboard"
        ):
            raise HTTPException(403, "Only the displayed analytics refresh is allowed.")
        result = await session.app_connection.checked_call(session.app_tool, {})
        return result.model_dump(mode="json", by_alias=True, exclude_none=True)

    @app.post("/api/close")
    async def close(request: Request):
        session = session_for(request, True)
        await session.close()
        sessions.pop(request.cookies.get("lumen_session"), None)
        response = JSONResponse({"closed": True})
        response.delete_cookie("lumen_session")
        return response

    app.mount("/assets", StaticFiles(directory=UI), name="assets")
    return WebBoundary(app, origin)


def main():
    import uvicorn

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8766)
    parser.add_argument("--config", type=type(CONFIG), default=CONFIG)
    args = parser.parse_args()
    uvicorn.run(
        make_web_app(f"http://127.0.0.1:{args.port}", args.config),
        host="127.0.0.1",
        port=args.port,
        access_log=False,
    )


if __name__ == "__main__":
    main()
