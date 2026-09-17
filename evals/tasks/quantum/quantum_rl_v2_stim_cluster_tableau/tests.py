import importlib.util

import numpy as np
import stim

I2 = np.eye(2, dtype=complex)
X2 = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
Z2 = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
Y2 = 1j * X2 @ Z2
SINGLE = {"_": I2, "I": I2, "X": X2, "Z": Z2, "Y": Y2}


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _pauli_matrix(pauli_string):
    mat = np.array([[1.0]])
    for ch in str(pauli_string)[1:]:
        mat = np.kron(mat, SINGLE[ch])
    if str(pauli_string)[0] == "-":
        mat = -mat
    return mat


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures: list[str] = []

    # --- circuit: no measurements ---
    try:
        circuit = module.cluster_circuit()
        n_meas = circuit.num_measurements
    except Exception as e:  # noqa: BLE001
        failures.append(f"cluster_circuit raised: {e}")
        n_meas = -1
    if n_meas != 0:
        failures.append(f"num_measurements={n_meas}, expected 0")

    # --- expected generators (sign and qubit-order conventions) ---
    generators = None
    try:
        generators = module.stabilizer_generators()
    except Exception as e:  # noqa: BLE001
        failures.append(f"stabilizer_generators raised: {e}")
    if generators is None or len(generators) != 4:
        n_g = len(generators) if generators is not None else 0
        failures.append(f"generator_count={n_g}, expected 4")
    else:
        expected = ["+XZ__", "+ZXZ_", "+_ZXZ", "+__ZX"]
        ok = 0
        for g, want in zip(generators, expected, strict=False):
            if isinstance(g, stim.PauliString) and str(g) == want:
                ok += 1
        if ok != 4:
            got = [str(g) for g in generators]
            failures.append(f"generators_matching={ok}, expected 4 (got {got})")
        # each generator must leave the prepared state invariant
        try:
            tableau = module.cluster_tableau()
            state = tableau.to_unitary_matrix(endian="big")[:, 0]
        except Exception as e:  # noqa: BLE001
            failures.append(f"cluster_tableau raised: {e}")
            state = None
        if state is not None:
            n_inv = 0
            for g in generators:
                if isinstance(g, stim.PauliString):
                    if np.allclose(_pauli_matrix(g) @ state, state, atol=1e-9):
                        n_inv += 1
            if n_inv != 4:
                failures.append(f"generator_invariants={n_inv}, expected 4")

    # --- combined tableau (circuit + inverse) is identity ---
    ident = None
    try:
        ident = bool(module.combined_tableau_is_identity())
    except Exception as e:  # noqa: BLE001
        failures.append(f"combined_tableau_is_identity raised: {e}")
    if ident is not None and not ident:
        failures.append("combined_identity=0, expected 1")

    # --- harness-side independent check of the inverse-appended tableau ---
    try:
        circuit = module.cluster_circuit()
        circuit += stim.Tableau.from_circuit(circuit).inverse().to_circuit()
        combined = stim.Tableau.from_circuit(circuit)
        n_ok = 0
        for i in range(4):
            z_exp = stim.PauliString("_" * i + "Z" + "_" * (3 - i))
            x_exp = stim.PauliString("_" * i + "X" + "_" * (3 - i))
            if combined.z_output(i) == z_exp and combined.x_output(i) == x_exp:
                n_ok += 1
        if n_ok != 4:
            failures.append(f"combined_identity_checks={n_ok}, expected 4")
    except Exception as e:  # noqa: BLE001
        failures.append(f"harness inverse-appended tableau raised: {e}")

    return {
        "passed": not failures,
        "details": failures
        or [
            "4-qubit linear cluster: no measurements, stabilizers "
            "+XZ__/+ZXZ_/_ZXZ/__ZX via public z_output API, all 4 "
            "generators leave the state invariant, inverse-appended "
            "tableau is identity",
        ],
    }
