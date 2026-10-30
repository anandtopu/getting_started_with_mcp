"""Compare shared semantic output across real Python and TypeScript processes."""

import pytest

from scripts.tier1 import script_client


@pytest.mark.anyio
async def test_note_and_rich_content_language_parity():
    results = []
    for language, extension in [("python", "py"), ("typescript", "ts")]:
        path = f"modules/02_first_server_tools/{language}/use_case/main.{extension}"
        async with script_client(path) as client:
            created = await client.call_tool(
                "create_note", {"title": "Parity", "body": "Same fixture", "confirmed": True}
            )
            tagged = await client.call_tool(
                "tag_note", {"note_id": 2, "tag": "checked", "confirmed": True}
            )
            found = await client.call_tool("search_notes", {"query": "Parity"})
            results.append(
                [created.structured_content, tagged.structured_content, found.structured_content]
            )
    assert results[0] == results[1]
    contents = []
    for language, extension in [("python", "py"), ("typescript", "ts")]:
        path = f"modules/02_first_server_tools/{language}/examples/02_rich_results.{extension}"
        async with script_client(path) as client:
            content = (await client.call_tool("review_assets", {})).content
            contents.append([c.model_dump(mode="json", exclude_none=True) for c in content])
    assert contents[0] == contents[1]


@pytest.mark.anyio
async def test_embedded_prompt_language_parity():
    messages = []
    for language, extension in [("python", "py"), ("typescript", "ts")]:
        path = f"modules/04_prompts/{language}/use_case/main.{extension}"
        async with script_client(path) as client:
            result = await client.get_prompt(
                "summarize_incident", {"space": "incident_postmortems", "page": "page-01"}
            )
            messages.append([m.model_dump(mode="json", exclude_none=True) for m in result.messages])
    assert messages[0] == messages[1]
