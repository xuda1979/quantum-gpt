import pennylane as qml
from pennylane import numpy as np


def heisenberg_hamiltonian(J: float = 1.0):
    """
    Two-qubit XXX Heisenberg Hamiltonian H = J (X X + Y Y + Z Z).

    Returns a PennyLane Hamiltonian with exactly three terms.
    """
    coeffs = [J, J, J]
    ops = [
        qml.PauliX(0) @ qml.PauliX(1),
        qml.PauliY(0) @ qml.PauliY(1),
        qml.PauliZ(0) @ qml.PauliZ(1),
    ]
    return qml.Hamiltonian(coeffs, ops)


def vqe_circuit(params: list[float]) -> None:
    """
    Two-qubit ansatz with four parameters in this order: RY on wire 0, RY on
    wire 1, CNOT 0->1, RY on wire 0, RY on wire 1.
    """
    qml.RY(params[0], wires=0)
    qml.RY(params[1], wires=1)
    qml.CNOT(wires=[0, 1])
    qml.RY(params[2], wires=0)
    qml.RY(params[3], wires=1)


def run_vqe(steps: int = 80, seed: int = 0) -> dict:
    """
    Deterministic seeded variational minimization of the Heisenberg energy.

    Returns {'energy': the final expectation as a float, 'params': the four
    final parameter values}. Compute the result from the circuit and the
    Hamiltonian rather than hard-coding an energy.
    """
    H = heisenberg_hamiltonian(1.0)
    dev = qml.device("default.qubit", wires=2)

    @qml.qnode(dev)
    def cost_fn(params):
        vqe_circuit(params)
        return qml.expval(H)

    np.random.seed(seed)
    params = np.random.uniform(-np.pi, np.pi, 4)
    opt = qml.AdamOptimizer(stepsize=0.15)
    for _ in range(steps):
        params = opt.step(cost_fn, params)
    return {
        "energy": float(cost_fn(params)),
        "params": [float(p) for p in np.asarray(params, dtype=float)],
    }
