"""Deutsch-Jozsa algorithm on a constant function f(x)=1 for all x.

For a 3-bit input x, f(x)=1 (constant). The Deutsch-Jozsa algorithm
prepares |-> = (|0>-|1>)/sqrt(2) on the auxiliary qubit and applies
the oracle U_f: |x>|y> -> |x>|y xor f(x)>. After H^{⊗n} on the input
register, a constant function yields |000...0> with probability 1.
"""
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


def main():
    n = 3  # number of input qubits
    qc = QuantumCircuit(n + 1, n)
    # Initialize auxiliary in |-> state
    qc.x(n)
    qc.h(n)
    # Apply H^{⊗n} to input register
    for i in range(n):
        qc.h(i)
    # Oracle: f(x) = 1 (constant). This is X on the auxiliary controlled by
    # nothing (always flips), equivalently just X on auxiliary.
    # U_f |x>|y> = |x>|y xor 1> = |x>|NOT y>
    qc.x(n)
    # Apply H^{⊗n} again to input register
    for i in range(n):
        qc.h(i)
    # Measure input register
    qc.measure(range(n), range(n))
    counts = StatevectorSampler().run([qc], shots=4000).result()[0].data.c.get_counts()
    top = max(counts, key=counts.get)
    # For a constant function, we always measure 000.
    is_constant = (top == "000")
    print(f"Measurement: {top}")
    print(f"Function is: {'constant' if is_constant else 'balanced'}")


if __name__ == "__main__":
    main()
