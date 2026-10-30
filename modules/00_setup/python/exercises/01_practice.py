"""Return custom connectors and standard adapters for N hosts and M systems.
Run: uv run python modules/00_setup/python/exercises/01_practice.py
Check: uv run python scripts/check_exercise.py --module 0 --exercise 1
The starter demonstrates a narrower behavior. Extend it to satisfy the checks.
"""


def solve(hosts: int, systems: int):
    # YOUR CODE HERE: Return custom connectors and standard adapters for N hosts and M systems.
    return {"custom": hosts * systems, "standard": hosts * systems}


def main() -> None:
    print(solve(*[3, 4]))


if __name__ == "__main__":
    main()
