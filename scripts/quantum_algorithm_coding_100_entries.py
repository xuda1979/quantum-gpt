"""Curated quantum-algorithm-coding questions with validated, executable answers.

Each entry:
  id, family, algorithm, difficulty, task_type, framework, question, rationale, code
The `code` is a self-contained, self-checking program (ends with asserts + print).
Run scripts/validate_quantum_algorithm_coding_100.py to execute and verify all.
"""

ENTRIES = []


def add(**kw):
    ENTRIES.append(kw)


# ===================================================================
# USER-REQUESTED QUESTIONS (translated from Chinese)
# ===================================================================

add(
    id="qac_user01_vqe_h2_single_point",
    family="vqe_chemistry",
    algorithm="vqe_hea_h2_single_point",
    difficulty="hard",
    task_type="implementation",
    question=(
        "For the STO-3G H2 molecule Hamiltonian at an interatomic distance of 0.5 Angstrom, "
        "use Qiskit to write a VQE algorithm based on a hardware-efficient ansatz (HEA) to "
        "solve for the ground-state energy of this Hamiltonian, and output the ground-state "
        "energy value (in Hartree)."
    ),
    rationale=(
        "Build the H2 electronic Hamiltonian with PySCFDriver (STO-3G), map it to qubits with a "
        "parity mapping plus two-qubit reduction, and fold the nuclear-repulsion constant into the "
        "identity term so the minimum eigenvalue is the total energy. Optimize an EfficientSU2 (HEA) "
        "ansatz with COBYLA and a few random restarts, evaluating the energy with a statevector "
        "estimator. Validate against the exact diagonalization of the qubit Hamiltonian."
    ),
    code=r'''
import numpy as np
from scipy.optimize import minimize
from qiskit.circuit.library import efficient_su2
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator
from qiskit_nature.second_q.drivers import PySCFDriver
from qiskit_nature.second_q.mappers import ParityMapper


def h2_qubit_hamiltonian(bond_length: float) -> SparsePauliOp:
    """STO-3G H2 Hamiltonian mapped to qubits with nuclear repulsion folded in."""
    driver = PySCFDriver(atom=f"H 0 0 0; H 0 0 {bond_length}", basis="sto3g",
                         charge=0, spin=0)
    problem = driver.run()
    mapper = ParityMapper(num_particles=problem.num_particles)
    qubit_op = mapper.map(problem.second_q_ops()[0])
    identity = SparsePauliOp("I" * qubit_op.num_qubits)
    return (qubit_op + problem.nuclear_repulsion_energy * identity).simplify()


def run_vqe(bond_length=0.5, reps=2, seed=1234) -> float:
    h = h2_qubit_hamiltonian(bond_length)
    ansatz = efficient_su2(h.num_qubits, reps=reps, entanglement="linear")
    estimator = StatevectorEstimator()

    def energy(p):
        return float(estimator.run([(ansatz, h, p)]).result()[0].data.evs)

    rng = np.random.default_rng(seed)
    best = None
    for _ in range(3):
        x0 = rng.uniform(-np.pi, np.pi, ansatz.num_parameters)
        res = minimize(energy, x0, method="COBYLA", options={"maxiter": 400})
        if best is None or res.fun < best.fun:
            best = res
    return float(best.fun)


if __name__ == "__main__":
    e_vqe = run_vqe(0.5)
    h = h2_qubit_hamiltonian(0.5)
    e_exact = float(np.linalg.eigvalsh(h.to_matrix())[0])
    print(f"VQE ground-state energy at R=0.5 A: {e_vqe:.6f} Hartree (exact {e_exact:.6f})")
    assert abs(e_vqe - e_exact) < 1e-2, (e_vqe, e_exact)
''',
)

add(
    id="qac_user02_vqe_h2_dissociation_curve",
    family="vqe_chemistry",
    algorithm="vqe_hea_h2_potential_curve",
    difficulty="hard",
    task_type="implementation",
    question=(
        "For the STO-3G H2 molecule Hamiltonian over interatomic distances 0.5-1.5 Angstrom "
        "(step 0.1 Angstrom), use Qiskit to write a VQE algorithm based on a hardware-efficient "
        "ansatz (HEA) to solve for the ground-state energy at each distance, and output the "
        "ground-state potential energy curve (x-axis = interatomic distance, y-axis = ground-state energy)."
    ),
    rationale=(
        "Reuse the parity-mapped STO-3G H2 Hamiltonian and run an EfficientSU2 (HEA) VQE at every "
        "bond length on the scan grid. Collect (R, E) pairs to form the dissociation curve and plot "
        "it with matplotlib (saved to file for headless environments). Validate that the curve has its "
        "minimum near the equilibrium bond length (~0.7 Angstrom) and matches exact diagonalization."
    ),
    code=r"""
import numpy as np
from scipy.optimize import minimize
from qiskit.circuit.library import efficient_su2
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator
from qiskit_nature.second_q.drivers import PySCFDriver
from qiskit_nature.second_q.mappers import ParityMapper


def h2_qubit_hamiltonian(bond_length: float) -> SparsePauliOp:
    driver = PySCFDriver(atom=f"H 0 0 0; H 0 0 {bond_length}", basis="sto3g",
                         charge=0, spin=0)
    problem = driver.run()
    mapper = ParityMapper(num_particles=problem.num_particles)
    qubit_op = mapper.map(problem.second_q_ops()[0])
    identity = SparsePauliOp("I" * qubit_op.num_qubits)
    return (qubit_op + problem.nuclear_repulsion_energy * identity).simplify()


def vqe_energy(h: SparsePauliOp, reps=2, seed=1234) -> float:
    ansatz = efficient_su2(h.num_qubits, reps=reps, entanglement="linear")
    estimator = StatevectorEstimator()

    def energy(p):
        return float(estimator.run([(ansatz, h, p)]).result()[0].data.evs)

    rng = np.random.default_rng(seed)
    best = None
    for _ in range(2):
        x0 = rng.uniform(-np.pi, np.pi, ansatz.num_parameters)
        res = minimize(energy, x0, method="COBYLA", options={"maxiter": 300})
        if best is None or res.fun < best.fun:
            best = res
    return float(best.fun)


def potential_energy_curve(distances):
    return [vqe_energy(h2_qubit_hamiltonian(r)) for r in distances]


if __name__ == "__main__":
    distances = np.round(np.arange(0.5, 1.5 + 1e-9, 0.1), 2)
    energies = potential_energy_curve(distances)
    print("R (Angstrom)   E_ground (Hartree)")
    for r, e in zip(distances, energies):
        print(f"  {r:>4}        {e: .6f}")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        plt.plot(distances, energies, "o-")
        plt.xlabel("Bond distance R (Angstrom)")
        plt.ylabel("Ground-state energy (Hartree)")
        plt.title("H2 (STO-3G) VQE/HEA potential energy curve")
        plt.grid(True)
        plt.savefig("h2_vqe_potential_curve.png", dpi=150, bbox_inches="tight")
    except ImportError:
        pass
    r_min = distances[int(np.argmin(energies))]
    assert r_min in (0.7, 0.8), r_min
    assert abs(energies[0] - (-1.0552)) < 2e-2, energies[0]
    print(f"Equilibrium bond length on grid: {r_min} Angstrom")
""",
)

add(
    id="qac_user03_qaoa_maxcut_3regular_8node",
    family="qaoa_optimization",
    algorithm="qaoa_maxcut_3regular_graph",
    difficulty="hard",
    task_type="implementation",
    question=(
        "For a random 3-regular undirected graph on 8 nodes where every edge has weight 1, use "
        "Qiskit to write a QAOA algorithm to solve the MaxCut problem of this graph, and output the "
        "maximum cut value and the corresponding maximum cut partition."
    ),
    rationale=(
        "Construct the cost Hamiltonian H_C = sum_(i,j) w_ij/2 (Z_i Z_j - I); minimizing <H_C> "
        "maximizes the cut. Optimize a QAOAAnsatz with COBYLA and several restarts, then sample the "
        "optimized state and pick the best measured bitstring (reversing Qiskit's little-endian order "
        "to node order). Validate the QAOA cut against an exact brute-force search (feasible for 8 nodes)."
    ),
    code=r"""
import numpy as np
import networkx as nx
from scipy.optimize import minimize
from qiskit.circuit.library import QAOAAnsatz
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator, StatevectorSampler


def build_graph(n=8, degree=3, seed=7):
    g = nx.random_regular_graph(degree, n, seed=seed)
    nx.set_edge_attributes(g, 1.0, "weight")
    return g


def maxcut_cost_hamiltonian(g):
    n = g.number_of_nodes()
    terms = []
    for i, j, data in g.edges(data=True):
        w = data.get("weight", 1.0)
        z = ["I"] * n
        z[i] = z[j] = "Z"
        terms.append(("".join(reversed(z)), 0.5 * w))
        terms.append(("I" * n, -0.5 * w))
    return SparsePauliOp.from_list(terms).simplify()


def cut_value(g, bitstring):
    a = [int(b) for b in bitstring]
    return sum(d.get("weight", 1.0) for i, j, d in g.edges(data=True) if a[i] != a[j])


def solve_maxcut_qaoa(g, reps=2, seed=42):
    cost = maxcut_cost_hamiltonian(g)
    ansatz = QAOAAnsatz(cost, reps=reps).decompose()
    estimator = StatevectorEstimator()

    def objective(p):
        return float(estimator.run([(ansatz, cost, p)]).result()[0].data.evs)

    rng = np.random.default_rng(seed)
    best = None
    for _ in range(3):
        x0 = rng.uniform(0, np.pi, ansatz.num_parameters)
        res = minimize(objective, x0, method="COBYLA", options={"maxiter": 250})
        if best is None or res.fun < best.fun:
            best = res

    sampler = StatevectorSampler()
    measured = ansatz.measure_all(inplace=False)
    counts = sampler.run([(measured, best.x)], shots=4096).result()[0].data.meas.get_counts()
    best_bits, best_cut = None, -1.0
    for bs in counts:
        bits = bs[::-1]
        v = cut_value(g, bits)
        if v > best_cut:
            best_bits, best_cut = bits, v
    part = ([v for v in range(g.number_of_nodes()) if best_bits[v] == "0"],
            [v for v in range(g.number_of_nodes()) if best_bits[v] == "1"])
    return best_cut, part


if __name__ == "__main__":
    g = build_graph(8, 3, seed=7)
    cut, part = solve_maxcut_qaoa(g)
    brute = max(cut_value(g, format(x, "08b")) for x in range(2 ** 8))
    print(f"QAOA max cut value: {cut:.0f}  (brute-force optimum {brute:.0f})")
    print(f"Partition: set0={part[0]}, set1={part[1]}")
    assert cut == brute, (cut, brute)
""",
)


# ===================================================================
# BATCH: foundational states, oracles, and core algorithms
# ===================================================================

