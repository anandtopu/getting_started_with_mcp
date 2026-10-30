"""Build local distributions from shared sources; never upload or auto-install them."""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path, PurePosixPath, PureWindowsPath

from common.config import ROOT


def run(command, cwd=ROOT, **kwargs):
    result = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
        **kwargs,
    )
    if result.returncode:
        raise RuntimeError(f"Build command failed: {command[0]}\n{result.stderr[-3000:]}")
    return result.stdout


def artifacts():
    sources = [
        ROOT / p
        for p in [
            "common/notes.py",
            "common/distributed_notes.py",
            "common/typescript/notes.ts",
            "distribution/npm/src/cli.ts",
            "distribution/npm/package.json",
            "distribution/python/pyproject.toml",
            "distribution/python/README.md",
            "distribution/npm/README.md",
            "distribution/mcpb/manifest.json",
            "scripts/build_notes.mjs",
            "scripts/bundle_licenses.mjs",
            "common/packaging.py",
            "distribution/python/src/lumen_notes/__init__.py",
            "LICENSE",
            "package-lock.json",
        ]
    ]
    digest = hashlib.sha256(b"".join(p.read_bytes() for p in sources)).hexdigest()[:16]
    output = ROOT / ".runtime/packages" / digest
    output.mkdir(parents=True, exist_ok=True)
    marker = output / "artifacts.json"
    if marker.exists():
        values = json.loads(marker.read_text())
        if all((output / name).is_file() for name in values.values()):
            result = {key: output / name for key, name in values.items()}
            inspect_artifacts(result)
            return result
    uv, node, npm = shutil.which("uv"), shutil.which("node"), shutil.which("npm")
    if not all([uv, node, npm]):
        raise RuntimeError("Install uv and Node. See scripts/check_env.py.")
    # The sdist must contain its own sources, not references back to this checkout.
    with tempfile.TemporaryDirectory(prefix="lumen-build-") as temporary:
        stage = Path(temporary) / "source"
        shutil.copytree(ROOT / "distribution/python", stage, ignore=shutil.ignore_patterns("dist"))
        for original, filename in [
            ("notes.py", "notes.py"),
            ("distributed_notes.py", "__main__.py"),
        ]:
            shutil.copyfile(ROOT / "common" / original, stage / "src/lumen_notes" / filename)
        run(
            [
                uv,
                "build",
                str(stage),
                "--no-build-isolation",
                "--python",
                sys.executable,
                "--out-dir",
                str(output),
            ]
        )
    run([node, "scripts/build_notes.mjs"])
    # npm.cmd is invoked as an argument list on Windows; no interpolated shell text.
    packed = json.loads(
        run([npm, "pack", "./distribution/npm", "--json", "--pack-destination", str(output)])
    )
    bundle = output / "bundle"
    (bundle / "server").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "distribution/mcpb/manifest.json", bundle / "manifest.json")
    shutil.copyfile(ROOT / "distribution/npm/dist/cli.cjs", bundle / "server/cli.cjs")
    shutil.copyfile(ROOT / "LICENSE", bundle / "LICENSE")
    shutil.copyfile(
        ROOT / "distribution/npm/dist/THIRD_PARTY_LICENSES.txt", bundle / "THIRD_PARTY_LICENSES.txt"
    )
    cli = ROOT / "node_modules/@anthropic-ai/mcpb/dist/cli/cli.js"
    run([node, "--max-old-space-size=256", str(cli), "validate", str(bundle / "manifest.json")])
    run(
        [
            node,
            "--max-old-space-size=256",
            str(cli),
            "pack",
            str(bundle),
            str(output / "lumen-notes.mcpb"),
        ]
    )
    values = {
        "wheel": next(output.glob("*.whl")).name,
        "sdist": next(output.glob("*.tar.gz")).name,
        "npm": packed[0]["filename"],
        "bundle": "lumen-notes.mcpb",
    }
    marker.write_text(json.dumps(values, indent=2) + "\n")
    result = {key: output / name for key, name in values.items()}
    inspect_artifacts(result)
    return result


def inspect_artifacts(paths):
    forbidden = {".env", ".git", "node_modules", "__pycache__", ".venv", "data"}
    inventories = {}
    for kind, path in paths.items():
        if kind in {"wheel", "bundle"}:
            with zipfile.ZipFile(path) as archive:
                names = archive.namelist()
        else:
            with tarfile.open(path) as archive:
                names = archive.getnames()
        if any(
            set(PurePosixPath(n.replace("\\", "/")).parts) & forbidden
            or any(part.startswith(".env.") for part in PurePosixPath(n).parts)
            or PureWindowsPath(n).drive
            or PurePosixPath(n).is_absolute()
            or ".." in PurePosixPath(n.replace("\\", "/")).parts
            for n in names
        ):
            raise ValueError("Unexpected private, dependency-tree or escaping path in artifact.")
        inventories[kind] = names
    assert "lumen_notes/notes.py" in inventories["wheel"]
    assert "server/cli.cjs" in inventories["bundle"]
    return inventories


async def smoke_packages(*, offline=True):
    from mcp import Client, StdioServerParameters

    from common.protocol import SPEC_REVISION

    paths = artifacts()
    # uvx installs the built wheel into its tool cache; it cannot import the checkout.
    commands = [
        [
            shutil.which("uvx"),
            *(["--offline"] if offline else []),
            "--python",
            sys.executable,
            "--from",
            str(paths["wheel"]),
            "lumen-notes",
        ],
        [
            shutil.which("npm"),
            "exec",
            "--offline",
            "--yes",
            "--package",
            str(paths["npm"]),
            "--",
            "lumen-notes",
        ],
    ]
    with tempfile.TemporaryDirectory(prefix="lumen-installed-") as temporary:
        for command in commands:
            async with Client(
                StdioServerParameters(
                    command=command[0],
                    args=command[1:],
                    cwd=temporary,
                    env={
                        "LUMEN_NOTES_READ_ONLY": "true",
                        "UV_CACHE_DIR": run([shutil.which("uv"), "cache", "dir"]).strip(),
                        **{
                            key: os.environ[key]
                            for key in ("UV_CACHE_DIR", "UV_PYTHON_INSTALL_DIR")
                            if key in os.environ
                        },
                    },
                ),
                mode=SPEC_REVISION,
                read_timeout_seconds=15,
            ) as client:
                assert [t.name for t in (await client.list_tools()).tools] == ["search_notes"]
                result = await client.call_tool("search_notes", {"query": "release"})
                assert not result.is_error and "Release handover" in result.content[0].text
    return {key: str(value.relative_to(ROOT)) for key, value in paths.items()}
