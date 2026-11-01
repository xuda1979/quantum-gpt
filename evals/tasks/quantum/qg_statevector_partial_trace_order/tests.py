"""SAPO RL harness for qg_statevector_partial_trace_order (C-10611 v26 corpus task).

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
        check(module.trace_out_first)
    except AssertionError as exc:
        return {"passed": False, "details": [f"check failed: {exc}"]}
    except Exception as exc:  # noqa: BLE001 — candidate errors are task signal
        return {"passed": False, "details": [f"{type(exc).__name__}: {exc}"]}
    return {"passed": True, "details": ["ok"]}


def check(candidate):
    import numpy as np
    m = candidate()
    assert m.shape == (2, 2)
    assert np.isclose(m[0, 0], 0.0, atol=1e-9)
    assert np.isclose(m[1, 1], 1.0, atol=1e-9)
