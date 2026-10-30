"""DELIBERATELY UNSAFE, synthetic-only second fixture. Explicit --lab required."""

import argparse

from common.audit_lab import audit_server

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lab", action="store_true", required=True)
    parser.parse_args()
    audit_server(repaired=False).run()
