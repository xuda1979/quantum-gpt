import pennylane as qml
from pennylane import numpy as np


def make_xor_data() -> tuple[np.ndarray, np.ndarray]:
    """
    Deterministic 16-point two-feature XOR dataset.

    X holds 16 points in [-0.7, 0.7]^2; y[i] = 1 iff x0 * x1 > 0 (the XOR
    of the signs). Balanced: 8 points per class, NOT linearly separable.
    """
    X = np.array(
        [
            [-0.7, -0.7],
            [0.7, 0.7],
            [-0.7, 0.7],
            [0.7, -0.7],
            [-0.3, -0.3],
            [0.3, 0.3],
            [-0.3, 0.3],
            [0.3, -0.3],
            [-0.7, 0.3],
            [0.7, -0.3],
            [0.7, 0.3],
            [-0.7, -0.3],
            [0.3, -0.7],
            [-0.3, 0.7],
            [-0.3, -0.7],
            [0.3, 0.7],
        ],
        dtype=float,
    )
    y = np.array([1.0 if x0 * x1 > 0.0 else 0.0 for x0, x1 in X])
    return X, y


def variational_circuit(params: list[float], x: list[float]) -> None:
    """
    Two-qubit angle-embedding variational circuit: RY(pi x0) on wire 0,
    RY(pi x1) on wire 1, CNOT 0->1, then four variational RY rotations
    interleaved with a second CNOT.
    """
    qml.RY(x[0] * np.pi, wires=0)
    qml.RY(x[1] * np.pi, wires=1)
    qml.CNOT(wires=[0, 1])
    qml.RY(params[0], wires=0)
    qml.RY(params[1], wires=1)
    qml.CNOT(wires=[1, 0])
    qml.RY(params[2], wires=0)
    qml.RY(params[3], wires=1)


def train_classifier(steps: int = 60, seed: int = 0) -> dict:
    """
    Train the variational classifier on the XOR dataset.

    Returns {'accuracy': the train-set accuracy as a float, 'n': 16,
    'params': the four final parameter values}. Deterministic for a fixed
    seed; the circuit and the data determine the result.
    """
    X, y = make_xor_data()
    dev = qml.device("default.qubit", wires=2)

    @qml.qnode(dev)
    def circuit(params, x):
        variational_circuit(params, x)
        return qml.expval(qml.PauliZ(0))

    def loss(params):
        total = 0.0
        for xi, yi in zip(X, y):
            pred = circuit(params, xi)
            total += (pred - (2 * yi - 1)) ** 2
        return total / len(y)

    np.random.seed(seed)
    params = np.random.uniform(-np.pi, np.pi, 4)
    opt = qml.AdamOptimizer(stepsize=0.2)
    for _ in range(steps):
        params = opt.step(loss, params)

    acc = np.mean(
        [
            1.0 if (circuit(params, xi) > 0.0) == (yi == 1.0) else 0.0
            for xi, yi in zip(X, y)
        ]
    )
    return {
        "accuracy": float(acc),
        "n": int(len(y)),
        "params": [float(p) for p in np.asarray(params, dtype=float)],
    }


def predict(params: list[float], x: list[float]) -> int:
    """Predict the class (0 or 1) of a two-feature sample."""
    dev = qml.device("default.qubit", wires=2)

    @qml.qnode(dev)
    def circuit(params, x):
        variational_circuit(params, x)
        return qml.expval(qml.PauliZ(0))

    return 1 if circuit(params, x) > 0.0 else 0
