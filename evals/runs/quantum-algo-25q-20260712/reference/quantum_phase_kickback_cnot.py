"""Phase kickback via CNOT.

When the control of a CNOT is in |+> = (|0>+|1>)/sqrt(2) and the target
is in |-> = (|0>-|1>)/sqrt(2), the CNOT applies a phase of -1 to the
|11> component, which is equivalent to applying Z to the control qubit.
We verify by measuring the control in the X basis: a |+> state gives
measurement 0 with probability 1, but after the kickback it becomes
|-> and gives measurement 1 with probability 1.
"""
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


def main():
    qc = QuantumCircuit(2, 1)
    qc.h(0)  # control in |+>
    qc.x(1)  # target in |1>
    qc.h(1)  # target in |->
    qc.cx(0, 1)  # phase kickback: control picks up a Z (becomes |->)
    # Measure control in X basis: apply H then measure
    qc.h(0)
    qc.measure(0, 0)
    counts = StatevectorSampler().run([qc], shots=4000).result()[0].data.c.get_counts()
    total = sum(counts.values())
    p1 = counts.get("1", 0) / total
    print(f"P(control=1) = {p1:.3f}")
    print(f"kickback: {p1 > 0.9}")


if __name__ == "__main__":
    main()
