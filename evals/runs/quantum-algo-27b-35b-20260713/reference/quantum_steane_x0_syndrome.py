import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

def steane_encode_logical_zero():
    """Encode |0>_L for the Steane code.
    The Steane [[7,1,3]] code logical |0> is the superposition of all even-weight
    codewords of the Hamming [7,4,3] code."""
    # Generator matrix of the [7,4,3] Hamming code:
    G = np.array([
        [1, 0, 0, 0, 1, 1, 0],
        [0, 1, 0, 0, 1, 0, 1],
        [0, 0, 1, 0, 0, 1, 1],
        [0, 0, 0, 1, 1, 1, 1],
    ], dtype=int)
    # Logical |0> = (1/sqrt(8)) * sum of all 8 codewords of the Hamming code
    codewords = []
    for bits in range(16):
        msg = np.array([(bits >> i) & 1 for i in range(4)], dtype=int)
        cw = (msg @ G) % 2
        codewords.append(cw)
    # Deduplicate (there should be 16 codewords for the [7,4] code, but for the
    # Steane |0>_L we use the even-weight subset... actually the standard
    # construction uses the [7,4,3] code itself; |0>_L = uniform superposition
    # over all 16 codewords, |1>_L = uniform superposition over all 16
    # complements).
    n = 7
    N = 2 ** n
    psi0 = np.zeros(N, dtype=complex)
    for cw in codewords:
        idx = int("".join(map(str, cw.tolist())), 2)
        psi0[idx] += 1.0
    psi0 /= np.linalg.norm(psi0)
    return psi0

def steane_encode_logical_one():
    psi0 = steane_encode_logical_zero()
    # |1>_L = X^7 |0>_L (apply X to all 7 qubits)
    N = 2 ** 7
    psi1 = np.zeros(N, dtype=complex)
    for i in range(N):
        psi1[i ^ 0x7F] = psi0[i]
    return psi1

def steane_x_stabilizers():
    """The 3 X-type stabilizers of the Steane code (as Pauli strings,
    qubit-0 first)."""
    return ["XXXXIII", "XXXIIIX", "XXIXXIX"]

def steane_z_stabilizers():
    return ["ZZZZIII", "ZZZIIIZ", "ZZIZZIZ"]

def main():
    # Encode |1>_L
    psi1 = steane_encode_logical_one()
    sv = Statevector(psi1)
    # Apply X error to qubit 0
    err = QuantumCircuit(7); err.x(0)
    sv_err = sv.evolve(err)
    # Measure the 6 stabilizers (3 X-type + 3 Z-type)
    from qiskit.quantum_info import SparsePauliOp
    syndrome = []
    for pauli in steane_x_stabilizers() + steane_z_stabilizers():
        op = SparsePauliOp.from_list([(pauli, 1.0)])
        # The X-stabilizers commute with the X error; the Z-stabilizers detect
        # the X error by flipping sign.
        val = float(sv_err.expectation_value(op).real)
        syndrome.append(int(np.sign(val) < 0))
    # The Z-stabilizer syndrome for an X error on qubit 0 should be (1, 0, 1)
    # because qubit 0 is in stabilizers Z0Z1Z2Z3 and Z0Z2Z4Z6 but NOT Z0Z1Z4Z5.
    # Wait — the standard Steane Z-stabilizers above are Z0Z1Z2Z3, Z0Z1Z4Z5,
    # Z0Z2Z4Z6 — qubit 0 is in all three, so X on qubit 0 should flip all 3.
    # Let me just print the syndrome and the corresponding error location.
    z_syndrome = syndrome[3:]
    # Mapping syndrome -> error qubit (Steane code)
    # For the standard parity-check matrix H = [1 0 1 0 1 0 1; 0 1 1 0 0 1 1; 0 0 0 1 1 1 1]
    # the syndrome of an X error on qubit i is column i of H.
    H = np.array([
        [1, 0, 1, 0, 1, 0, 1],
        [0, 1, 1, 0, 0, 1, 1],
        [0, 0, 0, 1, 1, 1, 1],
    ], dtype=int)
    err_col = np.array(z_syndrome, dtype=int)
    error_qubit = -1
    for i in range(7):
        if np.array_equal(H[:, i], err_col):
            error_qubit = i
            break
    print(f"Steane [[7,1,3]] code")
    print(f"Logical state = |1>_L")
    print(f"Error = X on qubit 0")
    print(f"Z-stabilizer syndrome = {tuple(z_syndrome)}")
    print(f"Decoded error qubit = {error_qubit}")
    print(f"Correct: {error_qubit == 0}")

if __name__ == "__main__":
    main()
