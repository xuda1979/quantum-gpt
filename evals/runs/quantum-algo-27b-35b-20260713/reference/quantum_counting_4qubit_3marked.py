import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFT
from qiskit.quantum_info import Statevector
from fractions import Fraction

def grover_oracle(marked_ints, n):
    qc = QuantumCircuit(n)
    for m in marked_ints:
        bits = format(m, f"0{n}b")
        for q, b in enumerate(bits):
            if b == '0':
                qc.x(q)
        qc.h(n - 1)
        qc.mcx(list(range(n - 1)), n - 1)
        qc.h(n - 1)
        for q, b in enumerate(bits):
            if b == '0':
                qc.x(q)
    return qc

def grover_diffuser(n):
    qc = QuantumCircuit(n)
    qc.h(range(n))
    qc.x(range(n))
    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)
    qc.x(range(n))
    qc.h(range(n))
    return qc

def quantum_count(n, marked, n_count):
    """Estimate the number of marked items M in 2^n using quantum counting."""
    N = 2 ** n
    # Build Grover operator G = (2|s><s| - I) * Oracle
    oracle = grover_oracle(marked, n)
    diffuser = grover_diffuser(n)
    G = QuantumCircuit(n)
    G.compose(oracle, inplace=True)
    G.compose(diffuser, inplace=True)
    # QPE on G with n_count counting qubits
    # Eigenvalues of G are exp(±2*pi*i*theta) where sin(theta) = sqrt(M/N)
    creg = QuantumCircuit(n + n_count)
    creg.h(range(n_count))
    # Prepare uniform superposition on the search register (the eigenstate
    # with non-trivial eigenvalue of G is |beta> = cos(theta)|bad> + sin(theta)|good>)
    creg.h(range(n_count, n + n_count))
    for q in range(n_count):
        # Controlled-G^(2^q)
        G_power = G.power(2 ** q)
        creg.compose(G_power.control(1), [q] + list(range(n_count, n + n_count)), inplace=True)
    creg.compose(QFT(n_count, inverse=True), range(n_count), inplace=True)
    sv = Statevector.from_instruction(creg)
    probs = sv.probabilities_dict()
    best = max(probs.items(), key=lambda kv: kv[1])[0]
    measured = int(best, 2)
    # The phase estimate theta = measured / 2^n_count
    # The two eigenvalues of G are exp(±2*pi*i*theta), so we get one of them.
    phase = measured / (2 ** n_count)
    if phase > 0.5:
        phase = 1.0 - phase
    theta = np.pi * phase  # since eigenvalue = exp(2*pi*i*phase) = exp(2*i*theta)
    # Actually: eigenvalue = exp(2*i*theta), so 2*pi*phase = 2*theta -> theta = pi*phase
    M_est = N * (np.sin(theta)) ** 2
    return M_est, theta

def main():
    n = 4
    marked = [3, 7, 11]  # M = 3
    n_count = 4
    M_est, theta = quantum_count(n, marked, n_count)
    N = 2 ** n
    M_true = len(marked)
    print(f"N = {N}")
    print(f"True M = {M_true}")
    print(f"Counting qubits = {n_count}")
    print(f"Estimated theta = {theta:.4f}")
    print(f"Estimated M = {M_est:.4f}")
    print(f"Rounded M = {int(round(M_est))}")
    print(f"Correct: {abs(M_est - M_true) < 0.5}")

if __name__ == "__main__":
    main()
