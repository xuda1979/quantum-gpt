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

    # --- independent dense DFT reference ---
    dft = None
    try:
        dft = module.dft2_matrix()
    except Exception as e:  # noqa: BLE001
        failures.append(f"dft2_matrix raised: {e}")
    if dft is not None:
        if dft.shape != (4, 4):
            failures.append(f"dft_shape={dft.shape}, expected (4, 4)")
        else:
            # verify the reference itself: F[j,k] = i^(jk)/2 (N=4)
            expected = (
                np.array(
                    [
                        [1, 1, 1, 1],
                        [1, 1j, -1, -1j],
                        [1, -1, 1, -1],
                        [1, -1j, -1, 1j],
                    ]
                )
                / 2.0
            )
            if float(np.max(np.abs(dft - expected))) > 1e-12:
                failures.append(
                    f"dft_reference_deviation={float(np.max(np.abs(dft - expected))):.3e}, expected 0.0"
                )

    # --- repaired circuit-style routine matches the DFT ---
    qm = None
    try:
        qm = module.qft2_matrix()
    except Exception as e:  # noqa: BLE001
        failures.append(f"qft2_matrix raised: {e}")
    if qm is not None and dft is not None:
        if qm.shape != (4, 4):
            failures.append(f"qft2_matrix_shape={qm.shape}, expected (4, 4)")
        else:
            aligned = None
            try:
                aligned = module.align_global_phase(dft, qm)
            except Exception as e:  # noqa: BLE001
                failures.append(f"align_global_phase raised: {e}")
            if aligned is not None:
                diff = float(np.max(np.abs(dft - aligned)))
                if diff > 1e-9:
                    failures.append(f"qft_matrix_deviation={diff:.6f}, expected <= 0.000000001")
            un = float(np.max(np.abs(qm.conj().T @ qm - np.eye(4, dtype=complex))))
            if un > 1e-9:
                failures.append(f"qft_unitarity={un:.3e}, expected 0.0")

    # --- every computational basis state maps correctly ---
    if qm is not None and dft is not None:
        for k in range(4):
            e = np.zeros(4, dtype=complex)
            e[k] = 1.0
            try:
                out = module.qft2_statevector(e)
            except Exception as ex:  # noqa: BLE001
                failures.append(f"qft2_statevector(|{k}>) raised: {ex}")
                continue
            expected_col = dft[:, k]
            diff = float(np.max(np.abs(np.asarray(out).reshape(-1) - expected_col)))
            if diff > 1e-9:
                failures.append(f"basis_state_error={diff:.6f} (|{k}>), expected <= 0.000000001")

    # --- forward then inverse = identity up to global phase ---
    if qm is not None:
        for k in range(4):
            e = np.zeros(4, dtype=complex)
            e[k] = 1.0
            try:
                back, orig = module.forward_inverse_roundtrip(e)
            except Exception as ex:  # noqa: BLE001
                failures.append(f"forward_inverse_roundtrip(|{k}>) raised: {ex}")
                continue
            # up to global phase: compare after phase alignment
            if float(np.real(np.vdot(orig, orig))) <= 0.0:
                continue
            phase = np.angle(np.vdot(orig, back))
            aligned = back * np.exp(-1.0j * phase)
            diff = float(np.max(np.abs(aligned - orig)))
            if diff > 1e-9:
                failures.append(f"roundtrip_error={diff:.6f} (|{k}>), expected <= 0.000000001")

    # --- regression checks: must catch wrong sign / missing swaps ---
    try:
        bug_dev = float(module.regression_checks())
    except AssertionError as e:  # noqa: BLE001
        failures.append(f"regression_checks assertion failed: {e}")
        bug_dev = None
    except Exception as e:  # noqa: BLE001
        failures.append(f"regression_checks raised: {e}")
        bug_dev = None
    if bug_dev is not None and not (bug_dev > 0.1):
        failures.append(f"regression_buggy_deviation={bug_dev:.4f}, expected > 0.1000")

    # --- the buggy routine must demonstrably differ from the DFT ---
    try:
        m_buggy = np.zeros((4, 4), dtype=complex)
        for k in range(4):
            e = np.zeros(4, dtype=complex)
            e[k] = 1.0
            m_buggy[:, k] = module.buggy_qft2_statevector(e)
        d_bug = float(np.max(np.abs(m_buggy - dft)))
        if not (d_bug > 0.1):
            failures.append(f"buggy_deviation={d_bug:.4f}, expected > 0.1000")
    except Exception as e:  # noqa: BLE001
        failures.append(f"buggy routine check raised: {e}")

    return {
        "passed": not failures,
        "details": failures
        or [
            "repaired 2-qubit QFT matches the dense DFT reference on all "
            "four basis states, is unitary, round-trips through the inverse "
            "up to global phase, and regression_checks catches the wrong "
            "phase sign / missing SWAP defects"
        ],
    }
