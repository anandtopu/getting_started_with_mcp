"""Build and launch a self-contained knowledge wheel and a validated MCPB bundle.
Run: uv run python scripts/knowledge_package.py [--prepare]
No upload. --prepare allows dependency downloads; otherwise uvx uses its cache.
"""

import argparse
import asyncio
import json
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

from mcp import Client, StdioServerParameters

from common.config import ROOT
from common.packaging import run
from common.protocol import SPEC_REVISION


def build():
    output = ROOT / ".runtime/phase8/knowledge"
    output.mkdir(parents=True, exist_ok=True)
    uv, node = shutil.which("uv"), shutil.which("node")
    if not uv or not node:
        raise RuntimeError("Install uv and Node; run scripts/check_env.py.")
    source = ROOT / "capstones/01_personal_knowledge/package"
    with tempfile.TemporaryDirectory(prefix="knowledge-build-") as temporary:
        stage = Path(temporary) / "source"
        shutil.copytree(source, stage)
        package = stage / "src/lumen_knowledge"
        package.mkdir(parents=True)
        (package / "__init__.py").write_text('"""Personal Knowledge MCP server."""\n')
        for original, target in [
            ("knowledge.py", "knowledge.py"),
            ("knowledge_cli.py", "__main__.py"),
        ]:
            shutil.copyfile(ROOT / "common" / original, package / target)
        shutil.copytree(ROOT / "capstones/01_personal_knowledge/notes", package / "notes")
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
    wheel = next(output.glob("*.whl"))
    bundle = output / "bundle"
    (bundle / "server").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(wheel, bundle / "server" / wheel.name)
    (bundle / "server/main.py").write_text("from lumen_knowledge.__main__ import main\nmain()\n")
    manifest_path = source / "mcpb.json"
    if manifest_path.stat().st_size > 64000:
        raise ValueError("Knowledge bundle manifest exceeds 64 KB.")
    manifest = json.loads(manifest_path.read_text())
    (bundle / "manifest.json").write_text(json.dumps(manifest, indent=2))
    shutil.copyfile(ROOT / "LICENSE", bundle / "LICENSE")
    cli = ROOT / "scripts/mcpb.mjs"
    # Retain the heap/time limits in addition to the packer's input bounds.
    run([node, "--max-old-space-size=256", str(cli), "validate", str(bundle / "manifest.json")])
    artifact = output / "lumen-knowledge.mcpb"
    run([node, "--max-old-space-size=256", str(cli), "pack", str(bundle), str(artifact)])
    with zipfile.ZipFile(artifact) as archive:
        assert "server/" + wheel.name in archive.namelist()
        assert not any(".env" in name or ".." in Path(name).parts for name in archive.namelist())
    return wheel, artifact


async def check(offline=True):
    wheel, bundle = build()
    uvx = shutil.which("uvx")
    if not uvx:
        raise RuntimeError("Install uv; run scripts/check_env.py.")
    with tempfile.TemporaryDirectory(prefix="knowledge-installed-") as temporary:
        extracted = Path(temporary) / "bundle"
        with zipfile.ZipFile(bundle) as archive:
            archive.extractall(extracted)  # Our just-built, inspected archive.
        for installed in (wheel, extracted / "server" / wheel.name):
            async with Client(
                StdioServerParameters(
                    command=uvx,
                    args=[
                        *(["--offline"] if offline else []),
                        "--python",
                        sys.executable,
                        "--from",
                        str(installed),
                        "lumen-knowledge",
                    ],
                    cwd=temporary,
                    env={"PYTHONPATH": "", "PYTHONNOUSERSITE": "1"},
                ),
                mode=SPEC_REVISION,
            ) as client:
                result = await client.call_tool(
                    "search_knowledge", {"query": "shipping", "mode": "semantic"}
                )
                assert not result.is_error and "release.md" in str(result)
                assert (await client.read_resource("knowledge://notes/release.md")).contents
    return {
        "wheel": str(wheel.relative_to(ROOT)),
        "bundle": str(bundle.relative_to(ROOT)),
        "installed_launches": 2,
        "desktop_gui_install": "manual",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    print(json.dumps(asyncio.run(check(not parser.parse_args().prepare)), indent=2))
