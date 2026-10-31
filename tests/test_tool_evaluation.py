"""Shared cross-language grading cases and the beginner-facing CLI boundary."""

import json
import os
import subprocess
import sys

import pytest

from common import tool_evaluation as evaluation
from common.config import ROOT, Settings
from common.tool_formats import ToolCall, Turn

REPLAYS = json.loads((ROOT / "tests/fixtures/tool_evaluation.json").read_text())


@pytest.mark.anyio
@pytest.mark.parametrize("replay", REPLAYS, ids=lambda replay: replay["name"])
async def test_shared_grading_contract(replay, monkeypatch):
    expected = next(row for row in evaluation.rows("issues") if row["id"] == 1)

    class ReplayModel:
        def __init__(self):
            self.turns = iter(replay["turns"])
            self.calls = 0

        async def turn(self, tools, results):
            step = next(self.turns)
            if step.get("failure"):
                raise RuntimeError("Private provider failure")
            if "calls" in step:
                mirror = any(tool["name"] == "issues__get_issues" for tool in tools)
                calls = []
                for issue_id in step["calls"]:
                    self.calls += 1
                    calls.append(
                        ToolCall(
                            str(self.calls),
                            "issues__get_issues" if mirror else "issues__issue_brief",
                            {"row_id" if mirror else "issue_id": issue_id},
                        )
                    )
                return Turn(calls=calls)
            answer = step["raw"] if "raw" in step else json.dumps(step["answer"])
            return Turn(text=answer.replace("$status", expected["status"]))

    monkeypatch.setattr(evaluation, "load_settings", lambda: Settings(provider="ollama"))
    monkeypatch.setattr(evaluation, "create_tool_model", lambda *_: ReplayModel())
    result = await evaluation.evaluate(live=True, limit=1)
    for catalog in ("mirror", "task_tools"):
        assert result[catalog]["completed"] == replay["completed"]


@pytest.mark.parametrize("limit", [0, 7, 1.5, True])
@pytest.mark.anyio
async def test_invalid_limits_are_usage_errors(limit):
    with pytest.raises(evaluation.EvaluationConfigurationError, match="scripts/check_env.py"):
        await evaluation.evaluate(limit=limit)


@pytest.mark.parametrize(
    ("provider", "model", "arguments"),
    [
        ("fake", "fixture", ["--live"]),
        ("PRIVATE_PROVIDER_SENTINEL", "fixture", ["--live"]),
        ("ollama", "fixture", ["--live"]),
        ("openai", "configured-model", ["--live"]),
        ("fake", "fixture", ["--limit", "0"]),
    ],
)
def test_cli_configuration_errors_are_friendly(provider, model, arguments):
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "modules/14_tool_design/python/examples/03_measure_change.py"),
            *arguments,
        ],
        cwd=ROOT,
        env={
            **os.environ,
            "LLM_PROVIDER": provider,
            "LLM_MODEL": model,
            "OPENAI_API_KEY": "",
            "ANTHROPIC_API_KEY": "",
            "GEMINI_API_KEY": "",
        },
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert result.returncode == 1
    assert not result.stdout
    assert "scripts/check_env.py" in result.stderr
    assert "Traceback" not in result.stderr
    assert "PRIVATE_PROVIDER_SENTINEL" not in result.stderr
