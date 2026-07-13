#!/usr/bin/env python3
"""Reference solutions for iter-3 gap-targeted tasks.

Each solution is a complete, runnable Python program that satisfies the task
prompt. These replace the ``__TEACHER_PENDING__`` markers in the iter-3 gap
rows with actual teacher-quality code that student models can learn from.

Solutions are designed to:
- Be self-contained (no external file dependencies)
- Print deterministic output (for eval verification)
- Use the correct framework API (braket/cirq/pennylane/qiskit)
- Include ``def main()`` per the full-program contract
- Be LIMA-style: clear, correct, minimal
"""

from __future__ import annotations

# ── A1: quantum_qaoa_maxcut_5cycle ───────────────────────────────────────────
QISKIT_QAOA_MAXCUT_5CYCLE = '''"""
QAOA Max-Cut on a 5-node cycle graph using Qiskit (StatevectorSampler).
Prints the deterministic cut value.

5-cycle: 0-1-2-3-4-0. Max-Cut = 4 (put 0,2,4 in one set and 1,3 in the other,
or any alternating assignment on an odd cycle leaves one edge uncut).
"""
import networkx as nx
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorSampler
from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA


def build_maxcut_pauli(edges, n):
    """Build the Max-Cut Hamiltonian  sum_{(i,j)} (Z_i Z_j - I)/2 as a SparsePauliOp."""
    paulis = []
    coeffs = []
    for i, j in edges:
        z = ["I"] * n
        z[i] = "Z"
        z[j] = "Z"
        paulis.append("".join(reversed(z)))  # Qiskit little-endian
        coeffs.append(0.5)
        paulis.append("I" * n)
        coeffs.append(-0.5)
    return SparsePauliOp.from_list(list(zip(paulis, coeffs)))


def main():
    n = 5
    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]
    G = nx.Graph()
    G.add_edges_from(edges)
    cost_op = build_maxcut_pauli(edges, n)

    sampler = StatevectorSampler(seed=42)
    qaoa = QAOA(sampler=sampler, optimizer=COBYLA(maxiter=200), reps=1)
    result = qaoa.compute_minimum_eigenvalue(cost_op)

    # Sample the optimal bitstring
    qc = qaoa.ansatz.assign_parameters(result.x)
    qc.measure_all()
    samples = sampler.run([qc], shots=1024).result()[0].data.meas.get_counts()
    best = max(samples, key=samples.get)
    bits = [int(b) for b in reversed(best)]  # little-endian -> node order

    cut = sum(1 for i, j in edges if bits[i] != bits[j])
    print(f"max-cut = {cut}")


if __name__ == "__main__":
    main()
'''

# ── A2a: quantum_partial_trace_bipartite ──────────────────────────────────────
QISKIT_PARTIAL_TRACE_BIPARTITE = '''"""
Reduced density matrix of a bipartite pure state using qiskit.quantum_info.
Demonstrates correct @ operator semantics for DensityMatrix multiplication.
"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import DensityMatrix, Statevector, partial_trace


def main():
    # Build a bipartite pure state |psi> = (|00> + |11>)/sqrt(2) on qubits A, B
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    psi = Statevector(qc)

    rho = DensityMatrix(psi)
    # Reduced density matrix of qubit A (trace out qubit B, index 1)
    rho_A = partial_trace(rho, [1])
    # Reduced density matrix of qubit B (trace out qubit A, index 0)
    rho_B = partial_trace(rho, [0])

    # Demonstrate @ operator semantics: rho @ rho should equal rho for a pure state
    rho_squared = rho @ rho
    purity = np.trace(rho_squared.data).real

    print("Full density matrix (4x4):")
    print(rho.data.round(4))
    print("Reduced density matrix of A (2x2):")
    print(rho_A.data.round(4))
    print("Reduced density matrix of B (2x2):")
    print(rho_B.data.round(4))
    print(f"Purity Tr(rho @ rho) = {purity:.6f} (pure state -> 1.0)")


if __name__ == "__main__":
    main()
'''

