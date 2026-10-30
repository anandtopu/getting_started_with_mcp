"""Executable acceptance for Personal Knowledge Server."""

import pytest

from scripts.capstones import run


@pytest.mark.anyio
async def test_reference_solution():
    await run(1)


def test_policy_evaluation():
    from scripts.check_capstone import check

    assert check(1) == 4
