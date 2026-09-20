import importlib.util

import numpy as np


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures: list[str] = []

    # --- graph and maxcut value ---
    try:
        edges = module.maxcut_ring4_edges()
    except Exception as e:  # noqa: BLE001
        edges = None
        failures.append(f"maxcut_ring4_edges raised: {e}")
    if edges is None:
        failures.append("maxcut_ring4_edges returned None, expected 4 edges")
        failures.append("edge_count=0, expected 4")
    else:
        expected_edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
        if list(edges) != expected_edges:
            failures.append(
                f"edge_count={len(list(edges)) if isinstance(edges, (list, tuple)) else 0}, expected 4"
            )

    try:
        opt = module.best_maxcut_value()
    except Exception as e:  # noqa: BLE001
        opt = None
        failures.append(f"best_maxcut_value raised: {e}")
    if opt is None:
        failures.append("best_maxcut_value=0, expected 4")
    elif opt != 4:
        failures.append(f"best_maxcut_value={opt}, expected 4")

    maxcut_checks = 0
    try:
        if module.maxcut_value("0101") == 4:
            maxcut_checks += 1
        if module.maxcut_value("0000") == 0:
            maxcut_checks += 1
        if module.maxcut_value("0011") == 2:
            maxcut_checks += 1
    except Exception as e:  # noqa: BLE001
        failures.append(f"maxcut_value raised: {e}")
    if maxcut_checks != 3:
        failures.append(f"maxcut_value_checks_correct={maxcut_checks}, expected 3")

    # --- circuit construction ---
    try:
        circuit = module.qaoa_ring4_circuit(0.6, 0.4)
    except Exception as e:  # noqa: BLE001
        circuit = None
        failures.append(f"qaoa_ring4_circuit raised: {e}")
    if circuit is None or not hasattr(circuit, "all_qubits"):
        failures.append("qaoa_ring4_circuit() did not return a Circuit-like object")
    else:
        try:
            qubits = sorted(circuit.all_qubits(), key=lambda q: q.x)
            n_qubits = len(qubits)
        except Exception:  # noqa: BLE001
            n_qubits = 0
        if n_qubits != 4:
            failures.append(f"qaoa_circuit_qubits={n_qubits}, expected 4")

    # --- exact expected cut at known points ---
    try:
        cut_0 = module.expected_cut_value(0.0, 0.0)
    except Exception as e:  # noqa: BLE001
        cut_0 = None
        failures.append(f"expected_cut_value raised: {e}")
    if cut_0 is None:
        failures.append("expected_cut_pi8=0.000000 need>=2.950000")
    else:
        if abs(cut_0 - 2.0) > 1e-6:
            failures.append(f"expected_cut_zero={cut_0:.6f}, expected 2.000000")
        # The p=1 optimum of the 4-ring is 3.0, reached near (pi/8, pi/8).
        try:
            cut_pi8 = module.expected_cut_value(np.pi / 8, np.pi / 8)
        except Exception as e:  # noqa: BLE001
            cut_pi8 = None
            failures.append(f"expected_cut_value(pi/8) raised: {e}")
        if cut_pi8 is None:
            failures.append("expected_cut_pi8=0.000000 need>=2.950000")
        elif cut_pi8 < 2.95:
            failures.append(f"expected_cut_pi8={cut_pi8:.6f} need>=2.950000")

    # --- angle optimization finds a good cut ---
    try:
        best = module.optimize_angles(steps=40, seed=0)
    except Exception as e:  # noqa: BLE001
        best = None
        failures.append(f"optimize_angles raised: {e}")
    if best is None or not isinstance(best, dict) or "cost" not in best:
        failures.append(
            "optimize_angles must return {'cost': float, 'gamma': float, 'beta': float}"
        )
        failures.append("best_cost=0.000000 need>=2.900000")
    else:
        cost = float(best["cost"])
        if cost < 2.9:
            failures.append(f"best_cost={cost:.6f} need>=2.900000")
        if cost > 4.0 + 1e-9:
            failures.append(f"best_cost={cost:.6f} above the physical maximum 4.0")

    return {
        "passed": not failures,
        "details": failures
        or ["QAOA ring-4 circuit, exact expected cut, and angle landscape all correct"],
    }
