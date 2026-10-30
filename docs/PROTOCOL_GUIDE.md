# Read the MCP protocol

Target: **2026-07-28**. This guide inventories all ten current core request methods and all eight current server-notification names, plus the Tasks and Skills methods this course implements. The schema has no current top-level server-request methods; elicitation is embedded in an input-required result. Direction and transport restrictions still apply. Legacy methods are explained only in the [migration guide](MIGRATING_FROM_OLDER_VERSIONS.md).

## Read one envelope

`jsonrpc` identifies the message format. A request has `id`, `method` and `params`; a response repeats `id` with either `result` or `error`. A notification has no ID and gets no response. Each current client request supplies protocol revision, client identity and capabilities under reserved `_meta` keys. The server reports its identity in result metadata. IDs correlate messages; they are not credentials.

`resultType: complete` means the operation finished, not necessarily that it succeeded: inspect `isError` on tool results. `input_required` asks the host to collect input, then retry with fresh request ID, exact opaque requestState and keyed inputResponses. Only a negotiated extension can introduce a different result such as a Task handle. Approval remains separate from protocol shape.

HTTP uses the same JSON-RPC bodies with current routing/version headers. The SDK derives those headers from the body. Inspect [actual HTTP captures](../modules/10_streamable_http/wire/manifest.json) for successful requests and rejected Host/Origin/header combinations. A notification and a JSON-RPC error are different from an HTTP status failure.

## Captured method reference

Every block below is copied intact from a committed capture, including synthetic values and redaction. The source link identifies the full conversation; a shortest successful exchange keeps this reference readable. `scripts/protocol_guide.py` regenerates it and fails when a required method lacks evidence.

### `server/discover`

Discover versions and capabilities; cache according to ttlMs and cacheScope. [Specification](https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning).

[Actual capture](../modules/02_first_server_tools/wire/typescript_01_hello_server.jsonl).

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "server/discover",
  "params": {
    "_meta": {
      "io.modelcontextprotocol/protocolVersion": "2026-07-28",
      "io.modelcontextprotocol/clientInfo": {
        "name": "mcp",
        "version": "0.1.0"
      },
      "io.modelcontextprotocol/clientCapabilities": {}
    }
  }
}
```

The same ID identifies this response:

```json
{
  "result": {
    "supportedVersions": [
      "2026-07-28"
    ],
    "capabilities": {
      "tools": {
        "listChanged": true
      }
    },
    "resultType": "complete",
    "ttlMs": 0,
    "cacheScope": "private",
    "_meta": {
      "io.modelcontextprotocol/serverInfo": {
        "name": "Lumen hello",
        "version": "1.0"
      }
    }
  },
  "jsonrpc": "2.0",
  "id": 1
}
```
### `tools/list`

List callable tools and schemas; follow bounded nextCursor pages. [Specification](https://modelcontextprotocol.io/specification/2026-07-28/server/tools).

[Actual capture](../modules/01_architecture_wire/wire/03_wiretap_client.jsonl).

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {
    "_meta": {
      "io.modelcontextprotocol/protocolVersion": "2026-07-28",
      "io.modelcontextprotocol/clientInfo": {
        "name": "mcp",
        "version": "0.1.0"
      },
      "io.modelcontextprotocol/clientCapabilities": {}
    }
  }
}
```

