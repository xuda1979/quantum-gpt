#!/usr/bin/env python3
"""C-10611 — compose the IBM-track GENERALIZATION corpus (v26).

WHY: the frozen IBM Qiskit HumanEval 139 benchmark (C-10609) is dominated
by qiskit-API work — quantum_info (65 tasks), transpiler (27), aer (21),
circuit construction (16) — while the internal 1048-task inventory is
almost entirely framework-free (61/1048 touch qiskit). An adapter trained
only on internal tasks cannot generalize to the qiskit API surface. This
card composes NEW training problems covering the same qiskit modules,
difficulty mix, and BOTH prompt styles (HumanEval-completion and
standalone instruction) as the IBM benchmark — WITHOUT any of the 139
benchmark tasks, signatures, solutions, or test bodies (leak guard).

LEAK GUARD (fail-closed, G2 below): every emitted completion is
sha256-compared against the set of all 139 canonical_solution bodies,
all 139 test bodies, and all 139 prompt prefixes. Zero tolerance: any
hash hit aborts the build. Problems are authored fresh (different
entry points, different functionality) so the guard is a backstop, not
the primary defense.

GATES (all must pass before any row is emitted):
  G1 freeze: IBM benchmark files match MANIFEST.json sha256.
  G2 leak guard: emitted completion/task_spec hashes disjoint from the
     139-benchmark {canonical_solution, test, prompt} hash set.
  G3 exec-green: every emitted completion actually runs green against
     its own tests under qiskit 2.x + aer (the same runtime as eval).
  G4 style mix: corpus contains BOTH HumanEval-completion style rows
     AND instruction-style rows for every task (2 prompt styles x N
     variants), mirroring the eval's dual-style protocol.

OUTPUT: outputs/C10611_ibm_track_v26_corpus.jsonl (chat-ml rows, same
schema as C-10606 v25 corpus) + outputs/C10611_ibm_track_v26_spec.json.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BENCH_DIR = REPO / "evals" / "benchmarks" / "ibm_qiskit"
OUT_DIR = REPO / "outputs"
PER_TASK_TIMEOUT_S = 180

SYS_PROMPT = (
    "You are an expert quantum computing programmer. Write correct, "
    "idiomatic Python using the Qiskit SDK. Return only the final Python "
    "code unless the task explicitly asks for an explanation."
)


def sha256b(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def now_utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# ---------------------------------------------------------------------------
# G1: freeze
# ---------------------------------------------------------------------------
def g1_freeze() -> list[dict]:
    man = json.loads((BENCH_DIR / "MANIFEST.json").read_text())
    rows = []
    for fn, meta in man["files"].items():
        p = BENCH_DIR / fn
        actual = sha256b(p.read_bytes())
        assert actual == meta["sha256"], f"G1 FREEZE DRIFT {fn}"
        rows.extend(json.loads(ln) for ln in open(p) if ln.strip())
    assert len(rows) == 2 * man["tasks"], "G1 row count drift"
    print(f"[G1] PASS: {len(rows)} benchmark rows frozen ({man['tasks']} tasks x 2 styles)")
    return rows


def leak_hash_set(bench_rows: list[dict]) -> set[str]:
    hs = set()
    for r in bench_rows:
        hs.add(sha256b(r["canonical_solution"].strip().encode()))
        hs.add(sha256b(r["test"].strip().encode()))
        hs.add(sha256b(r["prompt"].strip().encode()))
    return hs


# ---------------------------------------------------------------------------
# Task authoring: fresh qiskit problems (LEAK-FREE vs the 139).
# Each problem: id, difficulty, module, entry, docstring, solution, tests.
# ---------------------------------------------------------------------------
def author_tasks() -> list[dict]:
    """Fresh qiskit problems authored for generalization. Different entry
    points and functionality than the benchmark; same API surface."""
    T = []

    # ---- quantum_info (eval-heavy: 65) ------------------------------------
    T.append(
        dict(
            id="qg_bell_choi_validation",
            difficulty="basic",
            module="qiskit.quantum_info",
            entry="bell_choi_channel",
            docstring=(
                "Build the Choi representation of the fully-dephasing (Z) "
                "channel on one qubit, apply it to half of a Bell pair via "
                "qiskit.quantum_info DensityMatrix.evolve with qargs, and "
                "return the resulting DensityMatrix (purity 1/2)."
            ),
            solution='''import numpy as np
from qiskit.quantum_info import DensityMatrix, Choi, Statevector, Kraus

def bell_choi_channel():
    """Return the DensityMatrix left after sending qubit 0 of a Bell
    pair through the fully-dephasing channel."""
    bell = (Statevector.from_label("00") + Statevector.from_label("11")) / (2 ** 0.5)
    K0 = np.sqrt(0.5) * np.eye(2, dtype=complex)
    K1 = np.sqrt(0.5) * np.array([[1, 0], [0, -1]], dtype=complex)
    chan = Choi(Kraus([K0, K1]))
    dm = DensityMatrix(bell).evolve(chan, qargs=[0])
    return dm''',
            tests="""def check(candidate):
    from qiskit.quantum_info import DensityMatrix, partial_trace
    import numpy as np
    dm = candidate()
    assert isinstance(dm, DensityMatrix)
    assert dm.dims() == (2, 2)
    # dephasing removes Bell coherences: purity drops to 1/2
    assert np.isclose(dm.purity(), 0.5, atol=1e-8)""",
        )
    )

    T.append(
        dict(
            id="qg_stabilizer_clifford_compose",
            difficulty="basic",
            module="qiskit.quantum_info",
            entry="clifford_double_h",
            docstring=(
                "Return the qiskit.quantum_info Clifford obtained by composing "
                "two Hadamards on qubit 0 of a 1-qubit CliffordTableau, i.e. "
                "the identity Clifford, and report its effective single-qubit "
                "matrix via to_matrix()."
            ),
            solution='''import numpy as np
from qiskit.quantum_info import Clifford
from qiskit.circuit.library import HGate

def clifford_double_h():
    """Compose H.H on one qubit; return the Clifford (identity)."""
    h = Clifford(HGate())
    return h.compose(h)''',
            tests="""def check(candidate):
    import numpy as np
    c = candidate()
    m = c.to_matrix()
    assert np.allclose(m, np.eye(2), atol=1e-9)""",
        )
    )

    T.append(
        dict(
            id="qg_entropy_marginal",
            difficulty="intermediate",
            module="qiskit.quantum_info",
            entry="bell_marginal_entropy",
            docstring=(
                "Create the Bell |00>+|11> Statevector, compute the entropy of "
                "qubit 0 (marginal) via DensityMatrix and "
                "qiskit.quantum_info.entropy, and return it."
            ),
            solution='''import numpy as np
from qiskit.quantum_info import Statevector, DensityMatrix, entropy, partial_trace

def bell_marginal_entropy():
    """Entropy (base 2, qiskit default) of either single-qubit marginal
    of a Bell state: 1.0 bit."""
    sv = (Statevector.from_label("00") + Statevector.from_label("11")) / (2 ** 0.5)
    dm = DensityMatrix(sv)
    reduced = partial_trace(dm, [1])
    return entropy(reduced)''',
            tests="""def check(candidate):
    import numpy as np
    val = candidate()
    assert np.isclose(val, 1.0, atol=1e-8)""",
        )
    )

    T.append(
        dict(
            id="qg_pauli_evolve_expect",
            difficulty="intermediate",
            module="qiskit.quantum_info",
            entry="zz_chain_expectation",
            docstring=(
                "Prepare the 3-qubit GHZ Statevector, evolve it under the "
                "Pauli operator Z0Z1 using Statevector.evolve, then return the "
                "expectation value <psi|Z0Z1|psi>."
            ),
            solution='''import numpy as np
from qiskit.quantum_info import Statevector, Pauli

def zz_chain_expectation():
    """<GHZ| Z0Z1 |GHZ> = 1 (perfect pair correlation on a Bell-like cut)."""
    ghz = (Statevector.from_label("000") + Statevector.from_label("111")) / (2 ** 0.5)
    op = Pauli("ZZI")
    evolved = ghz.evolve(op)
    return float(np.real(evolved.expectation_value(op)))''',
            tests="""def check(candidate):
    import numpy as np
    val = candidate()
    assert np.isclose(val, 1.0, atol=1e-9)""",
        )
    )

    T.append(
        dict(
            id="qg_fidelity_interference",
            difficulty="intermediate",
            module="qiskit.quantum_info",
            entry="plus_state_fidelity",
            docstring=(
                "Return the quantum state fidelity between the |+> Statevector "
                "and the DensityMatrix of |+> (qiskit.quantum_info."
                "state_fidelity). The result must equal 1.0."
            ),
            solution='''import numpy as np
from qiskit.quantum_info import Statevector, DensityMatrix, state_fidelity

def plus_state_fidelity():
    """Fidelity between |+> as a Statevector and as a DensityMatrix."""
    plus = Statevector.from_label("+")
    dm = DensityMatrix(plus)
    return float(state_fidelity(plus, dm))''',
            tests="""def check(candidate):
    import numpy as np
    assert np.isclose(candidate(), 1.0, atol=1e-9)""",
        )
    )

    T.append(
        dict(
            id="qg_random_unitary_seed",
            difficulty="basic",
            module="qiskit.quantum_info",
            entry="seeded_random_unitary",
            docstring=(
                "Using qiskit.quantum_info.random_unitary with seed=7 on 2 "
                "qubits, verify the drawn matrix is unitary and return it."
            ),
            solution='''import numpy as np
from qiskit.quantum_info import random_unitary

def seeded_random_unitary():
    """Deterministic 4x4 unitary via seed; must be unitary."""
    u = random_unitary(4, seed=7)
    return u''',
            tests="""def check(candidate):
    import numpy as np
    from qiskit.quantum_info import Operator
    u = candidate()
    m = np.asarray(u)
    assert np.allclose(m @ m.conj().T, np.eye(4), atol=1e-9)""",
        )
    )

    T.append(
        dict(
            id="qg_sf_decomposition_reuse",
            difficulty="basic",
            module="qiskit.quantum_info",
            entry="schmidt_equal_split",
            docstring=(
                "Compute the Schmidt decomposition of the state |01> with "
                "qiskit.quantum_info.schmidt_decomposition and return the "
                "number of nonzero Schmidt coefficients (with default "
                "tolerance)."
            ),
            solution='''import numpy as np
from qiskit.quantum_info import Statevector, schmidt_decomposition

def schmidt_equal_split():
    """|01> has exactly one nonzero Schmidt coefficient across the 0|1 cut."""
    sv = Statevector.from_label("01")
    terms = schmidt_decomposition(sv, [0])
    return int(sum(1 for coeff, _, _ in terms if abs(coeff) > 1e-10))''',
            tests="""def check(candidate):
    assert candidate() == 1""",
        )
    )

    T.append(
        dict(
            id="qg_cnot_dihedral_phase",
            difficulty="difficult",
            module="qiskit.quantum_info",
            entry="cnotdihedral_phase_poly",
            docstring=(
                "Build a CNOTDihedral element from the circuit X on qubit 0, "
                "CX(0,1), Z on qubit 1, and return its phase polynomial "
                "(the .poly SpecialPolynomial) as a string."
            ),
            solution='''from qiskit import QuantumCircuit
from qiskit.quantum_info import CNOTDihedral

def cnotdihedral_phase_poly():
    """X0 then CX(0,1) then Z1: the phase polynomial gains x1 terms."""
    qc = QuantumCircuit(2)
    qc.x(0)
    qc.cx(0, 1)
    qc.z(1)
    elem = CNOTDihedral(qc)
    return str(elem.poly)''',
            tests="""def check(candidate):
    out = candidate()
    assert isinstance(out, str) and len(out) > 0
    s = out.replace(" ", "")
    # X0 → x_0 phase; CX propagates; Z1 adds x_1 (pi = 4 half-turns each)
    assert "4*x_0" in s, f"missing 4*x_0 term: {out!r}"
    assert "4*x_1" in s, f"missing 4*x_1 term: {out!r}"
    assert "x_0*x_1" not in s, f"unexpected mixed term: {out!r}\"""",
        )
    )

    # ---- circuit construction (eval: 16) ----------------------------------
    T.append(
        dict(
            id="qg_w_state_3q",
            difficulty="intermediate",
            module="qiskit.circuit",
            entry="w_state_3",
            docstring=(
                "Build a 3-qubit W-state (|001>+|010>+|100>)/sqrt(3) circuit "
                "with qiskit QuantumCircuit using Ry/CX rotations, and return "
                "the circuit."
            ),
            solution='''import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter

def w_state_3():
    """W state via Ry + negative-control CH + negative-control Toffoli."""
    import numpy as np
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(3)
    # P(q0=1) = 1/3
    qc.ry(2 * np.arcsin(1 / np.sqrt(3)), 0)
    # on the q0=0 branch (prob 2/3): H on q1 via X-sandwich
    qc.x(0)
    qc.ch(0, 1)
    # negative-control Toffoli: flip q2 iff q0=0 AND q1=0
    qc.x(1)
    qc.ccx(0, 1, 2)
    qc.x(1)
    qc.x(0)
    return qc''',
            tests="""def check(candidate):
    import numpy as np
    from qiskit.quantum_info import Statevector
    qc = candidate()
    sv = Statevector(qc)
    probs = np.abs(np.asarray(sv)) ** 2
    # support exactly on |001>, |010>, |100>
    target = {0b001: 1/3, 0b010: 1/3, 0b100: 1/3}
    for idx, p in enumerate(probs):
        if idx in target:
            assert np.isclose(p, target[idx], atol=1e-8)
        else:
            assert p < 1e-8""",
        )
    )

    T.append(
        dict(
            id="qg_qft_signal_swap",
            difficulty="intermediate",
            module="qiskit.circuit.library",
            entry="qft_no_final_swaps",
            docstring=(
                "Return the 4-qubit QFT circuit built from "
                "qiskit.circuit.library.QFT with do_swaps=False and "
                "inverse=True (i.e. the inverse QFT without the final swap "
                "layer), as a QuantumCircuit."
            ),
            solution='''from qiskit.circuit.library import QFT

def qft_no_final_swaps():
    """Inverse QFT on 4 qubits without swaps."""
    return QFT(4, do_swaps=False, inverse=True)''',
            tests="""def check(candidate):
    from qiskit.circuit.library import QFT
    import numpy as np
    qc = candidate()
    ref = QFT(4, do_swaps=False, inverse=True)
    from qiskit.quantum_info import Operator
    assert np.allclose(Operator(qc).data, Operator(ref).data, atol=1e-9)""",
        )
    )

    T.append(
        dict(
            id="qg_phase_oracle_3sat",
            difficulty="intermediate",
            module="qiskit.circuit",
            entry="three_sat_mark",
            docstring=(
                "Build a 3-qubit phase oracle that flips the sign of |111> "
                "using a QuantumCircuit (H/CX/CCZ construction or an MCZ), "
                "and return the circuit."
            ),
            solution='''from qiskit import QuantumCircuit

def three_sat_mark():
    """Phase oracle marking |111> via H-MCZ-H sandwich on target bit."""
    qc = QuantumCircuit(3)
    qc.h(2)
    qc.mcx([0, 1], 2)
    qc.h(2)
    return qc''',
            tests="""def check(candidate):
    import numpy as np
    from qiskit.quantum_info import Operator
    m = np.asarray(Operator(candidate()).data)
    diag = np.diag(m)
    # uniform superposition invariant except |111> flipped
    import cmath
    assert np.allclose(diag, [1, 1, 1, 1, 1, 1, 1, -1], atol=1e-9)""",
        )
    )

    # ---- transpiler (eval: 27) ---------------------------------------------
    T.append(
        dict(
            id="qg_transpile_depth_ring",
            difficulty="basic",
            module="qiskit.transpiler",
            entry="ring_depth_2",
            docstring=(
                "Transpile a 3-qubit ring of CX gates (CX(0,1), CX(1,2), "
                "CX(2,0)) onto the coupling map [[0,1],[1,0],[1,2],[2,1]] "
                "with optimization_level=3 and return the final circuit depth."
            ),
            solution='''from qiskit import QuantumCircuit
from qiskit.transpiler import CouplingMap
from qiskit import transpile

def ring_depth_2():
    """Depth after level-3 transpile of the CX ring on a line coupling."""
    qc = QuantumCircuit(3)
    qc.cx(0, 1)
    qc.cx(1, 2)
    qc.cx(2, 0)
    cmap = CouplingMap([[0, 1], [1, 0], [1, 2], [2, 1]])
    out = transpile(qc, coupling_map=cmap, optimization_level=3,
                    seed_transpiler=42)
    return out.depth()''',
            tests="""def check(candidate):
    d = candidate()
    assert isinstance(d, int) and d > 0""",
        )
    )

    T.append(
        dict(
            id="qg_basis_translate_rzz",
            difficulty="intermediate",
            module="qiskit.transpiler",
            entry="rzz_in_toffoli_basis",
            docstring=(
                "Transpile a single RZZGate(pi/4) into the basis ['cx','rz',"
                "'h'] with optimization_level=0 and return the number of CX "
                "gates in the output circuit."
            ),
            solution='''import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import RZZGate

def rzz_in_toffoli_basis():
    """RZZ(pi/4) decomposes to exactly 2 CX gates in the cx/rz/h basis."""
    qc = QuantumCircuit(2)
    qc.append(RZZGate(np.pi / 4), [0, 1])
    out = transpile(qc, basis_gates=["cx", "rz", "h"],
                    optimization_level=0)
    return sum(1 for inst in out.data if inst.operation.name == "cx")''',
            tests="""def check(candidate):
    assert candidate() == 2""",
        )
    )

    T.append(
        dict(
            id="qg_swap_strategy_layout",
            difficulty="difficult",
            module="qiskit.transpiler",
            entry="star_to_line_layout",
            docstring=(
                "Using SabreLayout via transpile with optimization_level=3 "
                "and seed_transpiler=1, transpile a 5-qubit star of CX gates "
                "(center 0 to leaves 1..4) onto a line coupling map "
                "[0-1-2-3-4] and return the number of added SWAP-equivalent "
                "gate count increase: (output 2q gate count) - (input 2q "
                "gate count)."
            ),
            solution='''from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import CouplingMap

def star_to_line_layout():
    """Star CX pattern onto a line: count the 2q-gate inflation."""
    qc = QuantumCircuit(5)
    for leaf in (1, 2, 3, 4):
        qc.cx(0, leaf)
    n_in = sum(1 for i in qc.data if len(i.qubits) == 2)
    cmap = CouplingMap([[0, 1], [1, 0], [1, 2], [2, 1], [2, 3],
                        [3, 2], [3, 4], [4, 3]])
    out = transpile(qc, coupling_map=cmap, optimization_level=3,
                    seed_transpiler=1)
    n_out = sum(1 for i in out.data if len(i.qubits) == 2)
    return n_out - n_in''',
            tests="""def check(candidate):
    delta = candidate()
    assert delta >= 0""",
        )
    )

    # ---- aer / simulation (eval: 21) ---------------------------------------
    T.append(
        dict(
            id="qg_aer_bell_counts",
            difficulty="basic",
            module="qiskit_aer",
            entry="bell_shot_counts",
            docstring=(
                "Simulate the Bell circuit (H + CX + measure) for 512 shots "
                "with qiskit_aer.AerSimulator and seed_simulator=3, and "
                "return the counts dict."
            ),
            solution='''from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

def bell_shot_counts():
    """Deterministic-ish Bell counts with seed 3, 512 shots."""
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    sim = AerSimulator(seed_simulator=3)
    return dict(sim.run(qc, shots=512).result().get_counts())''',
            tests="""def check(candidate):
    counts = candidate()
    assert set(counts.keys()) <= {"00", "11"}
    assert sum(counts.values()) == 512""",
        )
    )

    T.append(
        dict(
            id="qg_aer_noise_depolarizing",
            difficulty="intermediate",
            module="qiskit_aer",
            entry="depolarized_bell_fidelity",
            docstring=(
                "Build a NoiseModel with a 1-qubit depolarizing error (p=0.1) "
                "applied to 'h' and 'cx' in qiskit_aer, run the Bell circuit "
                "for 2048 shots with seed_simulator=11, and return the "
                "fraction of shots that are 00 or 11."
            ),
            solution='''from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

def depolarized_bell_fidelity():
    """Bell survival fraction under p=0.1 depolarizing noise."""
    noise = NoiseModel()
    noise.add_quantum_error(depolarizing_error(0.1, 1), ["h"], [0])
    noise.add_quantum_error(depolarizing_error(0.1, 2), ["cx"], [0, 1])
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    sim = AerSimulator(noise_model=noise, seed_simulator=11)
    counts = sim.run(qc, shots=2048).result().get_counts()
    good = counts.get("00", 0) + counts.get("11", 0)
    return good / 2048''',
            tests="""def check(candidate):
    frac = candidate()
    # p=0.1 depolarizing on both gates: survival ~0.66-0.82
    assert 0.5 < frac <= 1.0""",
        )
    )

    T.append(
        dict(
            id="qg_aer_statevector_snapshot",
            difficulty="intermediate",
            module="qiskit_aer",
            entry="ghz_save_statevector",
            docstring=(
                "Run the 3-qubit GHZ circuit on AerSimulator(method="
                "'statevector') with a save_statevector instruction appended "
                "and return the Statevector from the result's data."
            ),
            solution='''from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector

def ghz_save_statevector():
    """GHZ via save_statevector on Aer."""
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(0, 2)
    qc.save_statevector()
    sim = AerSimulator(method="statevector")
    res = sim.run(qc).result()
    return res.data(0)["statevector"]''',
            tests="""def check(candidate):
    import numpy as np
    sv = candidate()
    arr = np.asarray(sv)
    probs = np.abs(arr) ** 2
    assert np.isclose(probs[0b000], 0.5, atol=1e-8)
    assert np.isclose(probs[0b111], 0.5, atol=1e-8)
    assert np.allclose(probs[[1, 2, 3, 4, 5, 6]], 0.0, atol=1e-8)""",
        )
    )

    # ---- runtime-style primitives (eval: qiskit_ibm_runtime 30) -----------
    T.append(
        dict(
            id="qg_primitive_counts_batch",
            difficulty="intermediate",
            module="qiskit.primitives",
            entry="sampler_bell_batch",
            docstring=(
                "Using qiskit.primitives.StatevectorSampler (V2 primitives), "
                "run TWO copies of the Bell circuit in one pub and return the "
                "list of measured-bitstring counts dicts, one per copy."
            ),
            solution='''from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

def sampler_bell_batch():
    """Two Bell pubs in one sampler call with seed 5."""
    def bell():
        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure([0, 1], [0, 1])
        return qc
    sampler = StatevectorSampler(seed=5)
    job = sampler.run([bell(), bell()], shots=256)
    res = job.result()
    out = []
    for pub in res:
        out.append(dict(pub.data.c.get_counts()))
    return out''',
            tests="""def check(candidate):
    counts_list = candidate()
    assert len(counts_list) == 2
    for counts in counts_list:
        assert sum(counts.values()) == 256
        assert set(counts.keys()) <= {"00", "11"}""",
        )
    )

    T.append(
        dict(
            id="qg_estimator_observables",
            difficulty="intermediate",
            module="qiskit.primitives",
            entry="estimator_zz_expectation",
            docstring=(
                "Using qiskit.primitives.StatevectorEstimator (V2), estimate "
                "<ZZ> for the 2-qubit circuit X on qubit 0 then CX(0,1); "
                "return the single float expectation."
            ),
            solution='''from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator

def estimator_zz_expectation():
    """<ZZ> on |11> is +1; circuit X(0)+CX(0,1) prepares |11>."""
    qc = QuantumCircuit(2)
    qc.x(0)
    qc.cx(0, 1)
    op = SparsePauliOp("ZZ")
    est = StatevectorEstimator(seed=9)
    res = est.run([(qc, op)]).result()
    return float(res[0].data.evs)''',
            tests="""def check(candidate):
    import numpy as np
    assert np.isclose(candidate(), 1.0, atol=1e-8)""",
        )
    )

    # ---- converters / DAG / qpy / qasm (eval-surface) ----------------------
    T.append(
        dict(
            id="qg_dag_node_census",
            difficulty="basic",
            module="qiskit.dagcircuit",
            entry="dag_gate_census",
            docstring=(
                "Convert a QuantumCircuit with h, cx, x into a DAGCircuit "
                "via circuit_to_dag and return the count of op nodes of "
                "each name as a dict."
            ),
            solution='''from qiskit import QuantumCircuit
from qiskit.converters import circuit_to_dag

def dag_gate_census():
    """Count DAG op nodes by gate name for a small circuit."""
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.x(1)
    dag = circuit_to_dag(qc)
    census = {}
    for node in dag.op_nodes():
        census[node.name] = census.get(node.name, 0) + 1
    return census''',
            tests="""def check(candidate):
    c = candidate()
    assert c.get("h") == 1 and c.get("cx") == 1 and c.get("x") == 1""",
        )
    )

    T.append(
        dict(
            id="qg_qpy_roundtrip",
            difficulty="basic",
            module="qiskit.qpy",
            entry="qpy_roundtrip_depth",
            docstring=(
                "Serialize a QuantumCircuit (h, cx on 2 qubits) to QPY bytes "
                "with qiskit.qpy.dump and load it back with qpy.load; return "
                "the loaded circuit's depth."
            ),
            solution='''import io
from qiskit import QuantumCircuit
from qiskit import qpy

def qpy_roundtrip_depth():
    """QPY serialize + deserialize preserves structure."""
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    buf = io.BytesIO()
    qpy.dump(qc, buf)
    buf.seek(0)
    loaded = qpy.load(buf)
    return loaded[0].depth()''',
            tests="""def check(candidate):
    from qiskit import QuantumCircuit
    assert candidate() == 2""",
        )
    )

    T.append(
        dict(
            id="qg_qasm2_dump_parse",
            difficulty="basic",
            module="qiskit.qasm2",
            entry="qasm2_roundtrip_qubits",
            docstring=(
                "Dump a 3-qubit QuantumCircuit containing only a single X on "
                "qubit 2 to OpenQASM 2 text with qiskit.qasm2.dumps, re-load "
                "it with qasm2.loads, and return the loaded circuit's "
                "num_qubits."
            ),
            solution='''from qiskit import QuantumCircuit
from qiskit import qasm2

def qasm2_roundtrip_qubits():
    """QASM2 text roundtrip must preserve qubit count."""
    qc = QuantumCircuit(3)
    qc.x(2)
    text = qasm2.dumps(qc)
    loaded = qasm2.loads(text)
    return loaded.num_qubits''',
            tests="""def check(candidate):
    assert candidate() == 3""",
        )
    )

    T.append(
        dict(
            id="qg_synthesis_clifford_t",
            difficulty="difficult",
            module="qiskit.synthesis",
            entry="clifford_synth_2q",
            docstring=(
                "Generate a random 2-qubit Clifford with seed=13 (qiskit."
                "quantum_info.random_clifford), synthesize it to a circuit "
                "with qiskit.synthesis.synth_clifford_full, and verify "
                "operator equality: return True if the synthesized circuit's "
                "Operator equals the Clifford's operator."
            ),
            solution='''import numpy as np
from qiskit.quantum_info import random_clifford, Operator
from qiskit.synthesis import synth_clifford_full

def clifford_synth_2q():
    """Synthesize a seeded Clifford and check operator equality."""
    cliff = random_clifford(2, seed=13)
    qc = synth_clifford_full(cliff)
    return bool(np.allclose(Operator(qc).data, cliff.to_matrix(),
                            atol=1e-9))''',
            tests="""def check(candidate):
    assert candidate() is True""",
        )
    )

    T.append(
        dict(
            id="qg_parameter_bind_circuit",
            difficulty="intermediate",
            module="qiskit.circuit",
            entry="bound_rx_angle",
            docstring=(
                "Build a QuantumCircuit with a Parameter theta on an RX gate, "
                "bind theta=pi/2 via assign_parameters, and return the "
                "bound circuit's Statevector on |0> (qiskit.quantum_info."
                "Statevector) as a numpy array."
            ),
            solution='''import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.quantum_info import Statevector

def bound_rx_angle():
    """RX(pi/2)|0> = (|0> - i|1>)/sqrt(2)."""
    theta = Parameter("theta")
    qc = QuantumCircuit(1)
    qc.rx(theta, 0)
    bound = qc.assign_parameters({theta: np.pi / 2})
    return np.asarray(Statevector(bound))''',
            tests="""def check(candidate):
    import numpy as np
    sv = candidate()
    assert np.isclose(abs(sv[0]) ** 2, 0.5, atol=1e-9)
    assert np.isclose(abs(sv[1]) ** 2, 0.5, atol=1e-9)""",
        )
    )

    T.append(
        dict(
            id="qg_amplitude_damping_t1",
            difficulty="intermediate",
            module="qiskit_aer.noise",
            entry="amplitude_damping_survival",
            docstring=(
                "Simulate |1> under amplitude damping (gamma=0.25) for 512 "
                "shots with seed_simulator=2 using qiskit_aer's "
                "amplitude_damping_error on an 'id' gate applied twice; "
                "return the fraction of shots measured as 1."
            ),
            solution='''from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, amplitude_damping_error

def amplitude_damping_survival():
    """|1> survival after two damped id layers, gamma=0.25."""
    err = amplitude_damping_error(0.25)
    noise = NoiseModel()
    noise.add_quantum_error(err, ["id"], [0])
    qc = QuantumCircuit(1, 1)
    qc.x(0)
    qc.id(0)
    qc.id(0)
    qc.measure(0, 0)
    sim = AerSimulator(noise_model=noise, seed_simulator=2)
    counts = sim.run(qc, shots=512).result().get_counts()
    return counts.get("1", 0) / 512''',
            tests="""def check(candidate):
    frac = candidate()
    # (0.75)^2 = 0.5625 expected survival; sampling tolerance
    assert 0.45 < frac < 0.70""",
        )
    )

    T.append(
        dict(
            id="qg_hellinger_distinguish",
            difficulty="intermediate",
            module="qiskit.quantum_info",
            entry="hellinger_orthogonal",
            docstring=(
                "Compute qiskit.quantum_info.hellinger_fidelity between the "
                "probability dicts of |00> and |11> (basis states, given as "
                "counts-like dicts) and return the value."
            ),
            solution='''from qiskit.quantum_info import hellinger_fidelity

def hellinger_orthogonal():
    """Hellinger fidelity of disjoint distributions is 0."""
    p = {"00": 1}
    q = {"11": 1}
    return float(hellinger_fidelity(p, q))''',
            tests="""def check(candidate):
    import numpy as np
    assert np.isclose(candidate(), 0.0, atol=1e-9)""",
        )
    )

    T.append(
        dict(
            id="qg_statevector_partial_trace_order",
            difficulty="intermediate",
            module="qiskit.quantum_info",
            entry="trace_out_first",
            docstring=(
                "From the 2-qubit Statevector |10> (qubit 0 in |1>, qubit 1 "
                "in |0>), trace out qubit 0 and return the remaining "
                "single-qubit DensityMatrix as a numpy array (must be |1>: "
                "diag(0,1))."
            ),
            solution='''import numpy as np
from qiskit.quantum_info import Statevector, partial_trace, DensityMatrix

def trace_out_first():
    """Tracing qubit 0 of |10> leaves qubit 1 in |1>."""
    sv = Statevector.from_label("10")
    dm = partial_trace(sv, [0])
    return np.asarray(dm)''',
            tests="""def check(candidate):
    import numpy as np
    m = candidate()
    assert m.shape == (2, 2)
    assert np.isclose(m[0, 0], 0.0, atol=1e-9)
    assert np.isclose(m[1, 1], 1.0, atol=1e-9)""",
        )
    )

    T.append(
        dict(
            id="qg_barrier_grouping",
            difficulty="basic",
            module="qiskit.circuit",
            entry="barrier_split_count",
            docstring=(
                "Build a 3-qubit circuit with x(0), barrier, x(1), x(2), and "
                "return the number of instruction tuples (qc.data entries)."
            ),
            solution='''from qiskit import QuantumCircuit

def barrier_split_count():
    """x, barrier, x, x -> 4 data entries."""
    qc = QuantumCircuit(3)
    qc.x(0)
    qc.barrier()
    qc.x(1)
    qc.x(2)
    return len(qc.data)''',
            tests="""def check(candidate):
    assert candidate() == 4""",
        )
    )

    return T


