"""Check every worked extension against the learner contract."""

import pytest

from scripts.check_exercise import check


@pytest.mark.parametrize("exercise", [1, 2, 3])
def test_solutions(exercise: int) -> None:
    check(11, exercise, solution=True)