The same ID identifies this response:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "resultType": "complete",
    "_meta": {
      "io.modelcontextprotocol/serverInfo": {
        "name": "Lumen raw directory",
        "version": "1.0"
      }
    },
    "ttlMs": 0,
    "cacheScope": "private",
    "tools": [
      {
        "name": "directory_count",
        "description": "Count the synthetic employee sample.",
        "inputSchema": {
          "type": "object",
          "properties": {},
          "additionalProperties": false
        },
        "annotations": {
          "readOnlyHint": true,
          "destructiveHint": false,
          "idempotentHint": true,
          "openWorldHint": false
        }
      }
    ]
  }
}
```
### `tools/call`

Call one tool; distinguish protocol errors from a complete result with isError. [Specification](https://modelcontextprotocol.io/specification/2026-07-28/server/tools).

[Actual capture](../modules/bonus/B2_other_sdks/wire/java.jsonl).

```json
{
  "jsonrpc": "2.0",
  "id": 9,
  "method": "tools/call",
  "params": {
    "name": "tag_note",
    "arguments": {
      "note_id": 2,
      "tag": "reviewed",
      "confirmed": true
    }
  }
}
```

The same ID identifies this response:

```json
{
  "jsonrpc": "2.0",
  "id": 9,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"id\":2,\"tags\":[\"reviewed\"]}"
      }
    ],
    "isError": false
  }
}
```
### `resources/list`

List concrete resource URIs; listing does not read their content. [Specification](https://modelcontextprotocol.io/specification/2026-07-28/server/resources).

[Actual capture](../modules/bonus/B2_other_sdks/wire/java.jsonl).

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "resources/list"
}
```

The same ID identifies this response:

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "resources": [
      {
        "uri": "lumen://notes/help",
        "name": "Notes policy",
        "mimeType": "text/plain"
      }
    ]
  }
}
```
### `resources/templates/list`

List URI templates and their variable patterns. [Specification](https://modelcontextprotocol.io/specification/2026-07-28/server/resources).

[Actual capture](../docs/wire/foundation_server.jsonl).

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "resources/templates/list",
  "params": {
    "_meta": {
      "io.modelcontextprotocol/protocolVersion": "2026-07-28",
      "io.modelcontextprotocol/clientInfo": {
        "name": "mcp",
        "version": "0.1.0"
      },
      "io.modelcontextprotocol/clientCapabilities": {}
    }
  }
}
```

The same ID identifies this response:

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "cacheScope": "private",
    "resourceTemplates": [],
    "resultType": "complete",
    "ttlMs": 0,
    "_meta": {
      "io.modelcontextprotocol/serverInfo": {
        "name": "Lumen foundation",
        "version": ""
      }
    }
  }
}
```
### `resources/read`

Read addressable content; treat returned instructions as untrusted data. [Specification](https://modelcontextprotocol.io/specification/2026-07-28/server/resources).

[Actual capture](../modules/bonus/B2_other_sdks/wire/java.jsonl).

```json
{
  "jsonrpc": "2.0",
  "id": 11,
  "method": "resources/read",
  "params": {
    "uri": "lumen://notes/help"
  }
}
```

The same ID identifies this response:

```json
{
  "jsonrpc": "2.0",
  "id": 11,
  "result": {
    "contents": [
      {
        "uri": "lumen://notes/help",
        "mimeType": "text/plain",
        "text": "Review exact note text before creating. Restart clears writes."
      }
    ]
  }
}
```
### `prompts/list`

List reusable templates and their named arguments. [Specification](https://modelcontextprotocol.io/specification/2026-07-28/server/prompts).

[Actual capture](../modules/bonus/B2_other_sdks/wire/java.jsonl).

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "prompts/list"
}
```

The same ID identifies this response:

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "result": {
    "prompts": [
      {
        "name": "review_notes",
        "description": "Review notes without changing them",
        "arguments": []
      }
    ]
  }
}
```
### `prompts/get`

Render a selected template; the host controls whether to use its messages. [Specification](https://modelcontextprotocol.io/specification/2026-07-28/server/prompts).

[Actual capture](../modules/bonus/B2_other_sdks/wire/java.jsonl).

```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "prompts/get",
  "params": {
    "name": "review_notes"
  }
}
```

The same ID identifies this response:

```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "result": {
    "description": "Read-only review",
    "messages": [
      {
        "role": "user",
        "content": {
          "type": "text",
          "text": "Search release notes and cite evidence. Do not write without approval."
        }
      }
    ]
  }
}
```
### `completion/complete`

Suggest values for one prompt or URI-template argument. [Specification](https://modelcontextprotocol.io/specification/2026-07-28/server/utilities/completion).

[Actual capture](../modules/03_resources/wire/python_main.jsonl).

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "completion/complete",
  "params": {
    "ref": {
      "type": "ref/resource",
      "uri": "wiki://{space}/{page}"
    },
    "argument": {
      "name": "space",
      "value": "eng"
    },
    "_meta": {
      "io.modelcontextprotocol/protocolVersion": "2026-07-28",
      "io.modelcontextprotocol/clientInfo": {
        "name": "mcp",
        "version": "0.1.0"
      },
      "io.modelcontextprotocol/clientCapabilities": {}
    }
  }
}
```

