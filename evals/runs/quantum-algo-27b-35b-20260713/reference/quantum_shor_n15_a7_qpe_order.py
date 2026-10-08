import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import QFT
from qiskit.quantum_info import Statevector
from fractions import Fraction

def c_amod15(a, power):
    """Controlled a^power mod 15 gate on 4 target qubits."""
    U = QuantumCircuit(4)
    for _ in range(power):
        # a=7 permutation: 0->0, 1->7, 2->14, 4->13, 5->11, 8->2, 10->5, 7->4, etc.
        U.swap(0, 1); U.swap(1, 2); U.swap(2, 3)
        for q in range(4):
            U.x(q)
    U = U.to_gate().control(1)
    return U

def build_qpe_circuit(a, n_count=8):
    n_target = 4
    creg = ClassicalRegister(n_count, "c")
    qcount = QuantumRegister(n_count, "count")
    qtgt = QuantumRegister(n_target, "tgt")
    qc = QuantumCircuit(qcount, qtgt, creg)
    for q in range(n_count):
        qc.h(qcount[q])
    qc.x(qtgt[0])
    for q in range(n_count):
        qc.append(c_amod15(a, 2 ** q), [qcount[q]] + list(qtgt))
    qc.compose(QFT(n_count, inverse=True), qcount[:], inplace=True)
    qc.measure(qcount, creg)
    return qc

def measured_phase_to_order(counts_int, n_count):
    phase = counts_int / (2 ** n_count)
    frac = Fraction(phase).limit_denominator(15)
    return frac.denominator

def main():
    a = 7
    n_count = 8
    qc = build_qpe_circuit(a, n_count)
    # Use statevector + sampling without hardware
    sv = Statevector.from_instruction(qc.remove_final_measurements(inplace=False))
    probs = sv.probabilities_dict()
    # Pick the most likely bitstring
    best = max(probs.items(), key=lambda kv: kv[1])[0]
    counts_int = int(best, 2)
    r = measured_phase_to_order(counts_int, n_count)
    # Verify a^r mod 15 == 1
    ok = pow(a, r, 15) == 1
    print(f"a = {a}")
    print(f"N = 15")
    print(f"Measured order r = {r}")
    print(f"a^r mod N = {pow(a, r, 15)}")
    print(f"Valid order: {ok and r > 1}")
    # Try to extract a factor
    if r % 2 == 0:
        g = np.gcd(pow(a, r // 2, 15) - 1, 15)
        print(f"Factor found: {g}")
    else:
        print(f"Factor found: 0")

if __name__ == "__main__":
    main()
