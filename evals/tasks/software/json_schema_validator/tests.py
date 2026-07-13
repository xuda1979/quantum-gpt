import importlib.util


def _load(path: str):
    spec = importlib.util.spec_from_file_location("candidate", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def run_tests(candidate_path: str) -> dict:
    failures: list[str] = []
    try:
        mod = _load(candidate_path)
    except Exception as e:  # noqa: BLE001
        return {"passed": False, "details": [f"import failed: {e}"]}

    schema = {
        "type": "object",
        "required": ["name", "age"],
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer", "minimum": 0, "maximum": 150},
            "tags": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        },
        "additionalProperties": False,
    }

    # 1. Valid instance
    ok = {"name": "alice", "age": 30, "tags": ["x"]}
    if mod.validate(schema, ok):
        failures.append(f"valid instance reported errors: {mod.validate(schema, ok)}")

    # 2. Missing required
    if not mod.validate(schema, {"age": 30}):
        failures.append("missing 'name' not detected")

    # 3. Wrong type
    if not mod.validate(schema, {"name": 42, "age": 30, "tags": ["x"]}):
        failures.append("wrong type for 'name' not detected")

    # 4. Numeric bound violation
    if not mod.validate(schema, {"name": "a", "age": -1, "tags": ["x"]}):
        failures.append("minimum bound not enforced")

    # 5. Array minItems
    if not mod.validate(schema, {"name": "a", "age": 30, "tags": []}):
        failures.append("minItems not enforced")

    # 6. additionalProperties: false
    if not mod.validate(schema, {"name": "a", "age": 30, "tags": ["x"], "extra": 1}):
        failures.append("additionalProperties:false not enforced")

    # 7. is_valid helper
    if not mod.is_valid(schema, ok):
        failures.append("is_valid returned False for a valid instance")
    if mod.is_valid(schema, {"age": 30}):
        failures.append("is_valid returned True for an invalid instance")

    # 8. enum support
    enum_schema = {"type": "string", "enum": ["red", "green", "blue"]}
    if not mod.validate(enum_schema, "purple"):
        failures.append("enum violation not detected")
    if mod.validate(enum_schema, "red"):
        failures.append("enum false positive on a valid value")

    return {
        "passed": not failures,
        "details": failures
        or [
            "JSON Schema validator handles type/required/properties/items/bounds/enum/additionalProperties"
        ],
    }
