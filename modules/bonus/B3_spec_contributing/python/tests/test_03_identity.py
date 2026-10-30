"""Independent policy acceptance; select --starter with the checker to practice."""

import os
import runpy
from pathlib import Path


def test_contract():
    solve = runpy.run_path(
        str(
            Path(__file__).parents[1]
            / os.environ.get("LUMEN_EXERCISE_SOURCE", "solutions")
            / "03_identity.py"
        )
    )["solve"]
    assert solve("one", "skill://review") != solve("two", "skill://review")
