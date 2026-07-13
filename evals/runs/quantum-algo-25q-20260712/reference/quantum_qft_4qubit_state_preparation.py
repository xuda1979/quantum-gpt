"""4-qubit QFT applied to a computational basis state |5> = |0101>.

The QFT maps |x> -> (1/sqrt(N)) sum_k exp(2*pi*i*k*x/N) |k>.
For x=5, N=16: the amplitude of |k> is (1/4) * exp(2*pi*i*5*k/16).
The probability of measuring |k> is 1/16 = 0.0625 for all k (since
QFT of a basis state is a uniform superposition up to phases).
"""
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFT
from qiskit.primitives import StatevectorSampler


def main():
    n = 4
    x = 5  # |0101>
    qc = QuantumCircuit(n, n)
    # Prepare |5> = |0101> (qubit 0 = LSB = 1, qubit 1 = 0, qubit 2 = 1, qubit 3 = 0)
    for i in range(n):
        if (x >> i) & 1:
            qc.x(i)
    qc.append(QFT(n, inverse=False), range(n))
    qc.measure(range(n), range(n))
    counts = StatevectorSampler().run([qc], shots=8000).result()[0].data.c.get_counts()
    total = sum(counts.values())
    # All 16 outcomes should be roughly equally likely
    probs = {k: v / total for k, v in counts.items()}
    max_p = max(probs.values())
    min_p = min(probs.values())
    n_outcomes = len(probs)
    # Theoretical probability per outcome is 1/16 = 0.0625
    print(f"input_state = {x:0{n}b}")
    print(f"n_outcomes = {n_outcomes}")
    print(f"max_prob = {max_p:.3f}")
    print(f"min_prob = {min_p:.3f}")
    print(f"uniform: {n_outcomes == 16 and max_p - min_p < 0.05}")


if __name__ == "__main__":
    main()
