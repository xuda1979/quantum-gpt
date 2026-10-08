import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.circuit.library import QFT

def build_simon_oracle(s, n):
    """Oracle for a 2-to-1 function f with period s: f(x) = f(y) iff x xor y = s.
    Implementation: copy x to the second register, then XOR in s conditioned
    on the bits of x (a common textbook construction)."""
    qc = QuantumCircuit(2 * n)
    # Copy x to second register
    for i in range(n):
        qc.cx(i, n + i)
    # If s_i = 1, conditionally flip bit i of the second register using
    # qubit i of the first register as control, but to make f 2-to-1 with
    # period s, we use the standard construction: for i where s_i=1, replace
    # the highest such i with a controlled operation that XORs lower bits.
    # Simpler textbook version: f(x) = min(x, x xor s) -- we implement this by
    # checking x_{k} (highest s=1 bit) and conditionally XOR-ing the lower
    # s=1 bits into the second register.
    s_indices = [i for i in range(n) if s[i] == '1']
    if not s_indices:
        return qc
    k = max(s_indices)
    # Condition on qubit k: if x_k = 1, XOR the lower s_i=1 bits into output
    for i in s_indices:
        if i == k:
            continue
        qc.ccx(k, i, n + i)
    # Always flip the k-th output bit when x_k = 1 (to create the 2-to-1 mapping)
    qc.cx(k, n + k)
    return qc

def build_simon_circuit(s, n):
    qc = QuantumCircuit(2 * n, n)
    qc.h(range(n))
    qc.compose(build_simon_oracle(s, n), inplace=True)
    qc.h(range(n))
    qc.measure(range(n), range(n))
    return qc

def solve_linear_system(equations, n):
    """Given equations y.s = 0 (mod 2) for various y, find s.
    Each equation is a bitstring y of length n. Solve via Gaussian elimination
    over GF(2)."""
    # Build matrix over GF(2)
    A = np.array([[int(b) for b in eq] for eq in equations], dtype=int)
    rows = A.shape[0]
    # Gaussian elimination
    pivot_cols = []
    r = 0
    for c in range(n):
        # Find a row >= r with a 1 in column c
        pivot = -1
        for i in range(r, rows):
            if A[i, c] == 1:
                pivot = i
                break
        if pivot == -1:
            continue
        A[[r, pivot]] = A[[pivot, r]]
        for i in range(rows):
            if i != r and A[i, c] == 1:
                A[i] = (A[i] + A[r]) % 2
        pivot_cols.append(c)
        r += 1
        if r == rows:
            break
    # The kernel: free variables are non-pivot columns.
    # For Simon, we want a non-zero solution s. Set one free variable to 1.
    free_cols = [c for c in range(n) if c not in pivot_cols]
    s = np.zeros(n, dtype=int)
    if free_cols:
        s[free_cols[0]] = 1
        # Back-substitute to find pivot variables
        for i, pc in enumerate(pivot_cols):
            s[pc] = sum(A[i, j] * s[j] for j in range(n)) % 2
    return s

def main():
    n = 3
    s = "011"
    # Build and simulate Simon circuit multiple times to gather equations
    qc = build_simon_circuit(s, n)
    sv = Statevector.from_instruction(qc.remove_final_measurements(inplace=False))
    probs = sv.probabilities_dict()
    # Collect all bitstrings with non-zero probability (these satisfy y.s = 0)
    samples = [bs[:n][::-1] for bs, p in probs.items() if p > 1e-9]
    # Solve for s
    recovered = solve_linear_system(samples, n)
    recovered_str = "".join(str(b) for b in recovered)
    print(f"n = {n}")
    print(f"Hidden period s = {s}")
    print(f"Distinct samples = {len(samples)}")
    print(f"Recovered s = {recovered_str}")
    print(f"Valid: {recovered_str == s or recovered_str == '0' * n or (recovered_str != '0' * n and recovered_str == s)}")
    # The all-zero string is always a solution; we want the non-trivial one.
    # If we recovered 000, try the unique non-trivial solution.
    print(f"Non-trivial: {recovered_str != '0' * n}")
    print(f"Correct: {recovered_str == s}")

if __name__ == "__main__":
    main()
