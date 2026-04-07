def _normalize_username(name: str) -> str:
    return name.strip().lower().replace(" ", "_")


def build_user_record(name: str, email: str) -> dict[str, str]:
    return {
        "name": name.strip(),
        "email": email.strip().lower(),
        "username": _normalize_username(name),
    }


def build_audit_record(name: str, action: str) -> dict[str, str]:
    return {
        "actor": _normalize_username(name),
        "action": action.strip().lower(),
    }
