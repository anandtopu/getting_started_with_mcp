"""Follow the stable revision to its changelog, then SEP-2575; compare the current rule with
the historical design proposal.
Run: uv run python modules/bonus/B3_spec_contributing/python/examples/02_sep_index.py
Capture: uv run python scripts/bonus.py --module B3 --capture
"""

import json

from common.config import ROOT

print(json.loads((ROOT / "modules/bonus/B3_spec_contributing/data/sep-index.json").read_text()))
