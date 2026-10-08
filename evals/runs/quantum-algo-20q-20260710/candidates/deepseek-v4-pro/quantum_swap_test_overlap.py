from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


def main():
    # Build SWAP-test circuit
    qc = QuantumCircuit(3, 1)
    # Prepare state B = |+> on q2
    qc.h(2)
    # SWAP test: H on ancilla, CSWAPs, H on ancilla
    qc.h(0)
    qc.cswap(0, 1, 2)
    qc.h(0)
    # Measure ancilla
    qc.measure(0, 0)

    # Run with StatevectorSampler
    sampler = StatevectorSampler(seed=42)
    job = sampler.run([qc], shots=4000)
    result = job.result()[0]
    counts = result.data.c.get_counts()

    # Compute P(0)
    shots = 4000
    count0 = counts.get(0, 0)
    p0 = count0 / shots

    # Compute |<A|B>|^2 = 2*P(0) - 1
    overlap = 2 * p0 - 1

    print(f"P(0) = {p0:.3f}")
    print(f"|<A|B>|^2 = {overlap:.3f}")

if __name__ == "__main__":
    main()
