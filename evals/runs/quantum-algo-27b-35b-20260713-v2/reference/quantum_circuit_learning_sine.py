import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp, Statevector
from scipy.optimize import minimize

def encoding_state(x):
    qc = QuantumCircuit(2)
    qc.ry(x, 0)
    qc.ry(2 * np.arcsin(np.clip(x / 4.0, -1, 1)), 1)
    qc.cx(0, 1)
    qc.ry(x, 0)
    return Statevector.from_instruction(qc)

def observable(theta):
    return SparsePauliOp.from_list([("ZI", float(np.cos(theta))),
                                    ("IZ", float(np.sin(theta)))])

def expectation(x, theta):
    sv = encoding_state(x)
    M = observable(theta)
    return float(sv.expectation_value(M).real)

def mse(theta):
    xs = np.arange(0, 6.5, 0.5)
    targets = np.sin(xs)
    preds = np.array([expectation(x, theta) for x in xs])
    return float(np.mean((preds - targets) ** 2))

def main():
    res = minimize(mse, x0=[0.3], method="COBYLA", maxiter=300, tol=1e-6)
    theta_opt = float(res.x[0])
    final_mse = float(res.fun)
    pred_pi = expectation(np.pi, theta_opt)
    target_pi = 0.0
    err_pi = abs(pred_pi - target_pi)
    print(f"Training MSE = {final_mse:.4f}")
    print(f"Optimal theta = {theta_opt:.4f}")
    print(f"Prediction at x=pi = {pred_pi:.4f}")
    print(f"Target at x=pi = 0.0000")
    print(f"Fit error at x=pi = {err_pi:.4f}")

if __name__ == "__main__":
    main()