# ── A2b: quantum_density_matrix_pure_state ────────────────────────────────────
QISKIT_DENSITY_MATRIX_PURE_STATE = '''"""
Density matrix construction and pure-state verification using qiskit.quantum_info.
Shows that a pure state has Tr(rho^2) = 1 and demonstrates the @ operator.
"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import DensityMatrix, Statevector


def main():
    # Build a 3-qubit GHZ state
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(1, 2)
    psi = Statevector(qc)

    rho = DensityMatrix(psi)
    rho_squared = rho @ rho
    purity = np.trace(rho_squared.data).real

    # For a pure state, rho is idempotent: rho @ rho == rho
    is_idempotent = np.allclose(rho.data, rho_squared.data, atol=1e-9)

    print("Density matrix shape:", rho.data.shape)
    print(f"Tr(rho)   = {np.trace(rho.data).real:.6f}")
    print(f"Tr(rho^2) = {purity:.6f}")
    print(f"Idempotent (rho @ rho == rho): {is_idempotent}")
    print("Diagonal:", np.diag(rho.data).real.round(4))


if __name__ == "__main__":
    main()
'''

# ── A3a: quantum_grover_two_marked ────────────────────────────────────────────
QISKIT_GROVER_TWO_MARKED = '''"""
Grover's algorithm for 2 marked items in a 4-item database (2 qubits).
Uses qiskit.circuit.library.Grover and prints the marked items found.
"""
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.circuit.library import Grover


def main():
    # Oracle: mark |01> and |10> (the two non-trivial bitstrings)
    # Construct an oracle that flips the phase of |01> and |10>.
    oracle = QuantumCircuit(2)
    # Mark |01>: X on qubit 1, then controlled-Z, then X on qubit 1
    oracle.x(1)
    oracle.cz(0, 1)
    oracle.x(1)
    # Mark |10>: X on qubit 0, then controlled-Z, then X on qubit 0
    oracle.x(0)
    oracle.cz(0, 1)
    oracle.x(0)

    grover = Grover(oracle=oracle, num_iterations=1)
    full = grover.grover_circuit

    sv = Statevector(full)
    probs = sv.probabilities_dict()
    # The two marked states |01> and |10> should have the highest probabilities
    marked = sorted(probs, key=probs.get, reverse=True)[:2]
    print("Grover found marked items:", marked)


if __name__ == "__main__":
    main()
'''

# ── A3b: quantum_qft_entangled ────────────────────────────────────────────────
QISKIT_QFT_ENTANGLED = '''"""
Quantum Fourier Transform on an entangled 3-qubit state using Qiskit.
Applies QFT to a GHZ state and prints the resulting statevector.
"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.circuit.library import QFT


def main():
    # Build GHZ state on 3 qubits
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(1, 2)
    # Apply QFT
    qc.append(QFT(3), range(3))

    sv = Statevector(qic := qc)
    probs = sv.probabilities_dict()

    print("QFT(GHZ_3) statevector amplitudes:")
    for basis, amp in sorted(sv.to_dict().items()):
        print(f"  |{basis}>: {amp:.4f}")
    print("Top measurement probabilities:")
    for b, p in sorted(probs.items(), key=lambda kv: kv[1], reverse=True)[:4]:
        print(f"  |{b}>: {p:.4f}")


if __name__ == "__main__":
    main()
'''

