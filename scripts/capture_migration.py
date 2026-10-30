"""Run only the guide's labeled historical fixture; keep deprecated syntax there.

Run: uv run python scripts/capture_migration.py
Expected: refreshes real historical messages inside the migration guide.
"""

import json
import re
import subprocess
import sys

from common.config import ROOT


def main() -> None:
    guide = ROOT / "docs/MIGRATING_FROM_OLDER_VERSIONS.md"
    text = guide.read_text(encoding="utf-8")
    runtime = ROOT / ".runtime"
    runtime.mkdir(exist_ok=True)
    for role in ["server", "client"]:
        block = re.search(rf"<!-- migration:{role} -->\s*```python\n(.*?)\n```", text, re.S)
        if block is None:
            raise ValueError("Guide is missing a labeled historical fixture.")
        (runtime / f"migration_{role}.py").write_text(block[1] + "\n", encoding="utf-8")
    subprocess.run(
        [sys.executable, str(runtime / "migration_client.py")], cwd=ROOT, check=True, timeout=30
    )
    rows = [json.loads(line) for line in (runtime / "migration.jsonl").read_text().splitlines()]
    excerpt = "\n\n".join(
        "```json\n" + json.dumps(row["message"], indent=2) + "\n```"
        for row in rows[1:]
        if isinstance(row["message"], dict)
    )
    before, rest = text.split("<!-- migration:wire:start -->")
    _, after = rest.split("<!-- migration:wire:end -->")
    guide.write_text(
        before
        + "<!-- migration:wire:start -->\n\n"
        + excerpt
        + "\n\n<!-- migration:wire:end -->"
        + after,
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
