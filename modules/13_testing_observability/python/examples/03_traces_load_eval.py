"""Export real SDK spans, measure bounded HTTP load, and score fixture selection.

Run: uv run python modules/13_testing_observability/python/examples/03_traces_load_eval.py
Expected: PASS with the measured checks below.
"""

import argparse
import asyncio

from opentelemetry import trace

from common.config import load_settings
from common.quality import configure_traces, contracts, evaluate, evaluate_model, load
from scripts.auth_lab import auth_stack


async def main(live: bool = False, limit: int = 5) -> None:
    provider, exporter = configure_traces()
    try:
        with trace.get_tracer("lumen.lesson").start_as_current_span("quality-run"):
            await contracts()
        spans = exporter.get_finished_spans()
        root = next(span for span in spans if span.name == "quality-run")
        calls = [span for span in spans if span.attributes.get("mcp.method.name") == "tools/call"]
        assert calls and all(span.context.trace_id == root.context.trace_id for span in calls)
        assert any(span.status.status_code.name == "ERROR" for span in calls)
        async with auth_stack() as authority:
            print(await load(authority.resource, authority.token()))
        print(evaluate())
        if live:
            print(await evaluate_model(load_settings(), limit))
        print(f"PASS {len(calls)} SDK tool spans share the parent trace; exporter flushed")
    finally:
        provider.force_flush()
        provider.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()
    asyncio.run(main(args.live, args.limit))
