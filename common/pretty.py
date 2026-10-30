"""Human-readable diagnostics go to stderr, never a stdio protocol stream."""

import json
import re
from typing import Any

from rich.console import Console

SENSITIVE = re.compile(r"token|secret|password|authorization|api.?key", re.I)


def redact(value: Any, secrets: tuple[str, ...] = ()) -> Any:
    if isinstance(value, dict):
        return {
            k: "[REDACTED]" if SENSITIVE.search(k) else redact(v, secrets) for k, v in value.items()
        }
    if isinstance(value, list):
        return [redact(v, secrets) for v in value]
    if isinstance(value, str):
        for secret in secrets:
            if secret:
                value = value.replace(secret, "[REDACTED]")
    return value


def show(value: Any, *, label: str = "Lumen", secrets: tuple[str, ...] = ()) -> None:
    Console(stderr=True).print(label, markup=False)
    Console(stderr=True).print_json(json.dumps(redact(value, secrets), default=str))
