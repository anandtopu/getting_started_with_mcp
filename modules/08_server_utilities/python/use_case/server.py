"""Run: uv run python modules/08_server_utilities/python/use_case/server.py
Expected: service waits on stdio; use the adjacent main.py to exercise it.
"""

from common.reports import make_server

if __name__ == "__main__":
    make_server().run()
