"""Capstone-specific policy exercise. Runtime authorization also verifies claims and inputs."""


def choose(action: str, scopes: set[str], human_approved: bool) -> bool:
    # YOUR CODE HERE: implement this project's evaluation cases.
    return False


if __name__ == "__main__":
    print("Baseline denies requests. Run scripts/check_capstone.py --project 2 --starter.")
