"""Launch an isolated native adapter without changing the course environment.

Setup: uv sync --project frameworks/strands (or frameworks/adk)
Run: uv run python scripts/framework_extras.py strands
Expected: PASS plus the real local MCP result, without a model call.
"""

import argparse
import os
import subprocess
import sys

from common.config import ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("framework", choices=["strands", "adk"])
    args = parser.parse_args()
    root = ROOT / "frameworks" / args.framework
    python = root / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not python.exists():
        raise SystemExit(
            f"First run: uv sync --frozen --project frameworks/{args.framework}. "
            "See scripts/check_env.py."
        )
    result = subprocess.run(
        [str(python), str(root / "demo.py"), "--server-python", sys.executable],
        cwd=ROOT,
        timeout=45,
        check=False,
    )
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
