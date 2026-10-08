import numpy as np
import pennylane as qml
from scipy.optimize import minimize

dev = qml.device("default.qubit", wires=[0, 1, 2, 3], shots=None)

# Build Hamiltonian via qml.Hamiltonian.
coeffs = [-0.8105, 0.1722, 0.1722, -0.2258, -0.2258,
          0.1209, 0.1689, 0.1689, 0.0452, 0.0452]
ops = [
    qml.Identity(wires=[0]),
    qml.PauliZ(wires=0), qml.PauliZ(wires=1),
    qml.PauliZ(wires=[0, 1]), qml.PauliZ(wires=[2, 3]),
    qml.PauliZ(wires=[0, 1, 2, 3]),
    qml.PauliZ(wires=[0, 2]), qml.PauliZ(wires=[1, 3]),
    qml.PauliZ(wires=[0, 3]), qml.PauliZ(wires=[1, 2]),
]
H = qml.Hamiltonian(coeffs, ops)

@qml.qnode(dev)
def circuit(params):
    qml.RY(params[0], wires=2)
    qml.RY(params[1], wires=3)
    qml.CNOT(wires=[2, 3])
    qml.RY(params[2], wires=2)
    qml.RY(params[3], wires=3)
    return qml.expval(H)

def main():
    res = minimize(lambda p: circuit(p), x0=[0.1, 0.2, 0.3, 0.4],
                   method="COBYLA", maxiter=300, tol=1e-5)
    energy = float(res.fun)
    params = [float(p) for p in res.x]
    converged = abs(energy - (-1.8570)) < 0.02
    p_str = ", ".join(f"{p:.4f}" for p in params)
    print(f"VQE energy = {energy:.4f}")
    print(f"Optimal params = [{p_str}]")
    print(f"Converged: {converged}")

if __name__ == "__main__":
    main()
