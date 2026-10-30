"""Validate delivered files and report planned lessons honestly.

Run: uv run python scripts/check_course.py [--release]
--release fails until all 22 modules and their learning materials exist.
"""

import argparse
import json

from common.config import ROOT
from scripts.check_links import check

SECTIONS = [
    "Prerequisites",
    "Learning objectives",
    "The big idea",
    "How it works",
    "On the wire",
    "Key APIs at a glance",
    "Walkthrough",
    "Try it in a host",
    "Real-world use case",
    "Common mistakes",
    "Exercises",
    "Quiz",
    "Key takeaways",
    "Go deeper",
    "Next",
]


def validate(release: bool = False) -> list[str]:
    errors = check()
    manifest = json.loads((ROOT / "scripts/examples.json").read_text())
    for entry in manifest["servers"] + manifest["scripts"]:
        if not (ROOT / entry["path"]).is_file():
            errors.append(f"Missing delivered example: {entry['path']}")
    modules = sorted((ROOT / "modules").glob("[0-9][0-9]_*/README.md"))
    if release and len(modules) != 22:
        errors.append(f"Release needs 22 modules; {len(modules)} delivered.")
    for readme in modules:
        text = readme.read_text(encoding="utf-8")
        for section in SECTIONS:
            if f"## {section}" not in text:
                errors.append(f"{readme.parent.name}: missing section {section}")
        for folder in ("examples", "exercises", "solutions"):
            if len(list((readme.parent / "python" / folder).glob("[0-9][0-9]_*.py"))) < 3:
                errors.append(f"{readme.parent.name}: needs three {folder}")
        if not list((readme.parent / "wire").glob("*.jsonl")):
            errors.append(f"{readme.parent.name}: missing wire captures")
        for required in [
            "python/use_case/main.py",
            "python/tests/test_module.py",
            "quiz.md",
            "host_configs/vscode.json",
            "wire/manifest.json",
        ]:
            if not (readme.parent / required).is_file():
                errors.append(f"{readme.parent.name}: missing {required}")
        quiz = readme.parent / "quiz.md"
        if quiz.exists() and not 5 <= quiz.read_text(encoding="utf-8").count("<details>") <= 8:
            errors.append(f"{readme.parent.name}: quiz needs 5–8 expandable answers")
        if readme.parent.name[:2] in {"02", "03", "04", "05"}:
            for folder in ("examples", "exercises", "solutions"):
                if len(list((readme.parent / "typescript" / folder).glob("[0-9][0-9]_*.ts"))) < 3:
                    errors.append(f"{readme.parent.name}: needs three TypeScript {folder}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", action="store_true")
    args = parser.parse_args()
    errors = validate(args.release)
    print("Phase 3: modules 00-06 delivered; modules 07-21 remain planned.")
    for error in errors:
        print(error)
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
