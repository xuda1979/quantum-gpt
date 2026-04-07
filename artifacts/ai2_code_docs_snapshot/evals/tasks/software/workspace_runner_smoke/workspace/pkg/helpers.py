def normalize_name(name: str) -> str:
    return name.strip().lower().replace(" ", "_")


def suffix_for_kind(kind: str) -> str:
    return {
        "alpha": "-A",
        "beta": "-B",
    }[kind]
