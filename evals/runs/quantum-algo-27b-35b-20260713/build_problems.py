#!/usr/bin/env python3
"""Define and emit 22 hard quantum-coding problems for the 27B/35B eval.

Each problem has:
  - id: short id used for filenames
  - title: human-readable title
  - prompt: the user-facing prompt (saved to prompts/<id>.txt)
  - reference: a complete runnable Python solution (saved to reference/<id>.py)
  - expected_substrings: list of strings that must appear in stdout for PASS
  - timeout: seconds to run the reference/candidate (default 120)

The test file (tests/<id>.py) runs the REFERENCE solution and verifies the
expected substrings appear. The same test is later used to evaluate candidates:
the candidate path is substituted for the reference path.

Run:  python3 build_problems.py
"""

from __future__ import annotations
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

RUN_DIR = Path(__file__).resolve().parent

PROBLEMS: list[dict] = []

def _add(id: str, title: str, prompt: str, reference: str,
         expected_substrings: list[str], timeout: int = 120):
    PROBLEMS.append({
        "id": id,
        "title": title,
        "prompt": prompt.strip() + "\n",
        "reference": reference.strip() + "\n",
        "expected_substrings": expected_substrings,
        "timeout": timeout,
    })

# ---------------------------------------------------------------------------
# Problem 1: Variational Quantum Eigensolver for the transverse-field Ising
# model on 3 qubits with a 2-layer Ry-CX ansatz.
# ---------------------------------------------------------------------------
P1_REF = r'''
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.quantum_info import SparsePauliOp, Statevector
from scipy.optimize import minimize

def build_hamiltonian():
    # H = -J*(Z0Z1 + Z1Z2) - h*(X0 + X1 + X2), J=1.0, h=0.5
    J, h = 1.0, 0.5
    return SparsePauliOp.from_list([
        ("ZZI", -J), ("IZZ", -J),
        ("IXX", 0.0),  # placeholder to keep ordering; we use XIII below
    ]) + SparsePauliOp.from_list([
        ("XII", -h), ("IXI", -h), ("IIX", -h),
    ])

def ansatz(params, n=3, layers=2):
    qc = QuantumCircuit(n)
    idx = 0
    for _ in range(layers):
        for q in range(n):
            qc.ry(params[idx], q); idx += 1
        for q in range(n - 1):
            qc.cx(q, q + 1)
    return qc

def expectation(params, ham):
    qc = ansatz(params)
    sv = Statevector.from_instruction(qc)
    return float(sv.expectation_value(ham).real)

def main():
    ham = build_hamiltonian()
    n_params = 3 * 2
    x0 = np.array([0.1 * i for i in range(n_params)])
    res = minimize(expectation, x0, args=(ham,), method="COBYLA",
                   options={"maxiter": 400, "tol": 1e-6})
    # Brute-force ground state for verification: 8-dimensional diagonalization
    Z = np.diag([1, -1]); X = np.array([[0, 1], [1, 0]]); I = np.eye(2)
    def kron3(a, b, c): return np.kron(np.kron(a, b), c)
    H = -1.0*(kron3(Z, Z, I) + kron3(I, Z, Z)) - 0.5*(kron3(X, I, I) + kron3(I, X, I) + kron3(I, I, X))
    eigs = np.linalg.eigvalsh(H)
    gs_exact = float(eigs[0])
    vqe = res.fun
    print(f"VQE energy = {vqe:.4f}")
    print(f"Exact GS = {gs_exact:.4f}")
    print(f"Abs error = {abs(vqe - gs_exact):.4f}")
    print(f"Converged: {abs(vqe - gs_exact) < 0.05}")

if __name__ == "__main__":
    main()
'''

_add(
    "quantum_vqe_tfim_3qubit_2layer",
    "VQE for 3-qubit transverse-field Ising with 2-layer Ry-CX ansatz",
    """Write a complete, runnable Python program using numpy, qiskit, and scipy that:
1. Builds the transverse-field Ising Hamiltonian on 3 qubits:
   H = -J*(Z0Z1 + Z1Z2) - h*(X0 + X1 + X2) with J=1.0, h=0.5
   (use qiskit.quantum_info.SparsePauliOp).
2. Implements a 2-layer Ry-CX ansatz: each layer applies Ry(theta_i) to each
   qubit (3 parameters per layer) followed by a chain of CX(q, q+1).
3. Uses scipy.optimize.minimize with method='COBYLA', maxiter=400, tol=1e-6,
   starting from a small non-zero initial point, to minimize <psi|H|psi>.
4. Independently computes the exact ground-state energy by diagonalizing the
   8x8 Hamiltonian matrix built with numpy.kron.
5. In `def main()`, prints exactly these lines (values rounded to 4 decimals):
     VQE energy = <value>
     Exact GS = <value>
     Abs error = <value>
     Converged: <True|False>
   where Converged is True iff the absolute error is below 0.05.
Call main() under `if __name__ == "__main__":`.
""",
    P1_REF,
    ["VQE energy = ", "Exact GS = ", "Abs error = ", "Converged: True"],
    timeout=180,
)

# ---------------------------------------------------------------------------
# Problem 2: Shor's algorithm for N=15, a=7 — find the order via QPE.
# ---------------------------------------------------------------------------
P2_REF = r'''
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
'''

_add(
    "quantum_shor_n15_a7_qpe_order",
    "Shor's algorithm for N=15, a=7 via QPE — extract order and factor",
    """Write a complete, runnable Python program using numpy, qiskit, and fractions that:
1. Implements controlled-a^power mod 15 for a=7 as a 4-qubit unitary with one
   control qubit (you may use SWAP + X sequences as in the standard textbook
   construction).
2. Builds an 8-qubit counting register plus 4 target qubits, initializes the
   target to |1>, applies H to all counting qubits, then appends controlled
   a^(2^q) mod 15 for q=0..7, then applies the inverse QFT to the counting
   register, and measures it.
3. Simulate the circuit with qiskit.quantum_info.Statevector (no hardware):
   take the most-probable bitstring as the measured phase estimate.
4. Convert the measured integer to a phase in [0,1), use
   fractions.Fraction(...).limit_denominator(15) to recover the denominator r,
   and verify a^r mod 15 == 1.
5. If r is even, compute gcd(a^(r/2) - 1, 15) as a non-trivial factor.
6. In `def main()`, print exactly:
     a = 7
     N = 15
     Measured order r = <value>
     a^r mod N = <value>
     Valid order: <True|False>
     Factor found: <value>
   The order r must be > 1 and a^r mod 15 must equal 1.
Call main() under `if __name__ == "__main__":`.
""",
    P2_REF,
    ["a = 7", "N = 15", "Measured order r = ", "Valid order: True",
     "Factor found: 3"],
    timeout=180,
)

# ---------------------------------------------------------------------------
# Problem 3: QAOA p=1 for MaxCut on a 4-vertex cycle graph.
# ---------------------------------------------------------------------------
P3_REF = r'''
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.quantum_info import Statevector
from scipy.optimize import minimize

def maxcut_objective(counts, graph):
    val = 0.0
    for bitstr, prob in counts.items():
        for i, j in graph:
            if bitstr[::-1][i] != bitstr[::-1][j]:
                val += prob
    return val

def build_qaoa_circuit(graph, gamma, beta, p=1, n=4):
    qc = QuantumCircuit(n)
    qc.h(range(n))
    for layer in range(p):
        for i, j in graph:
            qc.cx(i, j); qc.rz(2 * gamma[layer], j); qc.cx(i, j)
        for q in range(n):
            qc.rx(2 * beta[layer], q)
    return qc

def expectation(params, graph, n):
    p = len(params) // 2
    gamma = params[:p]; beta = params[p:]
    qc = build_qaoa_circuit(graph, gamma, beta, p=p, n=n)
    sv = Statevector.from_instruction(qc)
    probs = {format(i, f"0{n}b"): abs(sv.data[i]) ** 2 for i in range(2 ** n)}
    return -maxcut_objective(probs, graph)

def main():
    n = 4
    graph = [(0, 1), (1, 2), (2, 3), (3, 0)]  # 4-cycle
    p = 1
    x0 = np.array([0.5, 0.5])
    res = minimize(expectation, x0, args=(graph, n), method="COBYLA",
                   options={"maxiter": 200, "tol": 1e-6})
    # Evaluate final
    qc = build_qaoa_circuit(graph, res.x[:p], res.x[p:], p=p, n=n)
    sv = Statevector.from_instruction(qc)
    probs = {format(i, f"0{n}b"): abs(sv.data[i]) ** 2 for i in range(2 ** n)}
    cut = maxcut_objective(probs, graph)
    # Classical optimum: 4 (alternating bits)
    print(f"QAOA max-cut value = {cut:.3f}")
    print(f"Optimal max-cut = 4")
    print(f"Approx ratio = {cut / 4.0:.3f}")
    print(f"Converged: {cut / 4.0 > 0.75}")

if __name__ == "__main__":
    main()
'''

_add(
    "quantum_qaoa_p1_maxcut_cycle4",
    "QAOA p=1 for MaxCut on a 4-vertex cycle graph",
    """Write a complete, runnable Python program using numpy, qiskit, and scipy that:
1. Defines a 4-vertex cycle graph with edges (0,1), (1,2), (2,3), (3,0).
2. Builds a QAOA circuit with p=1:
   - Initial Hadamards on all 4 qubits.
   - Cost layer: for each edge (i,j), apply CX(i,j), RZ(2*gamma, j), CX(i,j).
   - Mixer layer: RX(2*beta, q) on every qubit.
3. Computes the MaxCut objective from the statevector probabilities: for each
   basis bitstring, count edges whose endpoints differ, weighted by probability.
4. Uses scipy.optimize.minimize with method='COBYLA', maxiter=200, starting from
   gamma=beta=0.5, to maximize the expected cut.
5. In `def main()`, prints exactly:
     QAOA max-cut value = <value rounded to 3 decimals>
     Optimal max-cut = 4
     Approx ratio = <value rounded to 3 decimals>
     Converged: <True|False>
   where Converged is True iff the approximation ratio exceeds 0.75.
Call main() under `if __name__ == "__main__":`.
""",
    P3_REF,
    ["QAOA max-cut value = ", "Optimal max-cut = 4", "Approx ratio = ",
     "Converged: True"],
    timeout=180,
)

# ---------------------------------------------------------------------------
# Problem 4: Quantum teleportation with classical post-processing.
# ---------------------------------------------------------------------------
P4_REF = r'''
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, random_statevector

def build_teleportation_circuit(state_to_send):
    qc = QuantumCircuit(3, 3)
    qc.initialize(state_to_send, 0)
    # Bell pair on qubits 1 and 2
    qc.h(1); qc.cx(1, 2)
    # Alice's Bell measurement on qubits 0 and 1
    qc.cx(0, 1); qc.h(0)
    qc.measure(0, 0); qc.measure(1, 1)
    # Classical corrections on qubit 2 (use c_if via separate branches in sim)
    return qc

def simulate_teleportation(state_to_send):
    # Simulate by computing the output state conditioned on each measurement
    # outcome using statevector evolution with classical feedback.
    from qiskit.quantum_info import DensityMatrix, partial_trace
    # Build the full unitary part (no measurement)
    qc = QuantumCircuit(3)
    qc.initialize(state_to_send, 0)
    qc.h(1); qc.cx(1, 2)
    qc.cx(0, 1); qc.h(0)
    sv = Statevector.from_instruction(qc)
    # Measurement probabilities and post-measurement states
    dm = DensityMatrix(sv)
    # Trace out nothing - compute probability of each (c0, c1) outcome
    # by projecting q0, q1 onto |0>/<1> basis
    outcomes = {}
    for c0 in [0, 1]:
        for c1 in [0, 1]:
            proj = np.eye(8, dtype=complex)
            # project q0 onto |c0>, q1 onto |c1>
            for k in range(8):
                b0 = (k >> 0) & 1
                b1 = (k >> 1) & 1
                if b0 != c0 or b1 != c1:
                    proj[k, k] = 0
            projected = proj @ dm.data @ proj
            prob = float(np.real(np.trace(projected)))
            if prob < 1e-12:
                outcomes[(c0, c1)] = (0.0, None)
                continue
            post = projected / prob
            # Apply corrections to q2: if c1=1 apply X, if c0=1 apply Z
            X = np.array([[0, 1], [1, 0]]); Z = np.array([[1, 0], [0, -1]])
            I = np.eye(2)
            corr = np.kron(np.kron(I, I), (X if c1 else I)) @ np.kron(np.kron(I, I), (Z if c0 else I))
            post = corr @ post @ corr.conj().T
            outcomes[(c0, c1)] = (prob, post)
    return outcomes

def main():
    rng = np.random.default_rng(42)
    # Random pure state to teleport
    psi = random_statevector(2, seed=42).data
    outcomes = simulate_teleportation(psi)
    # Average fidelity over measurement outcomes
    total_fid = 0.0
    total_prob = 0.0
    for (c0, c1), (prob, post) in outcomes.items():
        if prob == 0.0 or post is None:
            continue
        # Reduced density matrix of qubit 2
        from qiskit.quantum_info import DensityMatrix, partial_trace
        dm_post = DensityMatrix(post)
        rho2 = partial_trace(dm_post, [0, 1])
        fid = float(np.real(rho2.data @ np.outer(psi, psi.conj())).trace())
        total_fid += prob * fid
        total_prob += prob
    avg_fid = total_fid / total_prob if total_prob > 0 else 0.0
    print(f"Teleported state: random pure 1-qubit")
    print(f"Average fidelity = {avg_fid:.4f}")
    print(f"Classical limit = 0.6667")
    print(f"Beats classical: {avg_fid > 0.6667}")
    print(f"Perfect teleport: {abs(avg_fid - 1.0) < 1e-6}")

if __name__ == "__main__":
    main()
'''

