"""Validate real JSON-RPC capture shapes and correlate response IDs.
Run: uv run python modules/bonus/B3_spec_contributing/python/examples/01_schema_contract.py
Capture: uv run python scripts/bonus.py --module B3 --capture
"""

from common.config import ROOT
from common.spec_reading import contract_report

print(contract_report(ROOT / "modules/01_architecture_wire/wire/01_jsonrpc.jsonl"))