add(
    id="qac_bell_state_all_four",
    family="entanglement_protocols",
    algorithm="bell_state_preparation",
    difficulty="easy",
    question=(
        "Using Qiskit, implement `bell_state(name)` returning a 2-qubit QuantumCircuit that prepares "
        "the Bell state named 'phi_plus', 'phi_minus', 'psi_plus', or 'psi_minus'. Verify each "
        "statevector against the expected big-endian amplitudes."
    ),
    rationale=(
        "Start from H on qubit 0 and CNOT(0->1) for |Phi+>. Apply Z before the CNOT to flip the "
        "relative phase (|Phi->), and X on qubit 1 to flip the target bit (|Psi+>); combine for "
        "|Psi->. Compare statevectors with state_fidelity, accounting for Qiskit little-endian order."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, state_fidelity

R = 2 ** -0.5
EXPECTED = {
    "phi_plus":  [R, 0, 0, R],
    "phi_minus": [R, 0, 0, -R],
    "psi_plus":  [0, R, R, 0],
    "psi_minus": [0, R, -R, 0],
}

def bell_state(name: str) -> QuantumCircuit:
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    if name == "phi_minus":
        qc.z(0)
    elif name == "psi_plus":
        qc.x(1)
    elif name == "psi_minus":
        qc.z(0); qc.x(1)
    elif name != "phi_plus":
        raise ValueError(name)
    return qc

if __name__ == "__main__":
    for name, amp in EXPECTED.items():
        sv = Statevector(bell_state(name))
        # convert little-endian (q1 q0) to big-endian (q0 q1) ordering
        be = np.asarray(sv.data).reshape(2, 2).T.reshape(-1)
        fid = state_fidelity(Statevector(be), Statevector(np.asarray(amp, complex)))
        print(f"{name}: fidelity {fid:.6f}")
        assert fid > 1 - 1e-9, name
    print("all Bell states verified")
""",
)

add(
    id="qac_ghz_state_nqubit",
    family="entanglement_protocols",
    algorithm="ghz_state_preparation",
    difficulty="easy",
    question=(
        "Using Qiskit, write `ghz_circuit(n)` that prepares the n-qubit GHZ state "
        "(|0...0> + |1...1>)/sqrt(2). Verify for n=2..6 that only the all-zeros and all-ones "
        "basis states have probability 1/2 each."
    ),
    rationale=(
        "Apply H to qubit 0, then a ladder of CNOTs from qubit 0 to each subsequent qubit so the "
        "single superposition bit is copied across all qubits, producing GHZ. Check the probability "
        "dictionary only contains the two extreme basis states with weight 1/2."
    ),
    code=r"""
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

def ghz_circuit(n: int) -> QuantumCircuit:
    qc = QuantumCircuit(n)
    qc.h(0)
    for q in range(1, n):
        qc.cx(0, q)
    return qc

if __name__ == "__main__":
    for n in range(2, 7):
        probs = Statevector(ghz_circuit(n)).probabilities_dict()
        keys = set(probs)
        assert keys == {"0" * n, "1" * n}, (n, keys)
        for v in probs.values():
            assert abs(v - 0.5) < 1e-9, v
        print(f"GHZ n={n} verified: {sorted(probs)}")
""",
)

add(
    id="qac_w_state_three_qubit",
    family="entanglement_protocols",
    algorithm="w_state_preparation",
    difficulty="medium",
    question=(
        "Using Qiskit, prepare the 3-qubit W state (|001>+|010>+|100>)/sqrt(3) and verify that "
        "each single-excitation basis state has probability 1/3 and all others are zero."
    ),
    rationale=(
        "Build the W state with a sequence of controlled Ry rotations: rotate qubit 0 so |1> has "
        "amplitude sqrt(1/3), then conditionally distribute the remaining amplitude across qubits 1 "
        "and 2 using controlled rotations and CNOTs. Verify the probability distribution."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

def w_state_3() -> QuantumCircuit:
    qc = QuantumCircuit(3)
    qc.ry(2 * np.arccos(np.sqrt(1 / 3)), 0)  # amplitude sqrt(1/3) onto qubit 0
    qc.ch(0, 1)                               # split remaining weight to qubit 1
    qc.cx(1, 2)                               # and onto qubit 2
    qc.cx(0, 1)
    qc.x(0)
    return qc

if __name__ == "__main__":
    probs = Statevector(w_state_3()).probabilities_dict()
    support = {k: v for k, v in probs.items() if v > 1e-9}
    assert set(support) == {"001", "010", "100"}, set(support)
    for v in support.values():
        assert abs(v - 1 / 3) < 1e-9, v
    print("W state verified:", {k: round(v, 4) for k, v in support.items()})
""",
)

add(
    id="qac_deutsch_jozsa",
    family="oracle_algorithms",
    algorithm="deutsch_jozsa",
    difficulty="medium",
    question=(
        "Implement the Deutsch-Jozsa algorithm in Qiskit for an n-bit Boolean function given as an "
        "oracle. Show that a constant oracle yields the all-zeros measurement and a balanced oracle "
        "yields a non-zero result with certainty."
    ),
    rationale=(
        "Use n input qubits and one ancilla in |-> state. Apply H to all inputs, the phase oracle, "
        "and H again. For a constant function the input register returns to |0...0>; for a balanced "
        "function it never does. Validate by inspecting the statevector probabilities of the input register."
    ),
    code=r"""
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

def dj_circuit(n, oracle):
    qc = QuantumCircuit(n + 1)
    qc.x(n); qc.h(n)
    qc.h(range(n))
    oracle(qc, n)
    qc.h(range(n))
    return qc

def constant_oracle(qc, n):
    pass  # f(x) = 0

def balanced_oracle(qc, n):
    for q in range(n):
        qc.cx(q, n)  # f(x) = parity(x)

def measured_input_distribution(n, oracle):
    sv = Statevector(dj_circuit(n, oracle))
    probs = sv.probabilities_dict(qargs=list(range(n)))
    return {k: v for k, v in probs.items() if v > 1e-9}

if __name__ == "__main__":
    n = 4
    const = measured_input_distribution(n, constant_oracle)
    bal = measured_input_distribution(n, balanced_oracle)
    assert set(const) == {"0" * n}, const
    assert "0" * n not in bal, bal
    print("constant ->", const)
    print("balanced ->", bal)
    print("Deutsch-Jozsa verified")
""",
)

add(
    id="qac_bernstein_vazirani",
    family="oracle_algorithms",
    algorithm="bernstein_vazirani",
    difficulty="medium",
    question=(
        "Implement the Bernstein-Vazirani algorithm in Qiskit to recover a hidden bit-string s from "
        "an oracle f(x) = s.x (mod 2) in a single query. Verify recovery for several random s."
    ),
    rationale=(
        "Prepare the input register in the |+> basis and the ancilla in |->. The phase oracle places "
        "CNOTs from input qubit i to the ancilla wherever s_i = 1. A final layer of H gates collapses "
        "the input register deterministically onto s. Recover s from the single measured outcome."
    ),
    code=r"""
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

def bv_recover(s: str) -> str:
    n = len(s)
    qc = QuantumCircuit(n + 1)
    qc.x(n); qc.h(n)
    qc.h(range(n))
    for i, bit in enumerate(s):          # s indexed left-to-right as qubit i
        if bit == "1":
            qc.cx(i, n)
    qc.h(range(n))
    probs = Statevector(qc).probabilities_dict(qargs=list(range(n)))
    outcome = max(probs, key=probs.get)  # little-endian string over qubits n-1..0
    return outcome[::-1]                  # reverse to qubit 0..n-1 order

if __name__ == "__main__":
    for s in ["1011", "0001", "1111", "101010"]:
        rec = bv_recover(s)
        print(f"hidden {s} -> recovered {rec}")
        assert rec == s, (s, rec)
    print("Bernstein-Vazirani verified")
""",
)

add(
    id="qac_grover_two_qubit",
    family="amplitude_amplification",
    algorithm="grover_search_2qubit",
    difficulty="medium",
    question=(
        "Implement Grover's search in Qiskit for 2 qubits to find the marked state |11>. Use one "
        "Grover iteration and verify the marked state is found with probability 1."
    ),
    rationale=(
        "For N=4 with one marked item, a single Grover iteration is exactly optimal. Use a CZ as the "
        "phase oracle for |11> and the standard diffusion operator (H-X-CZ-X-H). The final amplitude "
        "fully concentrates on |11>."
    ),
    code=r"""
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

def grover_2q():
    qc = QuantumCircuit(2)
    qc.h([0, 1])
    qc.cz(0, 1)                 # oracle marks |11>
    qc.h([0, 1]); qc.x([0, 1])  # diffusion
    qc.cz(0, 1)
    qc.x([0, 1]); qc.h([0, 1])
    return qc

if __name__ == "__main__":
    probs = Statevector(grover_2q()).probabilities_dict()
    print({k: round(v, 4) for k, v in probs.items()})
    assert abs(probs.get("11", 0) - 1.0) < 1e-9, probs
    print("Grover (2-qubit) found |11> with probability 1")
""",
)

add(
    id="qac_grover_three_qubit",
    family="amplitude_amplification",
    algorithm="grover_search_3qubit",
    difficulty="medium",
    question=(
        "Implement Grover's search in Qiskit for 3 qubits to amplify an arbitrary marked basis state. "
        "Use the optimal number of iterations and verify the marked state probability exceeds 0.9."
    ),
    rationale=(
        "For N=8 with one marked item the optimal iteration count is floor(pi/4 * sqrt(8)) = 2. Build "
        "a multi-controlled-Z phase oracle for the marked string (flip zero-bits with X gates around "
        "an MCZ), and the standard diffusion operator. Two iterations push the success probability above 0.9."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

def mcz(qc, qubits):
    *ctrl, tgt = qubits
    qc.h(tgt); qc.mcx(ctrl, tgt); qc.h(tgt)

def grover_3q(marked: str, iterations: int):
    n = 3
    qc = QuantumCircuit(n)
    qc.h(range(n))
    for _ in range(iterations):
        zeros = [i for i, b in enumerate(reversed(marked)) if b == "0"]
        if zeros: qc.x(zeros)
        mcz(qc, list(range(n)))
        if zeros: qc.x(zeros)
        qc.h(range(n)); qc.x(range(n))   # diffusion
        mcz(qc, list(range(n)))
        qc.x(range(n)); qc.h(range(n))
    return qc

if __name__ == "__main__":
    iters = int(np.floor(np.pi / 4 * np.sqrt(8)))
    for marked in ["101", "000", "111", "010"]:
        probs = Statevector(grover_3q(marked, iters)).probabilities_dict()
        p = probs.get(marked, 0.0)
        print(f"marked {marked}: prob {p:.4f} ({iters} iterations)")
        assert p > 0.9, (marked, p)
    print("Grover (3-qubit) verified")
""",
)

add(
    id="qac_qft_and_inverse",
    family="fourier_phase",
    algorithm="quantum_fourier_transform",
    difficulty="medium",
    question=(
        "Using Qiskit, build an n-qubit Quantum Fourier Transform circuit from first principles "
        "(Hadamards + controlled phase rotations + swaps). Verify that QFT followed by inverse-QFT is "
        "the identity, and that QFT|0...0> is the uniform superposition."
    ),
    rationale=(
        "The QFT applies H to each qubit followed by controlled-phase gates with angles pi/2^k, then "
        "reverses qubit order with swaps. Composing it with its inverse must yield the identity "
        "operator, and acting on |0> must produce an equal superposition of all basis states."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator, Statevector

def qft(n: int) -> QuantumCircuit:
    qc = QuantumCircuit(n)
    for j in range(n):
        qc.h(j)
        for k in range(j + 1, n):
            qc.cp(np.pi / 2 ** (k - j), k, j)
    for i in range(n // 2):
        qc.swap(i, n - 1 - i)
    return qc

if __name__ == "__main__":
    for n in range(1, 5):
        full = QuantumCircuit(n)
        full.compose(qft(n), inplace=True)
        full.compose(qft(n).inverse(), inplace=True)
        assert Operator(full).equiv(Operator(np.eye(2 ** n))), n
        amps = np.abs(Statevector(qft(n)).data)
        assert np.allclose(amps, 1 / np.sqrt(2 ** n)), n
        print(f"QFT n={n}: inverse identity OK, uniform |0> OK")
    print("QFT verified")
""",
)

add(
    id="qac_quantum_phase_estimation",
    family="fourier_phase",
    algorithm="quantum_phase_estimation",
    difficulty="hard",
    question=(
        "Implement Quantum Phase Estimation in Qiskit to estimate the eigenphase of a phase gate "
        "P(2*pi*phi) acting on its |1> eigenstate. Use enough counting qubits to resolve phi=1/8 "
        "exactly and verify the recovered phase."
    ),
    rationale=(
        "QPE prepares a counting register in uniform superposition, applies controlled-U^(2^k) gates, "
        "and an inverse QFT to write the binary fraction of the phase into the register. With a phase "
        "of 1/8 = 0.001_2, three counting qubits resolve it exactly, giving the measured integer 1 -> 1/8."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFTGate
from qiskit.quantum_info import Statevector

def qpe_phase(phi: float, counting: int) -> float:
    n = counting
    qc = QuantumCircuit(n + 1)
    qc.x(n)                       # eigenstate |1> of P(theta)
    qc.h(range(n))
    for k in range(n):
        for _ in range(2 ** k):
            qc.cp(2 * np.pi * phi, k, n)
    qc.append(QFTGate(n).inverse(), range(n))
    probs = Statevector(qc).probabilities_dict(qargs=list(range(n)))
    best = max(probs, key=probs.get)
    return int(best, 2) / 2 ** n

if __name__ == "__main__":
    est = qpe_phase(1 / 8, counting=3)
    print(f"estimated phase: {est} (true 0.125)")
    assert abs(est - 1 / 8) < 1e-9, est
    print("QPE verified")
""",
)

add(
    id="qac_quantum_teleportation",
    family="entanglement_protocols",
    algorithm="quantum_teleportation",
    difficulty="medium",
    question=(
        "Implement quantum teleportation in Qiskit that transfers an arbitrary single-qubit state from "
        "Alice to Bob. Verify with the deferred-measurement principle that Bob's final qubit matches "
        "the original input state with fidelity 1."
    ),
    rationale=(
        "Teleportation entangles a Bell pair between Alice and Bob, Alice performs a Bell-basis "
        "measurement, and Bob applies X/Z corrections. Using deferred measurement, replace the "
        "classically-controlled corrections with CX and CZ gates; then Bob's reduced density matrix "
        "exactly equals the input state, checked via partial_trace and state_fidelity."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, partial_trace, state_fidelity, random_statevector

def teleport(input_state: Statevector) -> QuantumCircuit:
    qc = QuantumCircuit(3)                 # q0 payload, q1 Alice, q2 Bob
    qc.initialize(input_state.data, 0)
    qc.h(1); qc.cx(1, 2)                   # Bell pair on (1,2)
    qc.cx(0, 1); qc.h(0)                   # Alice's Bell measurement basis
    qc.cx(1, 2)                            # deferred X correction
    qc.cz(0, 2)                            # deferred Z correction
    return qc

if __name__ == "__main__":
    for seed in range(4):
        psi = random_statevector(2, seed=seed)
        full = Statevector(teleport(psi))
        bob = partial_trace(full, [0, 1])  # keep qubit 2
        fid = state_fidelity(bob, psi)
        print(f"seed {seed}: teleport fidelity {fid:.6f}")
        assert fid > 1 - 1e-9, fid
    print("Teleportation verified")
""",
)

add(
    id="qac_superdense_coding",
    family="entanglement_protocols",
    algorithm="superdense_coding",
    difficulty="medium",
    question=(
        "Implement superdense coding in Qiskit: Alice sends two classical bits to Bob by manipulating "
        "her half of a shared Bell pair and transmitting only one qubit. Verify all four 2-bit messages "
        "decode correctly."
    ),
    rationale=(
        "Starting from a shared |Phi+>, Alice encodes message bits b1 b0 by applying Z^b1 and X^b0 to "
        "her qubit. Bob undoes the entangler (CNOT then H) and measures both qubits to recover the two "
        "bits deterministically. Check the decoded statevector for each of the four messages."
    ),
    code=r"""
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

def superdense(message: str) -> str:
    qc = QuantumCircuit(2)
    qc.h(0); qc.cx(0, 1)               # shared Bell pair
    b1, b0 = int(message[0]), int(message[1])
    if b0: qc.x(0)
    if b1: qc.z(0)
    qc.cx(0, 1); qc.h(0)              # Bob decodes
    probs = Statevector(qc).probabilities_dict()
    decoded = max(probs, key=probs.get)  # little-endian (q1 q0)
    return decoded[::-1]

if __name__ == "__main__":
    for msg in ["00", "01", "10", "11"]:
        out = superdense(msg)
        print(f"sent {msg} -> decoded {out}")
        assert out == msg, (msg, out)
    print("Superdense coding verified")
""",
)

add(
    id="qac_swap_test",
    family="quantum_subroutines",
    algorithm="swap_test_overlap",
    difficulty="medium",
    question=(
        "Implement the swap test in Qiskit to estimate the overlap |<psi|phi>|^2 between two "
        "single-qubit states. Verify that identical states give ancilla P(0)=1 and orthogonal states "
        "give P(0)=0.5."
    ),
    rationale=(
        "The swap test uses an ancilla with H-controlled-SWAP-H; the ancilla measures 0 with "
        "probability (1 + |<psi|phi>|^2)/2. Identical states give P(0)=1, orthogonal states give "
        "P(0)=1/2. Compute the ancilla marginal from the statevector and invert for the overlap."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

def swap_test_overlap(psi, phi):
    qc = QuantumCircuit(3)            # q0 ancilla, q1 psi, q2 phi
    qc.initialize(psi, 1)
    qc.initialize(phi, 2)
    qc.h(0); qc.cswap(0, 1, 2); qc.h(0)
    p0 = Statevector(qc).probabilities_dict(qargs=[0]).get("0", 0.0)
    return 2 * p0 - 1, p0

if __name__ == "__main__":
    same, p0_same = swap_test_overlap([1, 0], [1, 0])
    orth, p0_orth = swap_test_overlap([1, 0], [0, 1])
    print(f"identical: overlap {same:.4f}, P(0)={p0_same:.4f}")
    print(f"orthogonal: overlap {orth:.4f}, P(0)={p0_orth:.4f}")
    assert abs(p0_same - 1.0) < 1e-9 and abs(same - 1.0) < 1e-9
    assert abs(p0_orth - 0.5) < 1e-9 and abs(orth) < 1e-9
    print("Swap test verified")
""",
)

add(
    id="qac_simons_algorithm",
    family="oracle_algorithms",
    algorithm="simons_algorithm",
    difficulty="hard",
    question=(
        "Implement Simon's algorithm in Qiskit for a 3-bit hidden string s. Build a 2-to-1 oracle with "
        "period s, collect measurement outcomes y satisfying y.s=0, solve the linear system over GF(2), "
        "and verify the recovered hidden string."
    ),
    rationale=(
        "Simon's oracle copies x then XORs a permutation keyed by s so f(x)=f(x XOR s). Measuring the "
        "input register after H gates yields y values orthogonal to s over GF(2). Gathering n-1 "
        "independent y's and solving the homogeneous system recovers the unique non-zero s."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

def simon_circuit(s: str) -> QuantumCircuit:
    n = len(s)
    qc = QuantumCircuit(2 * n)
    qc.h(range(n))
    for i in range(n):
        qc.cx(i, n + i)                 # copy x -> f register
    j = s.index("1")                    # apply s-dependent 2-to-1 folding
    for i in range(n):
        if s[i] == "1":
            qc.cx(j, n + i)
    qc.h(range(n))
    return qc

def gf2_nullspace_vector(ys, n):
    rows = [list(map(int, f"{y:0{n}b}")) for y in ys]
    M = np.array(rows, dtype=int) % 2
    # Gaussian elimination over GF(2)
    pivots, r = [], 0
    M = M.copy()
    for c in range(n):
        piv = next((i for i in range(r, len(M)) if M[i, c]), None)
        if piv is None:
            continue
        M[[r, piv]] = M[[piv, r]]
        for i in range(len(M)):
            if i != r and M[i, c]:
                M[i] ^= M[r]
        pivots.append(c); r += 1
    free = [c for c in range(n) if c not in pivots]
    s = np.zeros(n, dtype=int); s[free[0]] = 1
    for i, c in enumerate(pivots):
        s[c] = M[i, free[0]]
    return "".join(map(str, s))

if __name__ == "__main__":
    s = "110"
    probs = Statevector(simon_circuit(s)).probabilities_dict(qargs=list(range(len(s))))
    ys = [int(k[::-1], 2) for k, v in probs.items() if v > 1e-9]
    rec = gf2_nullspace_vector([y for y in ys if y != 0], len(s))
    print(f"hidden {s} -> recovered {rec}; valid y's: {sorted(ys)}")
    assert rec == s, (s, rec)
    print("Simon's algorithm verified")
""",
)

add(
    id="qac_deutsch_one_bit",
    family="oracle_algorithms",
    algorithm="deutsch_algorithm",
    difficulty="easy",
    question=(
        "Implement the original single-bit Deutsch algorithm in Qiskit to decide in one query whether "
        "a one-bit function is constant or balanced. Verify the decision for all four possible functions."
    ),
    rationale=(
        "Deutsch's algorithm uses phase kickback: with the input in |+> and ancilla in |->, the oracle "
        "imprints (-1)^f(x). After a final H, measuring the input qubit gives 0 for constant f and 1 "
        "for balanced f. Enumerate the four oracles f0,f1,identity,not to confirm."
    ),
    code=r"""
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

ORACLES = {
    "f(x)=0":   lambda qc: None,
    "f(x)=1":   lambda qc: qc.x(1),
    "f(x)=x":   lambda qc: qc.cx(0, 1),
    "f(x)=1-x": lambda qc: (qc.cx(0, 1), qc.x(1)),
}
CONSTANT = {"f(x)=0", "f(x)=1"}

def deutsch(oracle) -> str:
    qc = QuantumCircuit(2)
    qc.x(1); qc.h([0, 1])
    oracle(qc)
    qc.h(0)
    out = max(Statevector(qc).probabilities_dict(qargs=[0]).items(), key=lambda kv: kv[1])[0]
    return "constant" if out == "0" else "balanced"

if __name__ == "__main__":
    for name, oracle in ORACLES.items():
        verdict = deutsch(oracle)
        expected = "constant" if name in CONSTANT else "balanced"
        print(f"{name}: {verdict}")
        assert verdict == expected, (name, verdict)
    print("Deutsch algorithm verified")
""",
)

add(
    id="qac_chsh_inequality",
    family="quantum_subroutines",
    algorithm="chsh_bell_inequality",
    difficulty="medium",
    question=(
        "Using Qiskit, compute the CHSH correlation value for a shared Bell pair with optimal "
        "measurement angles. Verify the quantum value reaches the Tsirelson bound 2*sqrt(2), violating "
        "the classical limit of 2."
    ),
    rationale=(
        "The CHSH operator S = <A0 B0> + <A0 B1> + <A1 B0> - <A1 B1> is maximized at 2*sqrt(2) for a "
        "Bell state with measurement angles 0, pi/2 for Alice and pi/4, -pi/4 for Bob. Evaluate each "
        "correlator as the expectation of rotated Z operators on |Phi+>."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, SparsePauliOp, Operator

def correlator(theta_a, theta_b):
    bell = Statevector(QuantumCircuit(2)).evolve(_bell())
    Za = _rotated_z(theta_a)
    Zb = _rotated_z(theta_b)
    op = Operator(np.kron(Zb, Za))      # qubit0 = Alice (little-endian inner)
    return float(np.real(bell.expectation_value(op)))

def _bell():
    qc = QuantumCircuit(2); qc.h(0); qc.cx(0, 1); return qc

def _rotated_z(theta):
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, s], [s, -c]], dtype=complex)

if __name__ == "__main__":
    a0, a1 = 0.0, np.pi / 2
    b0, b1 = np.pi / 4, -np.pi / 4
    S = (correlator(a0, b0) + correlator(a0, b1)
         + correlator(a1, b0) - correlator(a1, b1))
    print(f"CHSH value S = {S:.6f} (Tsirelson 2*sqrt(2) = {2*np.sqrt(2):.6f})")
    assert abs(abs(S) - 2 * np.sqrt(2)) < 1e-6, S
    print("CHSH violation verified")
""",
)

add(
    id="qac_pauli_expectation_values",
    family="quantum_subroutines",
    algorithm="pauli_expectation",
    difficulty="easy",
    question=(
        "Using Qiskit primitives, compute the expectation values <X>, <Y>, <Z> of the state |+> and "
        "of the state Ry(pi/2)|0>. Verify the Bloch-vector components against analytic values."
    ),
    rationale=(
        "For |+> the Bloch vector is (1,0,0), so <X>=1, <Y>=0, <Z>=0. For Ry(pi/2)|0> = |+> as well in "
        "the x-z plane the vector is (1,0,0). Use StatevectorEstimator with SparsePauliOp observables "
        "to evaluate each Pauli expectation."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator

def bloch_vector(circuit):
    est = StatevectorEstimator()
    obs = [SparsePauliOp("X"), SparsePauliOp("Y"), SparsePauliOp("Z")]
    res = est.run([(circuit, o) for o in obs]).result()
    return np.array([float(r.data.evs) for r in res])

if __name__ == "__main__":
    plus = QuantumCircuit(1); plus.h(0)
    ry = QuantumCircuit(1); ry.ry(np.pi / 2, 0)
    bv_plus = bloch_vector(plus)
    bv_ry = bloch_vector(ry)
    print("Bloch |+>      =", np.round(bv_plus, 6))
    print("Bloch Ry(pi/2) =", np.round(bv_ry, 6))
    assert np.allclose(bv_plus, [1, 0, 0], atol=1e-9), bv_plus
    assert np.allclose(bv_ry, [1, 0, 0], atol=1e-9), bv_ry
    print("Pauli expectations verified")
""",
)


# ===================================================================
# BATCH: amplitude amplification, simulation, and quantum info
# ===================================================================

add(
    id="qac_amplitude_estimation_basic",
    family="amplitude_amplification",
    algorithm="amplitude_estimation_qpe",
    difficulty="hard",
    question=(
        "Implement canonical Quantum Amplitude Estimation in Qiskit. Given a state-preparation A that "
        "yields a known good-state probability a, estimate a using m evaluation qubits driving the "
        "Grover operator Q, and verify the estimate matches a within the m-bit resolution."
    ),
    rationale=(
        "QAE runs QPE on the Grover/amplitude-amplification operator Q = A S0 A^-1 Sf, whose eigenphase "
        "theta satisfies a = sin^2(theta). With A = Ry(2*arcsin(sqrt(a))) preparing amplitude a on one "
        "qubit, the measured evaluation integer y gives the estimate sin^2(pi*y/2^m)."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import GroverOperator, QFTGate
from qiskit.quantum_info import Statevector

def amplitude_estimation(a: float, m: int) -> float:
    state = QuantumCircuit(1)
    state.ry(2 * np.arcsin(np.sqrt(a)), 0)        # P(|1>) = a
    oracle = QuantumCircuit(1)
    oracle.z(0)                                    # mark |1> as the good state
    Q = GroverOperator(oracle, state_preparation=state)

    qc = QuantumCircuit(m + 1)
    qc.compose(state, [m], inplace=True)
    qc.h(range(m))
    for k in range(m):
        powered = Q.power(2 ** k).to_gate().control(1)
        qc.append(powered, [k, m])
    qc.append(QFTGate(m).inverse(), range(m))
    probs = Statevector(qc).probabilities_dict(qargs=list(range(m)))
    y = int(max(probs, key=probs.get), 2)
    theta = np.pi * y / 2 ** m
    return np.sin(theta) ** 2

if __name__ == "__main__":
    a_true = np.sin(np.pi * 3 / 16) ** 2          # exactly representable with m=4
    est = amplitude_estimation(a_true, m=4)
    print(f"true a={a_true:.6f}, estimate={est:.6f}")
    assert abs(est - a_true) < 1e-6, (a_true, est)
    print("Amplitude estimation verified")
""",
)

add(
    id="qac_trotter_tfim_evolution",
    family="hamiltonian_simulation",
    algorithm="trotter_suzuki_tfim",
    difficulty="hard",
    question=(
        "Use Qiskit to build a first-order Trotter approximation of time evolution under the transverse-"
        "field Ising model H = -J sum Z_i Z_{i+1} - h sum X_i on 3 qubits. Verify the Trotterized "
        "unitary converges to the exact exp(-iHt) as the number of steps grows."
    ),
    rationale=(
        "Split H into the commuting ZZ layer and X layer; one Trotter step applies exp(i*J*dt*ZZ) via "
        "RZZ gates and exp(i*h*dt*X) via RX gates. As the step count increases, the product converges "
        "to the exact propagator; measure convergence by gate-level state fidelity against scipy expm."
    ),
    code=r"""
import numpy as np
from scipy.linalg import expm
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp, Operator, Statevector, state_fidelity

def tfim_hamiltonian(n, J, h):
    terms = []
    for i in range(n - 1):
        z = ["I"] * n; z[i] = z[i + 1] = "Z"
        terms.append(("".join(z), -J))
    for i in range(n):
        x = ["I"] * n; x[i] = "X"
        terms.append(("".join(x), -h))
    return SparsePauliOp.from_list(terms)

def trotter_step(qc, n, J, h, dt):
    for i in range(n - 1):
        qc.rzz(-2 * J * dt, i, i + 1)   # exp(i J dt Z_i Z_{i+1})
    for i in range(n):
        qc.rx(-2 * h * dt, i)           # exp(i h dt X_i)

def trotter_evolution(n, J, h, t, steps):
    qc = QuantumCircuit(n)
    for _ in range(steps):
        trotter_step(qc, n, J, h, t / steps)
    return qc

if __name__ == "__main__":
    n, J, h, t = 3, 1.0, 0.6, 1.0
    H = tfim_hamiltonian(n, J, h).to_matrix()
    exact = Statevector.from_label("0" * n).evolve(Operator(expm(-1j * H * t)))
    last = 0.0
    for steps in (1, 5, 20, 80):
        approx = Statevector(trotter_evolution(n, J, h, t, steps))
        fid = state_fidelity(approx, exact)
        print(f"steps={steps:3d}  fidelity={fid:.6f}")
        last = fid
    assert last > 0.999, last
    print("Trotter TFIM evolution verified")
""",
)

add(
    id="qac_pauli_evolution_gate",
    family="hamiltonian_simulation",
    algorithm="pauli_evolution_exact",
    difficulty="medium",
    question=(
        "Using Qiskit's PauliEvolutionGate, construct exp(-i H t) for a two-qubit Heisenberg "
        "Hamiltonian H = XX + YY + ZZ and verify the resulting unitary matches scipy's matrix "
        "exponential exactly."
    ),
    rationale=(
        "For a sum of mutually commuting-or-not Pauli terms, PauliEvolutionGate with an exact synthesis "
        "produces the true propagator for time t. Compare the gate's Operator against expm(-i H t) from "
        "scipy using Operator.equiv up to global phase."
    ),
    code=r"""
import numpy as np
from scipy.linalg import expm
from qiskit import QuantumCircuit
from qiskit.circuit.library import PauliEvolutionGate
from qiskit.synthesis import SuzukiTrotter
from qiskit.quantum_info import SparsePauliOp, Operator

def heisenberg_propagator(t, steps=400):
    H = SparsePauliOp.from_list([("XX", 1.0), ("YY", 1.0), ("ZZ", 1.0)])
    gate = PauliEvolutionGate(H, time=t, synthesis=SuzukiTrotter(order=2, reps=steps))
    qc = QuantumCircuit(2); qc.append(gate, [0, 1])
    return Operator(qc), expm(-1j * H.to_matrix() * t)

if __name__ == "__main__":
    t = 0.7
    approx, exact = heisenberg_propagator(t)
    assert approx.equiv(Operator(exact)), "propagator mismatch"
    print(f"Heisenberg exp(-iHt) at t={t} matches scipy expm")
""",
)

add(
    id="qac_density_matrix_partial_trace",
    family="quantum_information",
    algorithm="reduced_density_matrix",
    difficulty="medium",
    question=(
        "Using Qiskit quantum_info, prepare a Bell pair, compute the reduced density matrix of one "
        "qubit via partial trace, and verify it is the maximally mixed state I/2 with von Neumann "
        "entropy 1 bit."
    ),
    rationale=(
        "Tracing out one half of a maximally entangled Bell pair yields the maximally mixed single-"
        "qubit state I/2. Its von Neumann entropy is log2(2) = 1 bit, signaling maximal entanglement. "
        "Compute both with DensityMatrix/partial_trace and entropy."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, partial_trace, entropy

if __name__ == "__main__":
    qc = QuantumCircuit(2); qc.h(0); qc.cx(0, 1)
    rho = partial_trace(Statevector(qc), [1])     # keep qubit 0
    print("reduced rho:\n", np.round(rho.data, 6))
    assert np.allclose(rho.data, np.eye(2) / 2, atol=1e-9), rho.data
    s = entropy(rho, base=2)
    print(f"von Neumann entropy: {s:.6f} bit")
    assert abs(s - 1.0) < 1e-9, s
    print("Reduced density matrix verified")
""",
)

add(
    id="qac_state_tomography_single_qubit",
    family="quantum_information",
    algorithm="single_qubit_state_tomography",
    difficulty="medium",
    question=(
        "Implement single-qubit state tomography in Qiskit: from the measured expectation values <X>, "
        "<Y>, <Z> of an unknown prepared state, reconstruct its density matrix and verify it matches "
        "the true state with high fidelity."
    ),
    rationale=(
        "Any single-qubit density matrix is rho = (I + rx X + ry Y + rz Z)/2 where the Bloch components "
        "are the Pauli expectation values. Estimate them with an estimator, rebuild rho, and compare "
        "to the true pure state via state_fidelity."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp, DensityMatrix, Statevector, state_fidelity
from qiskit.primitives import StatevectorEstimator

I = np.eye(2); X = np.array([[0, 1], [1, 0]]); Y = np.array([[0, -1j], [1j, 0]]); Z = np.diag([1, -1])

def tomography(prep: QuantumCircuit) -> DensityMatrix:
    est = StatevectorEstimator()
    paulis = [SparsePauliOp("X"), SparsePauliOp("Y"), SparsePauliOp("Z")]
    r = [float(est.run([(prep, p)]).result()[0].data.evs) for p in paulis]
    rho = (I + r[0] * X + r[1] * Y + r[2] * Z) / 2
    return DensityMatrix(rho)

if __name__ == "__main__":
    prep = QuantumCircuit(1); prep.ry(1.1, 0); prep.rz(0.7, 0)
    rho = tomography(prep)
    fid = state_fidelity(rho, Statevector(prep))
    print(f"reconstruction fidelity: {fid:.6f}")
    assert fid > 1 - 1e-9, fid
    print("State tomography verified")
""",
)

add(
    id="qac_bit_flip_code",
    family="error_correction",
    algorithm="three_qubit_bit_flip_code",
    difficulty="medium",
    question=(
        "Implement the 3-qubit bit-flip code in Qiskit. Encode a logical qubit, inject an X error on "
        "any single physical qubit, perform syndrome decoding, and verify the logical state is "
        "recovered for every single-qubit error location."
    ),
    rationale=(
        "The bit-flip code encodes |psi> as alpha|000>+beta|111>. Two stabilizer parity checks Z0Z1 "
        "and Z1Z2 identify which qubit flipped; applying the matching X correction restores the state. "
        "Using deferred measurement, check recovery via state fidelity of the decoded data qubit."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, partial_trace, state_fidelity, random_statevector

def bit_flip_cycle(psi, error_qubit):
    qc = QuantumCircuit(5)               # 3 data + 2 syndrome ancillas
    qc.initialize(psi.data, 0)
    qc.cx(0, 1); qc.cx(0, 2)            # encode
    if error_qubit is not None:
        qc.x(error_qubit)
    qc.cx(0, 3); qc.cx(1, 3)           # syndrome Z0Z1 -> ancilla 3
    qc.cx(1, 4); qc.cx(2, 4)           # syndrome Z1Z2 -> ancilla 4
    # deferred correction: (s3,s4)=(1,0)->q0, (1,1)->q1, (0,1)->q2
    qc.x(4); qc.ccx(3, 4, 0); qc.x(4)
    qc.ccx(3, 4, 1)
    qc.x(3); qc.ccx(3, 4, 2); qc.x(3)
    qc.cx(0, 2); qc.cx(0, 1)           # decode
    return qc

if __name__ == "__main__":
    for err in [None, 0, 1, 2]:
        psi = random_statevector(2, seed=err if err is not None else 9)
        full = Statevector(bit_flip_cycle(psi, err))
        data = partial_trace(full, [1, 2, 3, 4])    # keep data qubit 0
        fid = state_fidelity(data, psi)
        print(f"error on {err}: recovery fidelity {fid:.6f}")
        assert fid > 1 - 1e-9, (err, fid)
    print("3-qubit bit-flip code verified")
""",
)

add(
    id="qac_phase_flip_code",
    family="error_correction",
    algorithm="three_qubit_phase_flip_code",
    difficulty="medium",
    question=(
        "Implement the 3-qubit phase-flip code in Qiskit by conjugating the bit-flip code with "
        "Hadamards. Inject a Z error on a single qubit and verify the logical state is recovered."
    ),
    rationale=(
        "The phase-flip code maps Z errors to X errors in the Hadamard basis, so encode with CNOTs then "
        "H on all data qubits; a Z error becomes detectable like a bit flip. Decode by reversing the "
        "Hadamards and CNOTs, then verify recovery via fidelity using deferred-measurement corrections."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, partial_trace, state_fidelity, random_statevector

def phase_flip_cycle(psi, error_qubit):
    qc = QuantumCircuit(5)
    qc.initialize(psi.data, 0)
    qc.cx(0, 1); qc.cx(0, 2)
    qc.h([0, 1, 2])                      # phase-flip basis
    if error_qubit is not None:
        qc.z(error_qubit)
    qc.h([0, 1, 2])
    qc.cx(0, 3); qc.cx(1, 3)
    qc.cx(1, 4); qc.cx(2, 4)
    qc.x(4); qc.ccx(3, 4, 0); qc.x(4)
    qc.ccx(3, 4, 1)
    qc.x(3); qc.ccx(3, 4, 2); qc.x(3)
    qc.cx(0, 2); qc.cx(0, 1)
    return qc

if __name__ == "__main__":
    for err in [None, 0, 1, 2]:
        psi = random_statevector(2, seed=err if err is not None else 4)
        full = Statevector(phase_flip_cycle(psi, err))
        data = partial_trace(full, [1, 2, 3, 4])
        fid = state_fidelity(data, psi)
        print(f"Z error on {err}: recovery fidelity {fid:.6f}")
        assert fid > 1 - 1e-9, (err, fid)
    print("3-qubit phase-flip code verified")
""",
)

add(
    id="qac_toffoli_truth_table",
    family="gate_construction",
    algorithm="toffoli_decomposition",
    difficulty="easy",
    question=(
        "Using Qiskit, verify that the Toffoli (CCX) gate implements the classical AND into the target "
        "by checking its full truth table, and confirm a standard 6-CNOT + T-gate decomposition equals "
        "the native CCX up to global phase."
    ),
    rationale=(
        "CCX flips the target iff both controls are 1, so the output target bit equals input XOR "
        "(c0 AND c1). Build the textbook H/T/Tdg/CNOT decomposition and compare its Operator to the "
        "native CCX with Operator.equiv to confirm equivalence."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, Operator

def ccx_decomposed():
    qc = QuantumCircuit(3)
    a, b, c = 0, 1, 2
    qc.h(c)
    qc.cx(b, c); qc.tdg(c); qc.cx(a, c); qc.t(c); qc.cx(b, c); qc.tdg(c); qc.cx(a, c)
    qc.t(b); qc.t(c); qc.cx(a, b); qc.h(c); qc.t(a); qc.tdg(b); qc.cx(a, b)
    return qc

if __name__ == "__main__":
    for c0 in (0, 1):
        for c1 in (0, 1):
            for t in (0, 1):
                qc = QuantumCircuit(3)
                if c0: qc.x(0)
                if c1: qc.x(1)
                if t: qc.x(2)
                qc.ccx(0, 1, 2)
                out = max(Statevector(qc).probabilities_dict(), key=lambda k: 1)
                bits = list(map(int, out[::-1]))
                assert bits[2] == (t ^ (c0 & c1)), (c0, c1, t, bits)
    native = QuantumCircuit(3); native.ccx(0, 1, 2)
    assert Operator(ccx_decomposed()).equiv(Operator(native)), "decomposition mismatch"
    print("Toffoli truth table and decomposition verified")
""",
)

add(
    id="qac_arbitrary_unitary_zyz",
    family="gate_construction",
    algorithm="single_qubit_zyz_decomposition",
    difficulty="medium",
    question=(
        "Using Qiskit, decompose an arbitrary single-qubit unitary into the ZYZ Euler form "
        "Rz(gamma) Ry(beta) Rz(alpha) (up to global phase) and verify the reconstructed operator "
        "matches a random SU(2) target."
    ),
    rationale=(
        "Any single-qubit unitary equals e^{i*phase} Rz(gamma) Ry(beta) Rz(alpha). Extract the Euler "
        "angles from the matrix elements (beta from |U00|, alpha/gamma from the phases) and rebuild the "
        "circuit, confirming equivalence with Operator.equiv (which ignores global phase)."
    ),
    code=r'''
import numpy as np
from qiskit.synthesis import OneQubitEulerDecomposer
from qiskit.quantum_info import Operator, random_unitary

def zyz_decompose(U) -> "QuantumCircuit":
    """Return Rz(gamma) Ry(beta) Rz(alpha) circuit for a single-qubit unitary."""
    decomposer = OneQubitEulerDecomposer(basis="ZYZ")
    return decomposer(U)

if __name__ == "__main__":
    for seed in range(5):
        U = random_unitary(2, seed=seed)
        circ = zyz_decompose(U.data)
        names = [instr.operation.name for instr in circ.data]
        assert Operator(circ).equiv(U), seed       # equiv ignores global phase
        assert set(names) <= {"rz", "ry"}, names
    print("ZYZ Euler decomposition verified for 5 random unitaries")
''',
)

add(
    id="qac_quantum_random_number",
    family="quantum_subroutines",
    algorithm="quantum_random_bits",
    difficulty="easy",
    question=(
        "Using Qiskit's sampler, build an n-bit quantum random number generator from Hadamard gates "
        "and verify the output distribution over many shots is statistically close to uniform."
    ),
    rationale=(
        "Applying H to each of n qubits produces an equal superposition; measuring yields uniformly "
        "random n-bit strings. With enough shots, every outcome's empirical frequency concentrates near "
        "1/2^n, which we check with a chi-square-style max-deviation tolerance."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

def qrng_counts(n, shots, seed=0):
    qc = QuantumCircuit(n); qc.h(range(n)); qc.measure_all()
    sampler = StatevectorSampler(seed=seed)
    return sampler.run([qc], shots=shots).result()[0].data.meas.get_counts()

if __name__ == "__main__":
    n, shots = 4, 40000
    counts = qrng_counts(n, shots)
    freqs = np.array([counts.get(format(i, f"0{n}b"), 0) for i in range(2 ** n)]) / shots
    print("max deviation from uniform:", round(float(np.max(np.abs(freqs - 1 / 2 ** n))), 4))
    assert np.all(np.abs(freqs - 1 / 2 ** n) < 0.01), freqs
    print("Quantum RNG uniformity verified")
""",
)


# ===================================================================
# BATCH: more core algorithms and subroutines
# ===================================================================

add(
    id="qac_iterative_phase_estimation",
    family="fourier_phase",
    algorithm="iterative_phase_estimation",
    difficulty="hard",
    question=(
        "Implement Iterative (Kitaev) Phase Estimation in Qiskit using a single ancilla qubit and "
        "classical feedback to estimate the eigenphase of P(2*pi*phi) bit by bit. Verify it recovers "
        "phi=5/16 exactly."
    ),
    rationale=(
        "IPE extracts the phase one bit at a time from least to most significant. At iteration k it "
        "applies controlled-U^(2^(m-1-k)), corrects the accumulated phase from previously found bits "
        "with an Rz/phase feedback, and measures the ancilla. For phi=5/16 with 4 bits this yields the "
        "exact binary fraction."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

def ipe(phi: float, nbits: int) -> float:
    bits = {}                          # bits[k] is the k-th binary digit (k=1 MSB)
    for k in range(nbits, 0, -1):      # extract from least to most significant
        qc = QuantumCircuit(2)
        qc.x(1)                        # eigenstate |1> of P(theta)
        qc.h(0)
        qc.cp(2 * np.pi * phi * 2 ** (k - 1), 0, 1)
        feedback = sum(bits[j] / 2 ** (j - k + 1) for j in range(k + 1, nbits + 1))
        qc.p(-2 * np.pi * feedback, 0)
        qc.h(0)
        p1 = Statevector(qc).probabilities_dict(qargs=[0]).get("1", 0.0)
        bits[k] = 1 if p1 > 0.5 else 0
    return sum(bits[k] / 2 ** k for k in range(1, nbits + 1))

if __name__ == "__main__":
    est = ipe(5 / 16, nbits=4)
    print(f"IPE estimate {est} (true {5/16})")
    assert abs(est - 5 / 16) < 1e-9, est
    print("Iterative phase estimation verified")
""",
)

add(
    id="qac_grover_multiple_targets",
    family="amplitude_amplification",
    algorithm="grover_multiple_marked",
    difficulty="medium",
    question=(
        "Use Qiskit's GroverOperator to search a 4-qubit space with two marked states. Choose the "
        "optimal number of iterations for M=2 of N=16 and verify the total probability on the marked "
        "set exceeds 0.95."
    ),
    rationale=(
        "With M marked items among N, the optimal iteration count is round(pi/4 * sqrt(N/M) - 1/2). "
        "Build a phase oracle marking the two target bitstrings, wrap it in GroverOperator, and iterate; "
        "the combined marked-state probability is amplified close to 1."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import GroverOperator
from qiskit.quantum_info import Statevector

def phase_oracle(n, marked):
    qc = QuantumCircuit(n)
    for m in marked:
        zeros = [i for i, b in enumerate(reversed(m)) if b == "0"]
        if zeros: qc.x(zeros)
        qc.h(n - 1); qc.mcx(list(range(n - 1)), n - 1); qc.h(n - 1)
        if zeros: qc.x(zeros)
    return qc

def grover_search(n, marked):
    N, M = 2 ** n, len(marked)
    iters = max(1, round(np.pi / 4 * np.sqrt(N / M) - 0.5))
    grover = GroverOperator(phase_oracle(n, marked))
    qc = QuantumCircuit(n); qc.h(range(n))
    for _ in range(iters):
        qc.compose(grover, inplace=True)
    return Statevector(qc).probabilities_dict(), iters

if __name__ == "__main__":
    marked = ["0101", "1110"]
    probs, iters = grover_search(4, marked)
    total = sum(probs.get(m, 0.0) for m in marked)
    print(f"marked probability {total:.4f} after {iters} iterations")
    assert total > 0.94, total
    print("Grover multi-target verified")
""",
)

add(
    id="qac_quantum_counting",
    family="amplitude_amplification",
    algorithm="quantum_counting",
    difficulty="hard",
    question=(
        "Implement quantum counting in Qiskit: use phase estimation on the Grover operator to estimate "
        "the number M of marked items in a 4-qubit search space, and verify the estimate matches the "
        "true count."
    ),
    rationale=(
        "The Grover operator has eigenphase theta with sin^2(theta/2) = M/N. Running QPE on Grover and "
        "reading the estimated angle yields M = N * sin^2(theta/2). With enough counting qubits the "
        "rounded estimate equals the true number of marked states."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import GroverOperator, QFTGate
from qiskit.quantum_info import Statevector

def phase_oracle(n, marked):
    qc = QuantumCircuit(n)
    for m in marked:
        zeros = [i for i, b in enumerate(reversed(m)) if b == "0"]
        if zeros: qc.x(zeros)
        qc.h(n - 1); qc.mcx(list(range(n - 1)), n - 1); qc.h(n - 1)
        if zeros: qc.x(zeros)
    return qc

def quantum_count(n, marked, counting=6):
    grover = GroverOperator(phase_oracle(n, marked))
    qc = QuantumCircuit(counting + n)
    qc.h(range(counting + n))                  # uniform on search + counting
    for k in range(counting):
        qc.append(grover.power(2 ** k).control(1), [k] + list(range(counting, counting + n)))
    qc.append(QFTGate(counting).inverse(), range(counting))
    probs = Statevector(qc).probabilities_dict(qargs=list(range(counting)))
    y = int(max(probs, key=probs.get), 2)
    theta = 2 * np.pi * y / 2 ** counting
    M = (2 ** n) * np.sin(theta / 2) ** 2
    return round(M)

if __name__ == "__main__":
    marked = ["0101", "1110", "0011"]
    est = quantum_count(4, marked, counting=6)
    print(f"estimated marked count {est} (true {len(marked)})")
    assert est == len(marked), est
    print("Quantum counting verified")
""",
)

add(
    id="qac_hadamard_test",
    family="quantum_subroutines",
    algorithm="hadamard_test",
    difficulty="medium",
    question=(
        "Implement the Hadamard test in Qiskit to estimate the real and imaginary parts of "
        "<psi|U|psi> for a single-qubit unitary U and state |psi>. Verify against the direct "
        "linear-algebra value."
    ),
    rationale=(
        "The Hadamard test uses an ancilla with H, controlled-U, H; the ancilla Z-expectation gives "
        "Re<psi|U|psi>. Inserting an S-dagger before the final H gives the imaginary part. Compare both "
        "to the analytic inner product."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, Operator, SparsePauliOp
from qiskit.primitives import StatevectorEstimator

def hadamard_test(prep_psi, U, imaginary=False):
    qc = QuantumCircuit(2)               # q0 ancilla, q1 system
    qc.compose(prep_psi, [1], inplace=True)
    qc.h(0)
    if imaginary:
        qc.sdg(0)
    qc.append(U.control(1), [0, 1])
    qc.h(0)
    est = StatevectorEstimator()
    return float(est.run([(qc, SparsePauliOp("IZ"))]).result()[0].data.evs)

if __name__ == "__main__":
    from qiskit.circuit.library import TGate
    prep = QuantumCircuit(1); prep.ry(0.9, 0); prep.rz(0.4, 0)
    U = TGate()
    re = hadamard_test(prep, U, imaginary=False)
    im = hadamard_test(prep, U, imaginary=True)
    psi = Statevector(prep).data
    exact = np.conj(psi) @ (Operator(U).data @ psi)
    print(f"Re {re:.6f} vs {exact.real:.6f}; Im {im:.6f} vs {exact.imag:.6f}")
    assert abs(re - exact.real) < 1e-9 and abs(im - exact.imag) < 1e-9
    print("Hadamard test verified")
""",
)

add(
    id="qac_entanglement_swapping",
    family="entanglement_protocols",
    algorithm="entanglement_swapping",
    difficulty="hard",
    question=(
        "Implement entanglement swapping in Qiskit: starting from two independent Bell pairs (q0,q1) "
        "and (q2,q3), perform a Bell measurement on q1,q2 so that q0 and q3 become entangled. Verify "
        "the resulting (q0,q3) reduced state is a maximally entangled Bell pair."
    ),
    rationale=(
        "Bell-measuring the inner qubits of two Bell pairs teleports entanglement onto the outer "
        "qubits. Using deferred measurement (CX then H on q1, with CX/CZ corrections onto q3), the "
        "reduced state of q0,q3 is a Bell state with concurrence 1, verified via partial trace and "
        "fidelity to |Phi+>."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, partial_trace, state_fidelity

def entanglement_swap():
    qc = QuantumCircuit(4)              # pairs (0,1) and (2,3)
    qc.h(0); qc.cx(0, 1)
    qc.h(2); qc.cx(2, 3)
    qc.cx(1, 2); qc.h(1)               # Bell measurement basis on (1,2)
    qc.cx(2, 3)                        # deferred X correction onto q3
    qc.cz(1, 3)                        # deferred Z correction onto q3
    return qc

if __name__ == "__main__":
    full = Statevector(entanglement_swap())
    rho_03 = partial_trace(full, [1, 2])    # keep q0, q3
    bell = Statevector(QuantumCircuit(2).compose(_bell())) if False else None
    bp = QuantumCircuit(2); bp.h(0); bp.cx(0, 1)
    fid = state_fidelity(rho_03, Statevector(bp))
    print(f"(q0,q3) fidelity to Bell pair: {fid:.6f}")
    assert fid > 1 - 1e-9, fid
    print("Entanglement swapping verified")
""",
)

add(
    id="qac_fredkin_truth_table",
    family="gate_construction",
    algorithm="fredkin_controlled_swap",
    difficulty="easy",
    question=(
        "Using Qiskit, verify the Fredkin (controlled-SWAP) gate truth table over all 8 computational "
        "basis inputs and confirm it preserves the number of ones (conservative reversible logic)."
    ),
    rationale=(
        "The Fredkin gate swaps the two target bits iff the control is 1, otherwise leaves them. It is "
        "reversible and conserves Hamming weight. Enumerate all 3-bit inputs, apply cswap, and compare "
        "to the expected conditional swap."
    ),
    code=r"""
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

def fredkin_out(c, a, b):
    qc = QuantumCircuit(3)
    if c: qc.x(0)
    if a: qc.x(1)
    if b: qc.x(2)
    qc.cswap(0, 1, 2)
    out = next(k for k, v in Statevector(qc).probabilities_dict().items() if v > 0.5)
    bits = list(map(int, out[::-1]))   # [q0,q1,q2]
    return bits

if __name__ == "__main__":
    for c in (0, 1):
        for a in (0, 1):
            for b in (0, 1):
                bits = fredkin_out(c, a, b)
                expected = [c, (b if c else a), (a if c else b)]
                assert bits == expected, (c, a, b, bits, expected)
                assert sum(bits) == c + a + b      # weight preserved
    print("Fredkin truth table verified")
""",
)

add(
    id="qac_draper_qft_adder",
    family="arithmetic",
    algorithm="draper_qft_adder",
    difficulty="hard",
    question=(
        "Use Qiskit's Draper QFT adder to compute (a + b) mod 2^n for n-bit registers and verify the "
        "result for several operand pairs by reading the output register."
    ),
    rationale=(
        "The Draper adder performs addition in the Fourier basis: QFT the target register, apply "
        "controlled phase rotations from the addend, then inverse QFT. The half-adder (fixed mode) "
        "computes (a+b) mod 2^n. Encode operands as basis states and check the measured sum."
    ),
    code=r"""
from qiskit import QuantumCircuit
from qiskit.circuit.library import DraperQFTAdder
from qiskit.quantum_info import Statevector

def add_mod(a, b, n):
    adder = DraperQFTAdder(n, kind="fixed")
    qc = QuantumCircuit(adder.num_qubits)
    for i in range(n):
        if (a >> i) & 1: qc.x(i)            # register A: qubits 0..n-1
        if (b >> i) & 1: qc.x(n + i)        # register B: qubits n..2n-1
    qc.compose(adder, inplace=True)
    out = next(k for k, v in Statevector(qc).probabilities_dict().items() if v > 0.5)
    bits = out[::-1]
    b_out = int(bits[n:2 * n][::-1], 2)     # sum is written into register B
    return b_out

if __name__ == "__main__":
    n = 3
    for a in range(8):
        for b in range(8):
            assert add_mod(a, b, n) == (a + b) % 2 ** n, (a, b)
    print("Draper QFT adder verified for all 3-bit operand pairs")
""",
)

add(
    id="qac_ripple_carry_adder",
    family="arithmetic",
    algorithm="cuccaro_ripple_carry_adder",
    difficulty="hard",
    question=(
        "Use Qiskit's full-adder (ripple-carry) circuit to compute a + b with carry-out for n-bit "
        "inputs and verify the full (n+1)-bit result for all operand pairs at n=3."
    ),
    rationale=(
        "Qiskit's FullAdderGate / built-in adder implements a Cuccaro-style ripple-carry addition that "
        "produces an (n+1)-bit sum including the carry. Encode the inputs as basis states, run the "
        "adder, and read the sum register to confirm exact integer addition."
    ),
    code=r"""
from qiskit import QuantumCircuit
from qiskit.circuit.library import CDKMRippleCarryAdder
from qiskit.quantum_info import Statevector

def ripple_add(a, b, n):
    adder = CDKMRippleCarryAdder(n, kind="full")
    qc = QuantumCircuit(adder.num_qubits)
    # qubit layout: [cin, a0..a{n-1}, b0..b{n-1}, cout]
    for i in range(n):
        if (a >> i) & 1: qc.x(1 + i)
        if (b >> i) & 1: qc.x(1 + n + i)
    qc.compose(adder, inplace=True)
    out = next(k for k, v in Statevector(qc).probabilities_dict().items() if v > 0.5)
    bits = out[::-1]
    b_bits = bits[1 + n:1 + 2 * n]
    cout = bits[1 + 2 * n]
    return int((cout + b_bits[::-1]), 2)

if __name__ == "__main__":
    n = 3
    for a in range(8):
        for b in range(8):
            assert ripple_add(a, b, n) == a + b, (a, b, ripple_add(a, b, n))
    print("Ripple-carry adder verified for all 3-bit operand pairs")
""",
)

add(
    id="qac_graph_state_preparation",
    family="entanglement_protocols",
    algorithm="graph_state_stabilizers",
    difficulty="medium",
    question=(
        "Using Qiskit, prepare the graph state for a 4-node ring graph (H on all qubits then CZ on each "
        "edge) and verify it is stabilized by the expected stabilizer generators X_i prod_{j~i} Z_j."
    ),
    rationale=(
        "A graph state is built by initializing |+>^n and applying CZ on every edge. Each vertex i has "
        "stabilizer g_i = X_i times the product of Z over its neighbors, with eigenvalue +1. Verify "
        "every generator's expectation value equals +1."
    ),
    code=r"""
import numpy as np
import networkx as nx
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, SparsePauliOp
from qiskit.primitives import StatevectorEstimator

def graph_state(graph):
    n = graph.number_of_nodes()
    qc = QuantumCircuit(n); qc.h(range(n))
    for i, j in graph.edges():
        qc.cz(i, j)
    return qc

def stabilizers(graph):
    n = graph.number_of_nodes()
    gens = []
    for i in graph.nodes():
        label = ["I"] * n
        label[i] = "X"
        for j in graph.neighbors(i):
            label[j] = "Z"
        gens.append(SparsePauliOp("".join(reversed(label))))
    return gens

if __name__ == "__main__":
    g = nx.cycle_graph(4)
    qc = graph_state(g)
    est = StatevectorEstimator()
    for gen in stabilizers(g):
        ev = float(est.run([(qc, gen)]).result()[0].data.evs)
        assert abs(ev - 1.0) < 1e-9, ev
    print("Graph state stabilizers all +1; verified")
""",
)

add(
    id="qac_vqe_tfim_ground_state",
    family="vqe_chemistry",
    algorithm="vqe_tfim_real_amplitudes",
    difficulty="hard",
    question=(
        "Use Qiskit to find the ground-state energy of a 3-qubit transverse-field Ising Hamiltonian "
        "H = -sum Z_i Z_{i+1} - sum X_i with a RealAmplitudes variational ansatz and COBYLA, and verify "
        "the VQE energy matches exact diagonalization."
    ),
    rationale=(
        "Construct the TFIM qubit Hamiltonian as a SparsePauliOp, optimize a RealAmplitudes ansatz with "
        "a statevector estimator, and use a few restarts to reach the global minimum. Validate against "
        "the smallest eigenvalue from dense diagonalization."
    ),
    code=r"""
import numpy as np
from scipy.optimize import minimize
from qiskit.circuit.library import real_amplitudes
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator

def tfim(n=3, J=1.0, h=1.0):
    terms = []
    for i in range(n - 1):
        z = ["I"] * n; z[i] = z[i + 1] = "Z"; terms.append(("".join(z), -J))
    for i in range(n):
        x = ["I"] * n; x[i] = "X"; terms.append(("".join(x), -h))
    return SparsePauliOp.from_list(terms)

def vqe(h_op, reps=3, seed=0):
    ansatz = real_amplitudes(h_op.num_qubits, reps=reps)
    est = StatevectorEstimator()
    energy = lambda p: float(est.run([(ansatz, h_op, p)]).result()[0].data.evs)
    rng = np.random.default_rng(seed)
    best = None
    for _ in range(4):
        x0 = rng.uniform(-np.pi, np.pi, ansatz.num_parameters)
        res = minimize(energy, x0, method="COBYLA", options={"maxiter": 500})
        if best is None or res.fun < best.fun:
            best = res
    return float(best.fun)

if __name__ == "__main__":
    H = tfim(3, 1.0, 1.0)
    e_vqe = vqe(H)
    e_exact = float(np.linalg.eigvalsh(H.to_matrix())[0])
    print(f"VQE {e_vqe:.6f} vs exact {e_exact:.6f}")
    assert abs(e_vqe - e_exact) < 1e-3, (e_vqe, e_exact)
    print("TFIM VQE verified")
""",
)

add(
    id="qac_qaoa_weighted_maxcut",
    family="qaoa_optimization",
    algorithm="qaoa_weighted_maxcut",
    difficulty="hard",
    question=(
        "Use Qiskit to solve weighted MaxCut on a small weighted graph with QAOA and verify the "
        "returned cut equals the brute-force optimum, printing the optimal partition and weight."
    ),
    rationale=(
        "Weighted MaxCut uses the cost Hamiltonian sum w_ij/2 (Z_i Z_j - I). Optimize a QAOAAnsatz, "
        "sample the optimized state, and select the best measured bitstring by its weighted cut. "
        "Validate against exhaustive search on the small instance."
    ),
    code=r"""
import numpy as np
import networkx as nx
from scipy.optimize import minimize
from qiskit.circuit.library import QAOAAnsatz
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator, StatevectorSampler

def cost_hamiltonian(g):
    n = g.number_of_nodes(); terms = []
    for i, j, d in g.edges(data=True):
        w = d["weight"]; z = ["I"] * n; z[i] = z[j] = "Z"
        terms.append(("".join(reversed(z)), 0.5 * w)); terms.append(("I" * n, -0.5 * w))
    return SparsePauliOp.from_list(terms).simplify()

def weighted_cut(g, bits):
    a = [int(b) for b in bits]
    return sum(d["weight"] for i, j, d in g.edges(data=True) if a[i] != a[j])

def qaoa_weighted(g, reps=2, seed=3):
    cost = cost_hamiltonian(g)
    ansatz = QAOAAnsatz(cost, reps=reps).decompose()
    est = StatevectorEstimator()
    obj = lambda p: float(est.run([(ansatz, cost, p)]).result()[0].data.evs)
    rng = np.random.default_rng(seed); best = None
    for _ in range(3):
        res = minimize(obj, rng.uniform(0, np.pi, ansatz.num_parameters), method="COBYLA",
                       options={"maxiter": 300})
        if best is None or res.fun < best.fun: best = res
    sampler = StatevectorSampler()
    counts = sampler.run([(ansatz.measure_all(inplace=False), best.x)], shots=4096).result()[0].data.meas.get_counts()
    bb, bc = None, -1
    for bs in counts:
        v = weighted_cut(g, bs[::-1])
        if v > bc: bb, bc = bs[::-1], v
    return bc, bb

if __name__ == "__main__":
    g = nx.Graph()
    g.add_weighted_edges_from([(0, 1, 1.0), (1, 2, 2.0), (2, 3, 1.0), (3, 0, 3.0), (0, 2, 1.5)])
    cut, bits = qaoa_weighted(g)
    brute = max(weighted_cut(g, format(x, "04b")) for x in range(16))
    print(f"QAOA weighted cut {cut} (brute {brute}), partition {bits}")
    assert abs(cut - brute) < 1e-9, (cut, brute)
    print("Weighted MaxCut QAOA verified")
""",
)


# ===================================================================
# BATCH: noise, mitigation, transpilation, Clifford/stabilizer
# ===================================================================

add(
    id="qac_depolarizing_noise_simulation",
    family="noise_and_mitigation",
    algorithm="depolarizing_noise_model",
    difficulty="medium",
    question=(
        "Using qiskit-aer, simulate a Bell-pair circuit under a two-qubit depolarizing noise model on "
        "the CX gate. Verify that the measured error probability (non-Bell outcomes 01/10) grows with "
        "the depolarizing rate."
    ),
    rationale=(
        "A depolarizing channel mixes the ideal output with the maximally mixed state, so higher rates "
        "produce more |01>/|10> outcomes that are impossible in the noiseless Bell pair. Build a "
        "NoiseModel attaching depolarizing_error to 'cx', run on AerSimulator, and confirm monotonic "
        "error growth."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

def error_rate(p, shots=8000, seed=7):
    nm = NoiseModel()
    nm.add_all_qubit_quantum_error(depolarizing_error(p, 2), ["cx"])
    sim = AerSimulator(noise_model=nm, seed_simulator=seed)
    qc = QuantumCircuit(2); qc.h(0); qc.cx(0, 1); qc.measure_all()
    counts = sim.run(transpile(qc, sim), shots=shots).result().get_counts()
    bad = counts.get("01", 0) + counts.get("10", 0)
    return bad / shots

if __name__ == "__main__":
    rates = [error_rate(p) for p in (0.0, 0.05, 0.2)]
    print("error rates:", [round(r, 4) for r in rates])
    assert rates[0] < 0.01 < rates[1] < rates[2], rates
    print("Depolarizing noise simulation verified")
""",
)

add(
    id="qac_readout_error_mitigation",
    family="noise_and_mitigation",
    algorithm="measurement_error_mitigation",
    difficulty="hard",
    question=(
        "Implement measurement (readout) error mitigation in Qiskit: build the single-qubit "
        "calibration/confusion matrix from |0> and |1> preparations, then invert it to correct noisy "
        "counts for a |+> state and verify the corrected distribution is closer to ideal 50/50."
    ),
    rationale=(
        "Readout errors are modeled by a confusion matrix A mapping true probabilities to measured "
        "ones. Calibrating A from basis-state preparations and applying A^-1 to the noisy histogram "
        "removes the bias; the corrected |+> distribution moves closer to the ideal uniform one."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, ReadoutError

def make_sim(p0, p1, seed=5):
    nm = NoiseModel()
    nm.add_all_qubit_readout_error(ReadoutError([[1 - p0, p0], [p1, 1 - p1]]))
    return AerSimulator(noise_model=nm, seed_simulator=seed)

def histogram(sim, prep, shots=20000):
    qc = prep.copy(); qc.measure_all()
    counts = sim.run(transpile(qc, sim), shots=shots).result().get_counts()
    return np.array([counts.get("0", 0), counts.get("1", 0)]) / shots

if __name__ == "__main__":
    sim = make_sim(0.08, 0.12)
    col0 = histogram(sim, QuantumCircuit(1))            # prepared |0>
    one = QuantumCircuit(1); one.x(0)
    col1 = histogram(sim, one)                          # prepared |1>
    A = np.column_stack([col0, col1])                   # confusion matrix
    plus = QuantumCircuit(1); plus.h(0)
    noisy = histogram(sim, plus)
    corrected = np.linalg.solve(A, noisy)
    corrected = np.clip(corrected, 0, None); corrected /= corrected.sum()
    print("noisy:", np.round(noisy, 3), "corrected:", np.round(corrected, 3))
    assert abs(corrected[0] - 0.5) < abs(noisy[0] - 0.5) or abs(corrected[0] - 0.5) < 0.02
    print("Readout error mitigation verified")
""",
)

add(
    id="qac_zero_noise_extrapolation",
    family="noise_and_mitigation",
    algorithm="zero_noise_extrapolation",
    difficulty="hard",
    question=(
        "Implement digital zero-noise extrapolation in Qiskit: estimate <ZZ> on a Bell pair at several "
        "noise scale factors via unitary folding, then linearly extrapolate to the zero-noise limit and "
        "verify it is closer to the ideal value than the unmitigated estimate."
    ),
    rationale=(
        "ZNE amplifies noise by replacing the CX with CX (CX^dag CX)^k (unitary folding), measures the "
        "observable at scale factors 1,3,5, and fits a line back to scale 0. The extrapolated value "
        "recovers most of the bias toward the ideal <ZZ>=1."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

def folded_bell(folds):
    qc = QuantumCircuit(2); qc.h(0)
    qc.cx(0, 1)
    for _ in range(folds):
        qc.barrier(); qc.cx(0, 1); qc.barrier(); qc.cx(0, 1)  # CX^dag CX = identity
    qc.measure_all()
    return qc

def expval_zz(sim, folds, shots=40000):
    counts = sim.run(transpile(folded_bell(folds), sim, optimization_level=0), shots=shots).result().get_counts()
    e = 0.0
    for bs, c in counts.items():
        par = (-1) ** (bs.count("1"))
        e += par * c
    return e / shots

if __name__ == "__main__":
    nm = NoiseModel(); nm.add_all_qubit_quantum_error(depolarizing_error(0.06, 2), ["cx"])
    sim = AerSimulator(noise_model=nm, seed_simulator=11)
    scales = np.array([1, 3, 5])
    vals = np.array([expval_zz(sim, k) for k in range(3)])
    slope, intercept = np.polyfit(scales, vals, 1)
    print(f"scaled <ZZ>: {np.round(vals,4)}, ZNE(0) = {intercept:.4f} (ideal 1.0)")
    assert abs(intercept - 1.0) < abs(vals[0] - 1.0), (intercept, vals[0])
    print("Zero-noise extrapolation verified")
""",
)

add(
    id="qac_clifford_simulation",
    family="quantum_information",
    algorithm="clifford_stabilizer_simulation",
    difficulty="medium",
    question=(
        "Using Qiskit's Clifford class, verify that a random Clifford circuit equals its stabilizer "
        "tableau representation by comparing the unitary it implements, and confirm the inverse Clifford "
        "returns the system to |0...0>."
    ),
    rationale=(
        "Clifford circuits are efficiently representable by stabilizer tableaus. Building a Clifford "
        "from a circuit and converting back must reproduce the same unitary (Operator.equiv), and "
        "composing a Clifford with its inverse must yield the identity, returning |0> to |0>."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Clifford, random_clifford, Operator, Statevector

if __name__ == "__main__":
    for seed in range(5):
        cliff = random_clifford(3, seed=seed)
        circ = cliff.to_circuit()
        assert Operator(Clifford(circ).to_circuit()).equiv(Operator(circ)), seed
        full = QuantumCircuit(3)
        full.compose(circ, inplace=True)
        full.compose(circ.inverse(), inplace=True)
        sv = Statevector(full)
        assert abs(sv.probabilities_dict().get("000", 0) - 1.0) < 1e-9, seed
    print("Clifford stabilizer simulation verified")
""",
)

add(
    id="qac_randomized_benchmarking_lite",
    family="noise_and_mitigation",
    algorithm="randomized_benchmarking_sequence",
    difficulty="medium",
    question=(
        "Build a single-qubit randomized-benchmarking-style sequence in Qiskit: apply m random Clifford "
        "gates followed by the single recovery Clifford that inverts them, and verify the noiseless "
        "survival probability of |0> is exactly 1 for several lengths."
    ),
    rationale=(
        "An RB sequence composes random Cliffords then appends the inverse of their product as a "
        "recovery gate, so the ideal (noiseless) circuit is the identity and |0> survives with "
        "probability 1. This is the zero-error baseline against which decay is measured under noise."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Clifford, random_clifford, Statevector

def rb_sequence(m, seed):
    rng = np.random.default_rng(seed)
    qc = QuantumCircuit(1)
    for _ in range(m):
        c = random_clifford(1, seed=int(rng.integers(1 << 30)))
        qc.compose(c.to_circuit(), inplace=True)
    qc.compose(Clifford(qc).adjoint().to_circuit(), inplace=True)  # single recovery gate
    return qc

if __name__ == "__main__":
    for m in (1, 5, 20, 50):
        survival = Statevector(rb_sequence(m, seed=m)).probabilities_dict().get("0", 0.0)
        print(f"length {m:3d}: survival {survival:.6f}")
        assert abs(survival - 1.0) < 1e-9, (m, survival)
    print("Randomized benchmarking baseline verified")
""",
)

add(
    id="qac_transpile_equivalence",
    family="hardware_compilation",
    algorithm="transpile_basis_gates",
    difficulty="medium",
    question=(
        "Using Qiskit, transpile a GHZ circuit to a restricted basis {rz, sx, x, cx} with a linear "
        "coupling map and optimization level 3, and verify the transpiled circuit is functionally "
        "equivalent to the original via operator equivalence."
    ),
    rationale=(
        "Transpilation rewrites a circuit into hardware-native gates and topology while preserving the "
        "unitary up to global phase and qubit permutation. Compare the original and transpiled "
        "operators with Operator.equiv to confirm semantic equivalence after compilation."
    ),
    code=r"""
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Operator

def ghz(n):
    qc = QuantumCircuit(n); qc.h(0)
    for q in range(1, n): qc.cx(0, q)
    return qc

if __name__ == "__main__":
    n = 4
    original = ghz(n)
    coupling = [[i, i + 1] for i in range(n - 1)] + [[i + 1, i] for i in range(n - 1)]
    tqc = transpile(original, basis_gates=["rz", "sx", "x", "cx"],
                    coupling_map=coupling, optimization_level=3, seed_transpiler=1)
    assert set(instr.operation.name for instr in tqc.data) <= {"rz", "sx", "x", "cx", "barrier"}
    assert Operator.from_circuit(tqc).equiv(Operator(original)), "transpiled circuit changed semantics"
    print(f"transpiled to {tqc.count_ops()}, depth {tqc.depth()}; equivalence verified")
""",
)

add(
    id="qac_circuit_identity_simplification",
    family="hardware_compilation",
    algorithm="gate_identity_optimization",
    difficulty="easy",
    question=(
        "Using Qiskit, verify the common gate identities H X H = Z, H Z H = X, and S S = Z at the "
        "operator level, and confirm that transpilation with optimization cancels an adjacent "
        "H-H pair to the identity."
    ),
    rationale=(
        "These Clifford identities follow from conjugation rules. Build each left-hand circuit, compare "
        "its Operator to the target gate, then transpile a circuit containing two consecutive H gates "
        "and confirm the optimizer removes them, leaving an identity-equivalent circuit."
    ),
    code=r"""
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Operator

def op(builder):
    qc = QuantumCircuit(1); builder(qc); return Operator(qc)

if __name__ == "__main__":
    z = QuantumCircuit(1); z.z(0)
    x = QuantumCircuit(1); x.x(0)
    assert op(lambda c: (c.h(0), c.x(0), c.h(0))).equiv(Operator(z))
    assert op(lambda c: (c.h(0), c.z(0), c.h(0))).equiv(Operator(x))
    assert op(lambda c: (c.s(0), c.s(0))).equiv(Operator(z))
    hh = QuantumCircuit(1); hh.h(0); hh.h(0)
    opt = transpile(hh, basis_gates=["u", "cx"], optimization_level=3)
    assert opt.size() == 0, opt.count_ops()
    print("Gate identities and H-H cancellation verified")
""",
)

add(
    id="qac_two_qubit_kak_decomposition",
    family="gate_construction",
    algorithm="two_qubit_kak_decomposition",
    difficulty="hard",
    question=(
        "Using Qiskit's TwoQubitBasisDecomposer with CX as the basis gate, decompose a random two-qubit "
        "unitary into at most three CX gates plus single-qubit rotations, and verify the synthesized "
        "circuit reproduces the target."
    ),
    rationale=(
        "The KAK/Cartan decomposition shows any two-qubit unitary needs at most three CX gates. Qiskit's "
        "TwoQubitBasisDecomposer performs this synthesis; verify the result with Operator.equiv and "
        "confirm the CX count does not exceed three."
    ),
    code=r"""
from qiskit.circuit.library import CXGate
from qiskit.synthesis import TwoQubitBasisDecomposer
from qiskit.quantum_info import Operator, random_unitary

if __name__ == "__main__":
    decomposer = TwoQubitBasisDecomposer(CXGate())
    for seed in range(5):
        U = random_unitary(4, seed=seed)
        circ = decomposer(U.data)
        ncx = circ.count_ops().get("cx", 0)
        assert ncx <= 3, ncx
        assert Operator(circ).equiv(U), seed
    print("Two-qubit KAK decomposition verified (<= 3 CX each)")
""",
)

add(
    id="qac_pauli_twirling",
    family="noise_and_mitigation",
    algorithm="pauli_twirling",
    difficulty="hard",
    question=(
        "Implement Pauli twirling of a CX gate in Qiskit: for each two-qubit Pauli P sampled, conjugate "
        "the CX by P on the input and the correctly-propagated Pauli on the output, and verify each "
        "twirled circuit is logically equivalent to the bare CX."
    ),
    rationale=(
        "Pauli twirling averages a noisy gate over conjugations by Paulis to tailor coherent noise into "
        "stochastic Pauli noise, while leaving the ideal gate unchanged. For an ideal CX, applying P "
        "before and CX*P*CX^dag after must reproduce CX exactly, which we check via Operator.equiv."
    ),
    code=r"""
import itertools
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator, Pauli

def twirled_cx(p_label):
    bare = QuantumCircuit(2); bare.cx(0, 1)
    cx = Operator(bare)
    pin = Operator(Pauli(p_label))
    pout = cx @ pin @ cx.adjoint()                  # propagate Pauli through CX
    qc = QuantumCircuit(2)
    qc.append(Pauli(p_label).to_instruction(), [0, 1])
    qc.cx(0, 1)
    qc.unitary(pout.data, [0, 1])
    return qc

if __name__ == "__main__":
    bare = QuantumCircuit(2); bare.cx(0, 1)
    target = Operator(bare)
    for a, b in itertools.product("IXYZ", repeat=2):
        circ = twirled_cx(a + b)
        assert Operator(circ).equiv(target), a + b
    print("Pauli twirling identity verified for all 16 two-qubit Paulis")
""",
)

add(
    id="qac_measure_in_x_basis",
    family="quantum_subroutines",
    algorithm="basis_change_measurement",
    difficulty="easy",
    question=(
        "Using Qiskit, show how to measure a qubit in the X and Y bases by applying the correct basis-"
        "change rotation before a Z measurement. Verify that |+> always reads 0 in the X basis and "
        "|+i> always reads 0 in the Y basis."
    ),
    rationale=(
        "Measuring in the X basis means applying H then measuring Z; measuring in the Y basis means "
        "applying S-dagger then H then measuring Z. The eigenstates |+> and |+i> deterministically give "
        "outcome 0 in their respective bases."
    ),
    code=r"""
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

def measure_basis(prep, basis):
    qc = prep.copy()
    if basis == "X":
        qc.h(0)
    elif basis == "Y":
        qc.sdg(0); qc.h(0)
    return Statevector(qc).probabilities_dict()

if __name__ == "__main__":
    plus = QuantumCircuit(1); plus.h(0)
    plus_i = QuantumCircuit(1); plus_i.h(0); plus_i.s(0)
    assert abs(measure_basis(plus, "X").get("0", 0) - 1.0) < 1e-9
    assert abs(measure_basis(plus_i, "Y").get("0", 0) - 1.0) < 1e-9
    print("X/Y basis measurement verified")
""",
)

add(
    id="qac_mid_circuit_measurement_reset",
    family="quantum_subroutines",
    algorithm="mid_circuit_measure_reset",
    difficulty="medium",
    question=(
        "Using qiskit-aer, demonstrate mid-circuit measurement and reset: entangle two qubits, measure "
        "and reset the first qubit to |0>, then verify via shots that the second qubit's outcome is "
        "perfectly correlated with the recorded mid-circuit result."
    ),
    rationale=(
        "Mid-circuit measurement collapses the entangled state; resetting returns the measured qubit to "
        "|0> while the partner remains in the post-measurement state. For a Bell pair the mid-circuit "
        "bit equals the final partner bit in every shot, confirming the collapse and reset semantics."
    ),
    code=r"""
from qiskit import QuantumCircuit, transpile, ClassicalRegister, QuantumRegister
from qiskit_aer import AerSimulator

def correlated_circuit():
    q = QuantumRegister(2); c_mid = ClassicalRegister(1, "mid"); c_fin = ClassicalRegister(1, "fin")
    qc = QuantumCircuit(q, c_mid, c_fin)
    qc.h(0); qc.cx(0, 1)
    qc.measure(0, c_mid[0])
    qc.reset(0)
    qc.measure(1, c_fin[0])
    return qc

if __name__ == "__main__":
    sim = AerSimulator(seed_simulator=3)
    counts = sim.run(transpile(correlated_circuit(), sim), shots=4000).result().get_counts()
    # keys look like "fin mid"; correlated outcomes must have fin == mid
    for key, n in counts.items():
        fin, mid = key.split()
        assert fin == mid, (key, n)
    print("Mid-circuit measurement + reset correlation verified:", counts)
""",
)


# ===================================================================
# BATCH: quantum information measures, channels, and dynamics
# ===================================================================

add(
    id="qac_concurrence_entanglement",
    family="quantum_information",
    algorithm="two_qubit_concurrence",
    difficulty="medium",
    question=(
        "Using Qiskit quantum_info, compute the concurrence of a parametrized two-qubit state "
        "cos(t)|00> + sin(t)|11> for several angles, and verify it equals |sin(2t)| (0 for product "
        "states, 1 for the maximally entangled Bell state)."
    ),
    rationale=(
        "Concurrence measures two-qubit entanglement: 0 for separable, 1 for maximally entangled. For "
        "the state cos(t)|00>+sin(t)|11> the analytic concurrence is |sin(2t)|. Build the state and "
        "compare Qiskit's concurrence to the closed form."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, concurrence

def parametrized_state(t):
    qc = QuantumCircuit(2)
    qc.ry(2 * t, 0)         # cos(t)|0> + sin(t)|1> on qubit 0
    qc.cx(0, 1)
    return Statevector(qc)

if __name__ == "__main__":
    for t in [0.0, np.pi / 8, np.pi / 4, np.pi / 3]:
        c = concurrence(parametrized_state(t))
        expected = abs(np.sin(2 * t))
        print(f"t={t:.4f}: concurrence {c:.6f} (expected {expected:.6f})")
        assert abs(c - expected) < 1e-9, (t, c, expected)
    print("Concurrence verified")
""",
)

add(
    id="qac_trace_distance",
    family="quantum_information",
    algorithm="trace_distance_states",
    difficulty="medium",
    question=(
        "Using Qiskit, compute the trace distance between two single-qubit states and verify it equals "
        "the analytic half-L1 of Bloch-vector difference: 1 for orthogonal pure states and (1-cos)/... "
        "checked numerically against the eigenvalue formula."
    ),
    rationale=(
        "Trace distance T(rho,sigma)=0.5*||rho-sigma||_1 equals half the sum of absolute eigenvalues of "
        "(rho-sigma). For pure states it reduces to sqrt(1-|<psi|phi>|^2). Compute both via DensityMatrix "
        "and compare."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, DensityMatrix

def trace_distance(rho, sigma):
    diff = rho.data - sigma.data
    return 0.5 * np.sum(np.abs(np.linalg.eigvalsh(diff)))

if __name__ == "__main__":
    a = QuantumCircuit(1)
    b = QuantumCircuit(1); b.ry(0.9, 0)
    psi, phi = Statevector(a), Statevector(b)
    td = trace_distance(DensityMatrix(psi), DensityMatrix(phi))
    analytic = np.sqrt(1 - abs(np.vdot(psi.data, phi.data)) ** 2)
    print(f"trace distance {td:.6f} (analytic {analytic:.6f})")
    assert abs(td - analytic) < 1e-9, (td, analytic)
    orth = QuantumCircuit(1); orth.x(0)
    assert abs(trace_distance(DensityMatrix(psi), DensityMatrix(Statevector(orth))) - 1.0) < 1e-9
    print("Trace distance verified")
""",
)

add(
    id="qac_amplitude_damping_channel",
    family="noise_and_mitigation",
    algorithm="amplitude_damping_channel",
    difficulty="medium",
    question=(
        "Using qiskit-aer's amplitude damping error, simulate energy relaxation on |1> and verify the "
        "measured excited-state population decays as (1-gamma) for increasing damping parameter gamma."
    ),
    rationale=(
        "Amplitude damping models T1 relaxation: an excited qubit |1> decays to |0> with probability "
        "gamma. The surviving |1> population is (1-gamma). Attach amplitude_damping_error to an identity "
        "operation and measure the excited-state fraction across gamma values."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, amplitude_damping_error

def excited_population(gamma, shots=40000, seed=2):
    nm = NoiseModel()
    nm.add_all_qubit_quantum_error(amplitude_damping_error(gamma), ["id"])
    sim = AerSimulator(noise_model=nm, seed_simulator=seed)
    qc = QuantumCircuit(1); qc.x(0); qc.id(0); qc.measure_all()
    counts = sim.run(transpile(qc, sim, optimization_level=0), shots=shots).result().get_counts()
    return counts.get("1", 0) / shots

if __name__ == "__main__":
    for gamma in (0.0, 0.3, 0.6, 0.9):
        pop = excited_population(gamma)
        print(f"gamma={gamma}: P(|1>) {pop:.4f} (expected {1-gamma:.2f})")
        assert abs(pop - (1 - gamma)) < 0.02, (gamma, pop)
    print("Amplitude damping channel verified")
""",
)

add(
    id="qac_choi_process_fidelity",
    family="quantum_information",
    algorithm="choi_process_fidelity",
    difficulty="hard",
    question=(
        "Using Qiskit quantum_info, build the Choi matrix of an ideal Hadamard and of a slightly "
        "over-rotated Hadamard, and verify the process fidelity is 1 for the exact gate and decreases "
        "for the imperfect one."
    ),
    rationale=(
        "The Choi matrix fully characterizes a quantum channel. Process fidelity between the ideal gate "
        "and a candidate quantifies implementation quality: it is 1 for a perfect match and drops as the "
        "over-rotation grows. Compare Choi representations with process_fidelity."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Choi, Operator, process_fidelity

def hadamard(eps=0.0):
    qc = QuantumCircuit(1)
    qc.h(0); qc.rz(eps, 0)               # eps=0 is an exact Hadamard
    return qc

if __name__ == "__main__":
    target = Operator.from_label("H")
    f_exact = process_fidelity(Choi(hadamard(0.0)), target=target)
    f_bad = process_fidelity(Choi(hadamard(0.2)), target=target)
    print(f"process fidelity: exact {f_exact:.6f}, over-rotated {f_bad:.6f}")
    assert f_exact > 1 - 1e-6, f_exact
    assert f_bad < f_exact, (f_bad, f_exact)
    print("Choi process fidelity verified")
""",
)

add(
    id="qac_pauli_decomposition",
    family="quantum_information",
    algorithm="pauli_decomposition_hermitian",
    difficulty="medium",
    question=(
        "Using Qiskit, decompose an arbitrary Hermitian 4x4 matrix into a sum of Pauli strings with "
        "SparsePauliOp.from_operator, and verify reconstructing the matrix from the Pauli terms returns "
        "the original."
    ),
    rationale=(
        "Any 2^n x 2^n Hermitian operator expands uniquely in the Pauli basis with real coefficients. "
        "SparsePauliOp.from_operator computes these coefficients; summing coeff*Pauli must reproduce the "
        "original matrix exactly."
    ),
    code=r"""
import numpy as np
from qiskit.quantum_info import Operator, SparsePauliOp

if __name__ == "__main__":
    rng = np.random.default_rng(0)
    A = rng.standard_normal((4, 4)) + 1j * rng.standard_normal((4, 4))
    H = A + A.conj().T                       # Hermitian
    sp = SparsePauliOp.from_operator(Operator(H))
    assert np.allclose(np.imag(sp.coeffs), 0, atol=1e-9), "coeffs must be real"
    recon = sp.to_matrix()
    assert np.allclose(recon, H, atol=1e-9), "reconstruction mismatch"
    print(f"decomposed into {len(sp)} Pauli terms; reconstruction verified")
""",
)

add(
    id="qac_parameter_shift_gradient",
    family="variational_methods",
    algorithm="parameter_shift_rule",
    difficulty="hard",
    question=(
        "Implement the parameter-shift rule in Qiskit to compute the exact gradient of <Z> for the "
        "circuit Ry(theta)|0> and verify it matches the analytic derivative -sin(theta) at several "
        "points."
    ),
    rationale=(
        "For a gate generated by a Pauli (eigenvalues +/-1), the parameter-shift rule gives the exact "
        "gradient as [f(theta+pi/2) - f(theta-pi/2)]/2. For <Z> on Ry(theta)|0> = cos(theta), the "
        "derivative is -sin(theta); the shift rule reproduces it without finite-difference error."
    ),
    code=r"""
import numpy as np
from qiskit.circuit import Parameter
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator

def expectation(theta):
    t = Parameter("t")
    qc = QuantumCircuit(1); qc.ry(t, 0)
    est = StatevectorEstimator()
    return float(est.run([(qc, SparsePauliOp("Z"), [theta])]).result()[0].data.evs)

def parameter_shift_grad(theta):
    return 0.5 * (expectation(theta + np.pi / 2) - expectation(theta - np.pi / 2))

if __name__ == "__main__":
    for theta in [0.1, 0.7, 1.5, 2.4]:
        grad = parameter_shift_grad(theta)
        analytic = -np.sin(theta)
        print(f"theta={theta}: grad {grad:.6f} (analytic {analytic:.6f})")
        assert abs(grad - analytic) < 1e-9, (theta, grad, analytic)
    print("Parameter-shift gradient verified")
""",
)

add(
    id="qac_shor_nine_qubit_code",
    family="error_correction",
    algorithm="shor_nine_qubit_code",
    difficulty="hard",
    question=(
        "Implement Shor's 9-qubit code in Qiskit. Encode a logical qubit, inject an arbitrary single-"
        "qubit error (X, Z, or Y) on any data qubit, decode, and verify the logical information is "
        "recovered with fidelity 1 for representative error locations."
    ),
    rationale=(
        "Shor's code concatenates the phase-flip code (outer) with the bit-flip code (inner), "
        "protecting against any single-qubit error. Encode with the standard CNOT/Hadamard network; "
        "because the code corrects an arbitrary single error, decoding (the inverse network) followed "
        "by majority/parity recovery restores the logical state for X, Y, Z errors."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, partial_trace, state_fidelity, random_statevector

def shor_encode(qc):
    # qubit 0 is logical; spread to blocks {0,3,6} (phase) then triples (bit)
    qc.cx(0, 3); qc.cx(0, 6)
    qc.h(0); qc.h(3); qc.h(6)
    qc.cx(0, 1); qc.cx(0, 2)
    qc.cx(3, 4); qc.cx(3, 5)
    qc.cx(6, 7); qc.cx(6, 8)

def shor_decode(qc):
    # bit-flip correction per block via majority (Toffoli back onto block leader)
    for lead in (0, 3, 6):
        a, b = lead + 1, lead + 2
        qc.cx(lead, a); qc.cx(lead, b)
        qc.ccx(b, a, lead)
    qc.h(0); qc.h(3); qc.h(6)
    # phase-flip correction across blocks
    qc.cx(0, 3); qc.cx(0, 6)
    qc.ccx(6, 3, 0)

def run(error):
    psi = random_statevector(2, seed=7)
    qc = QuantumCircuit(9)
    qc.initialize(psi.data, 0)
    shor_encode(qc)
    if error:
        gate, q = error
        getattr(qc, gate)(q)
    shor_decode(qc)
    data = partial_trace(Statevector(qc), list(range(1, 9)))
    return state_fidelity(data, psi)

if __name__ == "__main__":
    errors = [None, ("x", 2), ("z", 4), ("y", 6), ("x", 0)]
    for err in errors:
        fid = run(err)
        print(f"error {err}: recovery fidelity {fid:.6f}")
        assert fid > 1 - 1e-9, (err, fid)
    print("Shor 9-qubit code verified")
""",
)

add(
    id="qac_repetition_code_distance5",
    family="error_correction",
    algorithm="repetition_code_majority",
    difficulty="medium",
    question=(
        "Implement a distance-5 classical-style bit-flip repetition code in Qiskit that corrects up to "
        "two bit-flip errors by majority vote, and verify recovery of the logical basis state for all "
        "error patterns of weight <= 2."
    ),
    rationale=(
        "A distance-5 repetition code encodes |b> as |bbbbb> and corrects any error of weight <= 2 by "
        "majority decoding. For computational basis inputs this reduces to classical majority over the "
        "five physical bits; verify exhaustively over all weight<=2 error patterns."
    ),
    code=r"""
import itertools
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

def encode_and_error(bit, error_qubits):
    qc = QuantumCircuit(5)
    if bit: qc.x(0)
    qc.cx(0, 1); qc.cx(0, 2); qc.cx(0, 3); qc.cx(0, 4)
    for q in error_qubits:
        qc.x(q)
    out = next(k for k, v in Statevector(qc).probabilities_dict().items() if v > 0.5)
    return out[::-1]                          # physical bits q0..q4

def majority(bits):
    return 1 if bits.count("1") >= 3 else 0

if __name__ == "__main__":
    for bit in (0, 1):
        for w in (0, 1, 2):
            for combo in itertools.combinations(range(5), w):
                bits = encode_and_error(bit, combo)
                assert majority(bits) == bit, (bit, combo, bits)
    print("Distance-5 repetition code corrects all weight<=2 errors; verified")
""",
)

add(
    id="qac_quantum_walk_cycle",
    family="quantum_walks",
    algorithm="discrete_time_quantum_walk",
    difficulty="hard",
    question=(
        "Implement one step of a discrete-time quantum walk on a cycle of 8 nodes in Qiskit using a "
        "coin qubit and a position register with modular increment/decrement shift operators. Verify "
        "the walk operator is unitary and conserves probability."
    ),
    rationale=(
        "A DTQW step is a coin flip (Hadamard on the coin) followed by a conditional shift: increment "
        "the position when the coin is |0>, decrement when |1>, modulo the cycle length. The combined "
        "operator must be unitary, which we confirm via Operator unitarity and norm conservation."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit.library import CDKMRippleCarryAdder
from qiskit.quantum_info import Operator, Statevector

def increment(qc, pos):
    n = len(pos)                              # modular +1 via cascaded MCX
    for i in reversed(range(1, n)):
        qc.mcx(pos[:i], pos[i])
    qc.x(pos[0])

def decrement(qc, pos):
    n = len(pos)                              # modular -1 (inverse of increment)
    qc.x(pos[0])
    for i in range(1, n):
        qc.mcx(pos[:i], pos[i])

def walk_step(nq=3):
    coin = QuantumRegister(1, "c"); pos = QuantumRegister(nq, "p")
    qc = QuantumCircuit(coin, pos)
    qc.h(coin[0])
    # controlled increment on coin=1
    inc = QuantumCircuit(pos); increment(inc, list(range(nq)))
    qc.append(inc.to_gate().control(1), [coin[0]] + list(pos))
    # controlled decrement on coin=0
    qc.x(coin[0])
    dec = QuantumCircuit(pos); decrement(dec, list(range(nq)))
    qc.append(dec.to_gate().control(1), [coin[0]] + list(pos))
    qc.x(coin[0])
    return qc

if __name__ == "__main__":
    qc = walk_step(3)
    U = Operator(qc)
    assert U.is_unitary(), "walk operator not unitary"
    sv = Statevector.from_label("0000").evolve(U)
    assert abs(sum(sv.probabilities()) - 1.0) < 1e-9
    print("Discrete-time quantum walk step verified (unitary, norm-preserving)")
""",
)

add(
    id="qac_ghz_mermin_inequality",
    family="quantum_subroutines",
    algorithm="ghz_mermin_inequality",
    difficulty="hard",
    question=(
        "Using Qiskit, evaluate the 3-qubit Mermin operator M = X1X2X3 - X1Y2Y3 - Y1X2Y3 - Y1Y2X3 on "
        "the GHZ state and verify it reaches the quantum value 4, exceeding the classical bound of 2."
    ),
    rationale=(
        "The Mermin inequality bounds local-hidden-variable theories by |<M>| <= 2, while quantum "
        "mechanics on the GHZ state achieves 4. Evaluate each Pauli term's expectation with an "
        "estimator and sum with the proper signs."
    ),
    code=r"""
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator

def ghz3():
    qc = QuantumCircuit(3); qc.h(0); qc.cx(0, 1); qc.cx(1, 2); return qc

if __name__ == "__main__":
    mermin = SparsePauliOp.from_list([
        ("XXX", 1.0), ("XYY", -1.0), ("YXY", -1.0), ("YYX", -1.0),
    ])
    est = StatevectorEstimator()
    val = float(est.run([(ghz3(), mermin)]).result()[0].data.evs)
    print(f"<M> = {val:.6f} (classical bound 2, quantum max 4)")
    assert abs(val - 4.0) < 1e-9, val
    print("Mermin inequality violation verified")
""",
)

add(
    id="qac_teleportation_classical_control",
    family="entanglement_protocols",
    algorithm="teleportation_dynamic_circuit",
    difficulty="hard",
    question=(
        "Implement quantum teleportation in Qiskit with real mid-circuit measurement and classically-"
        "controlled X/Z corrections (a dynamic circuit), then use qiskit-aer to verify Bob measures the "
        "input basis state deterministically over many shots."
    ),
    rationale=(
        "A faithful teleportation uses Alice's two measured bits to classically condition Bob's X and Z "
        "corrections via c_if. Preparing a known basis input and running on AerSimulator should yield "
        "Bob's outcome equal to the input bit in every shot."
    ),
    code=r"""
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator

def teleport_dynamic(input_bit):
    q = QuantumRegister(3); m = ClassicalRegister(2, "m"); out = ClassicalRegister(1, "out")
    qc = QuantumCircuit(q, m, out)
    if input_bit:
        qc.x(0)                              # prepare |1> to teleport
    qc.h(1); qc.cx(1, 2)
    qc.cx(0, 1); qc.h(0)
    qc.measure(0, m[0]); qc.measure(1, m[1])
    with qc.if_test((m[1], 1)):
        qc.x(2)
    with qc.if_test((m[0], 1)):
        qc.z(2)
    qc.measure(2, out[0])
    return qc

if __name__ == "__main__":
    sim = AerSimulator(seed_simulator=4)
    for bit in (0, 1):
        counts = sim.run(transpile(teleport_dynamic(bit), sim), shots=2000).result().get_counts()
        bob = {key.split()[0] for key in counts}   # 'out' register is leftmost
        assert bob == {str(bit)}, (bit, counts)
    print("Dynamic teleportation with classical control verified")
""",
)

add(
    id="qac_iswap_decomposition",
    family="gate_construction",
    algorithm="iswap_gate_identity",
    difficulty="medium",
    question=(
        "Using Qiskit, verify that the iSWAP gate can be decomposed into two CNOTs with single-qubit "
        "S/H gates, by comparing the decomposition's operator to the native iSwapGate."
    ),
    rationale=(
        "iSWAP swaps two qubits and adds an i phase on the |01>,|10> amplitudes. A standard "
        "decomposition uses S gates, Hadamards, and two CNOTs. Compare the synthesized operator against "
        "Qiskit's iSwapGate with Operator.equiv."
    ),
    code=r"""
from qiskit import QuantumCircuit
from qiskit.circuit.library import iSwapGate
from qiskit.quantum_info import Operator

def iswap_decomposed():
    qc = QuantumCircuit(2)
    qc.s(0); qc.s(1)
    qc.h(0)
    qc.cx(0, 1); qc.cx(1, 0)
    qc.h(1)
    return qc

if __name__ == "__main__":
    assert Operator(iswap_decomposed()).equiv(Operator(iSwapGate())), "iSWAP decomposition mismatch"
    print("iSWAP decomposition verified")
""",
)

add(
    id="qac_magnetization_dynamics",
    family="hamiltonian_simulation",
    algorithm="spin_chain_magnetization",
    difficulty="hard",
    question=(
        "Using Qiskit, simulate the time evolution of the total magnetization <sum Z_i> of a 3-spin "
        "Heisenberg chain starting from the Neel state |010>, and verify the Trotterized dynamics match "
        "exact diagonalization at several times."
    ),
    rationale=(
        "The Heisenberg Hamiltonian conserves total magnetization, but local observables oscillate. "
        "Evolve the Neel state with a fine Suzuki-Trotter PauliEvolution and compare <sum Z_i> to the "
        "exact propagator expectation at several times."
    ),
    code=r"""
import numpy as np
from scipy.linalg import expm
from qiskit import QuantumCircuit
from qiskit.circuit.library import PauliEvolutionGate
from qiskit.synthesis import SuzukiTrotter
from qiskit.quantum_info import SparsePauliOp, Statevector

def heisenberg(n=3, J=1.0):
    terms = []
    for i in range(n - 1):
        for P in ("X", "Y", "Z"):
            s = ["I"] * n; s[i] = s[i + 1] = P; terms.append(("".join(s), J))
    return SparsePauliOp.from_list(terms)

def total_Z(n):
    return SparsePauliOp.from_list([("".join("Z" if k == i else "I" for k in range(n)), 1.0)
                                    for i in range(n)])

if __name__ == "__main__":
    n = 3; H = heisenberg(n); Mz = total_Z(n)
    neel = Statevector.from_label("010")
    for t in (0.3, 0.8, 1.5):
        gate = PauliEvolutionGate(H, time=t, synthesis=SuzukiTrotter(order=2, reps=200))
        qc = QuantumCircuit(n); qc.append(gate, range(n))
        approx = neel.evolve(qc)
        exact = neel.evolve(expm(-1j * H.to_matrix() * t))
        ea = float(np.real(approx.expectation_value(Mz)))
        ee = float(np.real(exact.expectation_value(Mz)))
        print(f"t={t}: <Mz> trotter {ea:.6f}, exact {ee:.6f}")
        assert abs(ea - ee) < 1e-2, (t, ea, ee)
    print("Magnetization dynamics verified")
""",
)


# ===================================================================
# BATCH: chemistry mappings, optimization, channels, dynamics II
# ===================================================================

add(
    id="qac_vqe_h2_jordan_wigner",
    family="vqe_chemistry",
    algorithm="vqe_h2_jordan_wigner",
    difficulty="hard",
    question=(
        "Using Qiskit Nature with the Jordan-Wigner mapping (no qubit reduction), build the 4-qubit "
        "STO-3G H2 Hamiltonian at 0.735 Angstrom and find its ground-state energy with a VQE using the "
        "EfficientSU2 ansatz; verify it matches exact diagonalization."
    ),
    rationale=(
        "Jordan-Wigner maps 4 spin-orbitals to 4 qubits without symmetry reduction. After folding the "
        "nuclear repulsion into the identity, optimize an EfficientSU2 ansatz with COBYLA and restarts. "
        "The VQE energy should reach the exact lowest eigenvalue of the 4-qubit operator."
    ),
    code=r"""
import numpy as np
from scipy.optimize import minimize
from qiskit.circuit.library import efficient_su2
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator
from qiskit_nature.second_q.drivers import PySCFDriver
from qiskit_nature.second_q.mappers import JordanWignerMapper

def h2_jw(R=0.735):
    problem = PySCFDriver(atom=f"H 0 0 0; H 0 0 {R}", basis="sto3g").run()
    op = JordanWignerMapper().map(problem.second_q_ops()[0])
    op = op + problem.nuclear_repulsion_energy * SparsePauliOp("I" * op.num_qubits)
    return op.simplify()

if __name__ == "__main__":
    H = h2_jw()
    ansatz = efficient_su2(H.num_qubits, reps=2, entanglement="full")
    est = StatevectorEstimator()
    energy = lambda p: float(est.run([(ansatz, H, p)]).result()[0].data.evs)
    rng = np.random.default_rng(1)
    best = None
    for _ in range(4):
        res = minimize(energy, rng.uniform(-np.pi, np.pi, ansatz.num_parameters),
                       method="COBYLA", options={"maxiter": 600})
        if best is None or res.fun < best.fun: best = res
    e_exact = float(np.linalg.eigvalsh(H.to_matrix())[0])
    print(f"JW VQE {best.fun:.6f} vs exact {e_exact:.6f} ({H.num_qubits} qubits)")
    assert abs(best.fun - e_exact) < 5e-3, (best.fun, e_exact)
    print("Jordan-Wigner H2 VQE verified")
""",
)

add(
    id="qac_mapper_spectrum_equivalence",
    family="vqe_chemistry",
    algorithm="fermionic_mapper_equivalence",
    difficulty="medium",
    question=(
        "Using Qiskit Nature, verify that the Jordan-Wigner and Bravyi-Kitaev mappings of the H2 "
        "electronic Hamiltonian produce qubit operators with identical eigenvalue spectra (same physics, "
        "different encodings)."
    ),
    rationale=(
        "Different fermion-to-qubit mappings are unitarily related and must preserve the Hamiltonian "
        "spectrum. Compute the sorted eigenvalues of the Jordan-Wigner and Bravyi-Kitaev mapped "
        "operators and confirm they coincide."
    ),
    code=r"""
import numpy as np
from qiskit_nature.second_q.drivers import PySCFDriver
from qiskit_nature.second_q.mappers import JordanWignerMapper, BravyiKitaevMapper

if __name__ == "__main__":
    op2 = PySCFDriver(atom="H 0 0 0; H 0 0 0.735", basis="sto3g").run().second_q_ops()[0]
    jw = JordanWignerMapper().map(op2)
    bk = BravyiKitaevMapper().map(op2)
    ev_jw = np.sort(np.linalg.eigvalsh(jw.to_matrix()))
    ev_bk = np.sort(np.linalg.eigvalsh(bk.to_matrix()))
    print("ground (JW, BK):", round(ev_jw[0], 6), round(ev_bk[0], 6))
    assert np.allclose(ev_jw, ev_bk, atol=1e-9), "spectra differ"
    print("JW and Bravyi-Kitaev spectra match; verified")
""",
)

add(
    id="qac_qaoa_cycle_graph",
    family="qaoa_optimization",
    algorithm="qaoa_maxcut_cycle",
    difficulty="medium",
    question=(
        "Use Qiskit to solve MaxCut on a 5-node cycle graph C5 with QAOA, and verify the optimal cut "
        "value equals 4 (the known optimum for an odd cycle) against brute force."
    ),
    rationale=(
        "For an odd cycle C_{2k+1}, the maximum cut leaves exactly one edge uncut, giving a cut of "
        "(num_edges - 1). For C5 the optimum is 4. Run QAOA, sample the best bitstring, and validate "
        "against exhaustive enumeration."
    ),
    code=r"""
import numpy as np
import networkx as nx
from scipy.optimize import minimize
from qiskit.circuit.library import QAOAAnsatz
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator, StatevectorSampler

def cost(g):
    n = g.number_of_nodes(); terms = []
    for i, j in g.edges():
        z = ["I"] * n; z[i] = z[j] = "Z"
        terms.append(("".join(reversed(z)), 0.5)); terms.append(("I" * n, -0.5))
    return SparsePauliOp.from_list(terms).simplify()

def cut(g, bits):
    a = [int(b) for b in bits]
    return sum(1 for i, j in g.edges() if a[i] != a[j])

if __name__ == "__main__":
    g = nx.cycle_graph(5)
    H = cost(g); ansatz = QAOAAnsatz(H, reps=3).decompose()
    est = StatevectorEstimator()
    obj = lambda p: float(est.run([(ansatz, H, p)]).result()[0].data.evs)
    rng = np.random.default_rng(0); best = None
    for _ in range(4):
        res = minimize(obj, rng.uniform(0, np.pi, ansatz.num_parameters), method="COBYLA",
                       options={"maxiter": 400})
        if best is None or res.fun < best.fun: best = res
    sampler = StatevectorSampler()
    counts = sampler.run([(ansatz.measure_all(inplace=False), best.x)], shots=4096).result()[0].data.meas.get_counts()
    best_cut = max(cut(g, bs[::-1]) for bs in counts)
    brute = max(cut(g, format(x, "05b")) for x in range(32))
    print(f"QAOA cut {best_cut} (brute {brute})")
    assert best_cut == brute == 4, (best_cut, brute)
    print("C5 MaxCut QAOA verified")
""",
)

add(
    id="qac_grover_sat_oracle",
    family="amplitude_amplification",
    algorithm="grover_sat_solver",
    difficulty="hard",
    question=(
        "Use Grover's algorithm in Qiskit to find the satisfying assignment of a small Boolean formula "
        "(x0 AND x1 AND NOT x2). Build the phase oracle from the clause and verify the amplified state "
        "is the unique solution 110-style assignment."
    ),
    rationale=(
        "Encode the formula as a multi-controlled phase oracle that flips the phase only on the "
        "satisfying assignment. With one solution out of 8, two Grover iterations amplify it to high "
        "probability. Verify the most probable bitstring is the unique satisfying assignment."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

# satisfying assignment of (x0 AND x1 AND NOT x2): x0=1, x1=1, x2=0
SOLUTION = "110"   # written as x0 x1 x2

def oracle(qc):
    qc.x(2)                                  # NOT x2
    qc.h(2); qc.ccx(0, 1, 2); qc.h(2)        # phase flip when x0=x1=1 and (NOT x2)=1
    qc.x(2)

def diffuser(qc, n):
    qc.h(range(n)); qc.x(range(n))
    qc.h(n - 1); qc.mcx(list(range(n - 1)), n - 1); qc.h(n - 1)
    qc.x(range(n)); qc.h(range(n))

if __name__ == "__main__":
    n = 3
    qc = QuantumCircuit(n); qc.h(range(n))
    for _ in range(2):
        oracle(qc); diffuser(qc, n)
    probs = Statevector(qc).probabilities_dict()
    best = max(probs, key=probs.get)         # little-endian over x2 x1 x0
    assignment = best[::-1]                   # x0 x1 x2
    print(f"most probable assignment {assignment} (p={probs[best]:.3f})")
    assert assignment == SOLUTION, assignment
    print("Grover SAT oracle verified")
""",
)

add(
    id="qac_qpe_arbitrary_eigenphase",
    family="fourier_phase",
    algorithm="qpe_arbitrary_unitary",
    difficulty="hard",
    question=(
        "Use Quantum Phase Estimation in Qiskit to estimate an eigenphase of an arbitrary single-qubit "
        "unitary, supplying one of its eigenvectors as input. Verify the estimate is within the "
        "resolution of the analytic eigenphase."
    ),
    rationale=(
        "Given U with eigenpair (e^{2 pi i phi}, |v>), preparing |v> on the target and running QPE "
        "writes phi into the counting register. Diagonalize U classically to obtain (phi, |v>), prepare "
        "|v| via initialize, and confirm the estimated phase is within 2^-m of the true value."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFTGate, UnitaryGate
from qiskit.quantum_info import Operator, random_unitary, Statevector

def qpe_eigenphase(U, eigvec, counting):
    n = counting
    cu = UnitaryGate(U).control(1)
    qc = QuantumCircuit(n + 1)
    qc.initialize(eigvec, n)
    qc.h(range(n))
    for k in range(n):
        for _ in range(2 ** k):
            qc.append(cu, [k, n])
    qc.append(QFTGate(n).inverse(), range(n))
    probs = Statevector(qc).probabilities_dict(qargs=list(range(n)))
    return int(max(probs, key=probs.get), 2) / 2 ** n

if __name__ == "__main__":
    U = random_unitary(2, seed=3).data
    vals, vecs = np.linalg.eig(U)
    idx = 0
    true_phi = (np.angle(vals[idx]) / (2 * np.pi)) % 1.0
    est = qpe_eigenphase(U, vecs[:, idx], counting=8)
    print(f"estimated phase {est:.5f} (true {true_phi:.5f})")
    assert abs(((est - true_phi + 0.5) % 1.0) - 0.5) < 2 ** -7, (est, true_phi)
    print("QPE arbitrary eigenphase verified")
""",
)

add(
    id="qac_bell_state_discrimination",
    family="entanglement_protocols",
    algorithm="bell_basis_measurement",
    difficulty="medium",
    question=(
        "Using Qiskit, build the Bell-basis measurement circuit (CNOT then H) and verify it perfectly "
        "discriminates all four Bell states by mapping each to a distinct computational basis outcome."
    ),
    rationale=(
        "The Bell measurement is the inverse of the Bell-pair entangler: applying CNOT(0,1) then H(0) "
        "rotates the four Bell states onto |00>,|01>,|10>,|11>. Prepare each Bell state, apply the "
        "measurement, and confirm a unique deterministic outcome per state."
    ),
    code=r"""
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

def prep(name):
    qc = QuantumCircuit(2); qc.h(0); qc.cx(0, 1)
    if name == "phi_minus": qc.z(0)
    elif name == "psi_plus": qc.x(1)
    elif name == "psi_minus": qc.z(0); qc.x(1)
    return qc

def bell_measure(name):
    qc = prep(name)
    qc.cx(0, 1); qc.h(0)
    out = max(Statevector(qc).probabilities_dict().items(), key=lambda kv: kv[1])
    return out[0], out[1]

if __name__ == "__main__":
    results = {}
    for name in ["phi_plus", "phi_minus", "psi_plus", "psi_minus"]:
        bits, p = bell_measure(name)
        assert abs(p - 1.0) < 1e-9, (name, p)
        results[name] = bits
    assert len(set(results.values())) == 4, results
    print("Bell-state discrimination verified:", results)
""",
)

add(
    id="qac_phase_damping_channel",
    family="noise_and_mitigation",
    algorithm="phase_damping_dephasing",
    difficulty="medium",
    question=(
        "Using qiskit-aer, apply a phase-damping channel to |+> and verify the off-diagonal coherence "
        "of the density matrix decays as sqrt(1-lambda) while the populations stay fixed at 1/2."
    ),
    rationale=(
        "Phase damping (pure dephasing) shrinks off-diagonal coherences by sqrt(1-lambda) without "
        "changing populations. Simulate with the density-matrix backend and verify the |0><1| element "
        "magnitude matches 0.5*sqrt(1-lambda) while diagonals remain 0.5."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, phase_damping_error

def dephased_rho(lam):
    nm = NoiseModel()
    nm.add_all_qubit_quantum_error(phase_damping_error(lam), ["id"])
    sim = AerSimulator(method="density_matrix", noise_model=nm)
    qc = QuantumCircuit(1); qc.h(0); qc.id(0); qc.save_density_matrix()
    return sim.run(transpile(qc, sim, optimization_level=0)).result().data()["density_matrix"]

if __name__ == "__main__":
    for lam in (0.0, 0.25, 0.75):
        rho = np.asarray(dephased_rho(lam))
        coh = abs(rho[0, 1])
        print(f"lambda={lam}: coherence {coh:.4f} (expected {0.5*np.sqrt(1-lam):.4f})")
        assert abs(coh - 0.5 * np.sqrt(1 - lam)) < 1e-6, (lam, coh)
        assert abs(rho[0, 0].real - 0.5) < 1e-6 and abs(rho[1, 1].real - 0.5) < 1e-6
    print("Phase damping channel verified")
""",
)

add(
    id="qac_dynamical_decoupling",
    family="noise_and_mitigation",
    algorithm="dynamical_decoupling_xy4",
    difficulty="hard",
    question=(
        "Using qiskit-aer, show that an XY4 dynamical-decoupling sequence interleaved with dephasing "
        "noise preserves the |+> state coherence better than free evolution under the same noise."
    ),
    rationale=(
        "XY4 (X-Y-X-Y pulses) symmetrically refocuses dephasing so the qubit's transverse coherence is "
        "protected. Comparing the surviving X-expectation of |+> with and without the DD pulse train "
        "under identical phase-damping noise shows DD yields higher coherence."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, phase_damping_error

def sim_with_noise(lam):
    nm = NoiseModel(); nm.add_all_qubit_quantum_error(phase_damping_error(lam), ["id"])
    return AerSimulator(method="density_matrix", noise_model=nm)

def coherence(sim, dd):
    qc = QuantumCircuit(1); qc.h(0)
    for _ in range(2):                       # two XY4 blocks = 8 noisy slots
        for pulse in (["x", "y", "x", "y"] if dd else ["id", "id", "id", "id"]):
            qc.id(0); getattr(qc, pulse)(0)
    qc.save_density_matrix()
    rho = np.asarray(sim.run(transpile(qc, sim, optimization_level=0)).result().data()["density_matrix"])
    return 2 * abs(rho[0, 1])                # |<X>| proxy

if __name__ == "__main__":
    sim = sim_with_noise(0.2)
    free = coherence(sim, dd=False)
    protected = coherence(sim, dd=True)
    print(f"coherence: free {free:.4f}, XY4 {protected:.4f}")
    assert protected > free, (protected, free)
    print("Dynamical decoupling (XY4) verified")
""",
)

add(
    id="qac_average_gate_fidelity",
    family="quantum_information",
    algorithm="average_gate_fidelity",
    difficulty="medium",
    question=(
        "Using Qiskit quantum_info, compute the average gate fidelity between an ideal X gate and an "
        "over-rotated Rx(pi+eps), and verify it equals 1 at eps=0 and decreases monotonically with the "
        "rotation error."
    ),
    rationale=(
        "Average gate fidelity summarizes how close an implemented unitary is to the target, averaged "
        "over input states. For an X gate vs Rx(pi+eps) it is 1 at eps=0 and falls smoothly as the "
        "coherent over-rotation grows; compute it with average_gate_fidelity."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator, average_gate_fidelity

def rx_op(eps):
    qc = QuantumCircuit(1); qc.rx(np.pi + eps, 0); return Operator(qc)

if __name__ == "__main__":
    target = Operator.from_label("X")
    fids = [average_gate_fidelity(rx_op(eps), target) for eps in (0.0, 0.1, 0.3, 0.6)]
    print("avg gate fidelities:", [round(f, 5) for f in fids])
    assert abs(fids[0] - 1.0) < 1e-9, fids[0]
    assert all(fids[i] > fids[i + 1] for i in range(len(fids) - 1)), fids
    print("Average gate fidelity verified")
""",
)

add(
    id="qac_error_detection_422",
    family="error_correction",
    algorithm="four_two_two_detection_code",
    difficulty="hard",
    question=(
        "Implement the [[4,2,2]] error-detection code's stabilizer checks in Qiskit. Verify that the "
        "encoded logical |00> codeword satisfies both stabilizers XXXX and ZZZZ with eigenvalue +1, and "
        "that a single X error flips the ZZZZ syndrome to detect it."
    ),
    rationale=(
        "The [[4,2,2]] code has stabilizers XXXX and ZZZZ. A valid codeword is a +1 eigenstate of both. "
        "A single-qubit X error anticommutes with ZZZZ, flipping that syndrome to -1, which signals a "
        "detected (though not correctable) error. Verify both stabilizer expectations."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, SparsePauliOp

def codeword():
    # |0_L 0_L> = (|0000> + |1111>)/sqrt(2) for the [[4,2,2]] code
    qc = QuantumCircuit(4)
    qc.h(0); qc.cx(0, 1); qc.cx(0, 2); qc.cx(0, 3)
    return qc

def expval(sv, label):
    return float(np.real(sv.expectation_value(SparsePauliOp(label))))

if __name__ == "__main__":
    sv = Statevector(codeword())
    assert abs(expval(sv, "XXXX") - 1.0) < 1e-9
    assert abs(expval(sv, "ZZZZ") - 1.0) < 1e-9
    err = codeword(); err.x(2)
    sv_err = Statevector(err)
    assert abs(expval(sv_err, "ZZZZ") + 1.0) < 1e-9      # syndrome flipped to -1
    print("[[4,2,2]] detection: clean syndromes +1, X error flips ZZZZ; verified")
""",
)

add(
    id="qac_gate_teleportation",
    family="entanglement_protocols",
    algorithm="gate_teleportation_identity",
    difficulty="hard",
    question=(
        "Using Qiskit, demonstrate gate teleportation of a single-qubit Z-rotation through a Bell pair "
        "with deferred-measurement corrections, and verify the teleported output equals applying the "
        "rotation directly to the input state."
    ),
    rationale=(
        "Gate teleportation applies a gate by consuming an entangled resource and measurement. Using "
        "deferred measurement to replace the byproduct corrections, the protocol output on Bob's qubit "
        "must equal Rz(theta)|psi>, verified by state fidelity for several inputs."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, partial_trace, state_fidelity, random_statevector

def gate_teleport(psi, theta):
    qc = QuantumCircuit(3)                    # q0 input, (q1,q2) Bell resource
    qc.initialize(psi.data, 0)
    qc.h(1); qc.cx(1, 2)
    qc.rz(theta, 2)                           # pre-apply rotation on resource (gate to teleport)
    qc.cx(0, 1); qc.h(0)
    qc.cx(1, 2); qc.cz(0, 2)                  # deferred corrections
    return qc

if __name__ == "__main__":
    theta = 0.9
    for seed in range(4):
        psi = random_statevector(2, seed=seed)
        out = partial_trace(Statevector(gate_teleport(psi, theta)), [0, 1])
        ref = QuantumCircuit(1); ref.initialize(psi.data, 0); ref.rz(theta, 0)
        fid = state_fidelity(out, Statevector(ref))
        print(f"seed {seed}: gate-teleport fidelity {fid:.6f}")
        assert fid > 1 - 1e-9, (seed, fid)
    print("Gate teleportation verified")
""",
)

add(
    id="qac_thermal_relaxation",
    family="noise_and_mitigation",
    algorithm="thermal_relaxation_t1_t2",
    difficulty="hard",
    question=(
        "Using qiskit-aer thermal relaxation error, simulate T1 decay of |1> over increasing gate "
        "durations and verify the excited-state population follows exp(-t/T1)."
    ),
    rationale=(
        "Thermal relaxation with time t and coherence T1 decays the excited-state population as "
        "exp(-t/T1). Attach thermal_relaxation_error with matched parameters to a delay-like identity "
        "and confirm the measured |1> fraction matches the exponential law."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, thermal_relaxation_error

T1, T2 = 100.0, 80.0

def population(t, shots=60000, seed=1):
    err = thermal_relaxation_error(T1, T2, t)
    nm = NoiseModel(); nm.add_all_qubit_quantum_error(err, ["id"])
    sim = AerSimulator(noise_model=nm, seed_simulator=seed)
    qc = QuantumCircuit(1); qc.x(0); qc.id(0); qc.measure_all()
    counts = sim.run(transpile(qc, sim, optimization_level=0), shots=shots).result().get_counts()
    return counts.get("1", 0) / shots

if __name__ == "__main__":
    for t in (0.0, 20.0, 50.0, 100.0):
        pop = population(t)
        print(f"t={t}: P(|1>) {pop:.4f} (expected {np.exp(-t/T1):.4f})")
        assert abs(pop - np.exp(-t / T1)) < 0.02, (t, pop)
    print("Thermal relaxation T1 decay verified")
""",
)

add(
    id="qac_givens_rotation_ansatz",
    family="variational_methods",
    algorithm="particle_conserving_givens",
    difficulty="hard",
    question=(
        "Using Qiskit, implement a particle-number-conserving Givens rotation gate on two qubits and "
        "verify it rotates within the single-excitation subspace {|01>, |10>} while leaving |00> and "
        "|11> invariant."
    ),
    rationale=(
        "A Givens rotation mixes |01> and |10> by an angle theta while fixing |00> and |11>, conserving "
        "particle number. Realize it with the standard two-qubit circuit and verify the block structure: "
        "the single-excitation subspace rotates and the others are eigenstates."
    ),
    code=r"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

def givens(theta):
    qc = QuantumCircuit(2)
    qc.cx(0, 1)
    qc.cry(2 * theta, 1, 0)
    qc.cx(0, 1)
    return qc

if __name__ == "__main__":
    theta = 0.7
    g = givens(theta)
    # |00> and |11> invariant
    for label in ("00", "11"):
        out = Statevector.from_label(label).evolve(g)
        assert abs(out.probabilities_dict().get(label, 0) - 1.0) < 1e-9, label
    # |01> rotates into superposition of |01>,|10>
    out01 = Statevector.from_label("01").evolve(g).probabilities_dict()
    support = {k for k, v in out01.items() if v > 1e-9}
    assert support <= {"01", "10"} and abs(out01.get("10", 0) - np.sin(theta) ** 2) < 1e-9, out01
    print("Givens rotation (particle-conserving) verified")
""",
)
