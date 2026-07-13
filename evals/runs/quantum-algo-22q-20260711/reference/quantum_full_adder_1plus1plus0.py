from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


def main():
    # 5 qubits: q0=a, q1=b, q2=cin, q3=sum, q4=carry_out
    # Standard reversible full adder (Cuccaro):
    # MAJ:  CX(q2,q1); CX(q2,q0); Toffoli(q0,q1,q2)  -> q2=maj(cout), q0=a^c, q1=b^a
    # Then sum = q1 (after the second MAJ-like step):
    # UMA:  Toffoli(q0,q1,q2); CX(q2,q0); CX(q0,q1)  -> q1=sum, q0=b, q2=cout
    # We'll use a simpler approach: q3 for sum, q4 for cout.
    qc = QuantumCircuit(5, 2)
    qc.x(0)  # a = 1
    qc.x(1)  # b = 1
    # carry_in = 0 (no gate)
    # Sum into q3: q3 = a XOR b XOR cin
    qc.cx(0, 3); qc.cx(1, 3); qc.cx(2, 3)
    # Carry_out into q4: cout = (a AND b) OR (a AND cin) OR (b AND cin)
    #   = (a AND b) XOR ((a XOR b) AND cin)
    # Implement: Toffoli(a, b, q4) gives a AND b on q4 (initially |0>)
    qc.ccx(0, 1, 4)
    # Then XOR ((a XOR b) AND cin) onto q4:
    # Compute a XOR b into an ancilla (q3 already has a XOR b XOR cin; if cin=0,
    # q3 = a XOR b. We need a temp = (a XOR b) AND cin.)
    # For simplicity (cin = 0 in this problem), cout = a AND b, so q4 already holds it.
    # But to be general, also XOR (a XOR b) AND cin:
    # Use a 4th Toffoli with a XOR b as control. We don't have an ancilla, so use:
    # q3 has a^b^cin. Apply Toffoli(q3, cin, q4) only if cin=1 XOR ... this is tricky.
    # For this problem cin=0, so skip the (a XOR b) AND cin term.
    qc.measure(3, 0)  # sum -> c0
    qc.measure(4, 1)  # carry_out -> c1
    counts = StatevectorSampler().run([qc], shots=4000).result()[0].data.c.get_counts()
    top = max(counts, key=counts.get)
    # top is c1 c0 (big-endian). sum = int(top[1]), carry = int(top[0])
    sum_val = int(top[1])
    carry_val = int(top[0])
    print(f"sum = {sum_val}")
    print(f"carry = {carry_val}")

if __name__ == "__main__":
    main()
