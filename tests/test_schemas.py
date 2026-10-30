import pytest
from jsonschema import Draft202012Validator, ValidationError

from common.schemas import portable_schema


def test_local_reference_and_composition():
    schema = {
        "$defs": {"name": {"type": "string", "minLength": 1}},
        "type": "object",
        "properties": {"name": {"$ref": "#/$defs/name"}},
        "required": ["name"],
    }
    validator = Draft202012Validator(portable_schema(schema))
    validator.validate({"name": "Lumen"})
    with pytest.raises(ValidationError):
        validator.validate({"name": ""})
    with pytest.raises(ValidationError):
        Draft202012Validator({"oneOf": [{"type": "integer"}, {"type": "number"}]}).validate(3)


@pytest.mark.parametrize(
    "schema",
    [
        {"$ref": "https://example.invalid/schema"},
        {"$dynamicRef": "https://example.invalid/schema"},
        {"$defs": {"loop": {"$ref": "#/$defs/loop"}}, "$ref": "#/$defs/loop"},
        {"$ref": "#/$defs/missing"},
    ],
)
def test_reject_external_recursive_and_missing_refs(schema):
    with pytest.raises(ValueError):
        portable_schema(schema)


def test_schema_budget():
    with pytest.raises(ValueError, match="limit"):
        portable_schema({"anyOf": [{"type": "string"}] * 10}, max_nodes=5)
