"""Evaluate a capstone's explicit permission cases, including the learner's starter.
Run: uv run python scripts/check_capstone.py --project 1 [--starter]
"""

import argparse
import json
import runpy

from common.config import ROOT
from scripts.capstones import NAMES


def check(project, starter=False):
    folder = ROOT / "capstones" / NAMES[project - 1]
    source = folder / ("starter/main.py" if starter else "solution/policy.py")
    choose = runpy.run_path(str(source))["choose"]
    rows = [json.loads(line) for line in (folder / "eval/cases.jsonl").read_text().splitlines()]
    for index, row in enumerate(rows, 1):
        actual = choose(row["action"], set(row["scopes"]), row["human_approved"])
        if actual is not row["expected"]:
            raise ValueError(f"Case {index}: expected {row['expected']}, received {actual}.")
    return len(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=int, choices=range(1, 6), required=True)
    parser.add_argument("--starter", action="store_true")
    args = parser.parse_args()
    try:
        print(f"PASS {check(args.project, args.starter)} permission evaluation cases")
    except ValueError as error:
        parser.exit(1, f"{error} Review the project rubric and edit the starter policy.\n")
