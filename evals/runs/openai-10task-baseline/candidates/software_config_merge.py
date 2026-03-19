def merge_config(defaults: dict, overrides: dict) -> dict:
    """Recursively merge configuration dictionaries without mutating inputs.

    If both the default value and override value for a key are dicts, they are
    merged recursively. Otherwise, the override value replaces the default
    value entirely. Keys present only in overrides are added to the result.
    """
    result = dict(defaults)

    for key, override_value in overrides.items():
        default_value = defaults.get(key)

        if isinstance(default_value, dict) and isinstance(override_value, dict):
            result[key] = merge_config(default_value, override_value)
        else:
            result[key] = override_value

    return result
