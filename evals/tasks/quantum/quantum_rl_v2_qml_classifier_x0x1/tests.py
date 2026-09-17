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

    # --- data: labels must match x0*x1 > 0, fixed balanced split ---
    data = None
    try:
        data = module.make_data()
    except Exception as e:  # noqa: BLE001
        failures.append(f"make_data raised: {e}")
    if data is not None:
        train_x, train_y, test_x, test_y = data
        if len(train_x) != len(train_y) or len(train_x) < 8:
            failures.append(f"train_size={len(train_x)}, expected >= 8")
        if len(test_x) != len(test_y) or len(test_x) < 4:
            failures.append(f"test_size={len(test_x)}, expected >= 4")
        wrong = 0
        for x, y in zip(np.asarray(train_x), np.asarray(train_y), strict=False):
            if float(x[0]) * float(x[1]) > 0:
                if float(y) != 1.0:
                    wrong += 1
            elif float(y) != 0.0:
                wrong += 1
        for x, y in zip(np.asarray(test_x), np.asarray(test_y), strict=False):
            if float(x[0]) * float(x[1]) > 0:
                if float(y) != 1.0:
                    wrong += 1
            elif float(y) != 0.0:
                wrong += 1
        if wrong != 0:
            failures.append(f"label_mismatches={wrong}, expected 0")
        # both classes must be present in train and test
        train_pos = int(np.sum(np.asarray(train_y) == 1.0))
        test_pos = int(np.sum(np.asarray(test_y) == 1.0))
        if train_pos == 0 or train_pos == len(train_y):
            failures.append(f"train_class_balance={train_pos}/{len(train_y)}")
        if test_pos == 0 or test_pos == len(test_y):
            failures.append(f"test_class_balance={test_pos}/{len(test_y)}")

    # --- training: loss decreases, accuracies, finite predictions ---
    result = None
    try:
        result = module.train()
    except Exception as e:  # noqa: BLE001
        failures.append(f"train raised: {e}")
    if result is None:
        failures.append("train_accuracy=0.00, expected >= 0.75")
        failures.append("test_accuracy=0.00, expected >= 0.75")
        failures.append("loss_decrease=0.00, expected >= 0.01")
    else:
        loss_first = result.get("loss_first")
        loss_last = result.get("loss_last")
        if loss_first is not None and loss_last is not None:
            if float(loss_last) >= float(loss_first):
                failures.append(
                    f"loss_decrease={float(loss_first) - float(loss_last):.6f}, "
                    "expected > 0.000000"
                )
        else:
            failures.append("loss_decrease=0.000000, expected > 0.000000")
        train_acc = result.get("train_accuracy")
        if train_acc is None:
            failures.append("train_accuracy=0.00, expected >= 0.75")
        elif float(train_acc) < 0.75:
            failures.append(f"train_accuracy={float(train_acc):.2f}, expected >= 0.75")
        test_acc = result.get("test_accuracy")
        if test_acc is None:
            failures.append("test_accuracy=0.00, expected >= 0.75")
        elif float(test_acc) < 0.75:
            failures.append(f"test_accuracy={float(test_acc):.2f}, expected >= 0.75")

    # --- predictions are finite ---
    params = result.get("params") if result else None
    bias = result.get("bias") if result else None
    if params is not None and bias is not None:
        train_x, _, test_x, _ = module.make_data()
        try:
            preds = [
                module.predict(np.array(params), np.asarray(x, dtype=float), float(bias))
                for x in test_x
            ]
            if not all(np.isfinite(float(p)) for p in preds):
                failures.append(
                    f"nonfinite_predictions={sum(1 for p in preds if not np.isfinite(float(p)))}, "
                    "expected 0"
                )
        except Exception as e:  # noqa: BLE001
            failures.append(f"predict raised: {e}")

    return {
        "passed": not failures,
        "details": failures
        or [
            "2-qubit PennyLane variational classifier on x0*x1>0: loss "
            "decreases, train/test accuracy >= 0.75, predictions finite",
        ],
    }
