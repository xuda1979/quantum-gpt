from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


def main():
    # 1. Build |5> = |101> on 3 qubits
    qc = QuantumCircuit(3)
    qc.x(0)
    qc.x(2)
    qc.barrier()

    # 2. Apply 3-qubit QFT
    # QFT on 3 qubits
    qc.h(2)
    qc.cp(3.141592653589793/2, 1, 2)  # pi/2
    qc.cp(3.141592653589793/4, 0, 2)  # pi/4
    qc.h(1)
    qc.cp(3.141592653589793/2, 0, 1)  # pi/2
    qc.h(0)
    # Swap qubits to get standard QFT ordering
    qc.swap(0, 2)

    qc.measure_all()

    # 3. Simulate with StatevectorSampler
    sampler = StatevectorSampler(seed=42)
    job = sampler.run([qc], shots=2000)
    result = job.result()

    # Get counts from the first (and only) circuit result
    counts = result[0].data.meas.get_counts()

    # Sort by count descending, get top two
    sorted_counts = sorted(counts.items(), key=lambda item: item[1], reverse=True)
    top1 = sorted_counts[0]
    top2 = sorted_counts[1] if len(sorted_counts) > 1 else ("N/A", 0)

    print(f"Top: {top1[0]} count={top1[1]}")
    print(f"2nd: {top2[0]} count={top2[1]}")

if __name__ == "__main__":
    main()
