"""Learner checks are opt-in; unfinished exercises are not a CI failure.
Run: uv run python modules/11_authorization/python/exercises/test_exercises.py
"""

from scripts.check_exercise import check

if __name__ == "__main__":
    for exercise in [1, 2, 3]:
        check(11, exercise)
