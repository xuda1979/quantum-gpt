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

    # --- dataset ---
    try:
        X, y = module.make_xor_data()
    except Exception as e:  # noqa: BLE001
        X = y = None
        failures.append(f"make_xor_data raised: {e}")
    if X is None or y is None:
        failures.append("make_xor_data returned None, expected (16, 2) features and 16 labels")
        failures.append("data_points=0, expected 16")
    else:
        Xa = np.asarray(X, dtype=float)
        ya = np.asarray(y, dtype=float)
        if Xa.shape != (16, 2):
            failures.append(f"data_points={int(np.prod(Xa.shape) / 2)}, expected 16")
        else:
            if ya.sum() != 8:
                failures.append(f"class_balance={int(ya.sum())}, expected 8")
            # XOR ground truth check on the returned data
            correct = int(
                np.sum(
                    [
                        1.0 if (x0 * x1 > 0) == (yy == 1) else 0.0
                        for (x0, x1), yy in zip(Xa, ya)
                    ]
                )
            )
            if correct != 16:
                failures.append(f"data_labels_correct={correct}, expected 16")

    # --- training ---
    try:
        out = module.train_classifier(steps=60, seed=0)
    except Exception as e:  # noqa: BLE001
        out = None
        failures.append(f"train_classifier raised: {e}")
    if out is None or not isinstance(out, dict) or "accuracy" not in out:
        failures.append(
            "train_classifier must return {'accuracy': float, 'n': int, 'params': [...]}"
        )
        failures.append("accuracy=0.000000 need>=0.875000")
    else:
        acc = float(out["accuracy"])
        n = out.get("n")
        if n != 16:
            failures.append(f"train_n={n if n is not None else 0}, expected 16")
        # 14/16 = 0.875: a real variational circuit must classify the XOR
        # pattern substantially better than chance (0.5).
        if acc < 0.875:
            failures.append(f"accuracy={acc:.6f} need>=0.875000")
        params = out.get("params")
        if not isinstance(params, (list, tuple)) or len(params) != 4:
            failures.append(f"params_length={len(params) if params is not None else 0}, expected 4")

    # --- predict with the trained parameters ---
    if isinstance(out, dict) and isinstance(out.get("params"), (list, tuple)):
        X, y = module.make_xor_data()
        correct = 0
        try:
            for xi, yi in zip(X, y):
                if module.predict(out["params"], xi) == int(yi):
                    correct += 1
        except Exception as e:  # noqa: BLE001
            failures.append(f"predict raised: {e}")
        if correct != 16:
            failures.append(f"predict_correct={correct}, expected 16")

    return {
        "passed": not failures,
        "details": failures
        or ["Variational XOR classifier trains to high accuracy and predicts consistently"],
    }
