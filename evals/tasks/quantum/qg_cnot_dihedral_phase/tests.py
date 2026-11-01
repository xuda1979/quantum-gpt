"""SAPO RL harness for qg_cnot_dihedral_phase (C-10611 v26 corpus task).

Contract: run_tests(candidate_path) -> {"passed": bool, "details": [str]}.
The check suite is the corpus builder's `check(candidate)` (G5-verified).
"""
import importlib.util


def _load(candidate_path):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    try:
        check(module.cnotdihedral_phase_poly)
    except AssertionError as exc:
        return {"passed": False, "details": [f"check failed: {exc}"]}
    except Exception as exc:  # noqa: BLE001 — candidate errors are task signal
        return {"passed": False, "details": [f"{type(exc).__name__}: {exc}"]}
    return {"passed": True, "details": ["ok"]}


def check(candidate):
    out = candidate()
    assert isinstance(out, str) and len(out) > 0
    s = out.replace(" ", "")
    # X0 → x_0 phase; CX propagates; Z1 adds x_1 (pi = 4 half-turns each)
    assert "4*x_0" in s, f"missing 4*x_0 term: {out!r}"
    assert "4*x_1" in s, f"missing 4*x_1 term: {out!r}"
    assert "x_0*x_1" not in s, f"unexpected mixed term: {out!r}"