# ── A4a: quantum_teleportation_fidelity ───────────────────────────────────────
QISKIT_TELEPORTATION_FIDELITY = '''"""
Quantum teleportation with fidelity verification using Qiskit.
Teleports |+> from Alice to Bob and measures <X> on Bob's qubit.
Prints exactly: <X> on Bob = 1.000000
"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, SparsePauliOp, DensityMatrix
from qiskit.primitives import StatevectorSampler


def main():
    # Build the teleportation circuit (no classical control for statevector analysis)
    # q0 = state to teleport (|+>), q1 = Alice's half of Bell pair, q2 = Bob's half
    qc = QuantumCircuit(3, 2)
    # Prepare |+> on q0
    qc.h(0)
    # Create Bell pair on q1, q2
    qc.h(1)
    qc.cx(1, 2)
    # Alice's Bell measurement
    qc.cx(0, 1)
    qc.h(0)
    qc.measure(0, 0)
    qc.measure(1, 1)
    # Bob's corrections (conditionally, but for statevector we simulate post-selected)
    qc.cx(1, 2)
    qc.cz(0, 2)

    # Simulate with density matrix to compute <X> on Bob (qubit 2)
    # Use StatevectorSampler to get counts, but for fidelity we use the ideal:
    # after teleporting |+>, Bob's state is |+>, so <X> = 1
    rho_full = DensityMatrix(Statevector(qc.remove_final_measurements(inplace=False)))
    # Trace out Alice's qubits (0, 1) to get Bob's reduced state (qubit 2)
    from qiskit.quantum_info import partial_trace
    rho_bob = partial_trace(rho_full, [0, 1])
    x_op = SparsePauliOp.from_list([("X", 1.0)])
    x_exp = rho_bob.expectation_value(x_op).real

    print(f"<X> on Bob = {x_exp:.6f}")


if __name__ == "__main__":
    main()
'''

# ── A4b: quantum_swap_test_overlap ────────────────────────────────────────────
QISKIT_SWAP_TEST_OVERLAP = '''"""
SWAP test to compute the overlap between two identical quantum states.
Prints exactly: overlap = 1.000000
"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.primitives import StatevectorSampler


def main():
    # SWAP test: ancilla q0, states on q1 and q2 (both |1> here -> identical)
    qc = QuantumCircuit(3, 1)
    # Prepare identical states on q1 and q2
    qc.x(1)
    qc.x(2)
    # SWAP test
    qc.h(0)
    qc.cswap(0, 1, 2)
    qc.h(0)
    qc.measure(0, 0)

    sampler = StatevectorSampler(seed=42)
    result = sampler.run([qc], shots=8192).result()[0]
    counts = result.data.c.get_counts()
    p0 = counts.get("0", 0) / sum(counts.values())
    overlap = 2 * p0 - 1  # |<psi|phi>|^2 = 2*P(0) - 1

    print(f"overlap = {overlap:.6f}")


if __name__ == "__main__":
    main()
'''

# ── A5a: quantum_deutsch_jozsa_balanced ───────────────────────────────────────
QISKIT_DEUTSCH_JOZSA_BALANCED = '''"""
Deutsch-Jozsa algorithm for a balanced oracle using Qiskit.
Includes explicit circuit construction and prints "balanced" or "constant".
"""
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector


def build_balanced_oracle(n: int) -> QuantumCircuit:
    """Balanced oracle: f(x) = x_0 (flips phase for half the inputs)."""
    oracle = QuantumCircuit(n + 1)
    # f(x) = x_0: controlled-X from qubit 0 to ancilla
    oracle.cx(0, n)
    return oracle


def main():
    n = 3  # number of input qubits
    oracle = build_balanced_oracle(n)

    qc = QuantumCircuit(n + 1, n)
    # Ancilla in |-> state
    qc.x(n)
    qc.h(n)
    # Superposition on inputs
    qc.h(range(n))
    # Oracle
    qc.compose(oracle, inplace=True)
    # H on inputs
    qc.h(range(n))
    # Measure inputs
    qc.measure(range(n), range(n))

    sv = Statevector(qc.remove_final_measurements(inplace=False))
    probs = sv.probabilities_dict()
    # For a balanced function, the probability of measuring all-zeros is 0
    p_zero = probs.get("0" * (n + 1), 0.0)

    if p_zero < 1e-9:
        print("balanced")
    else:
        print("constant")


if __name__ == "__main__":
    main()
'''

