"""A tiny JSON-Schema validator.

Supports a useful subset of draft-07: `type`, `properties`, `required`,
`items` (list schemas), `enum`, `minimum`, `maximum`, `minItems`,
`maxItems`, and `additionalProperties: false`. Returns a list of
human-readable error strings (empty list = valid).
"""


def validate(schema: dict, instance) -> list[str]:
    """Validate `instance` against `schema`. Returns a list of error strings."""
    errors: list[str] = []
    _validate(schema, instance, "$", errors)
    return errors


def _validate(schema: dict, instance, path: str, errors: list[str]) -> None:
    if not isinstance(schema, dict):
        errors.append(f"{path}: schema must be an object")
        return

    if "enum" in schema:
        if instance not in schema["enum"]:
            errors.append(f"{path}: {instance!r} not in enum {schema['enum']!r}")
            return

    if "type" in schema:
        t = schema["type"]
        if t == "object":
            if not isinstance(instance, dict):
                errors.append(f"{path}: expected object, got {type(instance).__name__}")
                return
            _validate_object(schema, instance, path, errors)
        elif t == "array":
            if not isinstance(instance, list):
                errors.append(f"{path}: expected array, got {type(instance).__name__}")
                return
            _validate_array(schema, instance, path, errors)
        elif t == "string":
            if not isinstance(instance, str):
                errors.append(f"{path}: expected string, got {type(instance).__name__}")
        elif t == "integer":
            if not isinstance(instance, int) or isinstance(instance, bool):
                errors.append(f"{path}: expected integer, got {type(instance).__name__}")
        elif t == "number":
            if not isinstance(instance, (int, float)) or isinstance(instance, bool):
                errors.append(f"{path}: expected number, got {type(instance).__name__}")
        elif t == "boolean":
            if not isinstance(instance, bool):
                errors.append(f"{path}: expected boolean, got {type(instance).__name__}")
        elif t == "null":
            if instance is not None:
                errors.append(f"{path}: expected null")

    # numeric bounds apply to both integer and number
    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: {instance} < minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: {instance} > maximum {schema['maximum']}")


def _validate_object(schema, instance, path, errors):
    required = schema.get("required", [])
    for r in required:
        if r not in instance:
            errors.append(f"{path}: missing required property {r!r}")
    props = schema.get("properties", {})
    for k, v in instance.items():
        if k in props:
            _validate(props[k], v, f"{path}.{k}", errors)
        elif schema.get("additionalProperties") is False:
            errors.append(f"{path}: additional property {k!r} not allowed")


def _validate_array(schema, instance, path, errors):
    if "minItems" in schema and len(instance) < schema["minItems"]:
        errors.append(f"{path}: {len(instance)} items < minItems {schema['minItems']}")
    if "maxItems" in schema and len(instance) > schema["maxItems"]:
        errors.append(f"{path}: {len(instance)} items > maxItems {schema['maxItems']}")
    items = schema.get("items")
    if items is not None:
        for i, v in enumerate(instance):
            _validate(items, v, f"{path}[{i}]", errors)


def is_valid(schema: dict, instance) -> bool:
    return not validate(schema, instance)
