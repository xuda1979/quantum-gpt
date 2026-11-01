"""SAPO RL harness for qg_random_unitary_seed (C-10611 v26 corpus task).

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
        check(module.seeded_random_unitary)
    except AssertionError as exc:
        return {"passed": False, "details": [f"check failed: {exc}"]}
    except Exception as exc:  # noqa: BLE001 — candidate errors are task signal
        return {"passed": False, "details": [f"{type(exc).__name__}: {exc}"]}
    return {"passed": True, "details": ["ok"]}


def check(candidate):
    import numpy as np
    from qiskit.quantum_info import Operator
    u = candidate()
    m = np.asarray(u)
    assert np.allclose(m @ m.conj().T, np.eye(4), atol=1e-9)