# ── A5b: quantum_bernstein_vazirani_hidden ────────────────────────────────────
QISKIT_BERNSTEIN_VAZIRANI_HIDDEN = '''"""
Bernstein-Vazirani algorithm for a hidden string s using Qiskit.
Recovers s = "1011" (4 qubits, little-endian: bit 0 = '1', bit 1 = '1',
bit 2 = '0', bit 3 = '1').
"""
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector


def build_bv_oracle(s: str) -> QuantumCircuit:
    """Oracle for f(x) = s . x mod 2. s is given big-endian for readability."""
    n = len(s)
    oracle = QuantumCircuit(n + 1)
    # s = "1011" -> apply CX from qubit i to ancilla where s[i] == '1'
    for i, bit in enumerate(reversed(s)):  # little-endian
        if bit == "1":
            oracle.cx(i, n)
    return oracle


def main():
    s = "1011"
    n = len(s)
    oracle = build_bv_oracle(s)

    qc = QuantumCircuit(n + 1, n)
    qc.x(n)
    qc.h(n)
    qc.h(range(n))
    qc.compose(oracle, inplace=True)
    qc.h(range(n))
    qc.measure(range(n), range(n))

    sv = Statevector(qc.remove_final_measurements(inplace=False))
    probs = sv.probabilities_dict()
    # The measured bitstring (on input qubits) encodes s in little-endian.
    # Pick the most probable outcome.
    best = max(probs, key=probs.get)
    # best is a string of length n+1 (includes ancilla). Input qubits are the
    # first n in Qiskit's little-endian convention; reverse to get big-endian s.
    measured = best[-n:][::-1]  # last n chars reversed -> big-endian
    print(measured)


if __name__ == "__main__":
    main()
'''

# ── B1: quantum_braket_bell_state ────────────────────────────────────────────
BRAKET_BELL_STATE = '''"""
Bell state construction and simulation using Amazon Braket.
Prints measurement statistics showing ~50% '00' and ~50% '11'.
"""
from braket.circuits import Circuit
from braket.devices import LocalSimulator


def main():
    # Build Bell state: |00> -> H(0) -> CNOT(0,1) -> |00>+|11>
    circuit = Circuit()
    circuit.h(0)
    circuit.cnot(0, 1)

    # Run on local simulator with 1000 shots
    device = LocalSimulator()
    result = device.run(circuit, shots=1000).result()

    # Aggregate measurement counts
    counts = result.measurement_counts
    print("Measurement statistics:")
    for state, count in sorted(counts.items()):
        prob = count / 1000.0
        print(f"  |{state}>: {count} shots ({prob:.1%})")

    # Verify Bell state correlations
    total = sum(counts.values())
    bell_count = counts.get("00", 0) + counts.get("11", 0)
    print(f"Bell correlation (00+11): {bell_count}/{total} = {bell_count/total:.1%}")


if __name__ == "__main__":
    main()
'''

# ── B2: quantum_cirq_qaoa_line ───────────────────────────────────────────────
CIRQ_QAOA_LINE = '''"""
QAOA Max-Cut on a 3-node line graph using Cirq.
Prints the deterministic cut value.
"""
import numpy as np
import cirq


def main():
    # 3-node line graph: 0 -- 1 -- 2
    # Max-Cut: {0, 2} vs {1} gives cut=2
    n = 3
    edges = [(0, 1), (1, 2)]
    qubits = cirq.LineQubit.range(n)

    # QAOA with p=1 layer
    gamma = 0.5
    beta = 0.3

    circuit = cirq.Circuit()
    # Initial state: uniform superposition
    circuit.append(cirq.H.on_each(qubits))
    # Cost unitary: exp(-i * gamma * H_C)
    for i, j in edges:
        circuit.append(cirq.ZZPowGate(exponent=2 * gamma / np.pi).on(qubits[i], qubits[j]))
    # Mixer unitary: exp(-i * beta * H_M)
    circuit.append(cirq.XPowGate(exponent=2 * beta / np.pi).on_each(qubits))
    # Measure
    circuit.append(cirq.measure(*qubits, key="m"))

    # Simulate
    simulator = cirq.Simulator()
    result = simulator.run(circuit, repetitions=10000)

    # Find best cut from measurement results
    measurements = result.measurements["m"]
    best_cut = 0
    best_assignment = None
    for bits in measurements:
        cut = 0
        for i, j in edges:
            if bits[i] != bits[j]:
                cut += 1
        if cut > best_cut:
            best_cut = cut
            best_assignment = tuple(bits)

    print(f"QAOA Max-Cut on 3-node line graph")
    print(f"Best cut value: {best_cut}")
    print(f"Best assignment: {best_assignment}")


if __name__ == "__main__":
    main()
'''

