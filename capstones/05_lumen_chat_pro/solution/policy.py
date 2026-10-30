"""Capstone-specific policy exercise. Runtime authorization also verifies claims and inputs."""


def choose(action: str, scopes: set[str], human_approved: bool) -> bool:
    return action in {"read", "write"} and human_approved is True and ("tool:" + action) in scopes
