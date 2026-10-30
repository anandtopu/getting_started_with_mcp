"""Executable solution contracts; run starter checks separately while learning."""

import pytest

from scripts.check_exercise import check


@pytest.mark.parametrize("exercise", [1, 2, 3])
def test_solutions(exercise):
    check(4, exercise, solution=True)
