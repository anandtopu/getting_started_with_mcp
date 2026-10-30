"""Lumen workspace service. Run: uv run python modules/02_first_server_tools/python/use_case/main.py
Protocol stdout only; inspect with scripts/tier1.py --module 2 --capture.
"""

from common.notes import notes_server


def main() -> None:
    notes_server().run()


if __name__ == "__main__":
    main()
