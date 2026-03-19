def _normalize_username(name: str) -> str:
    return name.strip().lower().replace(" ", "_")


def build_user_record(name: str, email: str) -> dict[str, str]:
    username = _normalize_username(name)
    return {
        "name": name.strip(),
        "email": email.strip().lower(),
        "username": username,
    }


def build_audit_record(name: str, action: str) -> dict[str, str]:
    username = _normalize_username(name)
    return {
        "actor": username,
        "action": action.strip().lower(),
    }
