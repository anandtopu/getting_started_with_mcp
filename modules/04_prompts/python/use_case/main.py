"""Lumen workspace service. Run: uv run python modules/04_prompts/python/use_case/main.py
Protocol stdout only; inspect with scripts/tier1.py --module 4 --capture.
"""

from common.prompts import prompt_server


def main() -> None:
    prompt_server().run()


if __name__ == "__main__":
    main()
