import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from scipy.optimize import minimize

def feature_map_state(x):
    qc = QuantumCircuit(2)
    qc.h([0, 1])
    qc.rz(x[0], 0)
    qc.rz(x[1], 1)
    qc.h([0, 1])
    return Statevector.from_instruction(qc)

def kernel(xi, xj):
    si = feature_map_state(xi)
    sj = feature_map_state(xj)
    return float(abs(si.conjugate().inner(sj)) ** 2)

def main():
    train_X = np.array([[0.5, 1.0], [1.0, 0.5], [0.8, 0.8], [1.2, 1.5],
                        [3.0, 3.5], [3.5, 3.0], [3.2, 3.2], [2.8, 3.8]])
    train_y = np.array([1, 1, 1, 1, -1, -1, -1, -1])
    n = len(train_X)
    K = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            K[i, j] = kernel(train_X[i], train_X[j])
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
    margin = 0.5 * float(alphas @ Q @ alphas)
    sv_idx = next((i for i in range(n) if alphas[i] > 1e-4), 0)
    b = train_y[sv_idx] - sum(alphas[j] * train_y[j] * K[j, sv_idx] for j in range(n))
    n_sv = int(np.sum(alphas > 1e-4))
    # Training accuracy
    correct = 0
    for i in range(n):
        f = sum(alphas[j] * train_y[j] * K[j, i] for j in range(n)) + b
        if (f >= 0) == (train_y[i] > 0):
            correct += 1
    acc = correct / n
    print(f"Training accuracy = {acc:.4f}")
    print(f"Margin = {margin:.4f}")
    print(f"Bias = {b:.4f}")
    print(f"Num support vectors = {n_sv}")

if __name__ == "__main__":
    main()
