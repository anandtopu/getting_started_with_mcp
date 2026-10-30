"""Executable acceptance for Lumen Chat Pro."""

import pytest

from scripts.capstones import run


@pytest.mark.anyio
async def test_reference_solution():
    await run(5)


def test_policy_evaluation():
    from scripts.check_capstone import check

    assert check(5) == 4