The same ID identifies this response:

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "result": {
    "completion": {
      "values": [
        "engineering"
      ]
    },
    "resultType": "complete",
    "_meta": {
      "io.modelcontextprotocol/serverInfo": {
        "name": "Lumen wiki",
        "version": "2.0"
      }
    }
  }
}
```
### `subscriptions/listen`

Open a filtered event stream; acknowledgment starts its lifetime. [Specification](https://modelcontextprotocol.io/specification/2026-07-28/basic/patterns/subscriptions).

[Actual capture](../modules/04_prompts/wire/python_main.jsonl).

```json
{
  "jsonrpc": "2.0",
  "id": "listen-3",
  "method": "subscriptions/listen",
  "params": {
    "notifications": {
      "promptsListChanged": true
    },
    "_meta": {
      "io.modelcontextprotocol/protocolVersion": "2026-07-28",
      "io.modelcontextprotocol/clientInfo": {
        "name": "mcp",
        "version": "0.1.0"
      },
      "io.modelcontextprotocol/clientCapabilities": {}
    }
  }
}
```

The stream is acknowledged by the notification shown next; it remains open until closed/cancelled.
### `notifications/subscriptions/acknowledged`

Confirm that a listener has been registered. [Specification](https://modelcontextprotocol.io/specification/2026-07-28/basic/patterns/subscriptions).

[Actual capture](../modules/04_prompts/wire/python_main.jsonl).

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/subscriptions/acknowledged",
  "params": {
    "_meta": {
      "io.modelcontextprotocol/subscriptionId": "listen-3"
    },
    "notifications": {
      "promptsListChanged": true
    }
  }
}
```
### `notifications/resources/updated`

Invalidate the named content; refetch under the current identity. [Specification](https://modelcontextprotocol.io/specification/2026-07-28/server/resources).

[Actual capture](../modules/03_resources/wire/python_main.jsonl).

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/resources/updated",
  "params": {
    "_meta": {
      "io.modelcontextprotocol/subscriptionId": "listen-1"
    },
    "uri": "lumen://bulletin"
  }
}
```
### `notifications/resources/list_changed`

Invalidate a resource catalog; do not infer the new contents. [Specification](https://modelcontextprotocol.io/specification/2026-07-28/server/resources).

[Actual capture](../modules/03_resources/wire/python_main.jsonl).

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/resources/list_changed",
  "params": {
    "_meta": {
      "io.modelcontextprotocol/subscriptionId": "listen-1"
    }
  }
}
```
### `notifications/tools/list_changed`

Refetch tool definitions and require a new review if semantics changed. [Specification](https://modelcontextprotocol.io/specification/2026-07-28/server/tools).

[Actual capture](../modules/03_resources/wire/python_main.jsonl).

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/tools/list_changed",
  "params": {
    "_meta": {
      "io.modelcontextprotocol/subscriptionId": "listen-1"
    }
  }
}
```
### `notifications/prompts/list_changed`

Refetch available prompt definitions. [Specification](https://modelcontextprotocol.io/specification/2026-07-28/server/prompts).

[Actual capture](../modules/04_prompts/wire/python_main.jsonl).

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/prompts/list_changed",
  "params": {
    "_meta": {
      "io.modelcontextprotocol/subscriptionId": "listen-3"
    }
  }
}
```
### `notifications/progress`

