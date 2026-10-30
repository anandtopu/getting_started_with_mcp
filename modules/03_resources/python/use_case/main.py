"""Lumen workspace service. Run: uv run python modules/03_resources/python/use_case/main.py
Protocol stdout only; inspect with scripts/tier1.py --module 3 --capture.
"""

from common.wiki import wiki_server


def main() -> None:
    wiki_server().run()


if __name__ == "__main__":
    main()
