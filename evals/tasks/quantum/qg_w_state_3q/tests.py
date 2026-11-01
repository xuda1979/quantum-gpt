"""SAPO RL harness for qg_w_state_3q (C-10611 v26 corpus task).

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
        check(module.w_state_3)
    except AssertionError as exc:
        return {"passed": False, "details": [f"check failed: {exc}"]}
    except Exception as exc:  # noqa: BLE001 — candidate errors are task signal
        return {"passed": False, "details": [f"{type(exc).__name__}: {exc}"]}
    return {"passed": True, "details": ["ok"]}


def check(candidate):
    import numpy as np
    from qiskit.quantum_info import Statevector
    qc = candidate()
    sv = Statevector(qc)
    probs = np.abs(np.asarray(sv)) ** 2
    # support exactly on |001>, |010>, |100>
    target = {0b001: 1/3, 0b010: 1/3, 0b100: 1/3}
    for idx, p in enumerate(probs):
        if idx in target:
            assert np.isclose(p, target[idx], atol=1e-8)
        else:
            assert p < 1e-8