# ---------------------------------------------------------------------------
# G3: exec-green validation
# ---------------------------------------------------------------------------
def run_solution(task: dict, workdir: Path) -> dict:
    prog = (
        task["solution"] + "\n\n" + task["tests"] + f"\ncheck({task['entry']})\nprint('PASS_OK')\n"
    )
    p = workdir / f"sol_{task['id']}.py"
    p.write_text(prog)
    try:
        r = subprocess.run(
            [sys.executable, str(p)],
            capture_output=True,
            text=True,
            timeout=PER_TASK_TIMEOUT_S,
            cwd=str(workdir),
        )
        return {
            "passed": r.returncode == 0 and "PASS_OK" in r.stdout,
            "stderr_tail": (r.stderr or "")[-300:],
        }
    except subprocess.TimeoutExpired:
        return {"passed": False, "stderr_tail": "EXEC_TIMEOUT"}


# ---------------------------------------------------------------------------
# Row emission (dual style, G4)
# ---------------------------------------------------------------------------
def build_completion_prompt(task: dict) -> str:
    """HumanEval-completion style: code prefix with imports + signature +
    docstring (exact text from the solution, ast-located)."""
    import ast
    import textwrap

    tree = ast.parse(task["solution"])
    fn = None
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == task["entry"]:
            fn = node
            break
    if fn is None:
        raise SystemExit(f"entry {task['entry']} not found for {task['id']}")
    lines = task["solution"].splitlines()
    # imports: all top-level Import/ImportFrom before the function
    imports = []
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append(ast.get_source_segment(task["solution"], node))
    # signature + docstring: def line through end of the docstring if the
    # first statement is a docstring (HumanEval prompts carry both).
    if (
        len(fn.body) > 1
        and isinstance(fn.body[0], ast.Expr)
        and isinstance(getattr(fn.body[0], "value", None), ast.Constant)
        and isinstance(fn.body[0].value.value, str)
    ):
        doc_end = fn.body[0].end_lineno
    else:
        doc_end = fn.body[0].lineno - 1
    sig = textwrap.dedent("\n".join(lines[fn.lineno - 1 : doc_end]))
    # ensure trailing colon after the signature (before docstring text)
    if ":" not in sig.split("\n")[0]:
        sig = sig.replace("\n", ":\n", 1)
    return "\n".join(imports) + "\n\n" + sig.strip() + "\n"


