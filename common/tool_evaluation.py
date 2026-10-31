"""Controlled task-completion evaluation; fixture results are not LLM evidence."""

import json
import time

from mcp import Client

from common.config import HELP, load_settings
from common.host import Host
from common.llm import create_tool_model
from common.protocol import SPEC_REVISION
from common.tool_design import mirror_server, rows, task_server
from common.tool_formats import ToolCall, Turn

CASES = [1, 13, 55, 112, 239, 400]


class EvaluationConfigurationError(ValueError):
    """Expected setup/usage failure, safe to show without a traceback."""

    def __init__(self, message: str):
        super().__init__(f"{message} {HELP}")


class EvidenceModel:
    def __init__(self, tool, arguments):
        self.tool, self.arguments = tool, arguments

    async def turn(self, tools, results):
        if not results:
            return Turn(calls=[ToolCall("lookup", self.tool, self.arguments)])
        payload = json.loads(results[0].text)["structuredContent"]
        return Turn(text=json.dumps({"id": payload["id"], "status": payload["status"]}))


async def evaluate(live=False, limit=6) -> dict:
    if type(limit) is not int or not 1 <= limit <= len(CASES):
        raise EvaluationConfigurationError("Evaluation limit must be an integer from 1 to 6.")
    try:
        settings = load_settings()
    except (ValueError, OSError):
        # Validation errors may contain raw configuration values; do not echo them.
        raise EvaluationConfigurationError(
            "Check LLM_PROVIDER, LLM_MODEL and the provider key in your environment or .env."
        ) from None
    if live and settings.provider == "fake":
        raise EvaluationConfigurationError("Choose a real LLM_PROVIDER and LLM_MODEL for --live.")
    output = {"mode": "live" if live else "deterministic plumbing only", "cases": limit}
    for label, factory, tool, parameter in [
        ("mirror", mirror_server, "get_issues", "row_id"),
        ("task_tools", task_server, "issue_brief", "issue_id"),
    ]:
        successes, durations, calls, catalog_chars = 0, [], [], 0
        async with Client(factory(), mode=SPEC_REVISION) as client:
            for issue_id in CASES[:limit]:
                prompt = (
                    f"Read issue {issue_id}. Return exactly a JSON object "
                    "with id and status. No other text."
                )

                async def approve(name, arguments):
                    return name.startswith("issues__")  # Both servers expose only read tools.

                host = Host({"issues": client}, approve, max_turns=4, max_calls=4)
                model = (
                    create_tool_model(prompt, settings)
                    if live
                    else EvidenceModel("issues__" + tool, {parameter: issue_id})
                )
                start = time.perf_counter()
                try:
                    answer = json.loads(await host.run(model))
                    expected = next(r for r in rows("issues") if r["id"] == issue_id)
                    # Match the TS contract: exact keys, JSON number (not bool),
                    # correct values, actual tool evidence and no failed calls.
                    successes += (
                        isinstance(answer, dict)
                        and set(answer) == {"id", "status"}
                        and type(answer["id"]) in (int, float)
                        and answer["id"] == issue_id
                        and answer["status"] == expected["status"]
                        and len(host.audit) > 0
                        and not any(reply.error for reply in host.audit)
                    )
                except (ValueError, RuntimeError, TimeoutError):
                    pass
                durations.append(round(time.perf_counter() - start, 4))
                calls.append(len(host.audit))
                catalog_chars = len(json.dumps(host.tools))
            output[label] = {
                "completed": successes,
                "tools": len((await client.list_tools()).tools),
                "catalog_characters": catalog_chars,
                "calls": calls,
                "seconds": durations,
            }
    return output
