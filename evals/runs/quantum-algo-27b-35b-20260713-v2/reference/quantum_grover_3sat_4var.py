import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.primitives import StatevectorSampler

def satisfies(x0, x1, x2, x3):
    c1 = x0 or (not x1) or x2
    c2 = (not x0) or x1 or (not x3)
    c3 = (not x1) or x2 or x3
    return c1 and c2 and c3

def build_oracle():
    # 4-variable phase oracle: phase -1 on satisfying assignments.
    # Use the standard multi-controlled Z decomposition: for each satisfying
    # assignment, flip the target qubit pattern, apply MCZ, then undo flips.
    qr = QuantumRegister(4, "x")
    qc = QuantumCircuit(qr, name="Oracle")
    satisfying = []
    for bits in range(16):
        x0 = (bits >> 0) & 1
        x1 = (bits >> 1) & 1
        x2 = (bits >> 2) & 1
        x3 = (bits >> 3) & 1
        if satisfies(x0, x1, x2, x3):
            satisfying.append(bits)
    for bits in satisfying:
        # qiskit little-endian: qr[0] is x0 (least-significant bit position in bitstring)
        for i in range(4):
            if not ((bits >> i) & 1):
                qc.x(qr[i])
        qc.mcz([qr[0], qr[1], qr[2]], qr[3])
        for i in range(4):
            if not ((bits >> i) & 1):
                qc.x(qr[i])
    return qc

def build_diffuser(n=4):
    qr = QuantumRegister(n, "x")
    qc = QuantumCircuit(qr, name="Diffuser")
    qc.h(qr)
    qc.x(qr)
    qc.mcz(list(qr[:-1]), qr[-1])
    qc.x(qr)
    qc.h(qr)
    return qc

def main():
    qr = QuantumRegister(4, "x")
    cr = ClassicalRegister(4, "c")
    qc = QuantumCircuit(qr, cr)
    qc.h(qr)
    oracle = build_oracle().to_gate()
    diff = build_diffuser(4).to_gate()
    # 2 Grover iterations (optimal for M=2, N=16)
    qc.append(oracle, qr)
    qc.append(diff, qr)
    qc.append(oracle, qr)
    qc.append(diff, qr)
    qc.measure(qr, cr)
    sampler = StatevectorSampler()
    result = sampler.run([qc], shots=4096).result()
    counts = result[0].data.c.get_counts()
    best, count = max(counts.items(), key=lambda kv: kv[1])
    total = sum(counts.values())
    peak = count / total
    # best is qiskit little-endian: b3 b2 b1 b0
    x0 = int(best[3]); x1 = int(best[2]); x2 = int(best[1]); x3 = int(best[0])
    valid = satisfies(x0, x1, x2, x3)
    # Count satisfying assignments
    nsat = sum(1 for b in range(16) if satisfies((b>>0)&1, (b>>1)&1, (b>>2)&1, (b>>3)&1))
    print(f"Satisfying count = {nsat}")
    print(f"Most likely = {best}")
    print(f"Valid: {valid}")
    print(f"Peak prob = {peak:.4f}")

if __name__ == "__main__":
    main()
