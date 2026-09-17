import importlib.util

import numpy as np


def _load(candidate_path):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_tests(candidate_path):
    failures = []
    try:
        m = _load(candidate_path)
    except Exception as e:  # noqa: BLE001
        return dict(passed=False, details=["candidate import failed: %s" % e])

    required = [
        "ghz_state",
        "mermin_operator",
        "expectation",
        "witness_value",
        "density_matrix",
        "run_checks",
    ]
    missing = [name for name in required if not hasattr(m, name)]
    if missing:
        failures.append("missing required function(s): %s" % ", ".join(missing))
        return dict(passed=False, details=failures)

    try:
        psi = np.asarray(m.ghz_state(), dtype=complex)
        if psi.shape != (8,):
            failures.append("ghz_state shape %s expected (8,)" % (psi.shape,))
        norm = float(np.sum(np.abs(psi) ** 2))
        if abs(norm - 1.0) > 1e-12:
            failures.append("ghz_state norm %.6f expected 1.0" % norm)
        amp0 = abs(psi[0])
        amp7 = abs(psi[7])
        if abs(amp0 - 0.5**0.5) > 1e-12 or abs(amp7 - 0.5**0.5) > 1e-12:
            failures.append("GHZ amplitudes must be (|000>+|111>)/sqrt(2)")
        mid = float(np.sum(np.abs(psi[1:7]) ** 2))
        if mid > 1e-12:
            failures.append("GHZ middle amplitudes must vanish")
    except Exception as e:  # noqa: BLE001
        failures.append("ghz_state raised: %s" % e)

    try:
        M = np.asarray(m.mermin_operator(), dtype=complex)
        if M.shape != (8, 8):
            failures.append("mermin_operator shape %s expected (8, 8)" % (M.shape,))
        psi = np.asarray(m.ghz_state(), dtype=complex)
        mexp = float(m.expectation(psi, M))
        if abs(abs(mexp) - 4.0) > 1e-9:
            failures.append("Mermin expectation %.6f expected magnitude 4.0" % mexp)
        w = float(m.witness_value(psi))
        if abs(w - 2.0) > 1e-9:
            failures.append("witness value %.6f expected 2.0" % w)
        if w <= 0:
            failures.append("witness must certify entanglement (positive)")
    except Exception as e:  # noqa: BLE001
        failures.append("mermin checks raised: %s" % e)

    try:
        psi = np.asarray(m.ghz_state(), dtype=complex)
        rho = np.asarray(m.density_matrix(psi), dtype=complex)
        if np.max(np.abs(rho - rho.conj().T)) > 1e-12:
            failures.append("density matrix must be Hermitian")
        if abs(float(np.trace(rho).real) - 1.0) > 1e-12:
            failures.append("density matrix trace must be 1")
        pur = float(np.sum(np.linalg.eigvalsh(rho) ** 2))
        if abs(pur - 1.0) > 1e-12:
            failures.append("GHZ density matrix must be pure (purity 1)")
    except Exception as e:  # noqa: BLE001
        failures.append("density matrix checks raised: %s" % e)

    try:
        res = m.run_checks()
        for key in ("m_exp", "witness", "is_pure"):
            if key not in res:
                failures.append("run_checks missing key %s" % key)
    except Exception as e:  # noqa: BLE001
        failures.append("run_checks raised: %s" % e)

    return dict(
        passed=not failures,
        details=failures
        or [
            "GHZ/MABK: |<M>| = 4 (LHV bound 2), witness +2, pure density matrix; "
            "all six entry points present"
        ],
    )