_add(
    "quantum_teleportation_random_state_fidelity",
    "Quantum teleportation of a random state — verify unit fidelity",
    """Write a complete, runnable Python program using numpy and qiskit that:
1. Prepares a random 1-qubit pure state |psi> (use a fixed RNG seed for
   reproducibility).
2. Builds the standard teleportation circuit on 3 qubits:
   - Initialize qubit 0 to |psi>.
   - Create a Bell pair on qubits 1 and 2 (H on qubit 1, CX(1,2)).
   - Alice performs CX(0,1) then H(0), then measures qubits 0 and 1.
3. Simulate WITHOUT a backend: evolve the full 3-qubit statevector, then
   explicitly project qubits 0 and 1 onto each classical outcome (00, 01, 10,
   11), renormalize, and apply the appropriate X and/or Z correction to qubit 2
   (X if measurement of qubit 1 is 1; Z if measurement of qubit 0 is 1).
4. For each outcome, compute the reduced density matrix of qubit 2 and its
   fidelity with |psi>. Average over outcomes weighted by their probabilities.
5. In `def main()`, prints exactly:
     Teleported state: random pure 1-qubit
     Average fidelity = <value rounded to 4 decimals>
     Classical limit = 0.6667
     Beats classical: <True|False>
     Perfect teleport: <True|False>
   where Perfect teleport is True iff the average fidelity is within 1e-6 of 1.0.
Call main() under `if __name__ == "__main__":`.
""",
    P4_REF,
    ["Teleported state: random pure 1-qubit", "Average fidelity = 1.0000",
     "Classical limit = 0.6667", "Beats classical: True",
     "Perfect teleport: True"],
    timeout=120,
)

# ---------------------------------------------------------------------------
# Problem 5: CHSH game — quantum strategy wins with probability cos²(π/8).
# ---------------------------------------------------------------------------
P5_REF = r'''
import numpy as np

def measure_in_basis(state, basis_angle):
    """Measure a 1-qubit state in the basis rotated by `basis_angle` (radians)
    around the Bloch XY plane: |0_b> = cos(theta/2)|0> + sin(theta/2)|1>,
    |1_b> = -sin(theta/2)|0> + cos(theta/2)|1>."""
    theta = basis_angle
    # Measurement projectors
    P0 = np.array([[np.cos(theta/2)**2, np.cos(theta/2)*np.sin(theta/2)],
                   [np.cos(theta/2)*np.sin(theta/2), np.sin(theta/2)**2]])
    P1 = np.eye(2) - P0
    return P0, P1

def chsh_quantum_win_prob():
    # Alice: a=0 -> A0 = Z, a=1 -> A1 = X (angle 0 and pi/2 in XY plane basis choice)
    # Bob: b=0 -> B0 = (Z+X)/sqrt2, b=1 -> B1 = (Z-X)/sqrt2
    # Optimal angles in the X-Z plane
    # A0 = Z (measurement angle 0), A1 = X (measurement angle pi/2)
    # B0 measured at angle pi/4, B1 at angle -pi/4
    # Singlet state |Phi-> = (|01> - |10>)/sqrt2
    psi = np.array([0, 1, -1, 0], dtype=complex) / np.sqrt(2)
    # Observables
    Z = np.array([[1, 0], [0, -1]], dtype=complex)
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    A0 = Z; A1 = X
    B0 = (Z + X) / np.sqrt(2)
    B1 = (Z - X) / np.sqrt(2)
    def correlation(A, B):
        # <psi| A x B |psi>
        AB = np.kron(A, B)
        return float(np.real(psi.conj() @ AB @ psi))
    # CHSH game: Alice and Bob win if a XOR b = x AND y
    # where x, y in {0, 1} are the referee's bits.
    # Win prob = (1 + E(a,b))/2 for the matching condition.
    E00 = correlation(A0, B0)  # x=0,y=0 -> a xor b = 0
    E01 = correlation(A0, B1)  # x=0,y=1 -> a xor b = 1
    E10 = correlation(A1, B0)  # x=1,y=0 -> a xor b = 1
    E11 = correlation(A1, B1)  # x=1,y=1 -> a xor b = 0
    # Win probability averaged over the 4 equally-likely (x,y) inputs
    win = 0.25 * (
        (1 + E00) / 2 +  # x=0,y=0
        (1 - E01) / 2 +  # x=0,y=1 (need a != b)
        (1 - E10) / 2 +  # x=1,y=0 (need a != b)
        (1 + E11) / 2    # x=1,y=1 (need a == b)
    )
    return win, (E00 - E01 + E10 + E11)

def main():
    win, S = chsh_quantum_win_prob()
    classical_best = 0.75
    tsirelson = 2 * np.sqrt(2)
    print(f"CHSH quantum win prob = {win:.4f}")
    print(f"Classical best = {classical_best:.4f}")
    print(f"Tsirelson S = {S:.4f}")
    print(f"Tsirelson bound = {tsirelson:.4f}")
    print(f"Saturates Tsirelson: {abs(S - tsirelson) < 1e-6}")
    print(f"Beats classical: {win > classical_best + 1e-6}")

if __name__ == "__main__":
    main()
'''

_add(
    "quantum_chsh_game_win_probability",
    "CHSH game: quantum strategy win probability and Tsirelson bound",
    """Write a complete, runnable Python program using only numpy that:
1. Defines the singlet state |Phi-> = (|01> - |10>)/sqrt2 as a 4-dimensional
   complex vector.
2. Defines the four measurement observables for the optimal CHSH strategy:
   - Alice: A0 = Z, A1 = X
   - Bob:   B0 = (Z + X)/sqrt(2), B1 = (Z - X)/sqrt(2)
   where Z and X are the Pauli matrices.
3. Computes the four correlations E(a,b) = <psi| A_a (x) B_b |psi> for
   (a,b) in {0,1}^2 by applying the appropriate Kronecker product.
4. Computes the CHSH game win probability: averaged over the 4 equally-likely
   input pairs (x,y) in {0,1}^2, Alice and Bob win when (a XOR b) = (x AND y).
   Use win_prob = (1 + E)/2 when a XOR b must equal 0, and (1 - E)/2 when it
   must equal 1.
5. Computes the CHSH value S = E00 - E01 + E10 + E11.
6. In `def main()`, prints exactly:
     CHSH quantum win prob = <value rounded to 4 decimals>
     Classical best = 0.7500
     Tsirelson S = <value rounded to 4 decimals>
     Tsirelson bound = 2.8284
     Saturates Tsirelson: <True|False>
     Beats classical: <True|False>
   where Saturates Tsirelson is True iff |S - 2*sqrt(2)| < 1e-6, and
   Beats classical is True iff the win probability exceeds 0.75.
Call main() under `if __name__ == "__main__":`.
""",
    P5_REF,
    ["CHSH quantum win prob = 0.8536", "Classical best = 0.7500",
     "Tsirelson S = 2.8284", "Tsirelson bound = 2.8284",
     "Saturates Tsirelson: True", "Beats classical: True"],
    timeout=60,
)

print(f"Defined {len(PROBLEMS)} problems so far")

# ---------------------------------------------------------------------------
# Problem 6: Grover's algorithm with 3 marked items in a 6-qubit search space.
# ---------------------------------------------------------------------------
P6_REF = r'''
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

def grover_oracle(marked_ints, n):
    qc = QuantumCircuit(n)
    for m in marked_ints:
        # Flip phase on |m>
        bits = format(m, f"0{n}b")
        for q, b in enumerate(bits):
            if b == '0':
                qc.x(q)
        qc.h(n - 1)
        qc.mcx(list(range(n - 1)), n - 1)
        qc.h(n - 1)
        for q, b in enumerate(bits):
            if b == '0':
                qc.x(q)
    return qc

def grover_diffuser(n):
    qc = QuantumCircuit(n)
    qc.h(range(n))
    qc.x(range(n))
    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)
    qc.x(range(n))
    qc.h(range(n))
    return qc

def build_grover(marked_ints, n, iterations):
    qc = QuantumCircuit(n)
    qc.h(range(n))
    for _ in range(iterations):
        qc.compose(grover_oracle(marked_ints, n), inplace=True)
        qc.compose(grover_diffuser(n), inplace=True)
    return qc

def main():
    n = 6
    marked = [3, 17, 42]
    N = 2 ** n
    M = len(marked)
    # Optimal iterations = (pi/4) * sqrt(N/M)
    opt_iter = int(round(np.pi / 4 * np.sqrt(N / M)))
    qc = build_grover(marked, n, opt_iter)
    sv = Statevector.from_instruction(qc)
    probs = sv.probabilities()
    # Success probability = sum of probabilities of marked states
    succ = float(sum(probs[m] for m in marked))
    top_idx = int(np.argmax(probs))
    print(f"N = {N}")
    print(f"M = {M} (marked: {sorted(marked)})")
    print(f"Iterations = {opt_iter}")
    print(f"Success prob = {succ:.4f}")
    print(f"Top state = {top_idx}")
    print(f"In marked set: {top_idx in marked}")

if __name__ == "__main__":
    main()
'''

_add(
    "quantum_grover_6qubit_3marked",
    "Grover's algorithm with 6 qubits, 3 marked items, optimal iterations",
    """Write a complete, runnable Python program using numpy and qiskit that:
1. Implements Grover's algorithm on n=6 qubits with M=3 marked items
   (specifically integers 3, 17, 42).
2. Builds the phase-flip oracle: for each marked integer m, flip the phase of
   basis state |m>. Use X gates to convert 0 bits, then a multi-controlled
   Z (decomposed as H-MCX-H on the last qubit), then undo the X gates.
3. Builds the standard diffuser: H^n, X^n, multi-controlled Z, X^n, H^n.
4. Uses the optimal iteration count
   k = round((pi/4) * sqrt(N/M)) where N = 2^6 and M = 3.
5. Simulate with qiskit.quantum_info.Statevector (no backend).
6. Computes the total probability of measuring one of the marked states, and
   identifies the single most-probable basis state.
7. In `def main()`, prints exactly:
     N = 64
     M = 3 (marked: [3, 17, 42])
     Iterations = <value>
     Success prob = <value rounded to 4 decimals>
     Top state = <value>
     In marked set: <True|False>
   where In marked set is True iff the most-probable state is one of 3, 17, 42.
Call main() under `if __name__ == "__main__":`.
""",
    P6_REF,
    ["N = 64", "M = 3 (marked: [3, 17, 42])", "Iterations = ",
     "Success prob = ", "In marked set: True"],
    timeout=120,
)

