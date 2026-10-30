"""Install checksum-verified mcp-publisher v1.8.7 and inspect its CLI; never log in/publish.
Run: uv run python scripts/publisher_tool.py [--validate-online]
The optional validation sends the public server.json to the official registry.
"""

import argparse
import hashlib
import io
import platform
import subprocess
import tarfile
import urllib.request

from common.config import ROOT

VERSION = "1.8.7"
BASE = f"https://github.com/modelcontextprotocol/registry/releases/download/v{VERSION}"


def download(name):
    with urllib.request.urlopen(BASE + "/" + name, timeout=30) as response:
        data = response.read(25_000_001)
    if len(data) > 25_000_000:
        raise ValueError("Publisher download exceeds 25 MB.")
    return data


def install():
    system = {"Windows": "windows", "Linux": "linux", "Darwin": "darwin"}[platform.system()]
    machine = {"amd64": "amd64", "x86_64": "amd64", "arm64": "arm64", "aarch64": "arm64"}[
        platform.machine().lower()
    ]
    name = f"mcp-publisher_{system}_{machine}.tar.gz"
    checksums = download(f"registry_{VERSION}_checksums.txt").decode()
    expected = next(line.split()[0] for line in checksums.splitlines() if line.endswith(name))
    archive = download(name)
    if hashlib.sha256(archive).hexdigest() != expected:
        raise ValueError("Publisher checksum mismatch.")
    target = ROOT / ".runtime/publisher" / VERSION
    target.mkdir(parents=True, exist_ok=True)
    executable = "mcp-publisher" + (".exe" if system == "windows" else "")
    with tarfile.open(fileobj=io.BytesIO(archive)) as source:
        matches = [m for m in source if m.name == executable and m.isfile()]
        if len(matches) != 1 or matches[0].size > 30_000_000:
            raise ValueError("Unexpected publisher archive contents.")
        (target / executable).write_bytes(source.extractfile(matches[0]).read())
    (target / executable).chmod(0o755)
    return target / executable


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate-online", action="store_true")
    args = parser.parse_args()
    executable = install()
    subprocess.run([str(executable), "--version"], check=True, timeout=10)
    subprocess.run([str(executable), "validate", "--help"], check=True, timeout=10)
    if args.validate_online:
        subprocess.run(
            [str(executable), "validate", "distribution/registry/server.json"],
            cwd=ROOT,
            check=True,
            timeout=30,
        )


if __name__ == "__main__":
    main()