Report progress correlated by a progress token; this is not the final result. [Specification](https://modelcontextprotocol.io/specification/2026-07-28/basic/utilities/progress).

[Actual capture](../modules/08_server_utilities/wire/python_main.jsonl).

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/progress",
  "params": {
    "progressToken": "[REDACTED]",
    "progress": 1,
    "total": 4,
    "message": "Q1: section 1"
  }
}
```
### `notifications/cancelled`

Request cooperative cancellation; reconcile uncertain side effects. [Specification](https://modelcontextprotocol.io/specification/2026-07-28/basic/utilities/cancellation).

[Actual capture](../modules/08_server_utilities/wire/python_main.jsonl).

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/cancelled",
  "params": {
    "requestId": 4,
    "reason": "caller cancelled"
  }
}
```
### `notifications/message`

Deprecated optional protocol logging still present in this revision. The capture opts into info; application lessons use stderr/OpenTelemetry. [Specification](https://modelcontextprotocol.io/specification/2026-07-28/server/utilities/logging).

[Actual capture](../docs/wire/logging_reference.jsonl).

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/message",
  "params": {
    "level": "info",
    "logger": "lumen.reference",
    "data": "Synthetic reference diagnostic"
  }
}
```
### `tasks/get`

Poll one owned task; completed state includes its original operation result. [Specification](https://modelcontextprotocol.io/extensions/tasks/overview).

[Actual capture](../modules/bonus/B1_typescript_track/wire/tasks.jsonl).

```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "method": "tasks/get",
  "params": {
    "taskId": "jKMH9P-RoERzTGNlNyX15Xt5z9r1N2EP",
    "_meta": {
      "io.modelcontextprotocol/protocolVersion": "2026-07-28",
      "io.modelcontextprotocol/clientInfo": {
        "name": "mcp",
        "version": "0.1.0"
      },
      "io.modelcontextprotocol/clientCapabilities": {
        "elicitation": {
          "form": {},
          "url": {}
        },
        "extensions": {
          "io.modelcontextprotocol/tasks": {}
        }
      }
    }
  }
}
```

The same ID identifies this response:

```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "result": {
    "resultType": "complete",
    "taskId": "jKMH9P-RoERzTGNlNyX15Xt5z9r1N2EP",
    "status": "cancelled",
    "createdAt": "2026-10-30T19:40:26.549Z",
    "lastUpdatedAt": "2026-10-30T19:40:26.550Z",
    "ttlMs": 300000,
    "pollIntervalMs": 25,
    "_meta": {
      "io.modelcontextprotocol/serverInfo": {
        "name": "Lumen raw TypeScript",
        "version": "1"
      }
    }
  }
}
```
### `tasks/update`

Supply an answer to a task input request; do not send an unrelated confirmation. [Specification](https://modelcontextprotocol.io/extensions/tasks/overview).

[Actual capture](../modules/16_composition/wire/python_main.jsonl).

```json
{
  "jsonrpc": "2.0",
  "id": 8,
  "method": "tasks/update",
  "params": {
    "taskId": "csiVQNP4_KLBIkCP2VnhiZ_iBtVW50XK",
    "inputResponses": {
      "details-1": {
        "action": "accept",
        "content": {
          "include_details": true
        }
      }
    },
    "_meta": {
      "io.modelcontextprotocol/protocolVersion": "2026-07-28",
      "io.modelcontextprotocol/clientInfo": {
        "name": "mcp",
        "version": "0.1.0"
      },
      "io.modelcontextprotocol/clientCapabilities": {
        "elicitation": {
          "form": {},
          "url": {}
        },
        "extensions": {
          "io.modelcontextprotocol/tasks": {}
        }
      }
    }
  }
}
```

The same ID identifies this response:

```json
{
  "jsonrpc": "2.0",
  "id": 8,
  "result": {
    "resultType": "complete",
    "_meta": {
      "io.modelcontextprotocol/serverInfo": {
        "name": "Lumen Gateway",
        "version": ""
      }
    }
  }
}
```
### `tasks/cancel`

Cancel pending work; terminal-state semantics stay with the extension. [Specification](https://modelcontextprotocol.io/extensions/tasks/overview).

[Actual capture](../modules/16_composition/wire/python_main.jsonl).

```json
{
  "jsonrpc": "2.0",
  "id": 11,
  "method": "tasks/cancel",
  "params": {
    "taskId": "FwpIZv1pRjGTRM63ItLvBbDrqivVCc2F",
    "_meta": {
      "io.modelcontextprotocol/protocolVersion": "2026-07-28",
      "io.modelcontextprotocol/clientInfo": {
        "name": "mcp",
        "version": "0.1.0"
      },
      "io.modelcontextprotocol/clientCapabilities": {
        "elicitation": {
          "form": {},
          "url": {}
        },
        "extensions": {
          "io.modelcontextprotocol/tasks": {}
        }
      }
    }
  }
}
```

The same ID identifies this response:

```json
{
  "jsonrpc": "2.0",
  "id": 11,
  "result": {
    "resultType": "complete",
    "_meta": {
      "io.modelcontextprotocol/serverInfo": {
        "name": "Lumen Gateway",
        "version": ""
      }
    }
  }
}
```
### `skills/list`

Discover skill manifests without activating instructions. [Specification](https://modelcontextprotocol.io/extensions/skills/overview).

[Actual capture](../modules/bonus/B4_whats_new/wire/skills.jsonl).

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "skills/list",
  "params": {
    "_meta": {
      "io.modelcontextprotocol/protocolVersion": "2026-07-28",
      "io.modelcontextprotocol/clientInfo": {
        "name": "mcp",
        "version": "0.1.0"
      },
      "io.modelcontextprotocol/clientCapabilities": {}
    }
  }
}
```

