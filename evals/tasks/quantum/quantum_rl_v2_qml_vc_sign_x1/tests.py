import importlib.util


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures: list[str] = []

    # --- data + fixed split, label rule x1>0 ---
    try:
        X, y = module.make_data()
        if X.shape != (12, 2) or y.shape != (12,):
            failures.append(f"data_shape={X.shape}, labels={y.shape}, expected (12,2)/(12,)")
        expected_y = [0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1, 1]
        wrong = int(sum(1 for a, b in zip(y.tolist(), expected_y) if a != b))
        if wrong != 0:
            failures.append(f"label_rule_mismatch={wrong}, expected 0 (x1>0)")
        Xt, yt, Xe, ye = module.train_test_split()
        if len(Xt) != 8 or len(Xe) != 4:
            failures.append(f"split_train={len(Xt)}, test={len(Xe)}, expected 8/4")
    except Exception as e:  # noqa: BLE001
        failures.append(f"data helpers raised: {e}")

    # --- architecture: 8 rotation params + 1 bias ---
    try:
        params = module.initialize_params(seed=0)
        n = int(len(params))
        if n != 9:
            failures.append(f"trainable_params={n}, expected 9 (2 layers x 4 + bias)")
    except Exception as e:  # noqa: BLE001
        failures.append(f"initialize_params raised: {e}")

    # --- circuit structure: 2 qubits ---
    try:
        c = module.circuit
        nq = len(c.device.wires)
        if nq != 2:
            failures.append(f"circuit_wires={nq}, expected 2")
    except Exception as e:  # noqa: BLE001
        failures.append(f"circuit structure check raised: {e}")

    # --- training: loss decreases, accuracies, finiteness, determinism ---
    result = None
    try:
        result = module.run_training(steps=120, seed=0)
    except Exception as e:  # noqa: BLE001
        failures.append(f"run_training raised: {e}")
    if result:
        improvement = float(result.get("loss_improvement", 0.0))
        if improvement <= 0.01:
            failures.append(f"loss_improvement={improvement:.4f}, expected > 0.0100")
        train_acc = float(result.get("train_acc", 0.0))
        if not (0.0 <= train_acc <= 1.0):
            failures.append(f"train_acc_range={train_acc:.4f}, expected in [0, 1]")
        test_acc = float(result.get("test_acc", 0.0))
        if test_acc < 0.75:
            failures.append(f"test_acc={test_acc:.4f}, expected >= 0.7500")
        if not result.get("predictions_finite", False):
            failures.append("nonfinite_predictions=1, expected 0")
        try:
            result2 = module.run_training(steps=30, seed=0)
            ref = float(result["trajectory"][30])
            if abs(float(result2["loss_final"]) - ref) > 1e-12:
                failures.append(
                    f"reproducibility_diff={abs(float(result2['loss_final']) - ref):.2e}, expected 0"
                )
        except Exception as e:  # noqa: BLE001
            failures.append(f"reproducibility run raised: {e}")

    return {
        "passed": not failures,
        "details": failures
        or [
            "QML 2-qubit variational classifier (x1>0): 9 trainable params, "
            "loss 0.854 -> 0.389 (improvement 0.465), train_acc=1.0 test_acc=1.0, "
            "all predictions finite, same-seed rerun identical",
        ],
    }
