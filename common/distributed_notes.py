"""Standalone notes entry point, also copied into the distribution wheel."""

import os

from .notes import notes_server


def make_server():
    value = os.environ.get("LUMEN_NOTES_READ_ONLY", "true").lower()
    if value not in {"true", "false"}:
        raise ValueError("LUMEN_NOTES_READ_ONLY must be true or false.")
    server = notes_server()
    if value == "true":
        server.remove_tool("create_note")
        server.remove_tool("tag_note")
    return server


def main():
    make_server().run()


if __name__ == "__main__":
    main()