The same ID identifies this response:

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "resultType": "complete",
    "skills": [
      {
        "uri": "skill://incident-review/SKILL.md",
        "frontmatter": {
          "name": "incident-review",
          "description": "Review a synthetic incident timeline."
        },
        "resources": [
          {
            "uri": "skill://incident-review/SKILL.md",
            "digest": "sha256:f88056dfd96e139170ef26572f70366d09f262f50c7030ba8321729ec6bb618b",
            "size": 154
          },
          {
            "uri": "skill://incident-review/references/checklist.md",
            "digest": "sha256:b54bdd4c25da620f86a11cdac7429d66a19d53017064e7a8b9863b364429f27c",
            "size": 69
          }
        ]
      }
    ],
    "ttlMs": 0,
    "cacheScope": "private",
    "_meta": {
      "io.modelcontextprotocol/serverInfo": {
        "name": "Lumen incident skills",
        "version": ""
      }
    }
  }
}
```
### `skills/get`

Get one manifest and verify its bytes before a separate activation decision. [Specification](https://modelcontextprotocol.io/extensions/skills/overview).

[Actual capture](../modules/bonus/B4_whats_new/wire/skills.jsonl).

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "skills/get",
  "params": {
    "uri": "skill://incident-review/SKILL.md",
    "_meta": {
      "io.modelcontextprotocol/protocolVersion": "2026-07-28",
      "io.modelcontextprotocol/clientInfo": {
        "name": "mcp",
        "version": "0.1.0"
      },
      "io.modelcontextprotocol/clientCapabilities": {}
    }
  }
}
```

