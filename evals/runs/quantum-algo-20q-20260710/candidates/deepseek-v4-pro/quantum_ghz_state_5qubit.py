from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


def main():
    # Build 5-qubit GHZ state
    qc = QuantumCircuit(5)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(1, 2)
    qc.cx(2, 3)
    qc.cx(3, 4)
    qc.measure_all()

    # Use StatevectorSampler with 4000 shots
    sampler = StatevectorSampler(seed=42)
    job = sampler.run([qc], shots=4000)
    result = job.result()[0]

    # Get counts
    counts = result.data.meas.get_counts()

    # Compute probability of all-0 or all-1
    total_shots = sum(counts.values())
    all_zero = counts.get('00000', 0)
    all_one = counts.get('11111', 0)
    prob = (all_zero + all_one) / total_shots

    print(f"P(all-0 or all-1) = {prob:.3f}")

if __name__ == "__main__":
    main()
