from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.primitives import Sampler


def main():
    # Create quantum circuit with 5 qubits (3 data + 2 syndrome) and 5 classical bits
    qc = QuantumCircuit(5, 5)

    # Step 1: Encode |1> into |111> by applying X on each data qubit
    qc.x(0)
    qc.x(1)
    qc.x(2)

    # Step 2: Apply X error on middle qubit (qubit 1)
    qc.x(1)

    # Step 3: Syndrome measurement
    # c0 = q0 XOR q1: CX q0->q3, CX q1->q3
    qc.cx(0, 3)
    qc.cx(1, 3)
    # c1 = q1 XOR q2: CX q1->q4, CX q2->q4
    qc.cx(1, 4)
    qc.cx(2, 4)

    # Step 4: Measure all 5 qubits
    qc.measure([0, 1, 2, 3, 4], [0, 1, 2, 3, 4])

    # Step 5: Use StatevectorSampler (1000 shots)
    backend = AerSimulator()
    sampler = Sampler()
    job = sampler.run([qc], shots=1000)
    result = job.result()

    # Get counts from the quasi-probabilities
    counts = result.quasi_dists[0].binary_probabilities()

    # Decode data qubits via majority vote
    majority_one_count = 0
    total_shots = 0

    for bitstring, prob in counts.items():
        # bitstring is little-endian: leftmost char = highest qubit index (q4)
        # So bitstring[0] = q4, bitstring[1] = q3, bitstring[2] = q2, bitstring[3] = q1, bitstring[4] = q0
        # Extract data qubits: q0 = bitstring[4], q1 = bitstring[3], q2 = bitstring[2]
        q0_val = int(bitstring[4])
        q1_val = int(bitstring[3])
        q2_val = int(bitstring[2])

        # Majority vote
        sum_bits = q0_val + q1_val + q2_val
        majority = 1 if sum_bits >= 2 else 0

        # Convert probability to count (approximate)
        count = int(round(prob * 1000))
        total_shots += count
        if majority == 1:
            majority_one_count += count

    # Calculate probability
    prob_majority_one = majority_one_count / total_shots if total_shots > 0 else 0.0

    print(f"P(majority=1) = {prob_majority_one:.3f}")

if __name__ == "__main__":
    main()
