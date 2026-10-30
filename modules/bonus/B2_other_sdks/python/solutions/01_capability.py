"""Runnable policy exercise. See the bonus README for the contract."""


def solve(capabilities: dict, extension: str) -> bool:
    return extension in capabilities.get("extensions", {})
