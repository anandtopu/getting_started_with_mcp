"""Run: uv run python modules/09_elicitation_sampling_roots/python/use_case/server.py
Expected: service waits on stdio; use the adjacent main.py to exercise it.
"""

from common.elicitation import make_server

if __name__ == "__main__":
    make_server().run()