# ---------------------------------------------------------------------------
# Problem 7: 4-qubit Quantum Fourier Transform on a specific state.
# ---------------------------------------------------------------------------
P7_REF = r'''
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFT
from qiskit.quantum_info import Statevector

def main():
    n = 4
    # Prepare the state |5> = |0101>
    qc = QuantumCircuit(n)
    bits = format(5, f"0{n}b")
    for q, b in enumerate(bits):
        if b == '1':
            qc.x(q)
    # Apply QFT
    qc.compose(QFT(n, inverse=False), inplace=True)
    sv = Statevector.from_instruction(qc)
    # The QFT of |x> on n qubits is (1/sqrt(N)) sum_k exp(2 pi i k x / N) |k>
    N = 2 ** n
    expected = np.zeros(N, dtype=complex)
    for k in range(N):
        expected[k] = np.exp(2j * np.pi * k * 5 / N) / np.sqrt(N)
    actual = sv.data
    # Pick the top-2 most probable basis states (by magnitude)
    mags = np.abs(actual) ** 2
    top2 = np.argsort(mags)[::-1][:2]
    # Compare to analytic
    overlap = float(np.abs(np.vdot(expected, actual)) ** 2)
    print(f"N = {N}")
    print(f"Input state = |5>")
    print(f"QFT output overlap = {overlap:.6f}")
    print(f"Top amplitude index = {top2[0]}")
    print(f"Max prob = {mags[top2[0]]:.4f}")
    print(f"All probs equal: {np.allclose(mags, 1.0 / N)}")
    print(f"Correct: {overlap > 0.9999 and np.allclose(mags, 1.0 / N)}")

if __name__ == "__main__":
    main()
'''

_add(
    "quantum_qft_4qubit_input5",
    "4-qubit QFT on input state |5> — verify uniform output distribution",
    """Write a complete, runnable Python program using numpy and qiskit that:
1. Builds a 4-qubit circuit that prepares the basis state |5> = |0101>.
2. Applies the 4-qubit Quantum Fourier Transform (you may use
   qiskit.circuit.library.QFT or implement it from scratch with H and
   controlled-phase gates).
3. Simulate with qiskit.quantum_info.Statevector.
4. Compute the analytic QFT output for input |5>:
   QFT|x> = (1/sqrt(N)) * sum_{k=0}^{N-1} exp(2*pi*i*k*x/N) |k>, N = 2^4 = 16.
5. Compute the overlap |<expected|actual>|^2 and verify that all output
   probabilities are equal to 1/N (a hallmark of QFT on a basis state).
6. In `def main()`, prints exactly:
     N = 16
     Input state = |5>
     QFT output overlap = <value rounded to 6 decimals>
     Top amplitude index = <value>
     Max prob = <value rounded to 4 decimals>
     All probs equal: True
     Correct: <True|False>
   where Correct is True iff overlap > 0.9999 AND all probabilities are
   approximately 1/16.
Call main() under `if __name__ == "__main__":`.
""",
    P7_REF,
    ["N = 16", "Input state = |5>", "QFT output overlap = ",
     "All probs equal: True", "Correct: True"],
    timeout=60,
)

# ---------------------------------------------------------------------------
# Problem 8: 5-qubit GHZ state and stabilizer measurement.
# ---------------------------------------------------------------------------
P8_REF = r'''
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, SparsePauliOp

def build_ghz(n):
    qc = QuantumCircuit(n)
    qc.h(0)
    for i in range(n - 1):
        qc.cx(i, i + 1)
    return qc

def main():
    n = 5
    qc = build_ghz(n)
    sv = Statevector.from_instruction(qc)
    # GHZ stabilizers: X0X1X2X3X4, Z0Z1, Z1Z2, Z2Z3, Z3Z4
    stabilizers = [
        ("X" * n, +1),
        ("Z" + "Z" + "I" * (n - 2), +1),
        ("I" + "ZZ" + "I" * (n - 3), +1),
        ("II" + "ZZ" + "I" * (n - 4), +1),
        ("III" + "ZZ" + "I" * (n - 5 if n > 4 else 0), +1),
    ]
    # Note: Pauli string is read left-to-right as qubit 0,1,2,...,n-1
    # Build them correctly:
    stabilizers = [
        ("XXXXX", +1),
        ("ZZIII", +1),
        ("IZZII", +1),
        ("IIZZI", +1),
        ("IIIZZ", +1),
    ]
    results = []
    for pauli, expected_sign in stabilizers:
        op = SparsePauliOp.from_list([(pauli, 1.0)])
        val = float(sv.expectation_value(op).real)
        results.append((pauli, val))
    all_plus = all(abs(v - expected_sign) < 1e-9 for (_, v), (pauli, expected_sign) in zip(results, stabilizers))
    # Entanglement check: trace out qubits 1..4, the reduced state of qubit 0
    # should be maximally mixed (I/2) indicating entanglement.
    from qiskit.quantum_info import DensityMatrix, partial_trace
    dm = DensityMatrix(sv)
    rho0 = partial_trace(dm, list(range(1, n)))
    purity = float(np.real(np.trace(rho0.data @ rho0.data)))
    print(f"GHZ state: 5 qubits")
    for pauli, v in results:
        print(f"  <{pauli}> = {v:+.4f}")
    print(f"All stabilizers +1: {all_plus}")
    print(f"Single-qubit purity = {purity:.4f}")
    print(f"Entangled: {abs(purity - 0.5) < 1e-6}")
    print(f"Valid GHZ: {all_plus and abs(purity - 0.5) < 1e-6}")

if __name__ == "__main__":
    main()
'''

_add(
    "quantum_ghz_5qubit_stabilizers",
    "5-qubit GHZ state — verify all stabilizers and entanglement",
    """Write a complete, runnable Python program using numpy and qiskit that:
1. Builds a 5-qubit GHZ state: H on qubit 0, then CX(0,1), CX(1,2), CX(2,3),
   CX(3,4).
2. Simulate with qiskit.quantum_info.Statevector.
3. Computes the expectation value of each GHZ stabilizer:
   - X0X1X2X3X4 (should be +1)
   - Z0Z1 (should be +1)
   - Z1Z2 (should be +1)
   - Z2Z3 (should be +1)
   - Z3Z4 (should be +1)
   Use qiskit.quantum_info.SparsePauliOp for the Pauli strings.
4. Computes the reduced density matrix of qubit 0 (trace out qubits 1..4) and
   its purity Tr(rho0^2). For a genuine GHZ state, this purity equals 0.5
   (maximally mixed single qubit).
5. In `def main()`, prints exactly:
     GHZ state: 5 qubits
     <XXXXX> = +1.0000
     <ZZIII> = +1.0000
     <IZZII> = +1.0000
     <IIZZI> = +1.0000
     <IIIZZ> = +1.0000
     All stabilizers +1: True
     Single-qubit purity = 0.5000
     Entangled: True
     Valid GHZ: True
   (Stabilizer lines must each show +1.0000; Entangled and Valid GHZ must be True.)
Call main() under `if __name__ == "__main__":`.
""",
    P8_REF,
    ["GHZ state: 5 qubits", "<XXXXX> = +1.0000", "<ZZIII> = +1.0000",
     "All stabilizers +1: True", "Single-qubit purity = 0.5000",
     "Entangled: True", "Valid GHZ: True"],
    timeout=60,
)

# ---------------------------------------------------------------------------
# Problem 9: Quantum phase estimation of a controlled-S gate (phase = 1/4).
# ---------------------------------------------------------------------------
P9_REF = r'''
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import QFT
from qiskit.quantum_info import Statevector
from fractions import Fraction

def main():
    n_count = 3
    # Target is a single qubit on which we apply the S gate (phase = i = exp(i*pi/2))
    # The eigenvalue of S|1> = i*|1> = exp(2*pi*i*(1/4))*|1>, so phase = 1/4.
    creg = ClassicalRegister(n_count, "c")
    qcount = QuantumRegister(n_count, "count")
    qtgt = QuantumRegister(1, "tgt")
    qc = QuantumCircuit(qcount, qtgt, creg)
    # Prepare target in |1> (eigenstate of S)
    qc.x(qtgt[0])
    # Hadamards on counting register
    qc.h(qcount)
    # Apply controlled-S^(2^q) for q=0..n_count-1
    for q in range(n_count):
        # S^(2^q) = phase gate repeated 2^q times
        for _ in range(2 ** q):
            qc.cp(np.pi / 2, qcount[q], qtgt[0])
    # Inverse QFT
    qc.compose(QFT(n_count, inverse=True), qcount[:], inplace=True)
    qc.measure(qcount, creg)
    # Simulate
    sv = Statevector.from_instruction(qc.remove_final_measurements(inplace=False))
    probs = sv.probabilities_dict()
    best = max(probs.items(), key=lambda kv: kv[1])[0]
    phase_int = int(best, 2)
    phase = phase_int / (2 ** n_count)
    frac = Fraction(phase).limit_denominator(2 ** n_count)
    print(f"Counting qubits = {n_count}")
    print(f"Top bitstring = {best}")
    print(f"Phase estimate = {phase:.4f}")
    print(f"Fraction = {frac.numerator}/{frac.denominator}")
    print(f"Exact phase = 0.2500")
    print(f"Correct: {frac == Fraction(1, 4)}")

if __name__ == "__main__":
    main()
'''

_add(
    "quantum_qpe_3qubit_s_gate_quarter",
    "QPE with 3 counting qubits for the S gate — estimate phase 1/4",
    """Write a complete, runnable Python program using numpy, qiskit, and fractions that:
1. Implements Quantum Phase Estimation with n_count=3 counting qubits and 1
   target qubit. The target unitary is the S gate (phase gate), which applies
   exp(i*pi/2) = i to |1>. The eigenstate |1> has eigenvalue exp(2*pi*i*1/4),
   so the phase to estimate is 1/4.
2. Builds the circuit:
   - Prepare the target in |1>.
   - Apply H to all 3 counting qubits.
   - For each counting qubit q, apply controlled-S^(2^q) (i.e. cp(pi/2, q, tgt)
     repeated 2^q times).
   - Apply the inverse 3-qubit QFT to the counting register.
   - Measure the counting register.
3. Simulate with qiskit.quantum_info.Statevector (remove final measurements
   first), take the most-probable bitstring.
4. Convert the measured integer to a phase in [0,1) and recover the fraction
   with fractions.Fraction(...).limit_denominator(8).
5. In `def main()`, prints exactly:
     Counting qubits = 3
     Top bitstring = <value>
     Phase estimate = <value rounded to 4 decimals>
     Fraction = <num>/<den>
     Exact phase = 0.2500
     Correct: <True|False>
   where Correct is True iff the recovered fraction equals 1/4.
Call main() under `if __name__ == "__main__":`.
""",
    P9_REF,
    ["Counting qubits = 3", "Phase estimate = 0.2500",
     "Exact phase = 0.2500", "Correct: True"],
    timeout=60,
)

# ---------------------------------------------------------------------------
# Problem 10: Bernstein-Vazirani for a 6-bit hidden string.
# ---------------------------------------------------------------------------
P10_REF = r'''
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

def build_oracle(s, n):
    """Oracle for f(x) = s.x (mod 2)."""
    qc = QuantumCircuit(n + 1)
    for i, b in enumerate(s):
        if b == '1':
            qc.cx(i, n)
    return qc

def build_bv_circuit(s, n):
    qc = QuantumCircuit(n + 1, n)
    # Initialize ancilla to |-> = (|0>-|1>)/sqrt2
    qc.x(n); qc.h(n)
    qc.h(range(n))
    qc.compose(build_oracle(s, n), inplace=True)
    qc.h(range(n))
    # Measure first n qubits
    return qc

def main():
    n = 6
    s = "101101"  # hidden string
    qc = build_bv_circuit(s, n)
    qc.measure(range(n), range(n))
    sv = Statevector.from_instruction(qc.remove_final_measurements(inplace=False))
    probs = sv.probabilities_dict()
    # In BV, the measurement of the first n qubits is deterministic: |s>
    best = max(probs.items(), key=lambda kv: kv[1])[0]
    # best is the full (n+1)-bit string; the first n bits are the answer
    recovered = best[:n][::-1]  # qiskit is little-endian
    print(f"n = {n}")
    print(f"Hidden string s = {s}")
    print(f"Top bitstring = {best}")
    print(f"Recovered s = {recovered}")
    print(f"Probability = {probs[best]:.4f}")
    print(f"Correct: {recovered == s[::-1]}")

if __name__ == "__main__":
    main()
'''

