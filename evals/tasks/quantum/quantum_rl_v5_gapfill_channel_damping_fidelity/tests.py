import importlib.util


def _load(candidate_path):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


RHO_1 = [[0.0, 0.0], [0.0, 1.0]]
RHO_0 = [[1.0, 0.0], [0.0, 0.0]]
RHO_PLUS = [[0.5, 0.5], [0.5, 0.5]]
I_HALF = [[0.5, 0.0], [0.0, 0.5]]


def _close(a, b, tol=1e-9):
    return all(abs(a[i][j] - b[i][j]) <= tol for i in range(2) for j in range(2))


def run_tests(candidate_path):
    failures = []
    try:
        m = _load(candidate_path)
    except Exception as e:  # noqa: BLE001
        return dict(passed=False, details=["candidate import failed: %s" % e])

    required = ["depolarizing_channel", "amplitude_damping_channel", "channel_fidelity"]
    missing = [name for name in required if not hasattr(m, name)]
    if missing:
        failures.append("missing required function(s): %s" % ", ".join(missing))
        return dict(passed=False, details=failures)

    try:
        if not _close(m.amplitude_damping_channel(RHO_1, 0.0), RHO_1):
            failures.append("gamma=0 must be the identity channel")
        if not _close(m.amplitude_damping_channel(RHO_1, 1.0), RHO_0):
            failures.append("gamma=1 must fully damp |1> to |0>")
        if not _close(m.depolarizing_channel(RHO_1, 0.0), RHO_1):
            failures.append("p=0 depolarizing must be identity")
        if not _close(m.depolarizing_channel(RHO_1, 1.0), I_HALF):
            failures.append("p=1 depolarizing must give I/2")
        if abs(m.channel_fidelity(RHO_PLUS, RHO_PLUS) - 1.0) > 1e-9:
            failures.append("channel_fidelity(rho, rho) must be 1")
        if abs(m.channel_fidelity(RHO_0, RHO_1)) > 1e-9:
            failures.append("channel_fidelity(|0>, |1>) must be 0")
        if abs(m.channel_fidelity(RHO_1, I_HALF) - 0.5) > 1e-9:
            failures.append("channel_fidelity(|1>, I/2) must be 0.5 (Tr=0.5, det product 0)")
    except Exception as e:  # noqa: BLE001
        failures.append("channel suite raised: %s" % e)

    return dict(passed=not failures, details=failures)
