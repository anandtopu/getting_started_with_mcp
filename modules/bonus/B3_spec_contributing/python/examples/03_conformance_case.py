"""Generate a local issue draft containing versions, reproduction and measured observations.
Nothing is submitted.
Run: uv run python modules/bonus/B3_spec_contributing/python/examples/03_conformance_case.py
Capture: uv run python scripts/bonus.py --module B3 --capture
"""

from common.config import ROOT
from common.spec_reading import issue_template

print(issue_template(ROOT / "modules/01_architecture_wire/wire/01_jsonrpc.jsonl"))