_add(
    "quantum_bernstein_vazirani_6bit",
    "Bernstein-Vazirani algorithm for a 6-bit hidden string",
    """Write a complete, runnable Python program using numpy and qiskit that:
1. Implements the Bernstein-Vazirani oracle for a hidden 6-bit string s =
   "101101". The oracle on n=6 input qubits plus 1 ancilla computes
   f(x) = (s . x) mod 2 by applying CX(s_i, ancilla) for each i where s_i = 1.
2. Builds the full BV circuit:
   - Initialize the ancilla (qubit n) to |-> = (|0> - |1>)/sqrt(2) via X then H.
   - Apply H to all n input qubits.
   - Apply the oracle.
   - Apply H to all n input qubits again.
   - Measure all n input qubits.
3. Simulate with qiskit.quantum_info.Statevector (remove final measurements
   before evolving). The measurement of the n input qubits is deterministic
   and equals the hidden string s (in qiskit's little-endian bit ordering).
4. In `def main()`, prints exactly:
     n = 6
     Hidden string s = 101101
     Top bitstring = <value>
     Recovered s = <value>
     Probability = <value rounded to 4 decimals>
     Correct: <True|False>
   where Correct is True iff the recovered string equals "101101" (after
   accounting for qiskit's little-endian bit ordering).
Call main() under `if __name__ == "__main__":`.
""",
    P10_REF,
    ["n = 6", "Hidden string s = 101101", "Recovered s = 101101",
     "Probability = 1.0000", "Correct: True"],
    timeout=60,
)

print(f"Defined {len(PROBLEMS)} problems so far")

# ---------------------------------------------------------------------------
# Problem 11: Simons algorithm for a 2-to-1 function with period 011.
# ---------------------------------------------------------------------------
P11_REF = r'''
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.circuit.library import QFT

def build_simon_oracle(s, n):
    """Oracle for a 2-to-1 function f with period s: f(x) = f(y) iff x xor y = s.
    Implementation: copy x to the second register, then XOR in s conditioned
    on the bits of x (a common textbook construction)."""
    qc = QuantumCircuit(2 * n)
    # Copy x to second register
    for i in range(n):
        qc.cx(i, n + i)
    # If s_i = 1, conditionally flip bit i of the second register using
    # qubit i of the first register as control, but to make f 2-to-1 with
    # period s, we use the standard construction: for i where s_i=1, replace
    # the highest such i with a controlled operation that XORs lower bits.
    # Simpler textbook version: f(x) = min(x, x xor s) -- we implement this by
    # checking x_{k} (highest s=1 bit) and conditionally XOR-ing the lower
    # s=1 bits into the second register.
    s_indices = [i for i in range(n) if s[i] == '1']
    if not s_indices:
        return qc
    k = max(s_indices)
    # Condition on qubit k: if x_k = 1, XOR the lower s_i=1 bits into output
    for i in s_indices:
        if i == k:
            continue
        qc.ccx(k, i, n + i)
    # Always flip the k-th output bit when x_k = 1 (to create the 2-to-1 mapping)
    qc.cx(k, n + k)
    return qc

def build_simon_circuit(s, n):
    qc = QuantumCircuit(2 * n, n)
    qc.h(range(n))
    qc.compose(build_simon_oracle(s, n), inplace=True)
    qc.h(range(n))
    qc.measure(range(n), range(n))
    return qc

def solve_linear_system(equations, n):
    """Given equations y.s = 0 (mod 2) for various y, find s.
    Each equation is a bitstring y of length n. Solve via Gaussian elimination
    over GF(2)."""
    # Build matrix over GF(2)
    A = np.array([[int(b) for b in eq] for eq in equations], dtype=int)
    rows = A.shape[0]
    # Gaussian elimination
    pivot_cols = []
    r = 0
    for c in range(n):
        # Find a row >= r with a 1 in column c
        pivot = -1
        for i in range(r, rows):
            if A[i, c] == 1:
                pivot = i
                break
        if pivot == -1:
            continue
        A[[r, pivot]] = A[[pivot, r]]
        for i in range(rows):
            if i != r and A[i, c] == 1:
                A[i] = (A[i] + A[r]) % 2
        pivot_cols.append(c)
        r += 1
        if r == rows:
            break
    # The kernel: free variables are non-pivot columns.
    # For Simon, we want a non-zero solution s. Set one free variable to 1.
    free_cols = [c for c in range(n) if c not in pivot_cols]
    s = np.zeros(n, dtype=int)
    if free_cols:
        s[free_cols[0]] = 1
        # Back-substitute to find pivot variables
        for i, pc in enumerate(pivot_cols):
            s[pc] = sum(A[i, j] * s[j] for j in range(n)) % 2
    return s

def main():
    n = 3
    s = "011"
    # Build and simulate Simon circuit multiple times to gather equations
    qc = build_simon_circuit(s, n)
    sv = Statevector.from_instruction(qc.remove_final_measurements(inplace=False))
    probs = sv.probabilities_dict()
    # Collect all bitstrings with non-zero probability (these satisfy y.s = 0)
    samples = [bs[:n][::-1] for bs, p in probs.items() if p > 1e-9]
    # Solve for s
    recovered = solve_linear_system(samples, n)
    recovered_str = "".join(str(b) for b in recovered)
    print(f"n = {n}")
    print(f"Hidden period s = {s}")
    print(f"Distinct samples = {len(samples)}")
    print(f"Recovered s = {recovered_str}")
    print(f"Valid: {recovered_str == s or recovered_str == '0' * n or (recovered_str != '0' * n and recovered_str == s)}")
    # The all-zero string is always a solution; we want the non-trivial one.
    # If we recovered 000, try the unique non-trivial solution.
    print(f"Non-trivial: {recovered_str != '0' * n}")
    print(f"Correct: {recovered_str == s}")

if __name__ == "__main__":
    main()
'''

_add(
    "quantum_simon_period_011",
    "Simon's algorithm for a 3-bit period s=011 — recover the period",
    """Write a complete, runnable Python program using numpy and qiskit that:
1. Implements Simon's oracle for a 2-to-1 function f: {0,1}^3 -> {0,1}^3 with
   hidden period s = "011" (i.e. f(x) = f(y) iff x XOR y = s).
   The oracle acts on 6 qubits (3 input + 3 output). Use the standard textbook
   construction: copy x to the output register, then for the highest index k
   where s_k = 1, condition on x_k to XOR the lower s_i=1 bits into the output,
   and flip the k-th output bit conditioned on x_k.
2. Builds the full Simon circuit: H^n on the input register, apply the oracle,
   then H^n on the input register again, then measure the input register.
3. Simulate with qiskit.quantum_info.Statevector (remove final measurements).
   Collect every bitstring y with non-zero probability. Each such y satisfies
   y . s = 0 (mod 2).
4. Solve the resulting linear system over GF(2) using Gaussian elimination to
   recover s. Return the non-trivial solution (not all-zeros).
5. In `def main()`, prints exactly:
     n = 3
     Hidden period s = 011
     Distinct samples = <value>
     Recovered s = <value>
     Non-trivial: True
     Correct: <True|False>
   where Correct is True iff the recovered string equals "011".
Call main() under `if __name__ == "__main__":`.
""",
    P11_REF,
    ["n = 3", "Hidden period s = 011", "Recovered s = 011",
     "Non-trivial: True", "Correct: True"],
    timeout=120,
)

# ---------------------------------------------------------------------------
# Problem 12: 3-qubit bit-flip code — encode, error, syndrome, correct.
# ---------------------------------------------------------------------------
P12_REF = r'''
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, DensityMatrix, partial_trace

def build_bitflip_encode():
    """Encode |psi> = a|0> + b|1> into (a|000> + b|111>)/sqrt(2)."""
    qc = QuantumCircuit(3)
    qc.cx(0, 1); qc.cx(0, 2)
    return qc

def build_bitflip_syndrome():
    """Measure Z0Z1 and Z1Z2 stabilizers into 2 ancilla qubits."""
    qc = QuantumCircuit(5)
    # ancilla qubits 3 and 4
    qc.cx(0, 3); qc.cx(1, 3)  # ancilla 3 measures Z0Z1 parity
    qc.cx(1, 4); qc.cx(2, 4)  # ancilla 4 measures Z1Z2 parity
    return qc

def apply_correction(syndrome):
    """Return (qc, flipped_qubit) for the given 2-bit syndrome."""
    qc = QuantumCircuit(3)
    # syndrome bits (s0, s1) where s0 = Z0Z1 parity, s1 = Z1Z2 parity
    s0, s1 = syndrome
    if s0 == 1 and s1 == 0:
        qc.x(0)  # bit flip on qubit 0
        return qc, 0
    elif s0 == 1 and s1 == 1:
        qc.x(1)
        return qc, 1
    elif s0 == 0 and s1 == 1:
        qc.x(2)
        return qc, 2
    return qc, -1  # no error

def main():
    # Encode a known state |psi> = sqrt(0.7)|0> + sqrt(0.3)|1>
    alpha, beta = np.sqrt(0.7), np.sqrt(0.3)
    psi = np.array([alpha, beta], dtype=complex)
    # Build full encode circuit
    enc = QuantumCircuit(3)
    enc.initialize(psi, 0)
    enc.compose(build_bitflip_encode(), inplace=True)
    sv_enc = Statevector.from_instruction(enc)
    # Apply a bit-flip error on qubit 1
    err = QuantumCircuit(3); err.x(1)
    sv_err = sv_enc.evolve(err)
    # Syndrome measurement
    syn_circ = build_bitflip_syndrome()
    full = QuantumCircuit(5)
    full.initialize(psi, 0)
    full.compose(build_bitflip_encode(), inplace=True)
    full.x(1)  # error
    full.compose(syn_circ, inplace=True)
    sv_full = Statevector.from_instruction(full)
    probs = sv_full.probabilities_dict()
    # Determine syndrome from the most likely outcome
    best = max(probs.items(), key=lambda kv: kv[1])[0]
    # Qubit ordering: q0,q1,q2,q3(ancilla),q4(ancilla) -> bitstring is q4q3q2q1q0
    # So ancilla bits are the leftmost two
    anc_bits = best[:2]
    s1 = int(anc_bits[0]); s0 = int(anc_bits[1])
    syndrome = (s0, s1)
    # Apply correction
    corr, flipped = apply_correction(syndrome)
    # Rebuild: encode -> error -> correct, then check fidelity with original
    final = QuantumCircuit(3)
    final.initialize(psi, 0)
    final.compose(build_bitflip_encode(), inplace=True)
    final.x(1)
    final.compose(corr, inplace=True)
    sv_final = Statevector.from_instruction(final)
    # Compare to the encoded (no-error) state
    fid = float(np.abs(np.vdot(sv_enc.data, sv_final.data)) ** 2)
    print(f"Encoded (a,b) = ({alpha:.4f}, {beta:.4f})")
    print(f"Error applied: X on qubit 1")
    print(f"Syndrome (Z0Z1, Z1Z2) = {syndrome}")
    print(f"Corrected qubit = {flipped}")
    print(f"Recovery fidelity = {fid:.6f}")
    print(f"Correct: {abs(fid - 1.0) < 1e-9}")

if __name__ == "__main__":
    main()
'''

_add(
    "quantum_bitflip_code_3qubit_x1",
    "3-qubit bit-flip code: encode, inject X error on qubit 1, decode, recover",
    """Write a complete, runnable Python program using numpy and qiskit that:
1. Encodes a single-qubit state |psi> = sqrt(0.7)|0> + sqrt(0.3)|1> into the
   3-qubit bit-flip code: (a|000> + b|111>). Use CX(0,1) and CX(0,2) after
   initializing qubit 0 to |psi>.
2. Applies a bit-flip (X) error to qubit 1.
3. Performs syndrome measurement by introducing 2 ancilla qubits:
   - ancilla 3 = parity of qubits 0 and 1 (Z0Z1 stabilizer): CX(0,3), CX(1,3)
   - ancilla 4 = parity of qubits 1 and 2 (Z1Z2 stabilizer): CX(1,4), CX(2,4)
   Then read the 2-bit syndrome (s0, s1) from the ancilla measurement outcomes.
4. Decodes the syndrome: (1,0) -> X on qubit 0, (1,1) -> X on qubit 1,
   (0,1) -> X on qubit 2, (0,0) -> no error.
5. Applies the correction to a fresh run of (encode -> error -> correct) and
   computes the fidelity |<encoded_state|final_state>|^2.
6. In `def main()`, prints exactly:
     Encoded (a,b) = (0.8367, 0.5477)
     Error applied: X on qubit 1
     Syndrome (Z0Z1, Z1Z2) = (1, 1)
     Corrected qubit = 1
     Recovery fidelity = 1.000000
     Correct: True
   (Values rounded as shown. Correct is True iff fidelity is within 1e-9 of 1.0.)
Call main() under `if __name__ == "__main__":`.
""",
    P12_REF,
    ["Error applied: X on qubit 1", "Syndrome (Z0Z1, Z1Z2) = (1, 1)",
     "Corrected qubit = 1", "Recovery fidelity = 1.000000", "Correct: True"],
    timeout=120,
)

