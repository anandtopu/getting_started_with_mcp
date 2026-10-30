"""Run a bonus exercise's independent assertions against a starter or solution.
Run: uv run python scripts/check_bonus_exercise.py B3 1 [--solution]
"""

import argparse
import os
import runpy

from common.config import ROOT


def check(module, exercise, solution=False):
    folder = next((ROOT / "modules/bonus").glob(module + "_*"))
    test = next((folder / "python/tests").glob(f"test_{exercise:02d}_*.py"))
    previous = os.environ.get("LUMEN_EXERCISE_SOURCE")
    os.environ["LUMEN_EXERCISE_SOURCE"] = "solutions" if solution else "exercises"
    try:
        runpy.run_path(str(test))["test_contract"]()
    finally:
        if previous is None:
            os.environ.pop("LUMEN_EXERCISE_SOURCE", None)
        else:
            os.environ["LUMEN_EXERCISE_SOURCE"] = previous


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("module", choices=["B2", "B3", "B4"])
    parser.add_argument("exercise", type=int, choices=[1, 2, 3])
    parser.add_argument("--solution", action="store_true")
    args = parser.parse_args()
    try:
        check(args.module, args.exercise, args.solution)
        print("PASS bonus exercise")
    except (AssertionError, ValueError, TypeError):
        parser.exit(1, "Exercise mismatch. Compare the README contract and edit the starter.\n")
