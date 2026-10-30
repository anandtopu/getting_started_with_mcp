"""Resolve local tool schema references with explicit depth and size limits.

This teaching host accepts inline schemas and #/$defs references. It never fetches
external schemas. Provider support for complex composition remains model-specific.
"""

from copy import deepcopy


def portable_schema(schema: dict, max_depth: int = 12, max_nodes: int = 1000) -> dict:
    nodes = 0

    def visit(value, depth=0, trail=()):
        nonlocal nodes
        nodes += 1
        if nodes > max_nodes or depth > max_depth:
            raise ValueError("Schema size or depth limit exceeded.")
        if isinstance(value, list):
            return [visit(item, depth + 1, trail) for item in value]
        if not isinstance(value, dict):
            return value
        if "$dynamicRef" in value or "$recursiveRef" in value:
            raise ValueError("Dynamic and recursive schema references are not supported.")
        if "$ref" in value:
            ref = value["$ref"]
            if not isinstance(ref, str) or not ref.startswith("#/$defs/") or ref in trail:
                raise ValueError("Only non-recursive local #/$defs references are supported.")
            target = schema.get("$defs", {}).get(ref.removeprefix("#/$defs/"))
            if not isinstance(target, dict):
                raise ValueError("Missing local schema definition.")
            resolved = visit(target, depth + 1, (*trail, ref))
            siblings = {
                key: visit(item, depth + 1, trail) for key, item in value.items() if key != "$ref"
            }
            return {"allOf": [resolved, siblings]} if siblings else resolved
        return {key: visit(item, depth + 1, trail) for key, item in value.items() if key != "$defs"}

    return visit(deepcopy(schema))
