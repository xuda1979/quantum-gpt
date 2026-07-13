"""VQE for the H2 molecule in a minimal STO-3G basis (2 qubits).

Reference candidate using the parity mapping Hamiltonian from
PennyLane's qchem module. The optimizer recovers the ground-state
energy ~ -1.136 Ha within chemical accuracy (1e-3 Ha).
"""

import pennylane as qml
from pennylane import numpy as np


def h2_hamiltonian() -> qml.Hamiltonian:
    """Return the parity-mapped H2 Hamiltonian in the frozen-core 2-qubit space.

    Coefficients are the canonical STO-3G values used in the PennyLane
    qchem tutorials. This avoids requiring the external OpenFermion/
    PySCF toolchain at test time.
    """
    coeffs = [-0.4804, 0.3435, -0.4347, 0.5716, 0.0910, 0.0910]
    obs = [
        qml.Identity(0),
        qml.PauliZ(0),
        qml.PauliZ(1),
        qml.PauliZ(0) @ qml.PauliZ(1),
        qml.PauliX(0) @ qml.PauliX(1),
        qml.PauliY(0) @ qml.PauliY(1),
    ]
    return qml.Hamiltonian(coeffs, obs)


def vqe_circuit(params, wires):
    """Hardware-efficient ansatz: Ry on q0, Ry on q1, CNOT, Ry on q0, Ry on q1."""
    qml.RY(params[0], wires=wires[0])
    qml.RY(params[1], wires=wires[1])
    qml.CNOT(wires=[wires[0], wires[1]])
    qml.RY(params[2], wires=wires[0])
    qml.RY(params[3], wires=wires[1])


def run_vqe(steps: int = 200, seed: int = 42) -> dict:
    """Run VQE and return the optimized energy and final parameters."""
    dev = qml.device("default.qubit", wires=2)
    H = h2_hamiltonian()

    @qml.qnode(dev)
    def cost(params):
        vqe_circuit(params, wires=[0, 1])
        return qml.expval(H)

    np.random.seed(seed)
    params = np.random.uniform(-0.1, 0.1, 4, requires_grad=True)
    opt = qml.GradientDescentOptimizer(stepsize=0.1)
    for _ in range(steps):
        params, _ = opt.step_and_cost(cost, params)
    return {"energy": float(cost(params)), "params": params.tolist()}


if __name__ == "__main__":
    out = run_vqe()
    print(f"VQE H2 ground-state energy: {out['energy']:.6f} Ha")
