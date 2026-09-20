import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from scipy.optimize import minimize

def feature_map_state(x):
    qc = QuantumCircuit(2)
    qc.ry(x[0], 0)
    qc.ry(x[1], 1)
    return Statevector.from_instruction(qc)

def kernel(xi, xj):
    si = feature_map_state(xi)
    sj = feature_map_state(xj)
    return float(abs(si.conjugate().inner(sj)) ** 2)

def main():
    train_X = np.array([[0.1, 0.2], [0.3, 0.5], [0.8, 0.1],
                        [2.5, 2.8], [2.9, 2.6], [2.7, 3.0]])
    train_y = np.array([1, 1, 1, -1, -1, -1])
    n = len(train_X)
    K = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            K[i, j] = kernel(train_X[i], train_X[j])
    # Solve dual QP: maximize sum a_i - 0.5 * a^T (y y^T .* K) a
    # subject to a >= 0, sum a_i y_i = 0.
    Q = np.outer(train_y, train_y) * K
    def neg_obj(a):
        return -(np.sum(a) - 0.5 * a @ Q @ a)
    def neg_grad(a):
        return -(np.ones(n) - Q @ a)
    cons = [{"type": "eq", "fun": lambda a: a @ train_y}]
    bounds = [(0, None)] * n
    res = minimize(neg_obj, x0=np.ones(n) * 0.1, jac=neg_grad,
                   method="SLSQP", bounds=bounds, constraints=cons,
                   options={"maxiter": 500, "ftol": 1e-9})
    alphas = res.x
    # Margin = 0.5 * a^T Q a
    margin = 0.5 * float(alphas @ Q @ alphas)
    # Find a support vector (alpha > 1e-4)
    sv_idx = next((i for i in range(n) if alphas[i] > 1e-4), 0)
    b = train_y[sv_idx] - sum(alphas[j] * train_y[j] * K[j, sv_idx] for j in range(n))
    # Test predictions
    test_X = np.array([[0.2, 0.3], [2.8, 2.9], [1.5, 1.5]])
    preds = []
    for xt in test_X:
        f = sum(alphas[i] * train_y[i] * kernel(train_X[i], xt) for i in range(n)) + b
        preds.append(1 if f >= 0 else -1)
    a_str = ", ".join(f"{a:.4f}" for a in alphas)
    print(f"SVM alphas = [{a_str}]")
    print(f"Margin = {margin:.4f}")
    pred_str = ", ".join(("+1" if p > 0 else "-1") for p in preds)
    print(f"Test predictions = [{pred_str}]")
    print(f"Bias term = {b:.4f}")

if __name__ == "__main__":
    main()
