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

    gamma = 0.12
    ket1 = np.array([[0.0], [1.0]], dtype=complex)
    rho1 = ket1 @ ket1.conj().T

    required = ["kraus", "apply", "purity", "excited_state_survival", "run_checks"]
    missing = [name for name in required if not hasattr(m, name)]
    if missing:
        failures.append("missing required function(s): %s" % ", ".join(missing))
        return dict(passed=False, details=failures)

    ks = None
    try:
        ks = m.kraus(gamma)
        if len(ks) != 2:
            failures.append("kraus must return exactly 2 operators, got %s" % len(ks))
        else:
            total = np.zeros((2, 2), dtype=complex)
            for k in ks:
                total += k.conj().T @ k
            dev = float(np.max(np.abs(total - np.eye(2))))
            if dev > 1e-12:
                failures.append("completeness dev %.2e expected < 1e-12" % dev)
    except Exception as e:  # noqa: BLE001
        failures.append("kraus raised: %s" % e)

    try:
        out = np.asarray(m.apply(rho1, ks))
        p00 = float(np.real(out[0, 0]))
        if abs(p00 - gamma) > 1e-12:
            failures.append("E(|1>) top-left %.6f expected %.6f" % (p00, gamma))
        if abs(float(np.trace(out).real) - 1.0) > 1e-12:
            failures.append("E(|1>) trace must be 1")
        pur = float(m.purity(out))
        expected_pur = (1.0 - gamma) ** 2 + gamma**2
        if abs(pur - expected_pur) > 1e-9:
            failures.append("purity %.6f expected %.6f" % (pur, expected_pur))
    except Exception as e:  # noqa: BLE001
        failures.append("apply/purity checks raised: %s" % e)

    try:
        t = 2.0
        surv = float(m.excited_state_survival(t, gamma))
        import math

        if abs(surv - math.exp(-gamma * t)) > 1e-12:
            failures.append("survival must be exp(-gamma*t)")
    except Exception as e:  # noqa: BLE001
        failures.append("excited_state_survival raised: %s" % e)

    try:
        res = m.run_checks(gamma=gamma, t=1.0, seed=1)
        for key in ("ks_ok", "rho1_00", "purity_before", "purity_after"):
            if key not in res:
                failures.append("run_checks missing key %s" % key)
        if float(res.get("ks_ok", 1.0)) > 1e-12:
            failures.append("run_checks ks_ok must be < 1e-12")
        if float(res.get("purity_after", 1.0)) >= float(res.get("purity_before", 0.0)):
            failures.append("run_checks purity must drop on the seeded mixed state")
    except Exception as e:  # noqa: BLE001
        failures.append("run_checks raised: %s" % e)

    return dict(
        passed=not failures,
        details=failures
        or [
            "Amplitude damping gamma=0.12: Kraus complete, E(|1>) diag (0.88, 0.12), "
            "purity (1-g)^2+g^2, survival exp(-g t); all five entry points present"
        ],
    )
