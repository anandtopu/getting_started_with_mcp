"""Capstone-specific policy exercise. Runtime authorization also verifies claims and inputs."""


def choose(action: str, scopes: set[str], human_approved: bool) -> bool:
    return action in {"read", "search_text", "search_semantic"} and "notes:read" in scopes