# ── B3: quantum_pennylane_vqe_h2 ─────────────────────────────────────────────
PENNYLANE_VQE_H2 = '''"""
VQE on H2 molecule using PennyLane.
Prints the ground-state energy (approximately -1.136 Ha).
"""
import pennylane as qml
from pennylane import numpy as np


def main():
    # H2 molecule, STO-3G basis, bond length 0.74 Angstrom
    symbols = ["H", "H"]
    coordinates = np.array([0.0, 0.0, -0.6614, 0.0, 0.0, 0.6614])

    # Build molecular Hamiltonian
    hamiltonian, qubits = qml.qchem.molecular_hamiltonian(
        symbols, coordinates, basis="sto-3g"
    )

    # Define ansatz: Hartree-Fock + single/double excitations
    dev = qml.device("default.qubit", wires=qubits)

    @qml.qnode(dev)
    def circuit(params):
        qml.BasisState(np.array([1, 1, 0, 0]), wires=range(qubits))
        qml.DoubleExcitation(params[0], wires=[0, 1, 2, 3])
        qml.DoubleExcitation(params[1], wires=[0, 1, 2, 3])
        return qml.expval(hamiltonian)

    # Optimize using gradient descent
    params = np.array([0.0, 0.0], requires_grad=True)
    optimizer = qml.GradientDescentOptimizer(stepsize=0.4)

    energy = circuit(params)
    for i in range(50):
        params, energy = optimizer.step_and_cost(circuit, params)

    print(f"VQE H2 ground-state energy: {energy:.6f} Ha")
    print(f"Optimal parameters: {params}")
    print(f"Qubits: {qubits}")


if __name__ == "__main__":
    main()
'''

# ── B4: quantum_qiskit_qft_entangled ─────────────────────────────────────────
QISKIT_QFT_ENTANGLED = '''"""
QFT on an entangled input state using Qiskit.
Prints the resulting statevector.
"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector


def main():
    n = 3
    qc = QuantumCircuit(n)

    # Create entangled input: H(0) -> CNOT(0,1) -> CNOT(1,2) = |000> + |111>
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(1, 2)

    # Apply QFT
    for i in range(n):
        qc.h(i)
        for j in range(i + 1, n):
            qc.cp(np.pi / 2 ** (j - i), j, i)
        # Swap to match standard QFT ordering
    for i in range(n // 2):
        qc.swap(i, n - 1 - i)

    # Get statevector
    sv = Statevector(qc)
    print(f"QFT of entangled state |000>+|111>:")
    print(f"Statevector (3 qubits):")
    for i, amp in enumerate(sv.data):
        if abs(amp) > 1e-10:
            basis = format(i, f"0{n}b")
            print(f"  |{basis}>: {amp:.6f}")

    print(f"\\nCircuit depth: {qc.depth()}")
    print(f"Number of gates: {qc.size()}")


if __name__ == "__main__":
    main()
'''

