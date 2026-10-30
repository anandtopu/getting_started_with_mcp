"""Check one learner exercise, or its separate worked solution.

Run: uv run python scripts/check_exercise.py --module 2 --exercise 1 [--solution]
An unfinished starter runs but fails its extension checks with a readable difference.
"""

import argparse
import json
import runpy

from common.config import ROOT
from scripts.tier1 import MODULES
from scripts.tier2 import MODULES as TIER2_MODULES
from scripts.tier3 import MODULES as TIER3_MODULES
from scripts.tier4 import MODULES as TIER4_MODULES
from scripts.tier5 import MODULES as TIER5_MODULES

MODULES = MODULES + TIER2_MODULES + TIER3_MODULES + TIER4_MODULES + TIER5_MODULES


def check(module: int, exercise: int, solution: bool = False) -> None:
    folder = ROOT / "modules" / MODULES[module] / "python"
    contract = json.loads((folder / "tests/exercise_cases.json").read_text(encoding="utf-8"))[
        exercise - 1
    ]
    target = "solutions" if solution else "exercises"
    solve = runpy.run_path(str(folder / target / (contract["stem"] + ".py")))["solve"]
    for arguments, expected in contract["cases"]:
        actual = solve(*arguments)
        assert actual == expected, f"{contract['task']}\nExpected {expected!r}; got {actual!r}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module", type=int, choices=range(22), required=True)
    parser.add_argument("--exercise", type=int, choices=range(1, 4), required=True)
    parser.add_argument("--solution", action="store_true")
    args = parser.parse_args()
    try:
        check(args.module, args.exercise, args.solution)
    except AssertionError as error:
        parser.exit(1, f"{error}\n")
    print("Exercise checks passed.")


if __name__ == "__main__":
    main()
