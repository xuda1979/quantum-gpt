import importlib.util
import math

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
    a, b = 1.0, 2.0

    # --- expectations: <X> = cos(a)sin(b), <Z> = cos(a)cos(b) ---
    try:
        expect = np.asarray(module.expectations(a, b), dtype=float)
        exp_x = math.cos(a) * math.sin(b)
        exp_z = math.cos(a) * math.cos(b)
        if abs(expect[0] - exp_x) > 1e-9:
            failures.append(f"expect_x={expect[0]:.4f}, expected {exp_x:.4f}")
        if abs(expect[1] - exp_z) > 1e-9:
            failures.append(f"expect_z={expect[1]:.4f}, expected {exp_z:.4f}")
    except Exception as e:  # noqa: BLE001
        failures.append(f"expectations raised: {e}")

    # --- analytic Jacobian J[i,j] = d O_i / d p_j ---
    J = np.array(
        [
            [-math.sin(a) * math.sin(b), math.cos(a) * math.cos(b)],
            [-math.sin(a) * math.cos(b), -math.cos(a) * math.sin(b)],
        ]
    )
    jacobians = {
        "qml": (module.qml_jacobian_matrix(a, b), "jac_dev_qml"),
        "shift": (module.shift_jacobian(a, b), "jac_dev_shift"),
        "fd": (module.fd_jacobian(a, b), "jac_dev_fd"),
    }
    for name, (Jcand, key) in jacobians.items():
        try:
            Jcand = np.asarray(Jcand, dtype=float)
            if Jcand.shape != (2, 2):
                failures.append(f"{name}_shape={Jcand.shape}, expected (2, 2)")
            else:
                dev = float(np.max(np.abs(Jcand - J)))
                if dev > 1e-6:
                    failures.append(f"{key}={dev:.4f}, expected < 1e-6")
                if abs(Jcand[0, 0] - J[0, 0]) > 1e-6:
                    failures.append(f"{name}_00={Jcand[0, 0]:.4f}, expected {J[0, 0]:.4f}")
                if abs(Jcand[1, 1] - J[1, 1]) > 1e-6:
                    failures.append(f"{name}_11={Jcand[1, 1]:.4f}, expected {J[1, 1]:.4f}")
        except Exception as e:  # noqa: BLE001
            failures.append(f"{name} jacobian raised: {e}")

    # --- pairwise agreement within 1e-7 ---
    try:
        result = module.run_checks(a=1.0, b=2.0)
        for key in ("max_dev_qml_shift", "max_dev_qml_fd", "max_dev_shift_fd"):
            dev = float(result.get(key, 1.0))
            if dev > 1e-7:
                failures.append(f"{key}={dev:.2e}, expected < 1e-7")
    except Exception as e:  # noqa: BLE001
        failures.append(f"run_checks raised: {e}")

    return {
        "passed": not failures,
        "details": failures
        or [
            "QML Jacobian RX(a)RY(b) at (1.0,2.0): <X>=0.4913 <Z>=-0.2248, "
            "qml.jacobian/shift/finite-diff all match analytic J "
            "[[-0.7651,-0.2248],[0.3502,-0.4913]] with pairwise dev < 1e-7",
        ],
    }
