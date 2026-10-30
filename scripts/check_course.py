"""Validate delivered course files, captures and printable references.

Run: uv run python scripts/check_course.py [--release]
--release also requires all Phase 8 bonuses, capstones and reference material.
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
    if release:
        from pypdf import PdfReader

        for index in range(1, 6):
            if not list((ROOT / "capstones").glob(f"{index:02d}_*/README.md")):
                errors.append(f"Release needs Phase 8 capstone {index}.")
        for index in range(1, 5):
            if not list((ROOT / "modules/bonus").glob(f"B{index}_*/README.md")):
                errors.append(f"Release needs Phase 8 bonus B{index}.")
        for readme in (ROOT / "modules/bonus").glob("B*/README.md"):
            content = readme.read_text(encoding="utf-8")
            for section in SECTIONS:
                if f"## {section}" not in content:
                    errors.append(f"{readme.parent.name}: missing {section}")
            for required in ["quiz.md", "wire/manifest.json", "host_configs/vscode.json"]:
                if not (readme.parent / required).is_file():
                    errors.append(f"{readme.parent.name}: missing {required}")
            quiz = (readme.parent / "quiz.md").read_text(encoding="utf-8")
            if not 5 <= quiz.count("<details>") <= 8:
                errors.append(f"{readme.parent.name}: needs 5-8 quiz answers")
        for folder in (ROOT / "capstones").glob("[0-9][0-9]_*"):
            for required in [
                "starter/main.py",
                "solution/main.py",
                "tests/test_capstone.py",
                "eval/cases.jsonl",
                "security_checklist.md",
                "rubric.md",
                "extend_it.md",
                "wire/main.jsonl",
            ]:
                if not (folder / required).is_file():
                    errors.append(f"{folder.name}: missing {required}")
        for document in [
            "MENTAL_MODEL",
            "PROTOCOL_GUIDE",
            "CHOOSING_THE_RIGHT_DESIGN",
            "HOST_SETUP",
            "SECURITY_CHECKLIST",
            "GLOSSARY",
            "TROUBLESHOOTING",
            "MIGRATING_FROM_OLDER_VERSIONS",
            "VERIFICATION_NOTES",
            "DEFINITION_OF_DONE",
        ]:
            if not (ROOT / f"docs/{document}.md").is_file():
                errors.append(f"Missing reference {document}")
        from scripts.protocol_guide import CORE, EXTENSIONS

        coverage = json.loads((ROOT / "docs/protocol_coverage.json").read_text())
        if set(coverage) != set(CORE) | set(EXTENSIONS):
            errors.append("Protocol reference lacks a current method or notification")
        sheets = list((ROOT / "cheatsheets").glob("*.pdf"))
        if len(sheets) != 6 or any(len(PdfReader(path).pages) != 1 for path in sheets):
            errors.append("Release needs six one-page PDF sheets")
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
        if release or readme.parent.name[:2] in {"02", "03", "04", "05", "10"}:
            for folder in ("examples", "exercises", "solutions"):
                if len(list((readme.parent / "typescript" / folder).glob("[0-9][0-9]_*.ts"))) < 3:
                    errors.append(f"{readme.parent.name}: needs three TypeScript {folder}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", action="store_true")
    args = parser.parse_args()
    errors = validate(args.release)
    print("Phase 8: modules 00-21, four bonuses, five capstones and final references.")
    for error in errors:
        print(error)
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
