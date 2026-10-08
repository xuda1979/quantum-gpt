import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator, Statevector
from qiskit.primitives import StatevectorSampler

def grover_Q(theta):
    # Q = -A S_0 A^{-1}  where A = R_y(2*theta) on |0> -> sin(theta)|1> + cos(theta)|0>
    # Marked state = |1>, so S_chi = I - 2|1><1| = diag(1, -1).
    # S_0 = I - 2|0><0| = diag(-1, 1).
    # Q = - A S_0 A^{-1} S_chi  (sign convention: eigenvalues e^{+/- i 2 theta})
    A = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
    S0 = np.diag([-1.0, 1.0])
    Schi = np.diag([1.0, -1.0])
    Q = -A @ S0 @ A.T @ Schi
    return Q

def build_qae_circuit(theta, t=3):
    Q = grover_Q(theta)
    # Register layout: q[0..t-1] = evaluation (phase) register, q[t] = target.
    qc = QuantumCircuit(t + 1, t)
    # Prepare target in sin(theta)|1> + cos(theta)|0> via Ry(2*theta)
    qc.ry(2 * theta, t)
    # Hadamards on phase register
    for k in range(t):
        qc.h(k)
    # Controlled-Q^{2^k}
    Qop = Operator(Q)
    for k in range(t):
        # Apply Q^{2^k} controlled by q[k]
        Qpow = np.linalg.matrix_power(Q, 2 ** k)
        qc.append(Operator(Qpow).control(1), [k, t])
    # Inverse QFT on phase register
    # QFT_t (forward): for i in range(t): H[i]; for j in range(i+1, t): CP(pi/2^{j-i}) j->i
    # Inverse: reverse and use negative angles.
    for i in reversed(range(t)):
        for j in range(t - 1, i, -1):
            qc.cp(-np.pi / 2 ** (j - i), j, i)
        qc.h(i)
    # Measure
    qc.measure(range(t), range(t))
    return qc

def main():
    theta = np.pi / 8.0
    target = float(np.sin(theta) ** 2)
    qc = build_qae_circuit(theta, t=3)
    sampler = StatevectorSampler()
    result = sampler.run([qc], shots=4096).result()
    counts = result[0].data.c.get_counts()
    # Pick the most likely bitstring; qiskit little-endian: bitstring b_{t-1}..b_0
    best = max(counts.items(), key=lambda kv: kv[1])[0]
    m = int(best, 2)
    est = float(np.sin(np.pi * m / 2 ** 3) ** 2)
    err = abs(est - target)
    print(f"Target amplitude = {target:.4f}")
    print(f"Estimated amplitude = {est:.4f}")
    print(f"Abs error = {err:.4f}")
    print(f"Converged: {err < 0.05}")

if __name__ == "__main__":
    main()
