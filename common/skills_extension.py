"""Small Skills extension over the official SDK's additive method hooks.

Discovery is not activation. The client checks manifest bytes and leaves approval
to the host; it never executes instructions obtained from a resource.
"""

import hashlib

from mcp import Client
from mcp.server import MCPServer
from mcp.server.extension import Extension, MethodBinding
from mcp.shared.exceptions import MCPError
from mcp_types import Request, RequestParams, Result
from pydantic import ConfigDict

IDENTIFIER = "io.modelcontextprotocol/skills"
URI = "skill://incident-review/SKILL.md"
FILES = {
    URI: "---\nname: incident-review\ndescription: Review a synthetic incident timeline.\n---\n"
    "Read references/checklist.md. Report evidence before proposing a change.\n",
    "skill://incident-review/references/checklist.md": (
        "# Checklist\nIdentify impact, timeline, recovery owner and follow-up.\n"
    ),
}


def entry():
    return {
        "uri": URI,
        "frontmatter": {
            "name": "incident-review",
            "description": "Review a synthetic incident timeline.",
        },
        "resources": [
            {
                "uri": uri,
                "digest": "sha256:" + hashlib.sha256(text.encode()).hexdigest(),
                "size": len(text.encode()),
            }
            for uri, text in FILES.items()
        ],
    }


class GetParams(RequestParams):
    uri: str


class ListParams(RequestParams):
    cursor: str | None = None


class Skills(Extension):
    identifier = IDENTIFIER

    def methods(self):
        return [
            MethodBinding("skills/list", ListParams, self.list),
            MethodBinding("skills/get", GetParams, self.get),
        ]

    async def list(self, ctx, params):
        if params.cursor is not None:
            raise MCPError(-32602, "Unknown skill cursor.")
        return {"resultType": "complete", "skills": [entry()], "ttlMs": 0, "cacheScope": "private"}

    async def get(self, ctx, params):
        if params.uri != URI:
            raise MCPError(-32602, "Unknown skill URI.")
        return {"resultType": "complete", "skill": entry(), "ttlMs": 0, "cacheScope": "private"}


class ExtensionResult(Result):
    model_config = ConfigDict(extra="allow")


def skills_server():
    server = MCPServer("Lumen incident skills", extensions=[Skills()])
    # Exact URI registrations make ../ traversal and unknown supporting files impossible.
    for uri, content in FILES.items():

        def handler(text):
            def read():
                return text

            return read

        server.resource(uri, mime_type="text/markdown")(handler(content))
    return server


async def load_skill(client: Client):
    from common.connections import discover

    capabilities = (await discover(client)).capabilities
    if IDENTIFIER not in (capabilities.extensions or {}):
        raise ValueError("Server did not declare Skills support.")
    result = await client.session.send_request(
        Request(method="skills/list", params=ListParams()), ExtensionResult
    )
    listed = result.model_dump(by_alias=True)["skills"][0]
    result = await client.session.send_request(
        Request(method="skills/get", params=GetParams(uri=listed["uri"])), ExtensionResult
    )
    skill = result.model_dump(by_alias=True)["skill"]
    if skill != listed:
        raise ValueError("Skill manifest changed after discovery.")
    retrieved = {}
    for resource in skill["resources"]:
        contents = (await client.read_resource(resource["uri"])).contents
        text = contents[0].text
        if (
            len(text.encode()) != resource["size"]
            or "sha256:" + hashlib.sha256(text.encode()).hexdigest() != resource["digest"]
        ):
            raise ValueError("Skill content changed after manifest review.")
        retrieved[resource["uri"]] = text
    return {"verified_files": len(retrieved), "activated": False}
