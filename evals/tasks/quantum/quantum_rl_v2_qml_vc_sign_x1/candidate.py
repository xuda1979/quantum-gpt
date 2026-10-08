"""Reproducible two-qubit PennyLane variational classifier.

Labels are defined by x1 > 0 on a small deterministic 2D training set
(12 grid points; the first 8 are train, the last 4 test). Features are
angle-encoded, two trainable rotation-entangling layers are followed by
an expectation-value output with a trainable bias, and the model is
trained with mini-batch-free Adam from a seeded initialization. The
loss must decrease from its initial value and all predictions must stay
finite."""

from __future__ import annotations

import numpy as np
import pennylane as qml
import pennylane.numpy as pnp

WIRES = [0, 1]
LAYERS = 2
ROTATIONS_PER_LAYER = 4
N_PARAMS = LAYERS * ROTATIONS_PER_LAYER + 1  # 8 rotations + bias

DEVICE = qml.device("default.qubit", wires=2)


def make_data() -> tuple[np.ndarray, np.ndarray]:
    """Deterministic 12-point grid with labels x1 > 0."""
    X = np.array(
        [
            [-1.0, -1.0],
            [-1.0, -0.5],
            [-1.0, 0.5],
            [-1.0, 1.0],
            [-0.5, -1.0],
            [-0.5, 1.0],
            [0.5, -1.0],
            [0.5, 1.0],
            [1.0, -1.0],
            [1.0, -0.5],
            [1.0, 0.5],
            [1.0, 1.0],
        ]
    )
    y = np.array([1.0 if x[1] > 0 else 0.0 for x in X])
    return X, y


def train_test_split() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Fixed split: first 8 points train, last 4 points test."""
    X, y = make_data()
    return X[:8], y[:8], X[8:], y[8:]


@qml.qnode(DEVICE)
def circuit(x: np.ndarray, params: np.ndarray) -> float:
    """Angle-encoded 2-qubit classifier: two RY/CNOT layers, <Z0> out."""
    qml.AngleEmbedding(x, wires=WIRES, rotation="Y")
    p = pnp.reshape(params[:-1], (LAYERS, ROTATIONS_PER_LAYER))
    for layer in range(LAYERS):
        qml.RY(p[layer, 0], wires=0)
        qml.RY(p[layer, 1], wires=1)
        qml.CNOT(wires=[0, 1])
        qml.RY(p[layer, 2], wires=0)
        qml.RY(p[layer, 3], wires=1)
    return qml.expval(qml.PauliZ(0))


def initialize_params(seed: int = 0) -> np.ndarray:
    """Seeded small random initialization (trainable)."""
    rng = np.random.RandomState(seed)
    return pnp.array(rng.uniform(-0.5, 0.5, size=N_PARAMS), requires_grad=True)


def loss(params: np.ndarray, X: np.ndarray, y: np.ndarray) -> float:
    """Binary cross-entropy on the biased logit <Z0> + bias."""
    logits = pnp.array([circuit(x, params) for x in X]) + params[-1]
    probs = 1.0 / (1.0 + pnp.exp(-logits))
    eps = 1e-12
    return -pnp.mean(y * pnp.log(probs + eps) + (1.0 - y) * pnp.log(1.0 - probs + eps))


def train(
    X: np.ndarray, y: np.ndarray, steps: int = 120, seed: int = 0
) -> tuple[np.ndarray, list[float]]:
    """Mini-batch-free Adam training; returns (params, loss trajectory)."""
    params = initialize_params(seed)
    optimizer = qml.AdamOptimizer(stepsize=0.1)
    trajectory = [float(loss(params, X, y))]
    for _ in range(steps):
        params = optimizer.step(lambda p: loss(p, X, y), params)
        trajectory.append(float(loss(params, X, y)))
    return params, trajectory


def predict(X: np.ndarray, params: np.ndarray) -> np.ndarray:
    """Predicted labels from the sign of <Z0> + bias."""
    logits = np.array([circuit(x, params) for x in X]) + float(params[-1])
    return (logits > 0.0).astype(int)


def accuracy(X: np.ndarray, y: np.ndarray, params: np.ndarray) -> float:
    """Fraction of correct predictions."""
    return float(np.mean(predict(X, params) == y))


def run_training(steps: int = 120, seed: int = 0) -> dict:
    """End-to-end training; returns all verifiable quantities."""
    X_train, y_train, X_test, y_test = train_test_split()
    params, trajectory = train(X_train, y_train, steps=steps, seed=seed)
    preds = predict(X_train, params)
    all_finite = bool(np.all(np.isfinite(preds)) and np.all(np.isfinite(trajectory)))
    return {
        "n_params": N_PARAMS,
        "loss_initial": trajectory[0],
        "loss_final": trajectory[-1],
        "loss_improvement": trajectory[0] - trajectory[-1],
        "train_acc": accuracy(X_train, y_train, params),
        "test_acc": accuracy(X_test, y_test, params),
        "predictions_finite": all_finite,
        "trajectory": trajectory,
    }


def main():
    result = run_training()
    print("n_params =", result["n_params"])
    print("loss_initial =", result["loss_initial"])
    print("loss_final =", result["loss_final"])
    print("train_acc =", result["train_acc"])
    print("test_acc =", result["test_acc"])
    assert result["loss_improvement"] > 0.0, "loss must decrease from initialization"
    assert result["predictions_finite"], "all predictions must be finite"


if __name__ == "__main__":
    main()
