from pkg.helpers import normalize_name, suffix_for_kind


def transform(name: str, kind: str) -> dict:
    normalized = normalize_name(name)
    return {
        "name": normalized,
        "kind": kind,
        "tag": normalized + suffix_for_kind(kind),
    }
