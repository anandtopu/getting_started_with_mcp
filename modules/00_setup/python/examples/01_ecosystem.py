"""Count integration edges and name the three roles.

Concepts/spec: see ../../README.md, Key APIs and Go deeper.
Run: uv run python modules/00_setup/python/examples/01_ecosystem.py
Expected: custom_connectors=12, standard_adapters=7
Inspect/capture: uv run python scripts/tier1.py --module 0 --capture
"""


def integration_counts(hosts: int, systems: int) -> dict[str, int]:
    if hosts < 0 or systems < 0:
        raise ValueError("Counts must be non-negative.")
    return {"custom_connectors": hosts * systems, "standard_adapters": hosts + systems}


def main() -> None:
    print(integration_counts(3, 4))
    print("Host: chat application; client: protocol connection; server: capability provider.")


if __name__ == "__main__":
    main()