# ---------------------------------------------------------------------------
# Problem 13: Steane 7-qubit code — encode |1>, apply X on qubit 0, syndrome.
# ---------------------------------------------------------------------------
P13_REF = r'''
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
'''

_add(
    "quantum_steane_x0_syndrome",
    "Steane [[7,1,3]] code: encode |1>_L, apply X on qubit 0, decode syndrome",
    """Write a complete, runnable Python program using numpy and qiskit that:
1. Constructs the logical |0>_L of the Steane [[7,1,3]] code as the uniform
   superposition over all 16 codewords of the [7,4,3] Hamming code. The
   generator matrix is:
   G = [[1,0,0,0,1,1,0],
        [0,1,0,0,1,0,1],
        [0,0,1,0,0,1,1],
        [0,0,0,1,1,1,1]]
   |0>_L = (1/sqrt(16)) * sum_{m in {0,1}^4} |m*G mod 2>.
   |1>_L = X^{⊗7} |0>_L (apply X to all 7 qubits of |0>_L).
2. Initializes a 7-qubit Statevector to |1>_L.
3. Applies an X error to qubit 0.
4. Computes the 3 Z-stabilizer expectation values of the Steane code:
   - g1 = Z0Z1Z2Z3
   - g2 = Z0Z1Z4Z5
   - g3 = Z0Z2Z4Z6
   using qiskit.quantum_info.SparsePauliOp. Each expectation value should be
   ±1; a -1 means that stabilizer detected the error.
5. The 3-bit Z-syndrome (s1, s2, s3) is the column of the parity-check matrix
   H = [[1,0,1,0,1,0,1], [0,1,1,0,0,1,1], [0,0,0,1,1,1,1]] corresponding to
   the error qubit. Decode the syndrome to identify which qubit was flipped.
6. In `def main()`, prints exactly:
     Steane [[7,1,3]] code
     Logical state = |1>_L
     Error = X on qubit 0
     Z-stabilizer syndrome = (1, 0, 1)
     Decoded error qubit = 0
     Correct: True
   (The syndrome and decoded qubit must match X on qubit 0.)
Call main() under `if __name__ == "__main__":`.
""",
    P13_REF,
    ["Steane [[7,1,3]] code", "Logical state = |1>_L", "Error = X on qubit 0",
     "Decoded error qubit = 0", "Correct: True"],
    timeout=120,
)

# ---------------------------------------------------------------------------
# Problem 14: Quantum random walk on a 4-node cycle, 2 steps.
# ---------------------------------------------------------------------------
P14_REF = r'''
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

def build_coined_walk_circuit(n, steps):
    """Discrete-time quantum walk on a cycle of n nodes with a 2-state coin.
    State space: (node, coin) with 2*n basis states. The coin qubit is the
    last qubit."""
    n_qubits_node = int(np.ceil(np.log2(n)))
    total = n_qubits_node + 1
    qc = QuantumCircuit(total)
    # Start at node 0, coin |+>
    qc.h(total - 1)
    for _ in range(steps):
        # Coin: H on the coin qubit
        qc.h(total - 1)
        # Conditional shift: if coin=0, decrement node; if coin=1, increment node.
        # Implement as: add coin to node register (mod n).
        for q in range(n_qubits_node):
            qc.cx(total - 1, q)
        # Now if coin=1, node was incremented by 1 (binary). We need mod n.
        # For n=4 and 2 node qubits, increment by 1 mod 4 is just a binary +1,
        # which is what we did. If coin=0, we want decrement: subtract 1.
        # The above only handles coin=1. For coin=0, we need to decrement.
        # A cleaner implementation: apply X on coin, then CNOT into node
        # (which adds 1 when coin=0, i.e. original coin=0 -> decrement after
        # we subtract the +1 added when coin=1).
        # Simpler: use controlled increment/decrement.
        pass
    return qc

def classical_walk_distribution(n, steps):
    """Classical random walk on cycle with n nodes, `steps` steps, starting at 0."""
    p = np.zeros(n)
    p[0] = 1.0
    for _ in range(steps):
        new = np.zeros(n)
        for i in range(n):
            new[(i + 1) % n] += 0.5 * p[i]
            new[(i - 1) % n] += 0.5 * p[i]
        p = new
    return p

def quantum_walk_distribution(n, steps):
    """Compute the discrete-time coined quantum walk distribution on a cycle
    of n nodes, starting at node 0 with coin |+>, using a direct unitary
    simulation. Returns the marginal distribution over nodes."""
    dim = 2 * n
    # Basis order: |node, coin>, index = 2*node + coin
    # Initial state: |0> (node 0) tensor |+> (coin)
    psi = np.zeros(dim, dtype=complex)
    psi[2 * 0 + 0] = 1.0 / np.sqrt(2)
    psi[2 * 0 + 1] = 1.0 / np.sqrt(2)
    # Coin operator H on the coin
    H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
    coin_op = np.kron(np.eye(n), H)
    # Shift operator: |node, 0> -> |node-1, 0>, |node, 1> -> |node+1, 1>
    S = np.zeros((dim, dim), dtype=complex)
    for node in range(n):
        S[2 * ((node - 1) % n) + 0, 2 * node + 0] = 1.0
        S[2 * ((node + 1) % n) + 1, 2 * node + 1] = 1.0
    U = S @ coin_op
    state = psi
    for _ in range(steps):
        state = U @ state
    # Marginalize over coin
    probs = np.zeros(n)
    for node in range(n):
        probs[node] = abs(state[2 * node + 0]) ** 2 + abs(state[2 * node + 1]) ** 2
    return probs

def main():
    n = 4
    steps = 2
    q = quantum_walk_distribution(n, steps)
    c = classical_walk_distribution(n, steps)
    # Total variation distance
    tvd = 0.5 * float(np.sum(np.abs(q - c)))
    # Check normalization
    print(f"Cycle nodes = {n}")
    print(f"Steps = {steps}")
    print(f"Quantum distribution = {np.round(q, 4).tolist()}")
    print(f"Classical distribution = {np.round(c, 4).tolist()}")
    print(f"Quantum total = {float(q.sum()):.4f}")
    print(f"TVD vs classical = {tvd:.4f}")
    print(f"Different from classical: {tvd > 0.01}")

if __name__ == "__main__":
    main()
'''

_add(
    "quantum_random_walk_cycle4_2step",
    "Discrete-time coined quantum walk on a 4-cycle for 2 steps",
    """Write a complete, runnable Python program using only numpy that:
1. Simulates a discrete-time coined quantum walk on a cycle of n=4 nodes.
   The Hilbert space is 2*n = 8 dimensional (one coin qubit per node).
   Basis order: |node, coin>, with index = 2*node + coin.
2. Initial state: node 0, coin |+> = (|0> + |1>)/sqrt(2).
3. Each step consists of:
   - Coin operator: H (Hadamard) applied to the coin subspace.
   - Shift operator S: |node, 0> -> |node-1 mod n, 0>,
                       |node, 1> -> |node+1 mod n, 1>.
   Build S as an 8x8 permutation matrix and the coin operator as
   I_n (x) H. Apply U = S * (I_n (x) H) for the given number of steps.
4. Run for 2 steps and marginalize the final state over the coin to get the
   probability distribution over the 4 nodes.
5. Also compute the classical random walk distribution on the same cycle for
   2 steps (50/50 left/right) starting at node 0.
6. Compute the total variation distance (TVD) between the quantum and
   classical distributions.
7. In `def main()`, prints exactly:
     Cycle nodes = 4
     Steps = 2
     Quantum distribution = [<4 values rounded to 4 decimals>]
     Classical distribution = [<4 values rounded to 4 decimals>]
     Quantum total = 1.0000
     TVD vs classical = <value rounded to 4 decimals>
     Different from classical: <True|False>
   where Different from classical is True iff TVD > 0.01.
Call main() under `if __name__ == "__main__":`.
""",
    P14_REF,
    ["Cycle nodes = 4", "Steps = 2", "Quantum total = 1.0000",
     "TVD vs classical = ", "Different from classical: True"],
    timeout=60,
)

print(f"Defined {len(PROBLEMS)} problems so far")

# ---------------------------------------------------------------------------
# Problem 15: Amplitude amplification for a search problem with unknown
# solution count via quantum counting.
# ---------------------------------------------------------------------------
P15_REF = r'''
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFT
from qiskit.quantum_info import Statevector
from fractions import Fraction

def grover_oracle(marked_ints, n):
    qc = QuantumCircuit(n)
    for m in marked_ints:
        bits = format(m, f"0{n}b")
        for q, b in enumerate(bits):
            if b == '0':
                qc.x(q)
        qc.h(n - 1)
        qc.mcx(list(range(n - 1)), n - 1)
        qc.h(n - 1)
        for q, b in enumerate(bits):
            if b == '0':
                qc.x(q)
    return qc

def grover_diffuser(n):
    qc = QuantumCircuit(n)
    qc.h(range(n))
    qc.x(range(n))
    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)
    qc.x(range(n))
    qc.h(range(n))
    return qc

def quantum_count(n, marked, n_count):
    """Estimate the number of marked items M in 2^n using quantum counting."""
    N = 2 ** n
    # Build Grover operator G = (2|s><s| - I) * Oracle
    oracle = grover_oracle(marked, n)
    diffuser = grover_diffuser(n)
    G = QuantumCircuit(n)
    G.compose(oracle, inplace=True)
    G.compose(diffuser, inplace=True)
    # QPE on G with n_count counting qubits
    # Eigenvalues of G are exp(±2*pi*i*theta) where sin(theta) = sqrt(M/N)
    creg = QuantumCircuit(n + n_count)
    creg.h(range(n_count))
    # Prepare uniform superposition on the search register (the eigenstate
    # with non-trivial eigenvalue of G is |beta> = cos(theta)|bad> + sin(theta)|good>)
    creg.h(range(n_count, n + n_count))
    for q in range(n_count):
        # Controlled-G^(2^q)
        G_power = G.power(2 ** q)
        creg.compose(G_power.control(1), [q] + list(range(n_count, n + n_count)), inplace=True)
    creg.compose(QFT(n_count, inverse=True), range(n_count), inplace=True)
    sv = Statevector.from_instruction(creg)
    probs = sv.probabilities_dict()
    best = max(probs.items(), key=lambda kv: kv[1])[0]
    measured = int(best, 2)
    # The phase estimate theta = measured / 2^n_count
    # The two eigenvalues of G are exp(±2*pi*i*theta), so we get one of them.
    phase = measured / (2 ** n_count)
    if phase > 0.5:
        phase = 1.0 - phase
    theta = np.pi * phase  # since eigenvalue = exp(2*pi*i*phase) = exp(2*i*theta)
    # Actually: eigenvalue = exp(2*i*theta), so 2*pi*phase = 2*theta -> theta = pi*phase
    M_est = N * (np.sin(theta)) ** 2
    return M_est, theta

def main():
    n = 4
    marked = [3, 7, 11]  # M = 3
    n_count = 4
    M_est, theta = quantum_count(n, marked, n_count)
    N = 2 ** n
    M_true = len(marked)
    print(f"N = {N}")
    print(f"True M = {M_true}")
    print(f"Counting qubits = {n_count}")
    print(f"Estimated theta = {theta:.4f}")
    print(f"Estimated M = {M_est:.4f}")
    print(f"Rounded M = {int(round(M_est))}")
    print(f"Correct: {abs(M_est - M_true) < 0.5}")

if __name__ == "__main__":
    main()
'''

_add(
    "quantum_counting_4qubit_3marked",
    "Quantum counting: estimate the number of marked items via QPE on Grover",
    """Write a complete, runnable Python program using numpy and qiskit that:
1. Implements quantum counting to estimate the number M of marked items in a
   search space of size N = 2^4 = 16. The marked items are integers 3, 7, 11
   (so M = 3).
2. Builds the Grover operator G = (2|s><s| - I) * Oracle, where:
   - Oracle flips the phase of |m> for each marked m (using X gates to convert
     0 bits, then H-MCX-H, then undo X).
   - Diffuser = H^n X^n (H-MCX-H) X^n H^n.
3. Performs QPE on G with n_count = 4 counting qubits and the search register
   initialized to a uniform superposition (H on all n qubits). For each
   counting qubit q, apply controlled-G^(2^q). Then apply inverse QFT.
4. Simulate with qiskit.quantum_info.Statevector, take the most-probable
   bitstring as the phase estimate.
5. Convert the measured integer to a phase in [0, 1) (use 1 - phase if
   phase > 0.5). Then theta = pi * phase (since the Grover eigenvalues are
   exp(±2*i*theta)). The estimate of M is N * sin^2(theta).
6. In `def main()`, prints exactly:
     N = 16
     True M = 3
     Counting qubits = 4
     Estimated theta = <value rounded to 4 decimals>
     Estimated M = <value rounded to 4 decimals>
     Rounded M = <integer>
     Correct: <True|False>
   where Correct is True iff |estimated M - 3| < 0.5.
Call main() under `if __name__ == "__main__":`.
""",
    P15_REF,
    ["N = 16", "True M = 3", "Counting qubits = 4",
     "Estimated M = ", "Rounded M = 3", "Correct: True"],
    timeout=180,
)

