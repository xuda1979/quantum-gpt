"""Quantum kernel matrix for 8 deterministic points in R^3.

The 3-qubit feature map angle-encodes the point with RY rotations
(AngleEmbedding) followed by one CZ on each unique ring edge
[(0, 1), (1, 2), (2, 0)]. Each kernel entry is K_ij =
|<phi(x_i)|phi(x_j)>|^2, computed through the adjoint-overlap circuit
(|0> -> U(x_j), then U^dagger(x_i), read P(0...0)) on default.qubit.
The full matrix must be symmetric, have unit diagonal, entries in
[0, 1], and be positive semidefinite up to eigenvalue tolerance
-1e-10. One entry is cross-checked from explicit state vectors."""

from __future__ import annotations

import numpy as np
import pennylane as qml

WIRES = [0, 1, 2]
RING_EDGES = [(0, 1), (1, 2), (2, 0)]

DEVICE = qml.device("default.qubit", wires=3)


def generate_data(seed: int = 42) -> np.ndarray:
    """8 deterministic points in R^3 from a seeded generator."""
    rng = np.random.RandomState(seed)
    return rng.uniform(-1.0, 1.0, size=(8, 3))


def feature_map(x: np.ndarray) -> None:
    """Angle encoding (RY) plus one CZ per unique ring edge."""
    qml.AngleEmbedding(x, wires=WIRES, rotation="Y")
    for a, b in RING_EDGES:
        qml.CZ(wires=[a, b])


@qml.qnode(DEVICE)
def _overlap_qnode(x_i: np.ndarray, x_j: np.ndarray) -> np.ndarray:
    """Adjoint-overlap circuit: |<phi(x_i)|phi(x_j)>|^2 = P(0...0)."""
    feature_map(x_j)
    qml.adjoint(feature_map)(x_i)
    return qml.probs(wires=WIRES)


@qml.qnode(DEVICE)
def _state_qnode(x: np.ndarray) -> np.ndarray:
    feature_map(x)
    return qml.state()


def kernel_entry(i: int, j: int, X: np.ndarray) -> float:
    """K_ij = |<phi(x_i)|phi(x_j)>|^2 via the adjoint-overlap circuit."""
    return float(_overlap_qnode(X[i], X[j])[0])


def kernel_matrix(X: np.ndarray) -> np.ndarray:
    """Symmetric 8x8 kernel matrix (diagonal filled via symmetry)."""
    n = len(X)
    K = np.zeros((n, n))
    for i in range(n):
        for j in range(i, n):
            value = kernel_entry(i, j, X)
            K[i, j] = value
            K[j, i] = value
    return K


def cross_check_entry(i: int, j: int, X: np.ndarray) -> float:
    """K_ij recomputed from explicit state vectors (independent path)."""
    psi_i = np.asarray(_state_qnode(X[i]))
    psi_j = np.asarray(_state_qnode(X[j]))
    return float(abs(np.vdot(psi_i, psi_j)) ** 2)


def run_kernel(seed: int = 42) -> dict:
    """End-to-end kernel construction with all verifiable quantities."""
    X = generate_data(seed)
    K = kernel_matrix(X)
    sym_dev = float(np.max(np.abs(K - K.T)))
    diag_dev = float(np.max(np.abs(np.diag(K) - 1.0)))
    eigvals = np.linalg.eigvalsh(K)
    cross = cross_check_entry(0, 1, X)
    return {
        "K": K,
        "min_eigval": float(eigvals[0]),
        "sym_dev": sym_dev,
        "diag_dev": diag_dev,
        "entry_min": float(K.min()),
        "entry_max": float(K.max()),
        "cross_dev": abs(cross - K[0, 1]),
        "cross_01": cross,
    }


def main():
    result = run_kernel()
    K = result["K"]
    print("min_eigval =", result["min_eigval"])
    print("sym_dev =", result["sym_dev"])
    print("diag_dev =", result["diag_dev"])
    print("entry_min =", result["entry_min"], "entry_max =", result["entry_max"])
    print("cross_dev =", result["cross_dev"])
    assert result["sym_dev"] < 1e-12, "kernel must be symmetric"
    assert result["diag_dev"] < 1e-12, "diagonal must be 1"
    assert -1e-12 <= K.min() and K.max() <= 1.0 + 1e-12, "entries in [0, 1]"
    assert result["min_eigval"] >= -1e-10, "kernel must be positive semidefinite"
    assert result["cross_dev"] < 1e-9, "cross-check from state vectors must agree"


if __name__ == "__main__":
    main()
