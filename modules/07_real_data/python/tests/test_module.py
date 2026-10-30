"""Check the worked extensions against their published contracts."""

import pytest

from scripts.check_exercise import check


@pytest.mark.parametrize("exercise", [1, 2, 3])
def test_solutions(exercise: int) -> None:
    check(7, exercise, solution=True)
