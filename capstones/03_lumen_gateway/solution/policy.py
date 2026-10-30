"""Capstone-specific policy exercise. Runtime authorization also verifies claims and inputs."""


def choose(action: str, scopes: set[str], human_approved: bool) -> bool:
    return "workspace:read" in scopes and (
        action == "read"
        or (action == "write" and "workspace:write" in scopes and human_approved is True)
    )
