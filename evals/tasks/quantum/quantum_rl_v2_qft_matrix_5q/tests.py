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
    n = 5
    n_states = 1 << n
    omega = np.exp(2.0j * np.pi / n_states)

    # --- direct matrix: dims and entries F[j,k] = omega^(jk)/sqrt(N) ---
    direct = None
    try:
        direct = module.qft_matrix(n)
    except Exception as e:  # noqa: BLE001
        failures.append(f"qft_matrix raised: {e}")
    if direct is not None:
        if direct.shape != (n_states, n_states):
            failures.append(f"qft_matrix_shape={direct.shape}, expected ({n_states}, {n_states})")
        else:
            j = np.arange(n_states).reshape(-1, 1)
            k = np.arange(n_states).reshape(1, -1)
            expected = (omega ** (j * k)) / np.sqrt(n_states)
            if float(np.max(np.abs(direct - expected))) > 1e-9:
                failures.append(
                    f"direct_matrix_deviation={float(np.max(np.abs(direct - expected))):.3e}, expected 0.0"
                )
            norm = float(np.max(np.abs(direct @ direct.conj().T - np.eye(n_states, dtype=complex))))
            if norm > 1e-9:
                failures.append(f"direct_unitarity={norm:.3e}, expected 0.0")

    # --- gate-based matrix ---
    gates = None
    try:
        gates = module.qft_gate_matrix(n)
    except Exception as e:  # noqa: BLE001
        failures.append(f"qft_gate_matrix raised: {e}")
    if gates is not None:
        if gates.shape != (n_states, n_states):
            failures.append(f"gate_matrix_shape={gates.shape}, expected ({n_states}, {n_states})")
        else:
            norm = float(np.max(np.abs(gates @ gates.conj().T - np.eye(n_states, dtype=complex))))
            if norm > 1e-9:
                failures.append(f"gate_unitarity={norm:.3e}, expected 0.0")
            # align global phase and compare with the direct matrix
            aligned = None
            try:
                aligned = module.align_global_phase(direct, gates)
            except Exception as e:  # noqa: BLE001
                failures.append(f"align_global_phase raised: {e}")
            if aligned is not None:
                diff = float(np.max(np.abs(direct - aligned)))
                if diff > 1e-9:
                    failures.append(f"matrix_max_diff={diff:.6f}, expected <= 0.000000001")
            # inverse round trip on basis state |1>
            e1 = np.zeros(n_states, dtype=complex)
            e1[1] = 1.0
            back = gates.conj().T @ (gates @ e1)
            if float(np.max(np.abs(back - e1))) > 1e-9:
                failures.append(
                    f"roundtrip_error={float(np.max(np.abs(back - e1))):.3e}, expected 0.0"
                )
            # image of basis state |1>: amplitudes omega^j/sqrt(N)
            img = gates @ e1
            expected_img = np.array([omega**j / np.sqrt(n_states) for j in range(n_states)])
            diff_img = float(np.max(np.abs(img - expected_img)))
            if diff_img > 1e-9:
                failures.append(f"basis_image_error={diff_img:.6f}, expected <= 0.000000001")
            # symmetry of the image: |amp_j| uniform = 1/sqrt(N)
            if abs(float(np.max(np.abs(np.abs(img) - 1.0 / np.sqrt(n_states)))) > 1e-9):
                failures.append(
                    f"image_amplitude_spread={float(np.max(np.abs(np.abs(img) - 1.0/np.sqrt(n_states)))):.3e}, expected 0.0"
                )

    # --- helper: 3-qubit block consistency of the direct matrix ---
    try:
        d3 = module.qft_matrix(3)
        if d3.shape != (8, 8):
            failures.append(f"qft_matrix(3)_shape={d3.shape}, expected (8, 8)")
    except Exception as e:  # noqa: BLE001
        failures.append(f"qft_matrix(3) raised: {e}")

    return {
        "passed": not failures,
        "details": failures
        or [
            "5-qubit QFT: direct omega^(jk)/sqrt(N) matrix and the embedded "
            "H + controlled-phase + SWAP construction agree to 1e-9 after "
            "phase alignment; unitarity, |1> image and inverse round trip "
            "exact"
        ],
    }
