"""Independent policy acceptance; select --starter with the checker to practice."""

import os
import runpy
from pathlib import Path

import pytest


def test_contract():
    solve = runpy.run_path(
        str(
            Path(__file__).parents[1]
            / os.environ.get("LUMEN_EXERCISE_SOURCE", "solutions")
            / "02_budget.py"
        )
    )["solve"]
    assert solve(["b", "a", "b"], 2) == ["a", "b"]
    with pytest.raises(ValueError):
        solve([], 0)
