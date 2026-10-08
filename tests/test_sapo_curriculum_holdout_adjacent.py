"""TDD gate for the SAPO holdout-adjacent curriculum (v8 training tasks).

2026-08-24 curriculum-builder workstream (manager directive 20:18 CST).
Every arm ties base at 8/18 on the frozen holdout because the training
manifest (targeted10) is disjoint from the holdout failure competences.
These tests lock the NEW holdout-adjacent tasks (same required skills, disjoint
instances/contracts) to four properties:

(a) every new task's reference candidate passes its own harness;
(b) each task's failure details parse to shaped > 0 for a plausible
    near-miss candidate (numeric graded feedback, enriched-harness
    conventions), and None-returning stubs are graded, not crashes;
(c) no new task overlaps the frozen holdout by ID or prompt (phrase +
    token-overlap isolation, reusing the conventions of
    test_promotion_eval_prompt_isolation.py);
(d) the new manifest regenerates deterministically with a valid header
    hash (task_contract_sha256 over sorted task.json + tests.py bytes,
    matching build_sapo_distill_question_manifest.task_contract_hash).

The frozen holdout sapo_promotion_holdout_v1_18.txt is read-only here.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from evals.runner.public_task_spec import build_public_task_spec
from training.grpo_utils import shaped_reward_from_details

ROOT = Path(__file__).resolve().parents[1]
HOLDOUT_MANIFEST = ROOT / "evals/benchmarks/sapo_promotion_holdout_v1_18.txt"
V7_MANIFEST = ROOT / "evals/benchmarks/quantum_grpo_training_v7_targeted_integrity.txt"
NEW_MANIFEST = ROOT / "evals/benchmarks/quantum_grpo_training_v8_holdout_adjacent.txt"
MANIFEST_BUILDER = ROOT / "scripts/build_grpo_v8_manifest.py"

# v8 adds exactly these 10 NEW task ids (v7's 10 ids stay untouched).
NEW_TASK_IDS: list[str] = [
    "quantum_three_qubit_entropy",
    "quantum_shor_phase_error_correction",
    "quantum_trotter_heisenberg_evolution",
    "quantum_depolarizing_entanglement_decay",
    "quantum_vqe_heisenberg_energy",
    "quantum_qaoa_ring4_landscape",
    "quantum_bell_basis_discrimination",
    "quantum_qft_periodic_state",
    "quantum_stabilizer_shor_generators",
    "quantum_qml_variational_classifier",
]

# Holdout failure competence per new task (for the report + isolation focus).
# Values are the holdout TASK DIRECTORY names (some lack the quantum_ prefix).
HOLDOUT_FAILURE_MAP = {
    "quantum_three_qubit_entropy": "density_matrix_partial_trace",
    "quantum_shor_phase_error_correction": "quantum_error_correction_shor_9qubit",
    "quantum_trotter_heisenberg_evolution": "trotterized_hamiltonian_evolution",
    "quantum_depolarizing_entanglement_decay": "quantum_channel_depolarizing",
    "quantum_vqe_heisenberg_energy": "pennylane_vqe_h2",
    "quantum_qaoa_ring4_landscape": "cirq_qaoa_line",
    "quantum_bell_basis_discrimination": "braket_bell_state",
    "quantum_qft_periodic_state": "qiskit_qft_entangled",
    "quantum_stabilizer_shor_generators": "qiskit_stabilizer_5qubit_code",
    "quantum_qml_variational_classifier": "pennylane_qml_iris_classification",
}

V7_IDS = [
    "quantum_bitstring_maxcut_landscape",
    "quantum_circuit_depth_optimization",
    "quantum_circuit_phase_repair",
    "quantum_error_detection_bit_flip",
    "quantum_gate_alias_casefold_barrier",
    "quantum_measurement_bug_repair",
    "quantum_phase_measurement_register",
    "quantum_stabilizer_tableau_update_repair",
    "quantum_superdense_pauli_router",
    "quantum_teleportation_corrections",
]

# Expected v7 header pin (guards against accidental modification of v7).
V7_CONTRACT_SHA256 = "af8429bd32a997d63c24b75ef50bf9d8e706809dd226578905de58272ac4faef"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _manifest_ids(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def _task_dir(task_id: str) -> Path:
    """Resolve a task id (manifest id) to its directory via task.json."""
    for task_json in (ROOT / "evals/tasks").glob("*/*/task.json"):
        meta = json.loads(task_json.read_text(encoding="utf-8"))
        if str(meta.get("id", task_json.parent.name)) == task_id:
            return task_json.parent
    return ROOT / "evals/tasks/quantum" / task_id


def _run(task_id: str, code: str) -> dict:
    task_dir = _task_dir(task_id)
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(code)
        path = f.name
    try:
        spec = importlib.util.spec_from_file_location(
            f"{task_id}_tests", str(task_dir / "tests.py")
        )
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        return mod.run_tests(path)
    finally:
        os.unlink(path)


def _shaped(task_id: str, code: str) -> float:
    result = _run(task_id, code)
    if result["passed"]:
        return 1.0
    return shaped_reward_from_details(False, result.get("details") or [])


def _public_prompt(task_id: str) -> str:
    task_dir = _task_dir(task_id)
    metadata = json.loads((task_dir / "task.json").read_text(encoding="utf-8"))
    return build_public_task_spec(task_dir, metadata)


_STOPWORDS = frozenset(
    """
    the a an and or of to in for on with from by is are was were be been being
    this that these those it its as at your you will hidden tests verify
    behavior return only complete python source without markdown fences
    explanation task domain category output file implement requested public
    api specification required signatures docstrings not but so if then than
    more most into over under again further once here there when where why
    how all any both each few other some such no nor only own same too very
    can just should shall would could may might must has have had do does did
    done
    """.split()
)


def _tokens(text: str) -> set[str]:
    """Content tokens: stopwords and prompt scaffolding removed.

    The public-prompt scaffolding ("Task:", "Domain:", "Implement the
    requested file...") is shared by every task in the repo, so an unfiltered
    Jaccard would be dominated by it. This is the lightweight
    prompt-embedding proxy for the holdout isolation check.
    """
    tokens = {t for t in re.findall(r"[A-Za-z_][A-Za-z0-9_]*|\d+\.?\d*", text.lower())}
    return {t for t in tokens if t not in _STOPWORDS and len(t) > 2}


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


def _task_contract_hash(task_ids: list[str]) -> str:
    registry: dict[str, Path] = {}
    for task_json in (ROOT / "evals/tasks").glob("*/*/task.json"):
        meta = json.loads(task_json.read_text(encoding="utf-8"))
        registry[str(meta["id"])] = task_json.parent
    digest = hashlib.sha256()
    for task_id in sorted(task_ids):
        task_dir = registry.get(task_id)
        assert task_dir is not None, f"missing task dir for {task_id}"
        for name in ("task.json", "tests.py"):
            path = task_dir / name
            assert path.is_file(), f"missing {task_dir / name}"
            digest.update(task_id.encode())
            digest.update(b"\0")
            digest.update(name.encode())
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")
    return digest.hexdigest()


# ---------------------------------------------------------------------------
# (a) reference passes
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("task_id", sorted(NEW_TASK_IDS))
def test_every_new_task_reference_passes(task_id: str) -> None:
    reference = (_task_dir(task_id) / "candidate.py").read_text(encoding="utf-8")
    result = _run(task_id, reference)
    assert result["passed"], f"{task_id} reference failed: {result['details']}"


# ---------------------------------------------------------------------------
# (b) near-miss and None-stub candidates are graded (shaped > 0, no crash)
# ---------------------------------------------------------------------------

# One plausible broken candidate per task: valid code, mostly right, one
# competence-level bug (wrong constant / dropped term / wrong convention).
NEAR_MISS_CANDIDATES: dict[str, str] = {
    # Natural-log entropy instead of log2: S(ghz reduced) = ln2 ~ 0.6931 vs 1.
    "quantum_three_qubit_entropy": """
import math

def density_from_state(state):
    n = len(state)
    return [[state[i] * state[j] for j in range(n)] for i in range(n)]

def tensor_product(a, b):
    da, db = len(a), len(b)
    size = da * db
    result = [[0.0] * size for _ in range(size)]
    for i in range(da):
        for j in range(da):
            for k in range(db):
                for l in range(db):
                    result[i * db + k][j * db + l] = a[i][j] * b[k][l]
    return result

def partial_trace(rho, dims, trace_out):
    kept = [i for i in range(len(dims)) if i not in trace_out]
    kept_dims = [dims[i] for i in kept]
    traced_dims = [dims[i] for i in trace_out]
    import itertools
    out_dim = 1
    for d in kept_dims:
        out_dim *= d
    result = [[0.0] * out_dim for _ in range(out_dim)]
    for kv in itertools.product(*(range(d) for d in kept_dims)):
        for tv in itertools.product(*(range(d) for d in traced_dims)):
            parts = [None] * len(dims)
            for ki, k in enumerate(kept):
                parts[k] = kv[ki]
            for ti, t in enumerate(trace_out):
                parts[t] = tv[ti]
            row = 0
            col = 0
            for p, d in zip(parts, dims):
                row = row * d + p
                col = col * d + p
            ri = 0
            ci = 0
            for d, p in zip(kept_dims, kv):
                ri = ri * d + p
                ci = ci * d + p
            result[ri][ci] += rho[row][col]
    return result

def von_neumann_entropy(rho, base=2):
    # BUG: ignores the base and uses natural log.
    n = len(rho)
    # 2x2 and 4x4 spectral support: project onto computational basis is wrong
    # for general matrices, so diagonalize numerically via trace recursion:
    return _entropy_natural(rho)

def _entropy_natural(rho):
    # iterative power trace for a 2x2/4x4 hermitian matrix
    import numpy as np
    w = np.linalg.eigvalsh(np.asarray(rho, dtype=complex))
    total = 0.0
    for lam in w:
        if lam > 1e-12:
            total -= lam * math.log(lam)
    return float(total)
""",
    # Encodes the Shor code with half the correct amplitude (1/(4*sqrt2)).
    "quantum_shor_phase_error_correction": """
import math
S2 = 1.0 / math.sqrt(2)

def _block(b):
    v = [0.0] * 8
    v[0] = S2 / 2  # BUG: half amplitude
    v[7] = (S2 / 2) if b == 0 else -(S2 / 2)
    return v

def shor_encode(logical):
    out = [1.0]
    for b in range(3):
        blk = _block(1 if logical else 0)
        out = [a * c for a in out for c in blk]
    return out

def apply_error(state, qubit, err):
    n = len(state)
    out = [0.0] * n
    bit = 1 << (8 - qubit)
    if err == "X":
        for i, a in enumerate(state):
            out[i ^ bit] = a
    elif err == "Z":
        for i, a in enumerate(state):
            out[i] = -a if (i & bit) else a
    else:  # Y = X then Z
        tmp = [0.0] * n
        for i, a in enumerate(state):
            tmp[i ^ bit] = a
        for i, a in enumerate(tmp):
            out[i] = -a if (i & bit) else a
    return out

def shor_decode(state):
    cw = {0: shor_encode(0), 1: shor_encode(1)}
    for err in ("I", "X", "Z", "Y"):
        for q in range(9):
            if err == "I" and q > 0:
                continue
            corrected = list(state)
            if err != "I":
                corrected = apply_error(corrected, q, err)
            p0 = abs(sum(a * b for a, b in zip(corrected, cw[0]))) ** 2
            p1 = abs(sum(a * b for a, b in zip(corrected, cw[1]))) ** 2
            if p0 > 0.999:
                return 0
            if p1 > 0.999:
                return 1
    return 0
""",
    # Trotter evolution that drops the transverse-field term: the product
    # exp(-i dt J ZZ) ** steps misses h(XI + IX), so the error never shrinks.
    "quantum_trotter_heisenberg_evolution": """
import numpy as np

def heisenberg_chain_matrix(J, h):
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    Z = np.array([[1, 0], [0, -1]], dtype=complex)
    I = np.eye(2, dtype=complex)
    return J * np.kron(Z, Z) + h * (np.kron(X, I) + np.kron(I, X))

def exact_evolution_matrix(J, h, t):
    H = heisenberg_chain_matrix(J, h)
    w, v = np.linalg.eigh(H)
    return (v * np.exp(-1j * w * t)) @ v.conj().T

def _expm(h, dt):
    w, v = np.linalg.eigh(h)
    return (v * np.exp(-1j * w * dt)) @ v.conj().T

def trotter_evolution_matrix(J, h, t, steps):
    Z = np.array([[1, 0], [0, -1]], dtype=complex)
    dt = t / steps
    # BUG: field term h(XI + IX) dropped from the split
    u_zz = _expm(J * np.kron(Z, Z), dt)
    u = np.eye(4, dtype=complex)
    for _ in range(steps):
        u = u_zz @ u
    return u

def trotter_max_abs_error(J, h, t, steps):
    return float(np.max(np.abs(trotter_evolution_matrix(J, h, t, steps) - exact_evolution_matrix(J, h, t))))
""",
    # 2-qubit depolarizing mixes with I/15 (the 15 non-identity Pauli
    # convention) instead of I/4 (the maximally-mixed-state convention):
    # coherence and fidelity decay at the wrong rate.
    "quantum_depolarizing_entanglement_decay": """
import math

def bell_density_matrix():
    return [[0.5, 0.0, 0.0, 0.5],
            [0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0],
            [0.5, 0.0, 0.0, 0.5]]

def two_qubit_depolarizing(rho, p):
    n = len(rho)
    out = [[0.0] * n for _ in range(n)]
    # BUG: uses p/15 instead of p/4
    for i in range(n):
        for j in range(n):
            out[i][j] = (1 - p) * rho[i][j] + (p / 15.0) * (1.0 if i == j else 0.0)
    return out

def werner_state(p):
    return two_qubit_depolarizing(bell_density_matrix(), p)

def fidelity_to_bell(rho):
    return 0.5 * (rho[0][0] + rho[3][3]) + rho[0][3]
""",
    # VQE ansatz without the entangling CNOT: no singlet states reachable, so
    # the energy floors around the best product-state value (-sqrt(2)), far
    # above the entangled ground state -3.0.
    "quantum_vqe_heisenberg_energy": """
import pennylane as qml
from pennylane import numpy as np

def heisenberg_hamiltonian(J=1.0):
    coeffs = [J, J, J]
    ops = [qml.PauliX(0) @ qml.PauliX(1),
           qml.PauliY(0) @ qml.PauliY(1),
           qml.PauliZ(0) @ qml.PauliZ(1)]
    return qml.Hamiltonian(coeffs, ops)

def vqe_circuit(params):
    qml.RY(params[0], wires=0)
    qml.RY(params[1], wires=1)
    # BUG: entangling CNOT omitted
    qml.RY(params[2], wires=0)
    qml.RY(params[3], wires=1)

def run_vqe(steps=80, seed=0):
    H = heisenberg_hamiltonian(1.0)
    dev = qml.device("default.qubit", wires=2)
    @qml.qnode(dev)
    def cost_fn(params):
        vqe_circuit(params)
        return qml.expval(H)
    np.random.seed(seed)
    params = np.random.uniform(-np.pi, np.pi, 4)
    opt = qml.AdamOptimizer(stepsize=0.15)
    for _ in range(steps):
        params = opt.step(cost_fn, params)
    return {"energy": float(cost_fn(params)), "params": list(np.asarray(params, dtype=float))}
""",
    # QAOA cost unitary uses the wrong sign for cirq's ZZPowGate convention
    # (exponent=+2 gamma/pi instead of -2 gamma/pi): the cost phase is
    # inverted, so the landscape peak at (pi/8, pi/8) is missed.
    "quantum_qaoa_ring4_landscape": """
import cirq
import numpy as np

def maxcut_ring4_edges():
    return [(0, 1), (1, 2), (2, 3), (3, 0)]

def best_maxcut_value():
    return 4

def maxcut_value(bitstring):
    bits = [int(c) for c in bitstring]
    return sum(1 for u, v in maxcut_ring4_edges() if bits[u] != bits[v])

def qaoa_ring4_circuit(gamma, beta):
    qubits = cirq.LineQubit.range(4)
    circuit = cirq.Circuit()
    circuit.append(cirq.H.on_each(*qubits))
    for u, v in maxcut_ring4_edges():
        # BUG: sign flipped (cirq ZZPowGate needs -2 gamma/pi)
        circuit.append(cirq.ZZPowGate(exponent=2 * gamma / np.pi)(qubits[u], qubits[v]))
    for q in qubits:
        circuit.append(cirq.XPowGate(exponent=2 * beta / np.pi)(q))
    return circuit

def expected_cut_value(gamma, beta):
    qubits = cirq.LineQubit.range(4)
    sim = cirq.Simulator()
    state = np.asarray(sim.simulate(qaoa_ring4_circuit(gamma, beta), qubit_order=qubits).final_state_vector)
    expectation = 0.0
    for u, v in maxcut_ring4_edges():
        agree = 0.0
        for i, amp in enumerate(state):
            if ((i >> (3 - u)) & 1) == ((i >> (3 - v)) & 1):
                agree += abs(amp) ** 2
        expectation += 1.0 - agree
    return float(expectation)

def optimize_angles(steps=40, seed=0):
    np.random.seed(seed)
    best = -1.0
    bg = bb = 0.0
    for gamma in np.linspace(0.0, np.pi, 13):
        for beta in np.linspace(0.0, np.pi, 13):
            c = expected_cut_value(gamma, beta)
            if c > best:
                best, bg, bb = c, gamma, beta
    return {"cost": float(best), "gamma": float(bg), "beta": float(bb)}
""",
    # Bell states encoded with half amplitude.
    "quantum_bell_basis_discrimination": """
import math
S2 = 0.5  # BUG: should be 1/sqrt(2)

def bell_statevector(k):
    if k == 0:
        return [S2, 0.0, 0.0, S2]
    if k == 1:
        return [S2, 0.0, 0.0, -S2]
    if k == 2:
        return [0.0, S2, S2, 0.0]
    return [0.0, S2, -S2, 0.0]

def bell_basis_unitary():
    return [[bell_statevector(k)[i] for k in range(4)] for i in range(4)]

def classify_bell(state):
    import numpy as np
    U = np.asarray(bell_basis_unitary(), dtype=complex)
    v = np.asarray(state, dtype=complex)
    probs = np.abs(U.conj().T @ v) ** 2
    return int(np.argmax(probs))

def entanglement_concurrence(state):
    a, b, c, d = state
    return 2 * abs(a * d - b * c)
""",
    # QFT circuit is correct, but the periodic input is built on the wrong
    # basis state (|001> instead of |100>): wrong interference pattern.
    "quantum_qft_periodic_state": """
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator

def qft_circuit(n=3):
    c = QuantumCircuit(n)
    for i in range(n - 1, -1, -1):
        c.h(i)
        for j in range(i):
            c.cp(np.pi / 2 ** (i - j), j, i)
    for i in range(n // 2):
        c.swap(i, n - 1 - i)
    return c

def periodic_state(n=3):
    v = np.zeros(2 ** n, dtype=complex)
    v[0] = 1 / np.sqrt(2)
    v[1] = 1 / np.sqrt(2)  # BUG: should be v[2**(n-1)] = |100>
    return list(v)

def apply_qft(state):
    n = int(round(np.log2(len(state))))
    u = np.asarray(Operator(qft_circuit(n)))
    return list(u @ np.asarray(state, dtype=complex))
""",
    # One stabilizer generator has a flipped sign: eigenvalues are -1 instead
    # of +1 on the codewords.
    "quantum_stabilizer_shor_generators": """
import math

def shor_codeword(logical):
    s2 = 1.0 / math.sqrt(2)
    out = [1.0]
    for b in range(3):
        blk = [0.0] * 8
        blk[0] = s2
        blk[7] = s2 if (1 if logical else 0) == 0 else -s2
        out = [a * c for a in out for c in blk]
    return out

def shor_stabilizer_generators():
    # BUG: g1 sign flipped
    return ["-ZZIIIIIII", "IZZIIIIII", "IIIZZIIII", "IIIIZZIII",
            "IIIIIIZZI", "IIIIIIIZZ", "XXXXXXIII", "IIIXXXXXX"]

def pauli_eigenvalue(pauli, state):
    sign = -1.0 if pauli.startswith("-") else 1.0
    pauli = pauli.lstrip("-")
    xmask = 0
    zmask = 0
    for q, ch in enumerate(pauli):
        bit = 1 << (8 - q)
        if ch in ("X", "Y"):
            xmask |= bit
        if ch in ("Z", "Y"):
            zmask |= bit
    n = len(state)
    out = [0.0] * n
    for i, a in enumerate(state):
        phase = sign * (-1.0) ** bin(i & zmask).count("1")
        out[i ^ xmask] += phase * a
    return sum(a * b for a, b in zip(state, out))

def pauli_commute(a, b):
    ax = 0
    az = 0
    bx = 0
    bz = 0
    for q, ch in enumerate(a.lstrip("-")):
        bit = 1 << (8 - q)
        if ch in ("X", "Y"):
            ax |= bit
        if ch in ("Z", "Y"):
            az |= bit
    for q, ch in enumerate(b.lstrip("-")):
        bit = 1 << (8 - q)
        if ch in ("X", "Y"):
            bx |= bit
        if ch in ("Z", "Y"):
            bz |= bit
    return bin(ax & bz).count("1") % 2 == bin(bx & az).count("1") % 2
""",
    # Variational classifier without the entangling gate: XOR is not
    # linearly separable, accuracy stays near chance.
    "quantum_qml_variational_classifier": """
import pennylane as qml
from pennylane import numpy as np

def make_xor_data():
    X = np.array([
        [-0.7, -0.7], [0.7, 0.7], [-0.7, 0.7], [0.7, -0.7],
        [-0.3, -0.3], [0.3, 0.3], [-0.3, 0.3], [0.3, -0.3],
        [-0.7, 0.3], [0.7, -0.3], [0.7, 0.3], [-0.7, -0.3],
        [0.3, -0.7], [-0.3, 0.7], [-0.3, -0.7], [0.3, 0.7],
    ], dtype=float)
    y = np.array([1.0 if x0 * x1 > 0 else 0.0 for x0, x1 in X])
    return X, y

def variational_circuit(params, x):
    qml.RY(x[0] * np.pi, wires=0)
    qml.RY(x[1] * np.pi, wires=1)
    # BUG: no CNOT entangling layer
    qml.RY(params[0], wires=0)
    qml.RY(params[1], wires=1)
    qml.RY(params[2], wires=0)
    qml.RY(params[3], wires=1)

def train_classifier(steps=60, seed=0):
    X, y = make_xor_data()
    dev = qml.device("default.qubit", wires=2)
    @qml.qnode(dev)
    def circuit(params, x):
        variational_circuit(params, x)
        return qml.expval(qml.PauliZ(0))
    def loss(params):
        total = 0.0
        for xi, yi in zip(X, y):
            pred = circuit(params, xi)
            total += (pred - (2 * yi - 1)) ** 2
        return total / len(y)
    np.random.seed(seed)
    params = np.random.uniform(-np.pi, np.pi, 4)
    opt = qml.AdamOptimizer(stepsize=0.2)
    for _ in range(steps):
        params = opt.step(loss, params)
    acc = np.mean([1.0 if (circuit(params, xi) > 0) == (yi == 1) else 0.0
                   for xi, yi in zip(X, y)])
    return {"accuracy": float(acc), "n": int(len(y)),
            "params": list(np.asarray(params, dtype=float))}

def predict(params, x):
    dev = qml.device("default.qubit", wires=2)
    @qml.qnode(dev)
    def circuit(params, x):
        variational_circuit(params, x)
        return qml.expval(qml.PauliZ(0))
    return 1 if circuit(params, x) > 0 else 0
""",
}

# None-returning stubs per task: the exact holdout failure class. These must
# be GRADED (numeric details, shaped > 0), never crashes.
NONE_STUB_CANDIDATES: dict[str, str] = {
    "quantum_three_qubit_entropy": (
        "def density_from_state(state):\n    return None\n\n"
        "def tensor_product(a, b):\n    return None\n\n"
        "def partial_trace(rho, dims, trace_out):\n    return None\n\n"
        "def von_neumann_entropy(rho, base=2):\n    return None\n"
    ),
    "quantum_shor_phase_error_correction": (
        "def shor_encode(logical):\n    return None\n\n"
        "def apply_error(state, qubit, err):\n    return None\n\n"
        "def shor_decode(state):\n    return None\n"
    ),
    "quantum_trotter_heisenberg_evolution": (
        "import numpy as np\n\n"
        "def heisenberg_chain_matrix(J):\n    return None\n\n"
        "def exact_evolution_matrix(J, t):\n    return None\n\n"
        "def trotter_evolution_matrix(J, t, steps):\n    return None\n\n"
        "def trotter_max_abs_error(J, t, steps):\n    return None\n"
    ),
    "quantum_depolarizing_entanglement_decay": (
        "def bell_density_matrix():\n    return None\n\n"
        "def two_qubit_depolarizing(rho, p):\n    return None\n\n"
        "def werner_state(p):\n    return None\n\n"
        "def fidelity_to_bell(rho):\n    return None\n"
    ),
    "quantum_vqe_heisenberg_energy": (
        "def heisenberg_hamiltonian(J=1.0):\n    return None\n\n"
        "def vqe_circuit(params):\n    return None\n\n"
        "def run_vqe(steps=80, seed=0):\n    return None\n"
    ),
    "quantum_qaoa_ring4_landscape": (
        "import cirq\nimport numpy as np\n\n"
        "def maxcut_ring4_edges():\n    return None\n\n"
        "def best_maxcut_value():\n    return None\n\n"
        "def maxcut_value(bitstring):\n    return None\n\n"
        "def qaoa_ring4_circuit(gamma, beta):\n    return None\n\n"
        "def expected_cut_value(gamma, beta):\n    return None\n\n"
        "def optimize_angles(steps=40, seed=0):\n    return None\n"
    ),
    "quantum_bell_basis_discrimination": (
        "def bell_statevector(k):\n    return None\n\n"
        "def bell_basis_unitary():\n    return None\n\n"
        "def classify_bell(state):\n    return None\n\n"
        "def entanglement_concurrence(state):\n    return None\n"
    ),
    "quantum_qft_periodic_state": (
        "import numpy as np\nfrom qiskit import QuantumCircuit\n"
        "from qiskit.quantum_info import Operator\n\n"
        "def qft_circuit(n=3):\n    return None\n\n"
        "def periodic_state(n=3):\n    return None\n\n"
        "def apply_qft(state):\n    return None\n"
    ),
    "quantum_stabilizer_shor_generators": (
        "import math\n\n"
        "def shor_codeword(logical):\n    return None\n\n"
        "def shor_stabilizer_generators():\n    return None\n\n"
        "def pauli_eigenvalue(pauli, state):\n    return None\n\n"
        "def pauli_commute(a, b):\n    return None\n"
    ),
    "quantum_qml_variational_classifier": (
        "import pennylane as qml\nfrom pennylane import numpy as np\n\n"
        "def make_xor_data():\n    return None\n\n"
        "def variational_circuit(params, x):\n    return None\n\n"
        "def train_classifier(steps=60, seed=0):\n    return None\n\n"
        "def predict(params, x):\n    return None\n"
    ),
}


@pytest.mark.parametrize("task_id", sorted(NEW_TASK_IDS))
def test_every_new_task_near_miss_scores_positive_shaped(task_id: str) -> None:
    code = NEAR_MISS_CANDIDATES[task_id]
    result = _run(task_id, code)
    assert not result["passed"], f"{task_id}: near-miss candidate unexpectedly passed"
    details = result.get("details") or []
    assert any(
        "=" in line or "expected" in line or "need" in line or "->" in line for line in details
    ), f"{task_id}: no graded numeric detail: {details}"
    shaped = shaped_reward_from_details(False, details)
    assert shaped > 0.3, f"{task_id}: near-miss shaped={shaped:.4f} details={details}"


@pytest.mark.parametrize("task_id", sorted(NEW_TASK_IDS))
def test_none_stub_is_graded_not_a_crash(task_id: str) -> None:
    result = _run(task_id, NONE_STUB_CANDIDATES[task_id])
    # A None stub must yield a clean harness result (no exception escape).
    assert isinstance(result, dict) and result["passed"] is False
    details = result.get("details") or []
    shaped = shaped_reward_from_details(False, details)
    assert shaped > 0.0, f"{task_id}: None stub shaped={shaped:.4f} details={details}"


# ---------------------------------------------------------------------------
# (c) frozen-holdout isolation (ID + prompt)
# ---------------------------------------------------------------------------


def test_new_task_ids_are_disjoint_from_frozen_holdout() -> None:
    holdout_ids = set(_manifest_ids(HOLDOUT_MANIFEST))
    assert len(holdout_ids) == 18
    assert set(NEW_TASK_IDS).isdisjoint(holdout_ids)
    assert set(NEW_TASK_IDS).isdisjoint(V7_IDS)


@pytest.mark.parametrize("task_id", sorted(NEW_TASK_IDS))
def test_new_task_prompt_does_not_leak_holdout_identity(task_id: str) -> None:
    prompt = _public_prompt(task_id).lower()
    holdout_ids = set(_manifest_ids(HOLDOUT_MANIFEST))
    for holdout_id in holdout_ids:
        assert holdout_id not in prompt, f"{task_id} prompt contains holdout task id {holdout_id}"
    # The mapped holdout task's FULL human name must not appear verbatim in
    # the new prompt. Shared single-word competence vocabulary (trace, error,
    # correction, ...) is the point of the curriculum, not an identity leak;
    # the token-overlap test below bounds the whole-prompt similarity.
    mapped = HOLDOUT_FAILURE_MAP[task_id]
    metadata = json.loads((_task_dir(mapped) / "task.json").read_text(encoding="utf-8"))
    name = " ".join(re.findall(r"[A-Za-z]+", str(metadata.get("name", "")).lower()))
    assert name not in prompt, f"{task_id} prompt contains holdout task name {name!r}"


def test_new_task_prompts_have_low_token_overlap_with_every_holdout_prompt() -> None:
    holdout_prompts = {tid: _public_prompt(tid) for tid in _manifest_ids(HOLDOUT_MANIFEST)}
    for task_id in NEW_TASK_IDS:
        new_tokens = _tokens(_public_prompt(task_id))
        for holdout_id, holdout_prompt in holdout_prompts.items():
            overlap = _jaccard(new_tokens, _tokens(holdout_prompt))
            assert overlap < 0.5, f"{task_id} vs {holdout_id} token overlap {overlap:.3f} >= 0.5"


# ---------------------------------------------------------------------------
# (d) v8 manifest regenerates with a valid header hash; v7 untouched
# ---------------------------------------------------------------------------


def test_v7_manifest_stays_intact() -> None:
    assert _manifest_ids(V7_MANIFEST) == V7_IDS
    source = V7_MANIFEST.read_text(encoding="utf-8")
    assert "# task_contract_sha256=" + V7_CONTRACT_SHA256 in source
    assert "quantum_bitstring_maxcut_landscape\n" in source


def test_v8_manifest_regenerates_with_valid_header_hash(tmp_path: Path) -> None:
    assert NEW_MANIFEST.is_file(), "v8 manifest missing"
    ids = _manifest_ids(NEW_MANIFEST)
    assert ids == V7_IDS + NEW_TASK_IDS, "v8 must be v7 tasks + new tasks, in order"
    assert len(ids) == len(set(ids)) == 20

    source = NEW_MANIFEST.read_text(encoding="utf-8")
    # header hash lines
    source_hash_line = next(line for line in source.splitlines() if line.startswith("# source="))
    assert f"sha256={hashlib.sha256(V7_MANIFEST.read_bytes()).hexdigest()}" in source_hash_line
    contract_line = next(
        line for line in source.splitlines() if line.startswith("# task_contract_sha256=")
    )
    expected_contract = _task_contract_hash(ids)
    assert contract_line.split("=", 1)[1] == expected_contract
    assert "# reference_execution_verified=true runs=3" in source
    assert "# targeted=20 deterministic=0 semantic=0" in source

    # regeneration is byte-identical
    regenerated = tmp_path / "regenerated.txt"
    result = subprocess.run(
        [sys.executable, str(MANIFEST_BUILDER), "--output", str(regenerated)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert regenerated.read_bytes() == NEW_MANIFEST.read_bytes()

    # every id in the manifest has a task dir with the harness artifacts
    for task_id in ids:
        task_dir = _task_dir(task_id)
        assert (task_dir / "task.json").is_file()
        assert (task_dir / "tests.py").is_file()
        assert (task_dir / "candidate.py").is_file()
