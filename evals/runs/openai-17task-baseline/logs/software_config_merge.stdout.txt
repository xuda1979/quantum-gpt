def merge_config(defaults: dict, overrides: dict) -> dict:
    """Recursively merge overrides into defaults without mutating inputs."""
    def clone_dict(value):
        result = {}
        for key, item in value.items():
            result[key] = clone_dict(item) if isinstance(item, dict) else item
        return result

    result = clone_dict(defaults)

    for key, override_value in overrides.items():
        if isinstance(result.get(key), dict) and isinstance(override_value, dict):
            result[key] = merge_config(result[key], override_value)
        else:
            result[key] = clone_dict(override_value) if isinstance(override_value, dict) else override_value

    return result