# ── B5: quantum_pennylane_qml_iris_classification ────────────────────────────
PENNYLANE_QML_IRIS = '''"""
Iris classification using PennyLane's variational quantum classifier.
Prints the classification accuracy.
"""
import pennylane as qml
from pennylane import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


def main():
    # Load Iris dataset (binary: setosa vs versicolor for simplicity)
    iris = load_iris()
    X = iris.data[:100]  # first 100 samples (setosa + versicolor)
    y = iris.target[:100]
    y = np.where(y == 0, -1, 1)  # map to {-1, +1}

    # Normalize features
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Quantum device: 2 qubits (for 4 features via angle embedding)
    n_qubits = 2
    dev = qml.device("default.qubit", wires=n_qubits)

    @qml.qnode(dev)
    def circuit(weights, x):
        qml.AngleEmbedding(x, wires=range(n_qubits), rotation="Y")
        qml.BasicEntanglerLayers(weights, wires=range(n_qubits))
        return qml.expval(qml.PauliZ(0))

    def variational_classifier(weights, bias, x):
        return circuit(weights, x) + bias

    # Initialize parameters
    n_layers = 3
    weights = 0.01 * np.random.randn(n_layers, n_qubits, requires_grad=True)
    bias = np.array(0.0, requires_grad=True)

    # Training
    opt = qml.GradientDescentOptimizer(stepsize=0.1)
    batch_size = 20
    for epoch in range(20):
        idx = np.random.choice(len(X_train), batch_size, replace=False)
        X_batch = X_train[idx]
        y_batch = y_train[idx]

        def cost(w, b):
            preds = np.array([variational_classifier(w, b, x) for x in X_batch])
            return np.mean((preds - y_batch) ** 2)

        weights, bias = opt.step(cost, weights, bias)

    # Evaluate
    predictions = []
    for x in X_test:
        pred = variational_classifier(weights, bias, x)
        predictions.append(1 if pred > 0 else -1)

    accuracy = np.mean(np.array(predictions) == y_test)
    print(f"Quantum Iris Classifier (PennyLane)")
    print(f"Training samples: {len(X_train)}, Test samples: {len(X_test)}")
    print(f"Qubits: {n_qubits}, Layers: {n_layers}")
    print(f"Classification accuracy: {accuracy:.1%}")


if __name__ == "__main__":
    main()
'''

# ── C1: software_log_parser_aggregator ───────────────────────────────────────
LOG_PARSER_AGGREGATOR = '''"""
Log file parser and level aggregator.
Parses 'timestamp level message' format and prints a summary table.
"""
import sys
from collections import Counter
from io import StringIO


SAMPLE_LOG = """2026-07-12T10:00:00 INFO Application started
2026-07-12T10:00:01 DEBUG Loading configuration
2026-07-12T10:00:02 INFO Server listening on port 8080
2026-07-12T10:00:05 WARNING High memory usage detected
2026-07-12T10:00:10 ERROR Failed to connect to database
2026-07-12T10:00:11 INFO Retrying connection
2026-07-12T10:00:12 ERROR Database connection timeout
2026-07-12T10:00:15 INFO Connection restored
2026-07-12T10:00:20 WARNING Disk space below 10%
2026-07-12T10:00:25 INFO Backup completed"""


def parse_log_line(line):
    """Parse 'timestamp level message' format."""
    parts = line.strip().split(" ", 2)
    if len(parts) < 3:
        return None
    return {"timestamp": parts[0], "level": parts[1], "message": parts[2]}


def aggregate_by_level(entries):
    """Count log entries by level."""
    return Counter(e["level"] for e in entries)


def main():
    # Read from stdin or sample data
    log_source = sys.stdin if not sys.stdin.isatty() else StringIO(SAMPLE_LOG)

    entries = []
    for line in log_source:
        entry = parse_log_line(line)
        if entry:
            entries.append(entry)

    counts = aggregate_by_level(entries)

    print("Log Level Summary")
    print("=" * 40)
    print(f"{'Level':<10} {'Count':>6} {'Percentage':>12}")
    print("-" * 40)
    total = sum(counts.values())
    for level in sorted(counts.keys()):
        count = counts[level]
        pct = count / total * 100 if total > 0 else 0
        print(f"{level:<10} {count:>6} {pct:>11.1f}%")
    print("-" * 40)
    print(f"{'TOTAL':<10} {total:>6} {'100.0%':>12}")


if __name__ == "__main__":
    main()
'''

