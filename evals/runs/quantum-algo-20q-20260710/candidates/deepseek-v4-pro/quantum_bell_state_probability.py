from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


def main():
    # Build 2-qubit Bell state |Phi+>
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()

    # Sample 2000 shots
    sampler = StatevectorSampler(seed=42)
    job = sampler.run([qc], shots=2000)
    result = job.result()[0]

    # Get counts
    counts = result.data.meas.get_counts()

    # Compute empirical probabilities
    total_shots = sum(counts.values())
    p00 = counts.get("00", 0) / total_shots
    p11 = counts.get("11", 0) / total_shots

    print(f"P(00) = {p00:.3f}")
    print(f"P(11) = {p11:.3f}")

if __name__ == "__main__":
    main()
