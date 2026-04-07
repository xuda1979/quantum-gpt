from pkg.models import conflict_signature


def render_conflict_report(result: dict) -> dict:
    conflicts = result["conflicts"]
    return {
        "applied_count": len(result["applied_patch_ids"]),
        "applied_patch_ids": list(result["applied_patch_ids"]),
        "conflict_count": len(conflicts),
        "conflict_keys": [key for key, _ in map(conflict_signature, conflicts)],
        "conflict_reasons": [reason for _, reason in map(conflict_signature, conflicts)],
    }
