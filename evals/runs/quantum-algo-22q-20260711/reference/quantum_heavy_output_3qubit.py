import numpy as np
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler
from qiskit.quantum_info import Statevector, random_unitary


def build_random_circuit(n=3, depth=3, seed=42):
    rng = np.random.default_rng(seed)
    qc = QuantumCircuit(n, n)
    for d in range(depth):
        for q in range(n):
            # Random SU(2) gate
            U = random_unitary(2, seed=int(rng.integers(0, 2**31 - 1)))
            qc.append(U, [q])
        # Random permutation
        perm = list(range(n))
        rng.shuffle(perm)
        # Apply permutation via SWAPs (simple approach: swap qubits to match perm)
        # For simplicity, apply a sequence of SWAPs based on the permutation.
        # A simple way: for each i, if perm[i] != i, swap qubit i with perm[i].
        for i in range(n):
            if perm[i] != i:
                qc.swap(i, perm[i])
                # Mark to avoid re-swapping
                perm[perm.index(i)] = perm[i]
                perm[i] = i
    qc.measure(range(n), range(n))
    return qc

def main():
    n = 3
    qc_meas = build_random_circuit(n, depth=3, seed=42)
    # Build the same circuit without measurement for statevector
    qc_sv = QuantumCircuit(n)
    for instr in qc_meas.data:
        if instr.operation.name != "measure":
            qc_sv.append(instr)
    sv = Statevector.from_instruction(qc_sv)
    probs = sv.probabilities_dict()
    # Median probability
    p_values = sorted(probs.values())
    median = p_values[len(p_values) // 2]
    heavy = {b for b, p in probs.items() if p > median}
    counts = StatevectorSampler().run([qc_meas], shots=8000).result()[0].data.c.get_counts()
    total = sum(counts.values())
    ho_count = sum(counts.get(b, 0) for b in heavy)
    ho_prob = ho_count / total
    print(f"heavy_output_prob = {ho_prob:.3f}")
    print(f"passes: {'True' if ho_prob > 0.687 else 'False'}")

if __name__ == "__main__":
    main()
