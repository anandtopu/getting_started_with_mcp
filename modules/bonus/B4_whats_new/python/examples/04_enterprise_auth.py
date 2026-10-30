"""Use the SDK ID-JAG provider for the second exchange leg; validate signed claims and reject
assertion reuse.
Run: uv run python modules/bonus/B4_whats_new/python/examples/04_enterprise_auth.py
Capture: uv run python scripts/bonus.py --module B4 --capture
"""

import asyncio

from common.machine_auth import run

print(asyncio.run(run(enterprise=True)))
