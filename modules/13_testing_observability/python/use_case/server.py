"""Lumen module 13 use-case server.
Run: uv run python modules/13_testing_observability/python/use_case/server.py
Expected: stdio JSON-RPC; diagnostics on stderr.
"""

from common.notes import notes_server
from common.quality import JsonSpanExporter, configure_traces

if __name__ == "__main__":
    configure_traces(JsonSpanExporter())
    notes_server().run()
