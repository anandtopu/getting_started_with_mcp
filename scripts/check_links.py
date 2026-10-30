"""Check local Markdown file links; optionally check external URLs.

Run: uv run python scripts/check_links.py [--external]
External checks require network; the default never does.
"""

import argparse
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from common.config import ROOT

EXCLUDED = {
    ".git",
    ".venv",
    "node_modules",
    ".runtime",
    ".uv-cache",
    ".npm-cache",
    "target",
    "bin",
    "obj",
    "dist",
    "build",
}


def documents(root: Path = ROOT):
    for folder, directories, files in os.walk(root):
        directories[:] = [name for name in directories if name not in EXCLUDED]
        for name in files:
            if name.endswith(".md"):
                yield Path(folder) / name


def check(external: bool = False) -> list[str]:
    failures = []
    urls = set()
    for path in documents():
        content = re.sub(r"```.*?```", "", path.read_text(encoding="utf-8"), flags=re.S)
        for target in re.findall(r"\]\(([^)]+)\)", content):
            target = target.strip("<>")
            if target.startswith(("https://", "http://")):
                urls.add(target)
            elif not target.startswith(("#", "mailto:")):
                local = urllib.parse.unquote(target.split("#")[0])
                if not (path.parent / local).exists():
                    failures.append(f"{path.relative_to(ROOT)} -> {target}")
    if external:

        def probe(url):
            for attempt in range(2):
                try:
                    request = urllib.request.Request(url, headers={"User-Agent": "LumenCourse/0.2"})
                    with urllib.request.urlopen(request, timeout=15) as response:
                        if response.status >= 400:
                            raise urllib.error.URLError(str(response.status))
                    break
                except (OSError, urllib.error.URLError) as error:
                    if attempt == 1:
                        return f"{url}: {error}"
            return None

        with ThreadPoolExecutor(max_workers=8) as workers:
            failures.extend(error for error in workers.map(probe, sorted(urls)) if error)
    return failures


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--external", action="store_true")
    args = parser.parse_args()
    failures = check(args.external)
    for failure in failures:
        print(failure)
    print(f"Link check: {len(failures)} failures.")
    raise SystemExit(bool(failures))


if __name__ == "__main__":
    main()
