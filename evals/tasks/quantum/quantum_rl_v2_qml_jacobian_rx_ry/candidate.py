"""Two-parameter PennyLane QNode RX(a) RY(b) returning (<X>, <Z>).

At (a, b) = (1.0, 2.0) the Jacobian is computed three ways: qml.jacobian,
a manual parameter-shift Jacobian (shift pi/2 for each parameter), and a
central finite-difference Jacobian. All three must agree pairwise within
1e-7. The canonical layout is J[i, j] = d O_i / d p_j (output row,
parameter column); qml.jacobian's output is transposed to match."""

from __future__ import annotations

import math

import numpy as np
import pennylane as qml
import pennylane.numpy as pnp

DEVICE = qml.device("default.qubit", wires=1)


@qml.qnode(DEVICE)
def circuit(a: pnp.ndarray, b: pnp.ndarray) -> pnp.ndarray:
    """QNode returning the vector (<X>, <Z>) after RX(a) RY(b)."""
    qml.RX(a, wires=0)
    qml.RY(b, wires=0)
    return qml.math.stack([qml.expval(qml.PauliX(0)), qml.expval(qml.PauliZ(0))])


def expectations(a: float, b: float) -> np.ndarray:
    """(<X>, <Z>) at (a, b)."""
    return np.asarray(circuit(pnp.array(a), pnp.array(b)), dtype=float)


def qml_jacobian_matrix(a: float, b: float) -> np.ndarray:
    """2x2 Jacobian via qml.jacobian, layout J[i, j] = d O_i / d p_j.

    pennylane returns the transposed layout (param row, output column),
    so the matrix is transposed to the canonical (output, param) form."""
    ta = pnp.array(a, requires_grad=True)
    tb = pnp.array(b, requires_grad=True)
    raw = np.asarray(qml.jacobian(circuit)(ta, tb), dtype=float)
    return raw.T


def shift_jacobian(a: float, b: float) -> np.ndarray:
    """Manual parameter-shift Jacobian: (f(x+h) - f(x-h)) / 2, h = pi/2."""
    h = math.pi / 2.0
    out = np.zeros((2, 2))
    out[:, 0] = (
        np.asarray(circuit(pnp.array(a + h), pnp.array(b)), dtype=float)
        - np.asarray(circuit(pnp.array(a - h), pnp.array(b)), dtype=float)
    ) / 2.0
    out[:, 1] = (
        np.asarray(circuit(pnp.array(a), pnp.array(b + h)), dtype=float)
        - np.asarray(circuit(pnp.array(a), pnp.array(b - h)), dtype=float)
    ) / 2.0
    return out


def fd_jacobian(a: float, b: float, h: float = 1e-4) -> np.ndarray:
    """Central finite-difference Jacobian with step h."""
    out = np.zeros((2, 2))
    out[:, 0] = (
        np.asarray(circuit(pnp.array(a + h), pnp.array(b)), dtype=float)
        - np.asarray(circuit(pnp.array(a - h), pnp.array(b)), dtype=float)
    ) / (2.0 * h)
    out[:, 1] = (
        np.asarray(circuit(pnp.array(a), pnp.array(b + h)), dtype=float)
        - np.asarray(circuit(pnp.array(a), pnp.array(b - h)), dtype=float)
    ) / (2.0 * h)
    return out


def run_checks(a: float = 1.0, b: float = 2.0) -> dict:
    """All three Jacobians plus pairwise agreement deviations."""
    jac_qml = qml_jacobian_matrix(a, b)
    jac_shift = shift_jacobian(a, b)
    jac_fd = fd_jacobian(a, b)
    return {
        "expect": expectations(a, b),
        "jac_qml": jac_qml,
        "jac_shift": jac_shift,
        "jac_fd": jac_fd,
        "max_dev_qml_shift": float(np.max(np.abs(jac_qml - jac_shift))),
        "max_dev_qml_fd": float(np.max(np.abs(jac_qml - jac_fd))),
        "max_dev_shift_fd": float(np.max(np.abs(jac_shift - jac_fd))),
    }


def main():
    result = run_checks()
    print("expect =", result["expect"])
    print("jac_qml =", result["jac_qml"])
    print("jac_shift =", result["jac_shift"])
    print("jac_fd =", result["jac_fd"])
    for key in ("max_dev_qml_shift", "max_dev_qml_fd", "max_dev_shift_fd"):
        print(key, "=", result[key])
        assert result[key] < 1e-7, "%s must stay below 1e-7" % key


if __name__ == "__main__":
    main()
