import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, partial_trace, DensityMatrix

def ry_angle(p):
    """Angle theta such that R_y(theta) |0> = sqrt(1-p)|0> + sqrt(p)|1>."""
    return 2 * np.arcsin(np.sqrt(p))

def build_bayes_circuit():
    qc = QuantumCircuit(3)
    # P(A=1) = 0.3 on q0
    qc.ry(ry_angle(0.3), 0)
    # P(B=1|A=0) = 0.2, P(B=1|A=1) = 0.8
    # Apply R_y(2*arcsin(sqrt(0.2))) controlled by q0=0,
    # and R_y(2*arcsin(sqrt(0.8))) controlled by q0=1.
    # qiskit cry is controlled by |1>, so:
    # 1. X(q0), cry(angle_low), X(q0) -> apply when q0=0
    # 2. cry(angle_high) -> apply when q0=1
    qc.x(0)
    qc.cry(ry_angle(0.2), 0, 1)
    qc.x(0)
    qc.cry(ry_angle(0.8), 0, 1)
    # P(C=1|B=0) = 0.1, P(C=1|B=1) = 0.7
    qc.x(1)
    qc.cry(ry_angle(0.1), 1, 2)
    qc.x(1)
    qc.cry(ry_angle(0.7), 1, 2)
    return qc

def main():
    qc = build_bayes_circuit()
    sv = Statevector.from_instruction(qc)
    probs = np.abs(sv.data) ** 2
    # P(A=1) = sum over b, c of P(a=1, b, c)
    P_A1 = float(sum(probs[(1 << 2) | (b << 1) | c] for b in range(2) for c in range(2)))
    # P(C=1) = sum over a, b
    P_C1 = float(sum(probs[(a << 2) | (b << 1) | 1] for a in range(2) for b in range(2)))
    # P(A=1, C=1) = sum over b
    P_A1_C1 = float(sum(probs[(1 << 2) | (b << 1) | 1] for b in range(2)))
    P_A1_given_C1 = P_A1_C1 / P_C1 if P_C1 > 0 else 0.0
    # Analytic check
    P_A1_an = 0.3
    P_B1_given_A = {0: 0.2, 1: 0.8}
    P_B1 = sum(P_B1_given_A[a] * (0.3 if a == 1 else 0.7) for a in range(2))
    P_C1_given_B = {0: 0.1, 1: 0.7}
    P_C1_an = sum(P_C1_given_B[b] * P_B1_given_A[b] * (0.3 if b == 1 else 0.7) for b in range(2))
    # Wait, the analytic calculation needs the joint marginalization:
    P_A = {0: 0.7, 1: 0.3}
    P_B = {0: 0, 1: 0}
    for a in range(2):
        for b in range(2):
            P_B[b] += P_B1_given_A[a] * (1 if b == 1 else (1 - P_B1_given_A[a])) * P_A[a]
    # Actually let me re-derive P_B[b]:
    P_B = {0: 0, 1: 0}
    for a in range(2):
        for b in range(2):
            P_B[b] += (P_B1_given_A[a] if b == 1 else (1 - P_B1_given_A[a])) * P_A[a]
    P_C1_an = 0.0
    for b in range(2):
        P_C1_an += P_C1_given_B[b] * P_B[b]
    P_A1_given_C1_an = 0.0
    # P(A=1, C=1) = sum_b P(A=1) P(B=b|A=1) P(C=1|B=b)
    P_A1_and_C1_an = 0.3 * sum((P_B1_given_A[1] if b == 1 else (1 - P_B1_given_A[1])) * P_C1_given_B[b] for b in range(2))
    P_A1_given_C1_an = P_A1_and_C1_an / P_C1_an
    quantum_val = P_A1_given_C1
    analytic_val = P_A1_given_C1_an
    match = abs(quantum_val - analytic_val) < 5e-4
    print(f"P(A=1) = {P_A1:.4f}")
    print(f"P(C=1) = {P_C1:.4f}")
    print(f"P(A=1|C=1) = {analytic_val:.4f}")
    print(f"Quantum P(A=1|C=1) = {quantum_val:.4f}")
    print(f"Match: {match}")

if __name__ == "__main__":
    main()
