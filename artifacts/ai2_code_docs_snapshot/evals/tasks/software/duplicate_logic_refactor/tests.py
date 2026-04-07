import importlib.util


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures = []

    user = module.build_user_record(" Ada Lovelace ", " ADA@EXAMPLE.COM ")
    audit = module.build_audit_record(" Ada Lovelace ", " LOGIN ")

    if user["username"] != "ada_lovelace":
        failures.append("user record username normalization failed")
    if audit["actor"] != "ada_lovelace":
        failures.append("audit record actor normalization failed")
    if not hasattr(module, "_normalize_username"):
        failures.append("expected shared helper _normalize_username to exist")

    return {"passed": not failures, "details": failures or ["shared normalization helper is used consistently"]}
