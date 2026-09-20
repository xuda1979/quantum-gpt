"""Reproducible two-qubit PennyLane variational classifier for labels
defined by x0*x1 > 0 on a small deterministic 2D training set: angle
encoding, two trainable rotation-entangling layers, an expectation-value
output with a trainable bias, mini-batch-free Adam optimization, and a
fixed train/test split. Loss must decrease from initialization and all
predictions must be finite; no accuracy threshold above 70 percent is
hard-coded in the candidate."""

import pennylane as qml
from pennylane import numpy as np

N_LAYERS = 2


def make_data():
    """Deterministic train/test split: 12 train points (radii 0.3, 0.6,
    0.9 in every quadrant) and 8 test points (radii 0.45, 0.75 in every
    quadrant). Labels are 1 iff x0*x1 > 0."""
    train_x = np.array(
        [
            [r * s0, r * s1]
            for r in (0.3, 0.6, 0.9)
            for s0, s1 in ((1.0, 1.0), (-1.0, -1.0), (-1.0, 1.0), (1.0, -1.0))
        ],
        dtype=float,
    )
    test_x = np.array(
        [
            [r * s0, r * s1]
            for r in (0.45, 0.75)
            for s0, s1 in ((1.0, 1.0), (-1.0, -1.0), (-1.0, 1.0), (1.0, -1.0))
        ],
        dtype=float,
    )
    train_y = np.array([1.0 if x0 * x1 > 0 else 0.0 for x0, x1 in train_x])
    test_y = np.array([1.0 if x0 * x1 > 0 else 0.0 for x0, x1 in test_x])
    return train_x, train_y, test_x, test_y


def variational_circuit(params, x):
    """Angle encoding RY(pi*x0), RY(pi*x1), then two trainable
    rotation-entangling layers: RY on each qubit followed by CNOT(0,1)."""
    qml.RY(np.pi * x[0], wires=0)
    qml.RY(np.pi * x[1], wires=1)
    for layer in range(N_LAYERS):
        base = 2 * layer
        qml.RY(params[base], wires=0)
        qml.RY(params[base + 1], wires=1)
        qml.CNOT(wires=[0, 1])


dev = qml.device("default.qubit", wires=2)


@qml.qnode(dev)
def circuit(params, x):
    variational_circuit(params, x)
    return qml.expval(qml.PauliZ(0))


def predict(params, x, bias):
    """Scalar prediction = <Z0> + bias (kept autograd-traceable)."""
    return circuit(params, x) + bias


def classify(params, x, bias):
    """1 if the prediction is positive else 0."""
    return 1 if predict(params, x, bias) > 0.0 else 0


def loss(params, bias, X, y):
    """Mean squared error against signed labels (+1/-1)."""
    total = 0.0
    for xi, yi in zip(X, y):
        signed = 2.0 * float(yi) - 1.0
        total += (predict(params, xi, bias) - signed) ** 2
    return total / len(X)


def accuracy(params, bias, X, y):
    correct = sum(1 for xi, yi in zip(X, y) if classify(params, xi, bias) == yi)
    return correct / len(y)


def train(steps=120, seed=42, stepsize=0.15):
    """Mini-batch-free Adam optimization with a seeded initialization."""
    train_x, train_y, test_x, test_y = make_data()
    np.random.seed(seed)
    params = np.random.uniform(-np.pi, np.pi, size=2 * N_LAYERS)
    bias = np.array(0.0)

    def cost(p, b):
        return loss(p, b, train_x, train_y)

    opt = qml.AdamOptimizer(stepsize=stepsize)
    loss_first = float(cost(params, bias))
    for _ in range(steps):
        params, bias = opt.step(cost, params, bias)
    loss_last = float(cost(params, bias))
    train_acc = accuracy(params, bias, train_x, train_y)
    test_acc = accuracy(params, bias, test_x, test_y)
    return {
        "loss_first": loss_first,
        "loss_last": loss_last,
        "train_accuracy": float(train_acc),
        "test_accuracy": float(test_acc),
        "params": list(np.asarray(params, dtype=float)),
        "bias": float(bias),
        "n_train": len(train_y),
        "n_test": len(test_y),
    }


def main():
    result = train()
    print("loss first =", result["loss_first"])
    print("loss last =", result["loss_last"])
    print("train accuracy =", result["train_accuracy"])
    print("test accuracy =", result["test_accuracy"])
    assert result["loss_last"] < result["loss_first"], "loss must decrease"
    train_x, train_y, test_x, test_y = make_data()
    params = np.array(result["params"])
    bias = result["bias"]
    preds = [predict(params, xi, bias) for xi in test_x]
    assert all(np.isfinite(p) for p in preds), "predictions must be finite"
    print("test predictions:", np.round(preds, 4))


if __name__ == "__main__":
    main()
