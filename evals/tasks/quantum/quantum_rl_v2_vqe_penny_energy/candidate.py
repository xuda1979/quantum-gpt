"""Exact-state VQE in PennyLane for H = 0.5 Z0Z1 + 0.8 X0 + 0.8 X1 + 0.2 Z0
with a three-layer RY-CNOT ansatz, AdamOptimizer, deterministic
initialization and six restarts. The best energy is compared with an
independently assembled NumPy matrix eigensolution; the variational bound
is asserted within 1e-8 and the final energy error below 1e-4."""

import numpy as np
import pennylane as qml

LAYERS = 3
N_RESTARTS = 6
STEPS = 300


def hamiltonian_terms():
    """(coeff, wire terms) list defining the H = 0.5 Z0Z1 + 0.8 X0 + 0.8 X1
    + 0.2 Z0 operator."""
    return [
        (0.5, [qml.PauliZ(0), qml.PauliZ(1)]),
        (0.8, [qml.PauliX(0)]),
        (0.8, [qml.PauliX(1)]),
        (0.2, [qml.PauliZ(0)]),
    ]


def hamiltonian():
    coeffs = [c for c, _ in hamiltonian_terms()]
    ops = []
    for _, terms in hamiltonian_terms():
        op = terms[0]
        for t in terms[1:]:
            op = op @ t
        ops.append(op)
    return qml.Hamiltonian(coeffs, ops)


def ansatz(params):
    """Three-layer RY-CNOT ansatz: RY on each qubit followed by CNOT(0,1)
    and CNOT(1,0) per layer (12 trainable parameters)."""
    for layer in range(LAYERS):
        qml.RY(params[4 * layer + 0], wires=0)
        qml.RY(params[4 * layer + 1], wires=1)
        qml.RY(params[4 * layer + 2], wires=0)
        qml.RY(params[4 * layer + 3], wires=1)
        qml.CNOT(wires=[0, 1])
        qml.CNOT(wires=[1, 0])


def cost_qnode(params):
    dev = qml.device("default.qubit", wires=2)

    @qml.qnode(dev)
    def circuit():
        ansatz(params)
        return qml.expval(hamiltonian())

    return float(circuit())


def exact_ground_energy():
    """Independently assembled NumPy matrix eigensolution."""
    Z = np.diag([1.0, -1.0]).astype(complex)
    X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
    I = np.eye(2, dtype=complex)
    H = 0.5 * np.kron(Z, Z) + 0.8 * np.kron(X, I) + 0.8 * np.kron(I, X) + 0.2 * np.kron(Z, I)
    return float(np.linalg.eigvalsh(H)[0])


def restart_starts(seed_base=0):
    """Deterministic restart initialization: six fixed seeds, each drawing
    a distinct start in [-pi, pi]."""
    starts = []
    for r in range(N_RESTARTS):
        rng = np.random.default_rng(seed_base + r)
        starts.append(rng.uniform(-np.pi, np.pi, size=4 * LAYERS))
    return starts


def run_vqe(max_steps=STEPS):
    """Run AdamOptimizer from six deterministic starts; returns the best
    (energy, params) and the trajectory of the best run."""
    best_energy = float("inf")
    best_params = None
    best_traj = []
    dev = qml.device("default.qubit", wires=2)

    @qml.qnode(dev)
    def circuit(params):
        ansatz(params)
        return qml.expval(hamiltonian())

    for start in restart_starts():
        params = qml.numpy.array(start, requires_grad=True)
        opt = qml.AdamOptimizer(stepsize=0.1)
        traj = []
        for _ in range(max_steps):
            params = opt.step(circuit, params)
            if _ % 20 == 0 or _ == max_steps - 1:
                traj.append(float(circuit(params)))
        e = float(circuit(params))
        if e < best_energy:
            best_energy = e
            best_params = params
            best_traj = traj
    return best_energy, best_params, best_traj


def vqe_energy():
    """Best variational energy over the six deterministic restarts."""
    e, _, _ = run_vqe()
    return e


def main():
    exact = exact_ground_energy()
    best, params, traj = run_vqe()
    assert best >= exact - 1e-8, f"variational bound violated: {best} < {exact}"
    assert best - exact < 1e-4, f"energy error {best - exact} >= 1e-4"
    print("exact_ground =", exact)
    print("vqe_best =", best)
    print("energy_error =", best - exact)
    print("trajectory =", traj)


if __name__ == "__main__":
    main()
