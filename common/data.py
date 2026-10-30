"""Locate read-only course fixtures independently of the current directory."""

import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from common.config import ROOT


def data_root() -> Path:
    root = Path(os.environ.get("LUMEN_REPO_ROOT", ROOT)).resolve() / "data"
    if not root.is_dir():
        raise FileNotFoundError("Course data missing. Set LUMEN_REPO_ROOT to your checkout.")
    return root


def safe_path(root: Path, relative: str) -> Path:
    """Reject absolute paths, traversal and symlinks escaping a trusted root.

    This check assumes the local fixture tree is not concurrently modified by an
    attacker. Production file servers need OS-level isolation as well.
    """
    base = root.resolve(strict=True)
    requested = Path(relative)
    if requested.is_absolute() or requested.drive or ".." in requested.parts:
        raise ValueError("Path must stay inside the allowed folder.")
    candidate = (base / requested).resolve()
    if not candidate.is_relative_to(base):
        raise ValueError("Path must stay inside the allowed folder.")
    return candidate


def load_json(relative: str):
    return json.loads(safe_path(data_root(), relative).read_text(encoding="utf-8"))


@contextmanager
def readonly_database(relative: str):
    """Database URI quoting handles Windows drive letters and spaces."""
    path = safe_path(data_root(), relative)
    connection = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only=ON")
    try:
        yield connection
    finally:
        connection.close()