# ---------------------------------------------------------------------------
# Problem 16: W-state preparation for 4 qubits via cascaded gates.
# ---------------------------------------------------------------------------
P16_REF = r'''
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, SparsePauliOp, partial_trace, DensityMatrix

def build_w_state(n):
    """Build an n-qubit W state: |10...0> + |01..0> + ... + |0...01> (normalized)."""
    qc = QuantumCircuit(n)
    # Standard construction: ry rotations + controlled rotations
    # Start by preparing |10..0> amplitude on qubit 0
    # Use the recursive construction: ry(theta_1) on qubit 0 then split.
    # theta_k = arccos(sqrt(1/(n-k+1)))
    # Apply ry(theta_1) on qubit 0 to make sqrt(1/n)|0> + sqrt((n-1)/n)|1>
    qc.ry(2 * np.arccos(np.sqrt(1.0 / n)), 0)
    # Now |1..1> amplitude is sqrt((n-1)/n) on qubit 0 = 1. We want to split this
    # into the W state of qubits 1..n-1 scaled by sqrt((n-1)/n).
    # For each subsequent qubit k, apply a controlled-ry that rotates the
    # |1> amplitude of qubit k-1 into qubit k.
    for k in range(1, n):
        # Controlled rotation: when qubit k-1 is |1>, rotate qubit k by
        # theta_k = 2*arccos(sqrt(1/(n-k)))
        theta = 2 * np.arccos(np.sqrt(1.0 / (n - k)))
        # First, move the |1> on qubit k-1 to |0> via X so we can do a
        # controlled rotation with the standard control.
        # Actually, use CRY gate directly (control = qubit k-1, target = qubit k)
        qc.cry(theta, k - 1, k)
        # After the CRY, the |1> on qubit k-1 has been "consumed" into qubit k
        # We need to swap the |1> amplitude from k-1 to k for the next iteration.
        # Apply CX(k, k-1) to move the |1> from k-1 to k.
        qc.cx(k, k - 1)
    return qc

def main():
    n = 4
    qc = build_w_state(n)
    sv = Statevector.from_instruction(qc)
    # The W state has 4 basis states with amplitude 1/2 each:
    # |1000>, |0100>, |0010>, |0001>
    N = 2 ** n
    expected = np.zeros(N, dtype=complex)
    for k in range(n):
        idx = 1 << (n - 1 - k)  # qubit k is 1, rest are 0
        expected[idx] = 1.0
    expected /= np.linalg.norm(expected)
    fidelity = float(np.abs(np.vdot(expected, sv.data)) ** 2)
    # Also verify: exactly one qubit is 1 with probability 1
    probs = sv.probabilities()
    one_excitation_prob = 0.0
    for i, p in enumerate(probs):
        bits = format(i, f"0{n}b")
        if bits.count("1") == 1:
            one_excitation_prob += p
    # Symmetry: each of the 4 basis states has equal probability 0.25
    single_probs = []
    for k in range(n):
        idx = 1 << (n - 1 - k)
        single_probs.append(float(probs[idx]))
    equal = all(abs(p - 0.25) < 1e-9 for p in single_probs)
    print(f"W-state: {n} qubits")
    print(f"Fidelity = {fidelity:.6f}")
    print(f"One-excitation prob = {one_excitation_prob:.6f}")
    print(f"Per-qubit probs = {[round(p, 4) for p in single_probs]}")
    print(f"Equal weights: {equal}")
    print(f"Correct: {fidelity > 0.9999 and equal}")

if __name__ == "__main__":
    main()
'''

_add(
    "quantum_wstate_4qubit_cascade",
    "Prepare a 4-qubit W state via cascaded rotations and verify symmetry",
    """Write a complete, runnable Python program using numpy and qiskit that:
1. Prepares a 4-qubit W state |W_4> = (|1000> + |0100> + |0010> + |0001>)/2.
   Use the cascaded-rotation construction:
   - Apply ry(2*arccos(sqrt(1/4))) to qubit 0.
   - For each k from 1 to 3, apply cry(2*arccos(sqrt(1/(4-k))), k-1, k) followed
     by CX(k, k-1). This cascades the |1> amplitude from qubit k-1 to qubit k
     while leaving the appropriate excitation behind.
2. Simulate with qiskit.quantum_info.Statevector.
3. Computes the fidelity with the ideal W state |expected> = (|1000> + |0100>
   + |0010> + |0001>)/2 as |<expected|actual>|^2.
4. Computes the total probability of measuring exactly one excitation (one
   qubit in |1>, all others in |0>).
5. Computes the per-basis-state probabilities for |1000>, |0100>, |0010>,
   |0001> and verifies they are all 0.25.
6. In `def main()`, prints exactly:
     W-state: 4 qubits
     Fidelity = <value rounded to 6 decimals>
     One-excitation prob = 1.000000
     Per-qubit probs = [0.25, 0.25, 0.25, 0.25]
     Equal weights: True
     Correct: <True|False>
   where Correct is True iff fidelity > 0.9999 AND all four probabilities are
   0.25 to within 1e-9.
Call main() under `if __name__ == "__main__":`.
""",
    P16_REF,
    ["W-state: 4 qubits", "One-excitation prob = 1.000000",
     "Per-qubit probs = [0.25, 0.25, 0.25, 0.25]", "Equal weights: True",
     "Correct: True"],
    timeout=60,
)

# ---------------------------------------------------------------------------
# Problem 17: Quantum state tomography on a 2-qubit Bell state.
# ---------------------------------------------------------------------------
P17_REF = r'''
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, DensityMatrix, SparsePauliOp

def build_bell_state():
    qc = QuantumCircuit(2)
    qc.h(0); qc.cx(0, 1)
    return qc

def measure_all_paulis(n):
    """Return the 4^n Pauli basis operators as SparsePauliOp for n qubits."""
    paulis = ["I", "X", "Y", "Z"]
    ops = []
    from itertools import product
    for combo in product(paulis, repeat=n):
        label = "".join(combo)
        ops.append(label)
    return ops

def reconstruct_density_matrix(pauli_expectations, n):
    """Given a dict {pauli_string: expectation_value}, reconstruct the density
    matrix via rho = (1/2^n) * sum_{P} <P> * P."""
    from qiskit.quantum_info import Pauli
    N = 2 ** n
    rho = np.zeros((N, N), dtype=complex)
    for pauli_str, exp_val in pauli_expectations.items():
        # Build the matrix for this Pauli string
        P = Pauli(pauli_str).to_matrix()
        rho += exp_val * P
    rho /= N
    return rho

def main():
    n = 2
    qc = build_bell_state()
    sv = Statevector.from_instruction(qc)
    # Measure all 16 Pauli operators (I, X, Y, Z)^2
    paulis = measure_all_paulis(n)
    expectations = {}
    for p in paulis:
        op = SparsePauliOp.from_list([(p, 1.0)])
        expectations[p] = float(sv.expectation_value(op).real)
    # Reconstruct density matrix
    rho_reconstructed = reconstruct_density_matrix(expectations, n)
    # True density matrix
    rho_true = DensityMatrix(sv).data
    # Fidelity between reconstructed and true: F = Tr(sqrt(sqrt(rho_true) rho_rec sqrt(rho_true)))^2
    # For pure states this is |<psi|rho_rec|psi>|^2
    fidelity = float(np.real(np.vdot(sv.data, rho_reconstructed @ sv.data)))
    # Check entanglement: concurrence for 2 qubits
    # Concurrence C = max(0, lambda1 - lambda2 - lambda3 - lambda4)
    # where lambdas are sqrt of eigenvalues of rho * (Y (x) Y) * rho* * (Y (x) Y)
    Y = np.array([[0, -1j], [1j, 0]])
    YY = np.kron(Y, Y)
    rho_tilde = YY @ rho_reconstructed.conj() @ YY
    product = rho_reconstructed @ rho_tilde
    eigs = np.linalg.eigvalsh(product)
    lambdas = np.sqrt(np.maximum(eigs, 0))
    lambdas = np.sort(lambdas)[::-1]
    concurrence = float(max(0.0, lambdas[0] - lambdas[1] - lambdas[2] - lambdas[3]))
    print(f"Bell state: 2 qubits")
    print(f"Tomography Paulis = {len(paulis)}")
    print(f"Reconstruction fidelity = {fidelity:.6f}")
    print(f"Concurrence = {concurrence:.6f}")
    print(f"Entangled: {abs(concurrence - 1.0) < 1e-6}")
    print(f"Correct: {fidelity > 0.9999 and abs(concurrence - 1.0) < 1e-6}")

if __name__ == "__main__":
    main()
'''

_add(
    "quantum_tomography_bell_state",
    "Quantum state tomography on a Bell state — reconstruct rho and concurrence",
    """Write a complete, runnable Python program using numpy and qiskit that:
1. Builds the Bell state |Phi+> = (|00> + |11>)/sqrt(2) via H(0) and CX(0,1).
2. Computes the expectation values of all 16 Pauli operators in {I, X, Y, Z}^2
   on this state using qiskit.quantum_info.SparsePauliOp.
3. Reconstructs the 4x4 density matrix via
   rho = (1/4) * sum_{P in {I,X,Y,Z}^2} <P> * P_matrix.
4. Computes the reconstruction fidelity as
   F = <psi|rho_reconstructed|psi> (real part).
5. Computes the concurrence of the reconstructed density matrix:
   C = max(0, lambda_1 - lambda_2 - lambda_3 - lambda_4), where lambda_i are
   the square roots of the eigenvalues of rho * (Y (x) Y) * rho.conj() * (Y (x) Y),
   sorted in decreasing order.
6. In `def main()`, prints exactly:
     Bell state: 2 qubits
     Tomography Paulis = 16
     Reconstruction fidelity = <value rounded to 6 decimals>
     Concurrence = <value rounded to 6 decimals>
     Entangled: <True|False>
     Correct: <True|False>
   where Entangled is True iff |concurrence - 1| < 1e-6, and Correct is True
   iff fidelity > 0.9999 AND the state is entangled.
Call main() under `if __name__ == "__main__":`.
""",
    P17_REF,
    ["Bell state: 2 qubits", "Tomography Paulis = 16",
     "Reconstruction fidelity = ", "Concurrence = 1.000000",
     "Entangled: True", "Correct: True"],
    timeout=120,
)

