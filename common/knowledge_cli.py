"""Installed personal knowledge entry point; allow one explicitly selected folder."""

import argparse
import os
from pathlib import Path

from .knowledge import knowledge_server


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--notes",
        type=Path,
        default=Path(os.environ.get("LUMEN_KNOWLEDGE_DIR", str(Path(__file__).with_name("notes")))),
    )
    args = parser.parse_args()
    try:
        server = knowledge_server(args.notes)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    server.run()


if __name__ == "__main__":
    main()
