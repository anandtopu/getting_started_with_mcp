"""Small measured contracts, deterministic evaluation and a local trace exporter."""

import asyncio
import json
import re
import statistics
import sys
import time

from mcp import Client
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExporter, SpanExportResult
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from common.config import ROOT
from common.connections import discover
from common.notes import notes_server


class JsonSpanExporter(SpanExporter):
    """Allowlist telemetry fields; never export arguments, results or credentials."""

    def export(self, spans):
        for span in spans:
            print(
                json.dumps(
                    {
                        "event": "span",
                        "name": span.name,
                        "trace_id": format(span.context.trace_id, "032x"),
                        "status": span.status.status_code.name,
                    }
                ),
                file=sys.stderr,
            )
        return SpanExportResult.SUCCESS

    def shutdown(self):
        pass


def configure_traces(exporter=None):
    provider = TracerProvider()
    exporter = exporter or InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    return provider, exporter


async def contracts():
    async with Client(notes_server(), raise_exceptions=False) as client:
        tools = (await client.list_tools()).tools
        names = {tool.name for tool in tools}
        assert {"search_notes", "create_note", "tag_note"} <= names
        create = next(tool for tool in tools if tool.name == "create_note")
        assert "title" in create.input_schema["required"]
        assert (await client.call_tool("create_note", {"title": "", "body": "x"})).is_error
        assert not (await client.call_tool("search_notes", {})).is_error
    return {"contracts": "passed", "tools": len(names)}


def select_tool(request: str) -> list[dict]:
    """Deterministic baseline, not an LLM usability measurement."""
    match = re.fullmatch(r"Read Lumen issue ([1-9][0-9]*)", request)
    return [{"name": "issues_get", "arguments": {"issue_id": int(match[1])}}] if match else []


def evaluate(selector=select_tool) -> dict:
    rows = [
        json.loads(line)
        for line in (ROOT / "data/eval/tool_selection.jsonl").read_text().splitlines()
    ]
    correct = sum(selector(row["request"]) == row["expected_calls"] for row in rows)
    return {
        "kind": "deterministic fixture baseline; not LLM evidence",
        "correct": correct,
        "total": len(rows),
        "accuracy": correct / len(rows),
    }


async def evaluate_model(settings, limit: int = 5, factory=None) -> dict:
    """Opt-in model selection only: evaluate proposals without executing tools."""
    from common.llm import create_tool_model

    if settings.provider == "fake" and factory is None:
        raise ValueError(
            "Select a real provider in .env for --live; default uses fixture evaluation"
        )
    if not 1 <= limit <= 30:
        raise ValueError("Choose 1-30 evaluation rows")
    factory = factory or create_tool_model
    rows = [
        json.loads(line)
        for line in (ROOT / "data/eval/tool_selection.jsonl").read_text().splitlines()
    ][:limit]
    tools = [
        {
            "name": "issues_get",
            "description": "Read a Lumen issue by its ID.",
            "inputSchema": {
                "type": "object",
                "properties": {"issue_id": {"type": "integer", "minimum": 1}},
                "required": ["issue_id"],
                "additionalProperties": False,
            },
        },
        {
            "name": "wiki_search",
            "description": "Find wiki documentation by search text.",
            "inputSchema": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    ]
    correct, errors = 0, 0
    start = time.perf_counter()
    for row in rows:
        try:
            model = factory(row["request"], settings=settings)
            async with asyncio.timeout(settings.timeout):
                turn = await model.turn(tools, [])
            actual = [{"name": call.name, "arguments": call.arguments} for call in turn.calls]
            correct += actual == row["expected_calls"]
        except (RuntimeError, TimeoutError):
            errors += 1
    return {
        "kind": "live model proposals; no tool execution",
        "provider": settings.provider,
        "model": settings.model,
        "correct": correct,
        "total": len(rows),
        "errors": errors,
        "accuracy": correct / len(rows),
        "elapsed_seconds": round(time.perf_counter() - start, 2),
    }


async def load(url: str, token: str, count: int = 20, concurrency: int = 4) -> dict:
    from scripts.http_lab import http_client

    if not 1 <= count <= 100 or not 1 <= concurrency <= 8:
        raise ValueError("Load lab limit: 100 requests, 8 concurrent")
    semaphore, times = asyncio.Semaphore(concurrency), []

    async def read():
        async with semaphore:
            start = time.perf_counter()
            async with http_client(url) as (client, http):
                http.headers["Authorization"] = "Bearer " + token
                await discover(client)
                result = await client.call_tool("read_issue", {"issue_id": 1})
                assert not result.is_error
            times.append((time.perf_counter() - start) * 1000)

    await asyncio.gather(*(read() for _ in range(count)))
    ordered = sorted(times)
    return {
        "requests": count,
        "concurrency": concurrency,
        "errors": 0,
        "p50_ms": round(statistics.median(times), 2),
        "p95_ms": round(ordered[max(0, int(count * 0.95) - 1)], 2),
    }


def validate_stdout(lines: str) -> int:
    count = 0
    for line in lines.splitlines():
        try:
            message = json.loads(line)
        except ValueError as error:
            raise ValueError("Protocol stdout contains non-JSON text; log to stderr") from error
        if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
            raise ValueError("Protocol stdout contains a non-JSON-RPC object")
        count += 1
    return count


def call_snapshot(path) -> list[dict]:
    """Snapshot call semantics; exclude IDs/timing/trace metadata, keep payloads."""
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    calls, result = {}, []
    for row in rows[1:]:
        message = row.get("message") or {}
        if message.get("method") == "tools/call":
            params = message["params"]
            calls[message["id"]] = {"name": params["name"], "arguments": params["arguments"]}
        elif message.get("id") in calls and "result" in message:
            payload = {k: v for k, v in message["result"].items() if k != "_meta"}
            result.append({"call": calls.pop(message["id"]), "result": payload})
    if calls:
        raise ValueError("Snapshot contains unanswered calls")
    return result