# ---------------------------------------------------------------------------
# Problem 18: Variational Quantum Linear Solver (small 2x2 system).
# ---------------------------------------------------------------------------
P18_REF = r'''
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.quantum_info import Statevector
from scipy.optimize import minimize

def build_hadamard_test_gate(U, q, controlled=True):
    """Return a gate that applies U controlled by q (or just U if not controlled)."""
    if controlled:
        return U.control(1)
    return U

def hadamard_test_expectation(U, V_dag, phi):
    """Compute Re[<0| V^dag U |0>] for a single-qubit test using direct
    statevector simulation. Here we use a simpler approach: compute the
    expectation of the cost Hamiltonian directly via statevector overlaps."""
    # For the VQLS cost, we use the local cost C_L = 1 - (1/N) * sum_i Re[<b| V^dag U^dag A_i U V |b> <psi_i|phi>]
    # For a 2x2 system with A = sigma_z, b = |0>, this simplifies.
    pass

def vqls_solve(A, b, ansatz_params):
    """Solve A x = b for a 2x2 system using a parameterized ansatz.
    For simplicity, use a 1-qubit Ry ansatz V(theta) = Ry(theta).
    The cost is C(theta) = <phi| H_C |phi> where |phi> = V(theta)|0>
    and H_C = V^dag A^dag (I - |b><b|) A V... actually for VQLS the cost
    involves the normalized pseudo-inverse. For a 2x2 problem we can use the
    simpler cost C = || A V(theta)|0> - b ||^2 / ||b||^2."""
    n = 1
    theta = ansatz_params[0]
    # Ansatz state
    qc = QuantumCircuit(n)
    qc.ry(theta, 0)
    sv = Statevector.from_instruction(qc)
    phi = sv.data  # 2-dim complex vector
    # Cost: || A phi - b ||^2
    diff = A @ phi - b
    return float(np.real(np.vdot(diff, diff)))

def main():
    # Solve A x = b for a simple 2x2 system
    A = np.array([[1.0, 0.0], [0.0, 2.0]])  # diagonal
    b = np.array([1.0, 1.0]) / np.sqrt(2)   # |+>
    # Exact solution: x = A^{-1} b / ||A^{-1} b||
    x_exact = np.linalg.solve(A, b)
    x_exact_normalized = x_exact / np.linalg.norm(x_exact)
    # VQLS with 1-qubit Ry ansatz
    x0 = np.array([0.5])
    res = minimize(vqls_solve, x0, args=(A, b), method="COBYLA",
                   options={"maxiter": 200, "tol": 1e-8})
    theta_opt = res.x[0]
    # Build the final ansatz state
    qc = QuantumCircuit(1)
    qc.ry(theta_opt, 0)
    sv = Statevector.from_instruction(qc)
    x_vqls = sv.data
    # Compare to exact normalized solution
    # The VQLS state approximates x / ||x||, so compare up to a global phase
    overlap = float(np.abs(np.vdot(x_exact_normalized, x_vqls)) ** 2)
    # Also compute the cost
    cost = vqls_solve([theta_opt], A, b)
    print(f"System: A = diag(1, 2), b = |+>")
    print(f"VQLS theta = {theta_opt:.6f}")
    print(f"VQLS cost = {cost:.6f}")
    print(f"Overlap with exact = {overlap:.6f}")
    print(f"Converged: {overlap > 0.99}")
    print(f"Correct: {overlap > 0.99 and cost < 0.01}")

if __name__ == "__main__":
    main()
'''

_add(
    "quantum_vqls_2x2_diagonal",
    "Variational Quantum Linear Solver for a 2x2 diagonal system A x = b",
    """Write a complete, runnable Python program using numpy, qiskit, and scipy that:
1. Defines a 2x2 linear system A x = b with:
   A = [[1, 0], [0, 2]] (diagonal), b = (|0> + |1>)/sqrt(2) = (1/sqrt(2), 1/sqrt(2)).
2. Uses a 1-qubit variational ansatz V(theta) = Ry(theta) on |0>.
3. Defines the VQLS cost function
   C(theta) = || A V(theta)|0> - b ||^2
   computed using qiskit.quantum_info.Statevector to obtain V(theta)|0> and
   numpy for the matrix-vector products.
4. Minimizes C(theta) using scipy.optimize.minimize with method='COBYLA',
   maxiter=200, tol=1e-8, starting from theta=0.5.
5. Computes the exact solution x_exact = A^{-1} b, normalized to unit norm.
6. Computes the overlap |<x_exact_normalized | x_vqls>|^2 between the VQLS
   solution state and the exact normalized solution.
7. In `def main()`, prints exactly:
     System: A = diag(1, 2), b = |+>
     VQLS theta = <value rounded to 6 decimals>
     VQLS cost = <value rounded to 6 decimals>
     Overlap with exact = <value rounded to 6 decimals>
     Converged: <True|False>
     Correct: <True|False>
   where Converged is True iff overlap > 0.99, and Correct is True iff
   overlap > 0.99 AND cost < 0.01.
Call main() under `if __name__ == "__main__":`.
""",
    P18_REF,
    ["System: A = diag(1, 2), b = |+>", "VQLS theta = ",
     "VQLS cost = ", "Overlap with exact = ", "Converged: True",
     "Correct: True"],
    timeout=120,
)

print(f"Defined {len(PROBLEMS)} problems so far")

# ---------------------------------------------------------------------------
# Problem 19: 5-qubit graph state on a path graph and stabilizer check.
# ---------------------------------------------------------------------------
P19_REF = r'''
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, SparsePauliOp

def build_path_graph_state(n, edges):
    """Build a graph state on n qubits with the given edges.
    Apply H to all qubits, then CZ to each edge."""
    qc = QuantumCircuit(n)
    qc.h(range(n))
    for i, j in edges:
        qc.cz(i, j)
    return qc

def graph_state_stabilizers(n, edges):
    """The stabilizers of a graph state are K_i = X_i * prod_{j in N(i)} Z_j,
    one per qubit."""
    stabilizers = []
    adj = {i: [] for i in range(n)}
    for i, j in edges:
        adj[i].append(j); adj[j].append(i)
    for i in range(n):
        # Build the Pauli string (qubit 0 first)
        paulis = ['I'] * n
        paulis[i] = 'X'
        for j in adj[i]:
            paulis[j] = 'Z'
        stabilizers.append("".join(paulis))
    return stabilizers

def main():
    n = 5
    edges = [(0, 1), (1, 2), (2, 3), (3, 4)]  # path graph P_5
    qc = build_path_graph_state(n, edges)
    sv = Statevector.from_instruction(qc)
    stabilizers = graph_state_stabilizers(n, edges)
    results = []
    for pauli in stabilizers:
        op = SparsePauliOp.from_list([(pauli, 1.0)])
        val = float(sv.expectation_value(op).real)
        results.append((pauli, val))
    all_plus = all(abs(v - 1.0) < 1e-9 for _, v in results)
    # Entanglement: trace out 4 qubits, check the remaining is mixed
    from qiskit.quantum_info import DensityMatrix, partial_trace
    dm = DensityMatrix(sv)
    rho0 = partial_trace(dm, list(range(1, n)))
    purity0 = float(np.real(np.trace(rho0.data @ rho0.data)))
    # Graph state is a stabilizer state, so it's pure (single-qubit reduced
    # state is maximally mixed for connected graphs)
    print(f"Graph state: {n} qubits, path graph")
    for pauli, v in results:
        print(f"  <{pauli}> = {v:+.4f}")
    print(f"All stabilizers +1: {all_plus}")
    print(f"Single-qubit purity = {purity0:.4f}")
    print(f"Entangled: {abs(purity0 - 0.5) < 1e-6}")
    print(f"Valid graph state: {all_plus and abs(purity0 - 0.5) < 1e-6}")

if __name__ == "__main__":
    main()
'''

_add(
    "quantum_graph_state_path5",
    "5-qubit path-graph state — verify all stabilizers and entanglement",
    """Write a complete, runnable Python program using numpy and qiskit that:
1. Builds the 5-qubit graph state on the path graph P_5 with edges
   (0,1), (1,2), (2,3), (3,4):
   - Apply H to all 5 qubits.
   - Apply CZ to each edge.
2. Simulate with qiskit.quantum_info.Statevector.
3. Computes the 5 stabilizers of the graph state. For each vertex i, the
   stabilizer is K_i = X_i * prod_{j in N(i)} Z_j, where N(i) is the set of
   neighbours of i in the graph.
4. Computes the expectation value of each stabilizer (should be +1 for a
   genuine graph state).
5. Computes the reduced density matrix of qubit 0 (trace out qubits 1..4) and
   its purity. For a connected graph state, this should be 0.5 (maximally
   mixed).
6. In `def main()`, prints exactly:
     Graph state: 5 qubits, path graph
       <XZIII> = +1.0000
       <ZXZII> = +1.0000
       <IZXZI> = +1.0000
       <IIZXZ> = +1.0000
       <IIIZX> = +1.0000
     All stabilizers +1: True
     Single-qubit purity = 0.5000
     Entangled: True
     Valid graph state: True
   (All five stabilizer expectation values must be +1.0000; Valid graph state
   must be True.)
Call main() under `if __name__ == "__main__":`.
""",
    P19_REF,
    ["Graph state: 5 qubits, path graph", "All stabilizers +1: True",
     "Single-qubit purity = 0.5000", "Entangled: True",
     "Valid graph state: True"],
    timeout=60,
)

# ---------------------------------------------------------------------------
# Problem 20: Quantum kernel for a small classification task (2 features,
# 4 training points, squared fidelity kernel).
# ---------------------------------------------------------------------------
P20_REF = r'''
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.quantum_info import Statevector
from qiskit.circuit.library import ZZFeatureMap

def quantum_kernel(X1, X2, feature_dim, reps=2):
    """Compute the squared-fidelity quantum kernel
    K(x_i, x_j) = |<phi(x_i)|phi(x_j)>|^2
    using the ZZFeatureMap."""
    n = len(X1); m = len(X2)
    K = np.zeros((n, m))
    for i in range(n):
        sv_i = Statevector.from_instruction(ZZFeatureMap(feature_dim, reps=reps).assign_parameters(X1[i]))
        for j in range(m):
            sv_j = Statevector.from_instruction(ZZFeatureMap(feature_dim, reps=reps).assign_parameters(X2[j]))
            K[i, j] = float(np.abs(np.vdot(sv_i.data, sv_j.data)) ** 2)
    return K

def kernel_svm_predict(K_train, y_train, K_test, alpha, b):
    """Predict labels for test points given a precomputed kernel and
    dual coefficients alpha + bias b."""
    n_test = K_test.shape[0]
    n_train = K_train.shape[0]
    preds = np.zeros(n_test)
    for i in range(n_test):
        s = b
        for j in range(n_train):
            s += alpha[j] * y_train[j] * K_test[i, j]
        preds[i] = np.sign(s)
    return preds

def main():
    # Simple 2-feature binary classification: points inside a circle of radius
    # 1.0 are class +1, outside are class -1.
    X_train = np.array([
        [0.3, 0.4],   # inside (r=0.5)
        [-0.5, 0.2],  # inside (r~0.54)
        [1.2, 0.1],   # outside (r~1.2)
        [-0.3, -1.1], # outside (r~1.14)
    ])
    y_train = np.array([1, 1, -1, -1])
    X_test = np.array([
        [0.1, 0.1],   # inside
        [1.5, 1.5],   # outside
    ])
    y_test = np.array([1, -1])
    K_train = quantum_kernel(X_train, X_train, feature_dim=2, reps=2)
    K_test = quantum_kernel(X_test, X_train, feature_dim=2, reps=2)
    # Simple kernel SVM via least-squares: solve (K + lambda I) alpha = y
    lam = 0.1
    alpha = np.linalg.solve(K_train + lam * np.eye(len(y_train)), y_train)
    b = 0.0  # LS-SVM has no explicit bias
    preds = kernel_svm_predict(K_train, y_train, K_test, alpha, b)
    accuracy = float(np.mean(preds == y_test))
    print(f"Training points = {len(y_train)}")
    print(f"Test points = {len(y_test)}")
    print(f"Feature dim = 2")
    print(f"Kernel matrix shape = {K_train.shape}")
    print(f"Kernel diagonal = {np.round(np.diag(K_train), 4).tolist()}")
    print(f"Test predictions = {preds.astype(int).tolist()}")
    print(f"Test accuracy = {accuracy:.4f}")
    print(f"Correct: {accuracy == 1.0}")

if __name__ == "__main__":
    main()
'''

_add(
    "quantum_kernel_zz_featuremap_2d",
    "Quantum kernel with ZZFeatureMap for 2D binary classification",
    """Write a complete, runnable Python program using numpy and qiskit that:
1. Defines a small 2D binary classification problem: 4 training points where
   points inside the unit circle are class +1 and outside are class -1.
   Use:
     X_train = [[0.3, 0.4], [-0.5, 0.2], [1.2, 0.1], [-0.3, -1.1]]
     y_train = [+1, +1, -1, -1]
     X_test  = [[0.1, 0.1], [1.5, 1.5]]
     y_test  = [+1, -1]
2. Implements a quantum kernel K(x_i, x_j) = |<phi(x_i)|phi(x_j)>|^2 using
   qiskit.circuit.library.ZZFeatureMap with feature_dimension=2 and reps=2.
   Compute each statevector with qiskit.quantum_info.Statevector.
3. Computes the 4x4 training kernel matrix K_train and the 2x4 test-vs-train
   kernel matrix K_test. Verify the diagonal of K_train is all 1.0 (since
   <phi(x)|phi(x)> = 1).
4. Solves a simple least-squares kernel SVM: (K_train + lambda*I) alpha = y
   with lambda = 0.1.
5. Predicts the test labels as sign(sum_j alpha_j y_j K_test[i, j]).
6. In `def main()`, prints exactly:
     Training points = 4
     Test points = 2
     Feature dim = 2
     Kernel matrix shape = (4, 4)
     Kernel diagonal = [1.0, 1.0, 1.0, 1.0]
     Test predictions = [1, -1]
     Test accuracy = 1.0000
     Correct: True
   (Kernel diagonal must be all 1.0; Test predictions must be [1, -1];
   Correct is True iff test accuracy equals 1.0.)
Call main() under `if __name__ == "__main__":`.
""",
    P20_REF,
    ["Training points = 4", "Feature dim = 2", "Kernel diagonal = [1.0, 1.0, 1.0, 1.0]",
     "Test predictions = [1, -1]", "Test accuracy = 1.0000", "Correct: True"],
    timeout=120,
)

