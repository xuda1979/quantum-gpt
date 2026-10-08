import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator
from qiskit.primitives import StatevectorSampler

def main():
    t = 5
    theta = 1.0 / 8.0  # T gate: phase e^{i*2*pi*theta} = e^{i*pi/4}
    U = np.diag([1.0, np.exp(1j * 2 * np.pi * theta)])
    # Build QPE circuit
    qc = QuantumCircuit(t + 1, t)
    # Target qubit in |1> (eigenvector of U with eigenvalue e^{i*2*pi*theta})
    qc.x(t)
    # Hadamards on evaluation register
    for k in range(t):
        qc.h(k)
    # Controlled-U^{2^k}
    for k in range(t):
        Uk = np.linalg.matrix_power(U, 2 ** k)
        qc.append(Operator(Uk).control(1), [k, t])
    # Inverse QFT on evaluation register
    for i in reversed(range(t)):
        for j in range(t - 1, i, -1):
            qc.cp(-np.pi / 2 ** (j - i), j, i)
        qc.h(i)
    qc.measure(range(t), range(t))
    sampler = StatevectorSampler()
    result = sampler.run([qc], shots=8192).result()
    counts = result[0].data.c.get_counts()
    best = max(counts.items(), key=lambda kv: kv[1])[0]
    m = int(best, 2)
    phi = m / 2 ** t
    true_phase = theta
    err = abs(phi - true_phase)
    print(f"True phase = {true_phase:.4f}")
    print(f"Estimated phase = {phi:.4f}")
    print(f"Most likely bitstring = {best}")
    print(f"Abs error = {err:.4f}")
    print(f"Converged: {err < 1.0 / 2 ** t}")

if __name__ == "__main__":
    main()
