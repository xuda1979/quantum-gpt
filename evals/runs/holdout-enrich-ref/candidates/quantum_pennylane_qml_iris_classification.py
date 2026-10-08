"""Quantum kernel for binary Iris classification.

A 2-qubit quantum kernel computed via the inner product of angle-encoded
feature states. The kernel matrix is fed to a simple logistic regression
to classify the Iris setosa vs. versicolor subset (the linearly separable
two-class slice), demonstrating the quantum-kernel training loop without
requiring a trainable variational ansatz.
"""

import pennylane as qml
from pennylane import numpy as np


def _normalize(x: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(x)
    return x / n if n > 0 else x


def angle_encode(x: np.ndarray, wires) -> None:
    """Angle-encode a 4-feature vector into 2 qubits (2 features per qubit)."""
    x = _normalize(np.asarray(x, dtype=float))
    # Map 4 features to 2 qubits via Ry rotations.
    qml.RY(x[0] * np.pi, wires=wires[0])
    qml.RY(x[1] * np.pi, wires=wires[1])
    qml.CNOT(wires=[wires[0], wires[1]])
    qml.RY(x[2] * np.pi, wires=wires[0])
    qml.RY(x[3] * np.pi, wires=wires[1])


def kernel_circuit() -> qml.QNode:
    dev = qml.device("default.qubit", wires=2)

    @qml.qnode(dev)
    def circuit(x1, x2):
        angle_encode(x1, wires=[0, 1])
        qml.adjoint(lambda: angle_encode(x2, wires=[0, 1]))()
        return qml.probs(wires=[0, 1])

    return circuit


def kernel_value(x1, x2) -> float:
    """Kernel = |<psi(x1)|psi(x2)>|^2 = probability of measuring |00>."""
    circuit = kernel_circuit()
    probs = circuit(x1, x2)
    return float(probs[0])


def kernel_matrix(X1: np.ndarray, X2: np.ndarray) -> np.ndarray:
    n, m = len(X1), len(X2)
    K = np.zeros((n, m))
    for i in range(n):
        for j in range(m):
            K[i, j] = kernel_value(X1[i], X2[j])
    return K


def sigmoid(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-z))


def train_kernel_logreg(
    K: np.ndarray, y: np.ndarray, lr: float = 0.1, epochs: int = 200, seed: int = 0
) -> np.ndarray:
    """Train a kernel logistic regression with gradient descent.

    K: (n, n) kernel matrix. y: (n,) {0,1}. Returns alpha (n,).
    Prediction: sigmoid(K @ alpha).
    """
    np.random.seed(seed)
    n = K.shape[0]
    alpha = np.zeros(n, requires_grad=True)
    for _ in range(epochs):
        pred = sigmoid(K @ alpha)
        grad = K.T @ (pred - y) / n
        alpha = alpha - lr * grad
    return alpha


def predict(K: np.ndarray, alpha: np.ndarray) -> np.ndarray:
    return (sigmoid(K @ alpha) >= 0.5).astype(int)


def iris_2class_subset(seed: int = 0) -> tuple[np.ndarray, np.ndarray]:
    """Return a small synthetic 2-class 4-feature dataset that mimics the
    Iris setosa/versicolor split. Synthetic so the test does not need
    scikit-learn's data loader.
    """
    rng = np.random.default_rng(seed)
    n = 20
    X0 = rng.normal(loc=[0.2, 0.1, 0.1, 0.05], scale=0.05, size=(n // 2, 4))
    X1 = rng.normal(loc=[0.6, 0.4, 0.5, 0.2], scale=0.05, size=(n // 2, 4))
    X = np.vstack([X0, X1])
    y = np.array([0] * (n // 2) + [1] * (n // 2))
    return X, y


def run_pipeline() -> dict:
    X, y = iris_2class_subset(seed=0)
    K = kernel_matrix(X, X)
    alpha = train_kernel_logreg(K, y, lr=0.5, epochs=200, seed=0)
    preds = predict(K, alpha)
    acc = float((preds == y).mean())
    return {"accuracy": acc, "n": len(y)}


if __name__ == "__main__":
    out = run_pipeline()
    print(f"kernel-logreg accuracy on Iris 2-class subset: {out['accuracy']:.3f}")