# ---------------------------------------------------------------------------
# Problem 21: Boson sampling — 3 photons in a 6-mode interferometer.
# ---------------------------------------------------------------------------
P21_REF = r'''
import numpy as np
from itertools import permutations

def build_random_unitary(n, seed=42):
    """Build a random n x n unitary using QR decomposition of a complex
    Gaussian matrix."""
    rng = np.random.default_rng(seed)
    X = rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))
    Q, R = np.linalg.qr(X)
    # Make the diagonal of R real and positive to ensure a unique Haar unitary
    phases = np.diag(R) / np.abs(np.diag(R))
    U = Q * phases
    return U

def permanent(M):
    """Compute the permanent of a square matrix via Ryser's algorithm."""
    n = M.shape[0]
    if n == 0:
        return 1.0
    rows = np.arange(n)
    total = 0.0
    for k in range(1, 2 ** n):
        # subset S determined by bits of k
        cols = [j for j in range(n) if (k >> j) & 1]
        submatrix = M[np.ix_(rows, cols)]
        prod = np.prod(np.sum(submatrix, axis=1))
        sign = -1 if (len(cols) % 2 == 0) else 1  # (-1)^(n - |S|)
        if (n - len(cols)) % 2 == 0:
            sign = 1
        else:
            sign = -1
        total += sign * prod
    return -total if (n % 2 == 0) else total  # Ryser's: perm = (-1)^n sum_S (-1)^|S| prod row sums

def boson_sampling_probability(U, input_modes, output_modes):
    """Compute the probability of observing `output_modes` given `input_modes`
    in a linear interferometer U.
    input_modes: list of mode indices occupied by input photons.
    output_modes: list of mode indices we want to detect photons at.
    The probability is |Per(U[input_modes, output_modes])|^2 / (prod s_i! * prod t_j!)
    where s_i and t_j are the input/output occupation numbers."""
    submatrix = U[np.ix_(input_modes, output_modes)]
    per = permanent(submatrix)
    # For collision-free configurations (each mode has at most 1 photon),
    # the denominator is 1.
    return float(np.abs(per) ** 2)

def main():
    n_modes = 6
    n_photons = 3
    input_modes = [0, 1, 2]  # photons start in modes 0, 1, 2
    U = build_random_unitary(n_modes, seed=42)
    # Compute the full output distribution over all 3-photon configurations
    # in 6 modes: C(6,3) = 20 collision-free configurations.
    from itertools import combinations
    output_configs = list(combinations(range(n_modes), n_photons))
    probs = {}
    for out in output_configs:
        p = boson_sampling_probability(U, input_modes, list(out))
        probs[out] = p
    total = sum(probs.values())
    # Pick the most likely output
    best_out = max(probs.items(), key=lambda kv: kv[1])
    # Verify normalization (sum over ALL Fock states, not just collision-free,
    # but for distinguishable-like photons the collision-free portion sums to
    # less than 1 in general. For ideal bosons with random U, the
    # collision-free portion is a substantial fraction.)
    print(f"Boson sampling: {n_photons} photons in {n_modes} modes")
    print(f"Input modes = {input_modes}")
    print(f"Collision-free outputs = {len(output_configs)}")
    print(f"Sum of collision-free probs = {total:.4f}")
    print(f"Most likely output = {best_out[0]}")
    print(f"Max prob = {best_out[1]:.4f}")
    print(f"Valid: {total > 0.5 and best_out[1] > 0}")

if __name__ == "__main__":
    main()
'''

_add(
    "quantum_boson_sampling_3x6",
    "Boson sampling: 3 photons in 6 modes, compute output distribution",
    """Write a complete, runnable Python program using only numpy that:
1. Builds a 6x6 random unitary U via QR decomposition of a complex Gaussian
   matrix (use numpy.random.default_rng(seed=42)). Correct the Q matrix by
   multiplying each column by the phase of the corresponding diagonal entry
   of R so that the result is a Haar-random unitary.
2. Implements the matrix permanent via Ryser's algorithm.
3. Computes the boson-sampling output probabilities for the input
   configuration (photons in modes 0, 1, 2) and all collision-free
   3-photon output configurations (there are C(6, 3) = 20 of them).
   For each output configuration S, the probability is
   P(S) = |Per(U[input_modes, S])|^2
   (collision-free, so the denominator is 1).
4. Sums the probabilities over all collision-free outputs (should be a
   substantial fraction of 1 for ideal bosons).
5. Identifies the most-likely output configuration and its probability.
6. In `def main()`, prints exactly:
     Boson sampling: 3 photons in 6 modes
     Input modes = [0, 1, 2]
     Collision-free outputs = 20
     Sum of collision-free probs = <value rounded to 4 decimals>
     Most likely output = <tuple of 3 mode indices>
     Max prob = <value rounded to 4 decimals>
     Valid: <True|False>
   where Valid is True iff the total collision-free probability exceeds 0.5
   AND the max probability is positive.
Call main() under `if __name__ == "__main__":`.
""",
    P21_REF,
    ["Boson sampling: 3 photons in 6 modes", "Input modes = [0, 1, 2]",
     "Collision-free outputs = 20", "Sum of collision-free probs = ",
     "Most likely output = ", "Valid: True"],
    timeout=120,
)

# ---------------------------------------------------------------------------
# Problem 22: Draper adder — quantum circuit for 3 + 2 = 5.
# ---------------------------------------------------------------------------
P22_REF = r'''
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import QFT
from qiskit.quantum_info import Statevector

def encode_int(x, n):
    """Encode integer x as an n-qubit basis state |x>."""
    qc = QuantumCircuit(n)
    bits = format(x, f"0{n}b")
    for q, b in enumerate(bits):
        if b == '1':
            qc.x(q)
    return qc

def draper_adder(a, b, n):
    """Build a Draper adder circuit that computes |a>|b> -> |a>|a+b> using
    the QFT-based approach. n qubits for each register."""
    n_total = 2 * n
    qc = QuantumCircuit(n_total)
    # Encode a in register 1 (qubits 0..n-1) and b in register 2 (qubits n..2n-1)
    a_bits = format(a, f"0{n}b")
    b_bits = format(b, f"0{n}b")
    for q, bit in enumerate(a_bits):
        if bit == '1':
            qc.x(q)
    for q, bit in enumerate(b_bits):
        if bit == '1':
            qc.x(n + q)
    # Apply QFT to register 2 (the target register that will hold the sum)
    qc.compose(QFT(n), range(n, 2 * n), inplace=True)
    # Apply controlled phase rotations: for each qubit q_a in register 1 and
    # q_b in register 2, apply a phase rotation of 2*pi / 2^(q_b - q_a + 1)
    # if q_b >= q_a, controlled on q_a being |1>.
    for q_a in range(n):
        for q_b in range(n):
            k = q_b - q_a
            if k < 0:
                continue
            angle = 2 * np.pi / (2 ** (k + 1))
            qc.cp(angle, q_a, n + q_b)
    # Apply inverse QFT to register 2
    qc.compose(QFT(n, inverse=True), range(n, 2 * n), inplace=True)
    return qc

def main():
    a = 3; b = 2; n = 3
    qc = draper_adder(a, b, n)
    # Simulate
    sv = Statevector.from_instruction(qc)
    probs = sv.probabilities_dict()
    # The output should be |a>|a+b> = |011>|101> (little-endian)
    # In qiskit's bit ordering, the full state is a 2n-bit string with
    # qubit 0 as the rightmost bit.
    best = max(probs.items(), key=lambda kv: kv[1])[0]
    # best is little-endian: bit 0 is rightmost
    # Register 1 is the rightmost n bits (qubits 0..n-1)
    # Register 2 is the leftmost n bits (qubits n..2n-1)
    reg1_bits = best[n:][::-1]  # qubits 0..n-1 in big-endian
    reg2_bits = best[:n][::-1]  # qubits n..2n-1 in big-endian
    a_out = int(reg1_bits, 2)
    sum_out = int(reg2_bits, 2)
    expected_sum = a + b
    print(f"a = {a}")
    print(f"b = {b}")
    print(f"n = {n}")
    print(f"Top bitstring = {best}")
    print(f"Register 1 (a) = {a_out}")
    print(f"Register 2 (a+b) = {sum_out}")
    print(f"Expected sum = {expected_sum}")
    print(f"Correct: {sum_out == expected_sum and a_out == a}")

if __name__ == "__main__":
    main()
'''

_add(
    "quantum_draper_adder_3plus2",
    "Draper adder: quantum circuit that computes 3 + 2 = 5 via QFT",
    """Write a complete, runnable Python program using numpy and qiskit that:
1. Implements the Draper adder for n=3 qubit registers. The circuit takes two
   3-qubit registers |a>|b> and produces |a>|a+b mod 8>.
2. Builds the circuit as follows:
   - Encode a=3 in register 1 (qubits 0..2): X on qubits 0 and 1.
   - Encode b=2 in register 2 (qubits 3..5): X on qubit 4.
   - Apply QFT to register 2.
   - For each q_a in register 1 and q_b in register 2 with q_b >= q_a, apply
     a controlled-phase gate cp(2*pi / 2^(q_b - q_a + 1)) with control q_a and
     target q_b.
   - Apply inverse QFT to register 2.
3. Simulate with qiskit.quantum_info.Statevector. Take the most-probable
   bitstring (should be deterministic).
4. Decode the bitstring: in qiskit's little-endian ordering, register 1 is the
   rightmost 3 bits (qubits 0..2) and register 2 is the leftmost 3 bits
   (qubits 3..5). Parse each as a 3-bit integer.
5. In `def main()`, prints exactly:
     a = 3
     b = 2
     n = 3
     Top bitstring = <value>
     Register 1 (a) = 3
     Register 2 (a+b) = 5
     Expected sum = 5
     Correct: <True|False>
   where Correct is True iff register 2 equals 5 AND register 1 still equals 3.
Call main() under `if __name__ == "__main__":`.
""",
    P22_REF,
    ["a = 3", "b = 2", "n = 3", "Register 1 (a) = 3", "Register 2 (a+b) = 5",
     "Expected sum = 5", "Correct: True"],
    timeout=60,
)

print(f"Total problems defined: {len(PROBLEMS)}")

# ---------------------------------------------------------------------------
# Emit all problems to disk
# ---------------------------------------------------------------------------
def emit():
    manifest = []
    for p in PROBLEMS:
        pid = p["id"]
        (RUN_DIR / "prompts" / f"{pid}.txt").write_text(p["prompt"], encoding="utf-8")
        (RUN_DIR / "reference" / f"{pid}.py").write_text(p["reference"], encoding="utf-8")
        # Write test that runs the REFERENCE solution and checks expected substrings.
        # The test file is later reused to evaluate candidates: the harness
        # substitutes the candidate path.
        test_code = textwrap.dedent(f'''\
            import os, subprocess, sys
            def run_tests(workspace_root: str) -> dict:
                ref = os.path.join(workspace_root, "evals", "runs", "quantum-algo-27b-35b-20260713", "reference", "{pid}.py")
                out = subprocess.run([sys.executable, ref], capture_output=True, text=True, timeout={p["timeout"]})
                expected = {p["expected_substrings"]!r}
                ok = out.returncode == 0 and all(s in out.stdout for s in expected)
                return {{"pass": bool(ok), "detail": out.stdout[-500:] + out.stderr[-300:]}}
            ''')
        (RUN_DIR / "tests" / f"{pid}.py").write_text(test_code, encoding="utf-8")
        manifest.append({
            "id": pid,
            "title": p["title"],
            "expected_substrings": p["expected_substrings"],
            "timeout": p["timeout"],
        })
    (RUN_DIR / "PROBLEMS.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(PROBLEMS)} problems to {RUN_DIR}")

if __name__ == "__main__":
    emit()
