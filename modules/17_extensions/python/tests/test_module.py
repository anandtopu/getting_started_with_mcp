"""Check the three worked solutions against the learner contracts."""

import pytest

from scripts.check_exercise import check


@pytest.mark.parametrize("exercise", [1, 2, 3])
def test_solutions(exercise):
    check(17, exercise, solution=True)
