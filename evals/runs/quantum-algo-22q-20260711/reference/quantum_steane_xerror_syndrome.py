from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

G1 = {0, 2, 4, 6}
G2 = {1, 2, 5, 6}
G3 = {3, 4, 5, 6}
GENS = [G1, G2, G3]

def syndrome_for(q):
    return "".join("1" if q in g else "0" for g in GENS)

def main():
    n_data = 7
    n_anc = 3
    total = n_data + n_anc
    qc = QuantumCircuit(total, n_anc)
    qc.x(3)  # inject X error on qubit 3
    for i, gen in enumerate(GENS):
        anc = n_data + i
        for q in gen:
            qc.cx(q, anc)
        qc.measure(anc, i)
    counts = StatevectorSampler().run([qc], shots=4000).result()[0].data.c.get_counts()
    top = max(counts, key=counts.get)
    # counts key is c2 c1 c0 (Qiskit big-endian), so reverse to get g1 g2 g3
    syndrome = top[::-1]
    error_qubit = -1
    for q in range(n_data):
        if syndrome_for(q) == syndrome:
            error_qubit = q
            break
    print(f"syndrome = {syndrome}")
    print(f"error_qubit = {error_qubit}")

if __name__ == "__main__":
    main()
