def merge_config(defaults: dict, overrides: dict) -> dict:
    """Return a recursive merge of two configuration dictionaries.

    - Inputs are not mutated.
    - Nested dictionaries are merged recursively.
    - Any non-dict override replaces the default value entirely.
    """
    result = {}

    for key, value in defaults.items():
        if isinstance(value, dict):
            result[key] = merge_config(value, {})
        else:
            result[key] = value

    for key, override_value in overrides.items():
        default_value = result.get(key)
        if isinstance(default_value, dict) and isinstance(override_value, dict):
            result[key] = merge_config(default_value, override_value)
        elif isinstance(override_value, dict):
            result[key] = merge_config({}, override_value)
        else:
            result[key] = override_value

    return result