The same ID identifies this response:

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "resultType": "complete",
    "skill": {
      "uri": "skill://incident-review/SKILL.md",
      "frontmatter": {
        "name": "incident-review",
        "description": "Review a synthetic incident timeline."
      },
      "resources": [
        {
          "uri": "skill://incident-review/SKILL.md",
          "digest": "sha256:f88056dfd96e139170ef26572f70366d09f262f50c7030ba8321729ec6bb618b",
          "size": 154
        },
        {
          "uri": "skill://incident-review/references/checklist.md",
          "digest": "sha256:b54bdd4c25da620f86a11cdac7429d66a19d53017064e7a8b9863b364429f27c",
          "size": 69
        }
      ]
    },
    "ttlMs": 0,
    "cacheScope": "private",
    "_meta": {
      "io.modelcontextprotocol/serverInfo": {
        "name": "Lumen incident skills",
        "version": ""
      }
    }
  }
}
```
### `resources/directory/read`

Read a skill directory only when directoryRead was advertised. [Specification](https://modelcontextprotocol.io/extensions/skills/overview).

[Actual capture](../modules/bonus/B4_whats_new/wire/typescript_skills.jsonl).

```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "method": "resources/directory/read",
  "params": {
    "uri": "skill://incident-review/references",
    "_meta": {
      "io.modelcontextprotocol/protocolVersion": "2026-07-28",
      "io.modelcontextprotocol/clientInfo": {
        "name": "mcp",
        "version": "0.1.0"
      },
      "io.modelcontextprotocol/clientCapabilities": {
        "elicitation": {
          "form": {},
          "url": {}
        }
      }
    }
  }
}
```

The same ID identifies this response:

```json
{
  "result": {
    "resources": [
      {
        "uri": "skill://incident-review/references/checklist.md",
        "name": "checklist.md",
        "mimeType": "text/markdown",
        "size": 59
      }
    ],
    "ttlMs": 0,
    "cacheScope": "private",
    "resultType": "complete",
    "_meta": {
      "io.modelcontextprotocol/serverInfo": {
        "name": "Lumen TypeScript skills",
        "version": "1.0"
      }
    }
  },
  "jsonrpc": "2.0",
  "id": 6
}
```

## Input, extensions and authentication

For embedded `elicitation/create`, see the [form and URL retry capture](../modules/09_elicitation_sampling_roots/wire/python_main.jsonl) and the [TypeScript form capture](../modules/bonus/B1_typescript_track/wire/forms.jsonl). The complete input-required response and retry are shown in [Module 09](../modules/09_elicitation_sampling_roots/README.md). Sampling and roots remain deprecated compatibility vocabulary; their old/current replacements are in the migration guide. An accepted form is not an OAuth grant.

Tasks begin when an operation returns a handle; there is no separate current task-create method. Polls, updates and cancellation use the extension methods above. [Tasks evidence](../modules/bonus/B1_typescript_track/wire/tasks.jsonl) includes TypeScript-server/Python-client interoperability. MCP Apps use a separate UI bridge; [the official bridge test](../common/typescript/apps.test.ts) covers initialization, results, allowed refresh and teardown. The browser boundary is tested in [Chat Pro](../capstones/05_lumen_chat_pro/README.md).

OAuth discovery and token exchanges are HTTP, not invented JSON-RPC methods. Inspect [machine](../modules/bonus/B4_whats_new/wire/machine.jsonl) and [enterprise](../modules/bonus/B4_whats_new/wire/enterprise.jsonl) captures with credentials redacted. Server Cards are HTTP metadata candidates, not an MCP permission grant.

## Errors to recognize

| Error | Meaning | Response |
|---|---|---|
| -32700 / -32600 | Invalid JSON / invalid JSON-RPC envelope | Fix serialization before retrying |
| -32601 / -32602 | Unknown method / invalid parameters | Check revision, capability and schema |
| -32603 | Internal failure | Preserve redacted diagnostics; do not assume a write failed cleanly |
| -32020 | HTTP metadata/body mismatch | Let the SDK derive matching headers |
| -32021 | Missing client capability | Advertise only supported features or choose a fallback |
| -32022 | Unsupported protocol revision | Select an explicitly supported revision |
| Complete tool result with isError | Application-level tool failure | Read its message; do not treat it as successful evidence |

[Troubleshooting](TROUBLESHOOTING.md) · [Feature map](FEATURE_MAP.md) · [One-page protocol sheet](../cheatsheets/06_protocol.md)
