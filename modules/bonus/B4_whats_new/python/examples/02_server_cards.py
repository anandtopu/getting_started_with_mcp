"""Validate the actual experimental card schema and apply a separate trusted-endpoint policy.
Run: uv run python modules/bonus/B4_whats_new/python/examples/02_server_cards.py
Capture: uv run python scripts/bonus.py --module B4 --capture
"""

import json

from common.server_cards import BASE, validate_card

print(validate_card(json.loads((BASE / "server-card.json").read_text()), "ops.lumen.example"))
