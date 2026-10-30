"""Executable acceptance for Security Audit Lab."""

import pytest

from scripts.capstones import run


@pytest.mark.anyio
async def test_reference_solution():
    await run(2)


def test_policy_evaluation():
    from scripts.check_capstone import check

    assert check(2) == 4
