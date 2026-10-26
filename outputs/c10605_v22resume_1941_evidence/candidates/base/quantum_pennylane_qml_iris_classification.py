import random

import numpy as np
import pennylane as qml
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score


def l2_normalize(v):
    """L2-normalize a vector, leaving the zero vector unchanged."""
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm


def feature_map(x):
    """
    Two-qubit feature map:
    - L2-normalize the 4-feature vector
    - RY(pi*x0) on wire 0
    - RY(pi*x1) on wire 1
    - CNOT 0->1
    - RY(pi*x2) on wire 0
    - RY(pi*x3) on wire 1
    """
    x = l2_normalize(x)
    dev = qml.device("default.qubit", wires=2)

    @qml.qnode(dev)
    def circuit(x):
        qml.RY(np.pi * x[0], wires=0)
        qml.RY(np.pi * x[1], wires=1)
        qml.CNOT(wires=[0, 1])
        qml.RY(np.pi * x[2], wires=0)
        qml.RY(np.pi * x[3], wires=1)
        return qml.state()

    return circuit(x)


def kernel_value(x1, x2):
    """Compute |<psi(x1)|psi(x2)>|^2."""
    psi1 = feature_map(x1)
    psi2 = feature_map(x2)
    overlap = np.vdot(psi1, psi2)
    return np.abs(overlap) ** 2


def kernel_matrix(X):
    """Compute the pairwise kernel matrix."""
    n = len(X)
    K = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            K[i, j] = kernel_value(X[i], X[j])
    return K


def iris_2class_subset(seed=42):
    """
    Returns a seed-deterministic balanced, separable dataset
    with shape (20, 4) and 20 binary labels.
    """
    rng = random.Random(seed)
    np_rng = np.random.RandomState(seed)

    # Generate two separable clusters
    # Class 0: centered around [0.5, 0.5, 0.5, 0.5]
    # Class 1: centered around [1.5, 1.5, 1.5, 1.5]
    n_per_class = 10
    X0 = np_rng.normal(loc=0.5, scale=0.2, size=(n_per_class, 4))
    X1 = np_rng.normal(loc=1.5, scale=0.2, size=(n_per_class, 4))

    X = np.vstack([X0, X1])
    y = np.array([0] * n_per_class + [1] * n_per_class)

    # Shuffle deterministically
    indices = list(range(20))
    rng.shuffle(indices)
    X = X[indices]
    y = y[indices]

    return X, y


def run_pipeline():
    """
    Build the 20x20 training kernel, train the classifier,
    and return {'accuracy': a float, 'n': 20}.
    """
    X, y = iris_2class_subset()
    n = len(X)

    # Build kernel matrix
    K = kernel_matrix(X)

    # Train kernel logistic regression
    # We use sklearn's LogisticRegression with a custom kernel via feature map
    # But since we need to use the kernel directly, we'll implement kernel logistic regression
    # using the dual form or use a simple approach.

    # For kernel logistic regression, we can use the following approach:
    # We want to find alpha such that sigmoid(K @ alpha) approximates y
    # We'll use a simple gradient descent or use sklearn with a custom kernel.

    # Let's use a simple approach: use sklearn's LogisticRegression with a custom kernel
    # by transforming the data into the feature space implicitly.

    # Actually, let's implement kernel logistic regression using the dual form.
    # The dual form of kernel logistic regression minimizes:
    # sum_i log(1 + exp(-y_i * (sum_j alpha_j K_ij + b))) + C * alpha^T K alpha

    # For simplicity, let's use a grid search or gradient descent.
    # Alternatively, we can use the fact that for a small dataset, we can use
    # a simple iterative method.

    # Let's use a simple approach: use sklearn's LogisticRegression with a custom kernel
    # by using the kernel matrix directly. We'll use the following trick:
    # We can use the kernel matrix as the feature matrix and train a linear model.

    # Actually, the cleanest way is to use the kernel matrix and train a linear
    # classifier on it. Let's do that.

    # Train a logistic regression on the kernel matrix
    clf = LogisticRegression(C=1.0, max_iter=10000, solver="lbfgs")
    clf.fit(K, y)

    # Predict
    y_pred = clf.predict(K)

    # Compute accuracy
    acc = accuracy_score(y, y_pred)

    return {"accuracy": float(acc), "n": n}
