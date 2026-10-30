"""Lumen module 11 use-case server.
Run: uv run python modules/11_authorization/python/use_case/server.py
Expected: loopback HTTP on port 8001, Keycloak required.
"""

from common.secured_issues import serve

if __name__ == "__main__":
    serve()
