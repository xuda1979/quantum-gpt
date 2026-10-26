import numpy as np
import pennylane as qml


def vqe_circuit(params, wires):
    """
    VQE circuit with four parameters:
    - RY on wire 0
    - RY on wire 1
    - CNOT 0->1
    - RY on wire 0
    - RY on wire 1
    """
    qml.RY(params[0], wires=wires[0])
    qml.RY(params[1], wires=wires[1])
    qml.CNOT(wires=[wires[0], wires[1]])
    qml.RY(params[2], wires=wires[0])
    qml.RY(params[3], wires=wires[1])


def run_vqe(num_steps=100, seed=42):
    """
    Perform deterministic seeded variational minimization for the requested number of steps.
    Returns {'energy': final expectation as float, 'params': four final parameter values}
    """
    # Define the Hamiltonian
    # H = -0.4804 I(0) + 0.3435 Z(0) - 0.4347 Z(1) + 0.5716 Z(0)Z(1) + 0.0910 X(0)X(1) + 0.0910 Y(0)Y(1)
    # Note: I(0) is identity on wire 0, which is equivalent to identity on both wires (since I ⊗ I = I)
    # Actually, I(0) means identity operator on wire 0. In a two-qubit system, this is I ⊗ I.

    # Let's build the Hamiltonian using PennyLane's qml.Hamiltonian
    coeffs = [-0.4804, 0.3435, -0.4347, 0.5716, 0.0910, 0.0910]
    obs = [
        qml.Identity(0),
        qml.PauliZ(0),
        qml.PauliZ(1),
        qml.PauliZ(0) @ qml.PauliZ(1),
        qml.PauliX(0) @ qml.PauliX(1),
        qml.PauliY(0) @ qml.PauliY(1),
    ]
    hamiltonian = qml.Hamiltonian(coeffs, obs)

    # Set up the device
    dev = qml.device("default.qubit", wires=2)

    # Define the cost function
    def cost(params):
        with qml.tape.QuantumTape() as tape:
            vqe_circuit(params, [0, 1])
            exp_val = qml.expval(hamiltonian)
        return tape.execute(dev)

    # Initialize parameters with a seeded random generator
    rng = np.random.default_rng(seed)
    params = rng.uniform(-np.pi, np.pi, size=4)

    # Use gradient descent with a fixed learning rate
    learning_rate = 0.5
    optimizer = qml.Adam(learning_rate=learning_rate)

    for _ in range(num_steps):
        grad = qml.grad(cost)(params)
        params = optimizer.step_and_grad(cost, params)

    # Compute final energy
    final_energy = float(cost(params))

    return {"energy": final_energy, "params": params.tolist()}
