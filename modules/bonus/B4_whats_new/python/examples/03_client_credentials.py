"""Use the SDK provider to discover a pinned issuer and acquire one reusable machine token.
Run: uv run python modules/bonus/B4_whats_new/python/examples/03_client_credentials.py
Capture: uv run python scripts/bonus.py --module B4 --capture
"""

import asyncio

from common.machine_auth import run

print(asyncio.run(run(enterprise=False)))
