import importlib.util


def _load(path: str):
    spec = importlib.util.spec_from_file_location("candidate", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def run_tests(candidate_path: str) -> dict:
    failures: list[str] = []
    try:
        mod = _load(candidate_path)
    except Exception as e:  # noqa: BLE001
        return {"passed": False, "details": [f"import failed: {e}"]}

    # 1. Kernel value is in [0, 1] and self-kernel is 1.0
    try:
        x = [0.2, 0.1, 0.1, 0.05]
        k_self = mod.kernel_value(x, x)
        if abs(k_self - 1.0) > 1e-6:
            failures.append(f"kernel_value(x, x) = {k_self:.6f}, expected 1.0")
        k_zero = mod.kernel_value([0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0])
        if not (0.0 <= k_zero <= 1.0):
            failures.append(f"kernel_value must be in [0,1], got {k_zero}")
    except Exception as e:  # noqa: BLE001
        failures.append(f"kernel_value() raised: {e}")

    # 2. kernel_matrix shape
    try:
        X, y = mod.iris_2class_subset(seed=0)
        K = mod.kernel_matrix(X, X)
        if K.shape != (20, 20):
            failures.append(f"kernel_matrix shape = {K.shape}, expected (20, 20)")
        if not ((K >= 0).all() and (K <= 1).all()):
            failures.append("kernel_matrix entries must be in [0, 1]")
    except Exception as e:  # noqa: BLE001
        failures.append(f"kernel_matrix() raised: {e}")

    # 3. End-to-end pipeline accuracy on the separable 2-class subset
    try:
        out = mod.run_pipeline()
        if out["accuracy"] < 0.85:
            failures.append(
                f"kernel-logreg accuracy {out['accuracy']:.3f} < 0.85 on separable subset"
            )
    except Exception as e:  # noqa: BLE001
        failures.append(f"run_pipeline() raised: {e}")

    return {
        "passed": not failures,
        "details": failures
        or ["PennyLane quantum kernel + logistic regression on Iris 2-class subset correct"],
    }
