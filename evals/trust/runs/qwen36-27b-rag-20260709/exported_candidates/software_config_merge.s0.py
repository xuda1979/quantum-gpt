def merge_config(defaults: dict, overrides: dict) -> dict:
    """Recursively merge overrides into defaults without mutating inputs.

    Nested dicts should be merged recursively.
    Non-dict override values replace the default value entirely.
    """
    result = dict(defaults)
    for key, override_value in overrides.items():
        default_value = result.get(key)
        if isinstance(default_value, dict) and isinstance(override_value, dict):
            result[key] = merge_config(default_value, override_value)
        else:
            result[key] = override_value
    return result