# ── C2: software_sql_join_resolver ───────────────────────────────────────────
SQL_JOIN_RESOLVER = '''"""
SQL JOIN resolver for in-memory tables.
Joins 'users' and 'orders' tables and prints the result.
"""


def main():
    # In-memory tables
    users = [
        {"user_id": 1, "name": "Alice", "email": "alice@example.com"},
        {"user_id": 2, "name": "Bob", "email": "bob@example.com"},
        {"user_id": 3, "name": "Carol", "email": "carol@example.com"},
    ]

    orders = [
        {"order_id": 101, "user_id": 1, "product": "Laptop", "amount": 1200},
        {"order_id": 102, "user_id": 2, "product": "Phone", "amount": 800},
        {"order_id": 103, "user_id": 1, "product": "Mouse", "amount": 25},
        {"order_id": 104, "user_id": 3, "product": "Tablet", "amount": 500},
    ]

    # Build index on users for O(1) lookup
    user_index = {u["user_id"]: u for u in users}

    # INNER JOIN: users.user_id = orders.user_id
    # Project: name, email, order_id, product, amount
    joined = []
    for order in orders:
        user = user_index.get(order["user_id"])
        if user:
            joined.append({
                "name": user["name"],
                "email": user["email"],
                "order_id": order["order_id"],
                "product": order["product"],
                "amount": order["amount"],
            })

    # Print result table
    print("INNER JOIN users + orders (on user_id)")
    print("=" * 70)
    print(f"{'name':<8} {'email':<25} {'order_id':>8} {'product':<10} {'amount':>8}")
    print("-" * 70)
    for row in joined:
        print(f"{row['name']:<8} {row['email']:<25} {row['order_id']:>8} "
              f"{row['product']:<10} {row['amount']:>8}")
    print("-" * 70)
    print(f"Total joined rows: {len(joined)}")

    # Aggregate: total amount per user
    print("\\nOrder totals per user:")
    from collections import defaultdict
    totals = defaultdict(float)
    for row in joined:
        totals[row["name"]] += row["amount"]
    for name, total in sorted(totals.items()):
        print(f"  {name}: ${total:.2f}")


if __name__ == "__main__":
    main()
'''

# ── Solution registry ────────────────────────────────────────────────────────
SOLUTIONS = {
    "A1": QISKIT_QAOA_MAXCUT_5CYCLE,
    "A2a": QISKIT_PARTIAL_TRACE_BIPARTITE,
    "A2b": QISKIT_DENSITY_MATRIX_PURE_STATE,
    "A3a": QISKIT_GROVER_TWO_MARKED,
    "A3b": QISKIT_QFT_ENTANGLED,
    "A4a": QISKIT_TELEPORTATION_FIDELITY,
    "A4b": QISKIT_SWAP_TEST_OVERLAP,
    "A5a": QISKIT_DEUTSCH_JOZSA_BALANCED,
    "A5b": QISKIT_BERNSTEIN_VAZIRANI_HIDDEN,
    "B1": BRAKET_BELL_STATE,
    "B2": CIRQ_QAOA_LINE,
    "B3": PENNYLANE_VQE_H2,
    "B4": QISKIT_QFT_ENTANGLED,
    "B5": PENNYLANE_QML_IRIS,
    "C1": LOG_PARSER_AGGREGATOR,
    "C2": SQL_JOIN_RESOLVER,
}


def get_solution(row_id: str) -> str | None:
    """Return the reference solution for a gap row ID, or None if not available."""
    return SOLUTIONS.get(row_id)


if __name__ == "__main__":
    print(f"Reference solutions available for {len(SOLUTIONS)} gap rows:")
    for row_id in sorted(SOLUTIONS.keys()):
        lines = SOLUTIONS[row_id].count("\n") + 1
        print(f"  {row_id}: {lines} lines")
