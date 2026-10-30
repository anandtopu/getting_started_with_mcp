"""Exercise token and PKCE boundaries through real HTTP and SDK auth.

Run: uv run python modules/11_authorization/python/examples/02_pkce_and_tokens.py
Expected: PASS with the measured checks below.
"""

import asyncio

from scripts.auth_lab import auth_stack, exercise_auth


async def main() -> None:
    async with auth_stack() as authority:
        await exercise_auth(authority)


if __name__ == "__main__":
    asyncio.run(main())
