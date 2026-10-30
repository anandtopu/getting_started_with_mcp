"""Run: uv run python modules/07_real_data/python/use_case/server.py
Expected: issues and analytics tools wait on stdio; all writes use a disposable copy.
"""

from common.analytics import register_analytics
from common.issues import make_server


def main() -> None:
    server = make_server()
    register_analytics(server)
    server.run()


if __name__ == "__main__":
    main()
