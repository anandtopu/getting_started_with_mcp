"""Opt-in learner checks; run this file by path after editing the starters."""

from scripts.check_exercise import check

if __name__ == "__main__":
    for exercise in [1, 2, 3]:
        check(14, exercise)
