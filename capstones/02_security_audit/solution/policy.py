"""Capstone-specific policy exercise. Runtime authorization also verifies claims and inputs."""


def choose(action: str, scopes: set[str], human_approved: bool) -> bool:
    return (action == "public" and "read" in scopes) or (
        action == "publish" and "write" in scopes and human_approved is True
    )
