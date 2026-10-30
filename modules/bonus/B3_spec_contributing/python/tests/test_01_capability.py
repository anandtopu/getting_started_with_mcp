"""Independent policy acceptance; select --starter with the checker to practice."""

import os
import runpy
from pathlib import Path


def test_contract():
    solve = runpy.run_path(
        str(
            Path(__file__).parents[1]
            / os.environ.get("LUMEN_EXERCISE_SOURCE", "solutions")
            / "01_capability.py"
        )
    )["solve"]
    assert solve({"extensions": {"skills": {}}}, "skills") is True
    assert solve({}, "skills") is False
