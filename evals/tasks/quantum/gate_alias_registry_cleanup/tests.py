import importlib.util
from types import ModuleType


def _load(candidate_path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures = []

    try:
        normalized = module.normalize_gate_sequence(["  h", "Pauli_X", "controlled-X"])
        if normalized != ["H", "X", "CX"]:
            failures.append(f"normalized = {normalized}, expected ['H','X','CX']")
    except Exception as exc:  # pragma: no cover - diagnostic
        failures.append(f"normalize gate sequence raised {type(exc).__name__}: {exc}")

    custom_registry = {"zz": "Z", "zzz": "Z"}
    try:
        normalized_custom = module.normalize_gate_sequence(
            ["ZZ"], alias_registry={**module.canonical_registry(), "zz": "Z", "zzz": "Z"}
        )
        if normalized_custom != ["Z"]:
            failures.append("custom registry did not resolve 'ZZ'")
    except ValueError as exc:
        failures.append(f"custom registry raised ValueError: {exc}")

    try:
        module.normalize_gate_sequence(["unknown"])
        failures.append("unknown alias did not raise ValueError")
    except ValueError:
        pass

    return {"passed": not failures, "details": failures or ["gate alias registry cleanup looks good"]}