def build_instruction_prompt(task: dict) -> str:
    return (
        task["docstring"] + f"\nYou must implement this using a function named "
        f"`{task['entry']}` taking no arguments."
    )


def completion_body(task: dict) -> str:
    """The gold completion for the completion-style prompt: the function
    body WITHOUT the signature/imports/docstring (all in the prompt).
    ast-based: robust against multiline signatures."""
    import ast

    tree = ast.parse(task["solution"])
    fn = None
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == task["entry"]:
            fn = node
            break
    if fn is None:
        raise SystemExit(f"entry {task['entry']} not found in solution for {task['id']}")
    lines = task["solution"].splitlines()
    # body starts after the docstring if present
    start = fn.body[0].lineno - 1
    if (
        len(fn.body) > 1
        and isinstance(fn.body[0], ast.Expr)
        and isinstance(getattr(fn.body[0], "value", None), ast.Constant)
        and isinstance(fn.body[0].value.value, str)
    ):
        start = fn.body[1].lineno - 1
    end = fn.end_lineno
    # keep original indentation: the completion continues INSIDE the def
    # (dedent would push the body to module level and break reassembly)
    body = "\n".join(lines[start:end])
    return body.rstrip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT_DIR / "C10611_ibm_track_v26_corpus.jsonl"))
    args = ap.parse_args()

    # G1 freeze
    bench_rows = g1_freeze()
    leak_set = leak_hash_set(bench_rows)
    print(f"[G2] leak set: {len(leak_set)} benchmark hashes")

    tasks = author_tasks()
    print(f"[authored] {len(tasks)} fresh qiskit tasks")

    # G3 exec-green on gold solutions
    workdir = OUT_DIR / "_c10611_work"
    workdir.mkdir(parents=True, exist_ok=True)
    green = []
    for t in tasks:
        res = run_solution(t, workdir)
        if res["passed"]:
            green.append(t)
        else:
            print(f"  RED {t['id']}: {res['stderr_tail'][-160:]}")
    print(f"[G3] gold green: {len(green)}/{len(tasks)}")
    if len(green) < len(tasks):
        # continue with green subset but record the red ones
        red_ids = [t["id"] for t in tasks if t not in green]
        print(f"[G3] dropping red tasks: {red_ids}")

    # G2 leak guard + G4 dual-style emission + G5 reassembly exec
    rows = []
    leaks = []
    reassembly_fails = []
    for t in green:
        comp_body = completion_body(t)
        pairs = [
            ("qhe_completion", build_completion_prompt(t), comp_body),
            ("hard_instruction", build_instruction_prompt(t), t["solution"]),
        ]
        # G5: prompt + completion + tests + check(entry) must exec green
        for style, prompt, completion in pairs:
            if style == "qhe_completion":
                program = (
                    prompt
                    + "\n"
                    + completion
                    + "\n\n"
                    + t["tests"]
                    + f"\ncheck({t['entry']})\nprint('PASS_OK')\n"
                )
            else:
                program = (
                    completion + "\n\n" + t["tests"] + f"\ncheck({t['entry']})\nprint('PASS_OK')\n"
                )
            p = workdir / f"g5_{t['id']}_{style}.py"
            p.write_text(program)
            try:
                r = subprocess.run(
                    [sys.executable, str(p)],
                    capture_output=True,
                    text=True,
                    timeout=PER_TASK_TIMEOUT_S,
                    cwd=str(workdir),
                )
                ok = r.returncode == 0 and "PASS_OK" in r.stdout
            except subprocess.TimeoutExpired:
                ok = False
            if not ok:
                reassembly_fails.append((t["id"], style))
        for style, prompt, completion in pairs:
            for blob in (completion, prompt):
                h = sha256b(blob.strip().encode())
                if h in leak_set:
                    leaks.append((t["id"], style))
            rows.append(
                {
                    "format": "chat-sft-v1",
                    "source_schema": "ibm-track-v26-c10611",
                    "example_id": f"{t['id']}::{style}",
                    "prompt_kind": f"v26_{style}",
                    "task_id": t["id"],
                    "module": t["module"],
                    "difficulty": t["difficulty"],
                    "entry_point": t["entry"],
                    "prompt_style": style,
                    "task_spec": prompt,
                    "completion": completion,
                    "completion_exec_green": True,
                    "messages": [
                        {"role": "system", "content": SYS_PROMPT},
                        {"role": "user", "content": prompt},
                        {"role": "assistant", "content": completion},
                    ],
                }
            )
    if leaks:
        print(f"[G2] FAIL-CLOSED: leak hits {leaks}")
        return 1
    print(f"[G2] PASS: 0 leak hits across {len(rows)} rows")
    if reassembly_fails:
        print(f"[G5] FAIL-CLOSED: prompt+completion reassembly RED: {reassembly_fails}")
        return 1
    print(f"[G5] PASS: {2 * len(green)} reassemblies green")

    # style census (G4)
    styles = {}
    for r in rows:
        styles[r["prompt_style"]] = styles.get(r["prompt_style"], 0) + 1
    assert set(styles) == {"qhe_completion", "hard_instruction"}
    print(f"[G4] PASS: dual style {styles}")

    out = Path(args.out)
    with open(out, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    spec = {
        "card": "C-10611",
        "created_utc": now_utc(),
        "tasks": len(green),
        "rows": len(rows),
        "styles": styles,
        "modules": sorted({r["module"] for r in rows}),
        "difficulty": {
            k: sum(1 for r in rows if r["difficulty"] == k)
            for k in ("basic", "intermediate", "difficult")
        },
        "leak_guard": "sha256 vs 139-benchmark {canonical,test,prompt} set: 0 hits",
        "benchmark_manifest": str(BENCH_DIR / "MANIFEST.json"),
        "no_fabrication": True,
    }
    (OUT_DIR / "C10611_ibm_track_v26_spec.json").write_text(json.dumps(spec, indent=1) + "\n")
    print(f"[written] {out} ({len(rows)} rows)")
    print(json.dumps(spec, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
