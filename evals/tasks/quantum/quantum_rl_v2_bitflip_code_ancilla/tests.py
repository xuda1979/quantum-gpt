import importlib.util
import math


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures: list[str] = []
    theta = 0.83
    exp_x_ideal = math.sin(theta)
    exp_z_ideal = math.cos(theta)

    # --- truth table: all four syndrome patterns map to the right qubit ---
    table = None
    try:
        table = module.syndrome_truth_table()
    except Exception as e:  # noqa: BLE001
        failures.append(f"syndrome_truth_table raised: {e}")
    if table is None:
        failures.append("truth_table_missing=0, expected 4 entries")
    else:
        expected = {(0, 0): -1, (1, 0): 0, (1, 1): 1, (0, 1): 2}
        ok = 0
        for key, want in expected.items():
            if table.get(key) == want:
                ok += 1
        if ok != 4:
            failures.append(f"truth_table_correct={ok}, expected 4")
        if len(table) != 4:
            failures.append(f"truth_table_entries={len(table)}, expected 4")

    # --- logical X with X error on data qubit 1 ---
    exp_x = None
    try:
        exp_x = float(module.logical_expectation(1, "X", shots=20000, seed=1234))
    except Exception as e:  # noqa: BLE001
        failures.append(f"logical_expectation(X) raised: {e}")
    if exp_x is not None:
        if abs(exp_x - exp_x_ideal) > 0.04:
            failures.append(f"logical_X={exp_x:.6f}, expected {exp_x_ideal:.6f} within 0.04")

    # --- logical Z with X error on data qubit 1 ---
    exp_z = None
    try:
        exp_z = float(module.logical_expectation(1, "Z", shots=20000, seed=1234))
    except Exception as e:  # noqa: BLE001
        failures.append(f"logical_expectation(Z) raised: {e}")
    if exp_z is not None:
        if abs(exp_z - exp_z_ideal) > 0.04:
            failures.append(f"logical_Z={exp_z:.6f}, expected {exp_z_ideal:.6f} within 0.04")

    # --- error-free baseline: no error injected should also match ---
    exp_x0 = None
    try:
        exp_x0 = float(module.logical_expectation(-1, "X", shots=20000, seed=1234))
    except Exception as e:  # noqa: BLE001
        failures.append(f"logical_expectation(X, no error) raised: {e}")
    if exp_x0 is not None and abs(exp_x0 - exp_x_ideal) > 0.04:
        failures.append(f"logical_X_noerror={exp_x0:.6f}, expected {exp_x_ideal:.6f} within 0.04")

    # --- circuit structure: encode + syndrome + correction + decode ---
    try:
        qc = module.build_circuit(1, "Z")
        nq = qc.num_qubits
        n_m = qc.num_ancillas  # noqa: F841 (ancilla qubits counted separately)

        n_cl = len(qc.clbits)
        if nq != 6:
            failures.append(f"circuit_qubits={nq}, expected 6")
        if n_cl != 3:
            failures.append(f"classical_bits={n_cl}, expected 3")
    except Exception as e:  # noqa: BLE001
        failures.append(f"build_circuit raised: {e}")

    return {
        "passed": not failures,
        "details": failures
        or [
            f"3-qubit bit-flip code, RY(0.83): syndrome truth table 4/4, "
            f"logical X {exp_x:.4f} vs ideal {exp_x_ideal:.4f}, "
            f"logical Z {exp_z:.4f} vs ideal {exp_z_ideal:.4f}, "
            "within 0.04 with X error on data qubit 1",
        ],
    }
