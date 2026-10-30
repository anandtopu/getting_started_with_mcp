"""Lumen module 12 use-case server.
Run: uv run python modules/12_security/python/use_case/server.py
Expected: stdio JSON-RPC; diagnostics on stderr.
"""

from common.defenses import make_server

if __name__ == "__main__":
    make_server().run()
