#!/usr/bin/env python3
"""Stage-B converter: distillation sampling rows -> RL tasks with SEMANTIC tests.

Rows in questions_and_code.jsonl whose reference stdout is nondeterministic
(random sampling) cannot use stage-A's output-equality tests. For each such
row this script:

  1. runs the reference 3x (fresh subprocess, per-process temp file),
  2. classifies the task from question + stdout (content-based; the
     nondet_categories.json assignment is used as a fallback hint),
  3. derives semantic-test parameters from the problem statement and/or the
     reference runs (thresholds),
  4. builds a self-contained tests.py whose run_tests(candidate_path) runs
     the candidate and asserts SEMANTIC properties (distribution / energy /
     phase / fidelity / decoded statistics ...),
  5. self-checks: the reference must pass 3/3; a deliberately broken variant
     (per-category code mutation) must fail — otherwise the row is recorded
     in /tmp/stageb/repair_report.jsonl instead of being shipped,
  6. writes evals/tasks/quantum_distill_sampling/<id>/{task.json,
     solution.py, tests.py} and the benchmark file
     evals/benchmarks/quantum_distill_v3_sampling.txt.

Rows whose reference FAILS its own checker 3/3 (broken references) are NOT
shipped — they need reference repair, not tests.

Usage:
  python3 scripts/build_rl_tasks_stageB.py [--start N] [--end N]
      [--out-dir evals/tasks/quantum_distill_sampling]
      [--benchmark evals/benchmarks/quantum_distill_v3_sampling.txt]
      [--workers 4] [--repair-report /tmp/stageb/repair_report.jsonl]
      [--checkpoint-dir /tmp/stageb/checkpoints]
"""

from __future__ import annotations

import argparse
import ast
import json
import math
import multiprocessing
import os
import pathlib
import re
import subprocess
import sys
import time
from collections import Counter

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import stageb_common as sc  # noqa: E402

DATA = (
    "/Users/daxu/software/quantum-gpt/data/generated/"
    "quantum_dedup_1k_glm52_soft_distill_v3_verified_nologit_v3/"
    "questions_and_code.jsonl"
)
CATEGORIES = "/tmp/stageb/nondet_categories.json"
OUT_DIR = pathlib.Path("evals/tasks/quantum_distill_sampling")
BENCHMARK_FILE = "evals/benchmarks/quantum_distill_v3_sampling.txt"
REPAIR_REPORT = "/tmp/stageb/repair_report.jsonl"
CHECKPOINT_DIR = "/tmp/stageb/checkpoints"
RUN_TIMEOUT = 180
RUNS = 3
MAX_WORKERS = 4

TASK_JSON = {
    "domain": "quantum",
    "category": "distill_v3_sampling",
    "candidate_file": "solution.py",
    "test_file": "tests.py",
    "allowed_import_roots": [],
    "derive_behavior_hints_from_tests": False,
}

# ------------------------------------------------------------------ helpers


def normalize(text: str) -> str:
    lines = []
    for line in text.splitlines():
        lines.append(" ".join(line.split()))
    return "\n".join(lines).strip()


def parse_edges(question: str):
    """First bracket group in the question containing >=2 (a, b) pairs."""
    m = re.search(r"\[[^\]]*\(\s*\d+\s*,\s*\d+\s*\)[^\]]*\]", question)
    if not m:
        return None
    pairs = re.findall(r"\(\s*(\d+)\s*,\s*(\d+)\s*\)", m.group(0))
    if len(pairs) < 2:
        return None
    return [(int(a), int(b)) for a, b in pairs]


def parse_float_pattern(text: str, patterns) -> float:
    for pat in patterns:
        m = re.search(pat, text, re.I)
        if m:
            try:
                return float(m.group(1))
            except (ValueError, IndexError):
                continue
    return None


def find_angle(text: str) -> float:
    m = re.search(r"(?:R|r)(?:Y|y|X|x)\(\s*([\d.]+)\s*\)", text)
    return float(m.group(1)) if m else None


def find_n_qubits(text: str) -> int:
    m = re.search(r"(\d+)\s+(?:evaluation )?qubits", text, re.I)
    if m:
        return int(m.group(1))
    m = re.search(r"(\d+)\s+nodes", text, re.I)
    if m:
        return int(m.group(1))
    return 0


# ------------------------------------------------------------------ classify


def classify_row(question: str, stdout: str, hint_cat: str) -> list:
    """Content-based checker candidate list (primary first), ordered so that
    ambiguous texts (e.g. surface-code bucket containing QAE/QPE/swap rows)
    resolve correctly."""
    q = question.lower()
    s = stdout.lower()
    cand = []
    if "hhl" in q:
        cand = ["hhl"]
    elif "amplitude estimation" in q:
        cand = ["qae"]
    elif "shor" in q or "order-finding" in q or "factors of" in s:
        cand = ["shor"]
    elif "phase estimation" in q or "estimated phase" in s:
        cand = ["qpe_phase"]
    elif "randomized benchmarking" in q or "error per clifford" in s:
        cand = ["random_benchmark"]
    elif "loschmidt" in q or " echo " in q or q.strip().startswith("echo"):
        cand = ["loschmidt"]
    elif "simon" in q or "hidden period" in q or "recovered period" in s:
        cand = ["simon"]
    elif "surface code" in q or "repetition code" in q or "logical error rate" in s:
        cand = ["surface_code"]
    elif "swap test" in q or "|<psi|phi>|" in s or "|<ψ|φ>|" in s:
        cand = ["swap_test"]
    elif "xeb" in q or "cross-entropy" in q or "xeb fidelity" in s:
        cand = ["xeb"]
    elif "teleport" in q:
        cand = ["teleport"]
    elif "grover" in q or "marked state" in q or "marked bitstring" in q:
        cand = ["grover"]
    elif "knapsack" in q:
        cand = ["knapsack"]
    elif "maxcut" in q or "max cut" in q or "qaoa" in q:
        cand = ["maxcut"]
    elif "vqe" in q:
        cand = ["vqe"]
    elif "imaginary-time" in q or "imaginary time" in q:
        cand = ["ite"]
    elif "ising chain" in q or "ising model" in q:
        cand = ["ising"]
    elif "xxz" in q or "heisenberg" in q:
        cand = ["xxz"]
    elif "hubbard" in q or "openfermion" in q:
        cand = ["hubbard"]
    elif "transpil" in q:
        cand = ["transpile"]
    elif "povm" in q or "discrimination" in q:
        cand = ["povm"]
    elif "random number" in q or "random integers" in s:
        cand = ["qrng"]
    elif "quantum walk" in q or "walk on a cycle" in q:
        cand = ["walk"]
    elif "bit-flip code" in q or "bitflip" in q or "bit flip code" in q:
        cand = ["bitflip"]
    elif "chsh" in q:
        cand = ["chsh"]
    elif "zero-noise extrapolation" in q or "extrapolation error" in s or "zne" in q:
        cand = ["zne"]
    elif ("mid-circuit" in q or ("if statement" in q and "qasm" in q)) and "ghz" not in q:
        cand = ["qasm3"]
    elif "ghz" in q:
        if "stabilizer" in s:
            cand = ["stabilizer", "concentration", "statevector"]
        elif "expectation value" in s or "<z" in s:
            cand = ["z_expectation", "concentration", "statevector"]
        else:
            cand = ["concentration", "statevector", "stabilizer"]
    elif "bell" in q:
        cand = ["concentration", "statevector"]
    elif "statevector" in q:
        cand = ["statevector", "concentration"]
    if cand:
        return cand
    # fall back to the (noisy) precomputed category
    cat_map = {
        "ghz_counts": ["concentration", "statevector"],
        "bell_counts": ["concentration", "statevector"],
        "maxcut_qaoa": ["maxcut"],
        "surface_code_stim": ["surface_code"],
        "grover_search": ["grover"],
        "other": [],
        "teleportation": ["teleport"],
        "qpe_phase": ["shor", "qpe_phase", "hhl"],
        "qasm3_midcircuit": ["qasm3"],
        "bitflip_code": ["bitflip"],
        "povm_discrimination": ["povm"],
        "random_benchmark": ["random_benchmark", "loschmidt"],
        "qrng": ["qrng"],
        "vqe_energy": ["vqe"],
        "quantum_walk": ["walk"],
        "statevector_fidelity": ["xeb", "statevector"],
        "knapsack_annealing": ["knapsack"],
    }
    return cat_map.get(hint_cat, [])


# ------------------------------------------------------------------ params


def derive_params(checker: str, question: str, stdouts: list, code: str):
    """Returns params dict or None if they cannot be derived."""
    if checker == "concentration":
        return {"p_lo": 0.30, "label": "counts", "total_min": 0.6}
    if checker == "statevector":
        return {"fid_min": 0.99}
    if checker == "stabilizer":
        return {"frac_min": 0.98}
    if checker == "z_expectation":
        return {"z_min": 0.85}
    if checker == "chsh":
        return {"s_min": 2.0}
    if checker == "zne":
        errs = []
        for s in stdouts:
            m = re.search(
                r"(?:Zero-noise extrapolated|ZNE extrapolated|"
                r"Zero-noise estimate|Extrapolated \(linear fit\)|"
                r"Extrapolated <ZZ>|extrapolated <ZZ>)[^\d.]*"
                r"([\d.]+)",
                s,
                re.I,
            )
            m2 = re.search(
                r"Ideal(?:\s*<ZZ>\s*(?:value)?|\s+value)?\s*" r"[:=]?\s*([\d.]+)",
                s,
                re.I,
            )
            if m and m2:
                errs.append(abs(float(m.group(1)) - float(m2.group(1))))
        if not errs:
            return None
        return {"err_max": max(errs) * 2 + 0.05}
    if checker == "maxcut":
        edges = parse_edges(question)
        if not edges:
            return None
        n_nodes = find_n_qubits(question)
        n_nodes = n_nodes or (max(max(e) for e in edges) + 1)
        return {"edges": edges, "n_nodes": n_nodes}
    if checker == "vqe":
        vqe_es = []
        for s in stdouts:
            es = re.findall(r"(?:VQE|vqe)[^:\n]*?(?:energy|Energy)\s*[:=]\s*(-?\d+\.?\d*)", s)
            if es:
                vqe_es.append(float(es[0]))
        if not vqe_es:
            return None
        return {"e_max": max(vqe_es) + 0.15, "exact_slack": 0.6}
    if checker == "qpe_phase":
        expected = parse_float_pattern(
            question,
            [
                r"Z\*\*\s*\(\s*2\s*\*\s*([\d.]+)\s*\)",
                r"exp\(\s*2\s*\*\s*pi\s*\*\s*i\s*\*\s*([\d.]+)\s*\)",
                r"target\s+phase[^\d]*([\d.]+)",
                r"phase[^\d]*([\d.]+)",
            ],
        )
        if expected is None:
            return None
        return {"expected": expected, "tol": 0.1}
    if checker == "shor":
        m = re.search(r"N\s*=\s*(\d+)", question)
        if not m:
            return None
        N = int(m.group(1))
        expected = None
        for f in range(2, int(math.sqrt(N)) + 1):
            if N % f == 0:
                expected = [f, N // f]
                break
        return {"N": N, "expected_factors": expected}
    if checker == "hhl":
        # 2x2 HHL with 3-4 clock qubits: a working implementation matches
        # numpy.linalg.solve to ~0.05-0.1; broken ones are >= 0.6. Fixed bar.
        if not any(re.search(r"Absolute\s+error\s*:", s, re.I) for s in stdouts):
            return None
        return {"err_max": 0.2}
    if checker == "qae":
        theta = find_angle(question)
        if theta is None:
            return None
        m = re.search(r"(\d+)\s+evaluation qubits", question, re.I)
        m_qubits = int(m.group(1)) if m else None
        return {"theta": theta, "m": m_qubits, "amp_tol": 0.04}
    if checker == "swap_test":
        angles = re.findall(r"(?:R|r)(?:Y|y|X|x)\(\s*([\d.]+)\s*\)", question)
        if len(angles) < 2:
            return None
        return {"theta_psi": float(angles[0]), "theta_phi": float(angles[1]), "tol": 0.06}
    if checker == "simon":
        m = re.search(
            r"(?:period|hidden string|hidden\s+period)\s*(?:s\s*)?[:=]?\s*" r"['\"]?([01]{3,})",
            question,
            re.I,
        )
        if not m:
            return None
        return {"expected_s": m.group(1)}
    if checker == "teleport":
        angle = find_angle(question)
        if angle is None:
            for s in stdouts:
                p = parse_float_pattern(
                    s,
                    [
                        r"Theoretical\s+P\(\|1>\)[:\s]*([\d.]+)",
                        r"Expected\s+P\(\|1>\)\s*=\s*([\d.]+)",
                        r"Expected\s+P\(1\)\s*=\s*([\d.]+)",
                        r"\(expected[:\s]*([\d.]+)\)",
                    ],
                )
                if p is not None and 0.0 < p < 1.0:
                    angle = 2 * math.asin(math.sqrt(p))
                    break
        if angle is None:
            return None
        return {"angle": angle, "tol": 0.06, "p_val_min": 0.001}
    if checker == "grover":
        target = None
        m = re.search(
            r"marked\s+(?:state|bitstring)\s*[:=]?\s*['\"]?\|?" r"([01]{3,})",
            question,
            re.I,
        )
        if m:
            target = m.group(1)
        if target is None:
            m = re.search(
                r"for\s+the\s+\d-qubit\s+marked\s+state\s*\|?" r"([01]{3,})",
                question,
                re.I,
            )
        if target is None:
            m = re.search(r"Grover\s+search\s+for\s*\|?([01]{3,})>?", question, re.I)
        if m:
            target = m.group(1)
        if target is None:
            for s in stdouts:
                m = re.search(
                    r"(?:Target state|Marked bitstring|Marked state)"
                    r"\s*[:=]\s*\|?['\"]?([01]{3,})",
                    s,
                    re.I,
                )
                if m:
                    target = m.group(1)
                    break
        if target is None:
            return None
        return {"target": target, "p_min": 0.6}
    if checker == "walk":
        supports, spreads, mixed = [], [], []
        for s in stdouts:
            m = re.findall(r"(?:Node|Position)\s+(\d+):\s*([\d.]+)", s, re.I)
            if not m:
                continue
            raw = {int(k): float(v) for k, v in m}
            tot = sum(raw.values())
            probs = {k: v / tot for k, v in raw.items()}
            supports.append(sum(1 for v in probs.values() if v > 1e-9))
            spreads.append(max(probs) - min(probs))
            mixed.append(len({p % 2 for p in probs}) > 1)
        if not supports:
            return None
        # even-step walks legitimately stay on one parity; only require mixed
        # parity when the reference itself shows both
        return {
            "support_min": max(2, min(supports) - 1),
            "spread_min": max(1, min(spreads) - 1),
            "require_mixed_parity": any(mixed),
        }
    if checker == "knapsack":
        m = re.search(r"values?\s*\[([^\]]*)\]", question, re.I)
        m2 = re.search(r"weights?\s*\[([^\]]*)\]", question, re.I)
        m3 = re.search(r"capacity\s*(\d+)", question, re.I)
        if not m or not m2 or not m3:
            return None
        values = [int(x) for x in re.findall(r"\d+", m.group(1))]
        weights = [int(x) for x in re.findall(r"\d+", m2.group(1))]
        return {"values": values, "weights": weights, "capacity": int(m3.group(1))}
    if checker == "xeb":
        return {"fid_min": 0.5}
    if checker == "surface_code":
        return {"max_rate": 0.5}
    if checker == "qasm3":
        return {}
    if checker == "povm":
        return {"wrong_max": 0.05, "correct_min": 0.1}
    if checker == "qrng":
        m = re.search(r"(\d+)\s+random integers?\s+in\s*\[0,\s*(\d+)\)", question, re.I)
        if not m:
            return None
        return {
            "count": int(m.group(1)),
            "range_max": int(m.group(2)),
            "mean_lo": 0.15,
            "mean_hi": 0.85,
        }
    if checker == "random_benchmark":
        return {"epc_max": 0.1, "monotone_tol": 0.05}
    if checker == "loschmidt":
        return {"echo_min": 0.9, "decay_gap": 0.003}
    if checker == "ising":
        m = re.search(r"(\d+)\s+spins", question)
        mj = re.search(r"(?:J|J_val|J_phys|Jj)\s*=\s*([\d.]+)", question)
        mh = re.search(r"h_?0\s*=\s*(-?[\d.]+)", question)
        if not m or not mj or not mh:
            return None
        return {
            "n": int(m.group(1)),
            "J": float(mj.group(1)),
            "h0": float(mh.group(1)),
            "etol": 1e-3,
        }
    if checker == "xxz":
        errs = []
        for s in stdouts:
            m = re.search(
                r"(?:Absolute difference|Absolute error)[:\s]*" r"([\d.]+)",
                s,
            )
            if m:
                errs.append(float(m.group(1)))
        if not errs:
            return None
        return {"err_max": max(errs) * 2 + 0.02}
    if checker == "hubbard":
        es = []
        for s in stdouts:
            m = re.search(r"Ground state energy\s*:\s*(-?[\d.]+)", s)
            if m:
                es.append(float(m.group(1)))
        if not es:
            return None
        return {"e_max": max(es) + 0.05}
    if checker == "transpile":
        return {}
    if checker == "ite":
        errs = []
        for s in stdouts:
            m = re.search(
                r"(?:Energy error|Energy difference)[:\s]*" r"([\d.eE+-]+)",
                s,
            )
            if m:
                try:
                    errs.append(float(m.group(1)))
                except ValueError:
                    continue
        if not errs:
            return None
        return {"err_max": max(errs) * 1e4 + 1e-5, "overlap_min": 0.999}
    if checker == "bitflip":
        theta = find_angle(question)
        if theta is None:
            return None
        return {"theta": theta, "tol": 0.08}
    return None


# ------------------------------------------------------------------ mutations
# Each returns a mutated code string, or None if the pattern is absent.
# A candidate is accepted when the semantic checker FAILS on its output.


def _mut_h_to_x(code):
    for pat, rep in [
        (r"qc\.h\(([^)]*)\)", r"qc.x(\1)"),
        (r"\.append\(cirq\.H\.on\(([^)]*)\)\)", r".append(cirq.X.on(\1))"),
        (r"cirq\.H\.on\(([^)]*)\)", r"cirq.X.on(\1)"),
        (r"cirq\.H\(([^)]*)\)", r"cirq.X(\1)"),
        (r"\.append\(cirq\.H\(([^)]*)\)\)", r".append(cirq.X(\1))"),
        (r"(append\(\s*)[\"']H[\"']", r'\g<1>"X"'),  # Stim
        (r"add_gate\(\s*H\(", r"add_gate(X("),  # qulacs
        (r"add_H_gate\(0\)", r"add_X_gate(1)"),  # qulacs method
        (r"ApplyToEach\(H,", r"ApplyToEach(X,"),  # Q#
        (r"^(\s*)H\(([^)]*)\);?(\s*)$", r"\1X(\2)\3"),  # Q# string
        (r"H\(([^)]*)\);?", r"X(\1)"),  # Q# inline
        (r"cirq\.H\.on_each\(", r"cirq.X.on_each("),  # Cirq
        (r"\.h\(([^)]*)\)", r".x(\1)"),  # generic
    ]:
        m = re.search(pat, code, re.M)
        if m:
            return re.sub(pat, rep, code, count=1, flags=re.M)
    return None


def _mut_delete_h(code):
    """Delete the state-prep H line(s): the circuit then measures |0...0>."""
    m = re.search(r"^\s*qc\.h\([^)]*\)\s*$", code, re.M)
    if m:
        return re.sub(r"^\s*qc\.h\([^)]*\)\s*$", "# h removed (broken)", code, count=1, flags=re.M)
    m = re.search(r"^\s*circuit\.append\(\s*[\"']H[\"']", code, re.M)
    if m:
        return re.sub(
            r"^\s*circuit\.append\(\s*[\"']H[\"'].*$",
            "# H removed (broken)",
            code,
            count=1,
            flags=re.M,
        )
    m = re.search(r"^\s*h\s*q\[\d+\];?\s*$", code, re.M)
    if m:
        return re.sub(r"^\s*h\s*q\[\d+\];?\s*$", "# h removed (broken)", code, count=1, flags=re.M)
    return None


def _mut_stab_ancilla_h(code):
    """Corrupt the ancilla Hadamard test: add an X after EVERY ancilla H so
    the ancilla leaves the X-measurement basis; the reported +1 fraction
    then drops to ~0/0.5, so 'deterministic +1' fails."""

    def _rep(mm, qarg):
        return f"{mm.group(1)}sim.h({qarg})\n{mm.group(1)}sim.x({qarg})"

    pat = r"^(\s*)sim\.h\((ancilla|n|[1-9][0-9]*)\)(\s*)$"
    m = re.search(pat, code, re.M)
    if m:
        return re.sub(pat, lambda mm: _rep(mm, mm.group(2)), code, flags=re.M)

    def _rep2(mm):
        return (
            f'{mm.group(1)}circuit.append("H", [{mm.group(2)}])\n'
            f'{mm.group(1)}circuit.append("X", [{mm.group(2)}])'
        )

    pat2 = r"^(\s*)circuit\.append\(\s*[\"']H[\"'],\s*\[?(ancilla)\]?\)\s*$"
    m = re.search(pat2, code, re.M)
    if m:
        return re.sub(pat2, _rep2, code, flags=re.M)
    return None


def _mut_shots(code):
    for pat, rep in [
        (r"(repetitions\s*=\s*)\d+", r"\g<1>10"),
        (r"(shots\s*=\s*)\d+", r"\g<1>10"),
        (r"(num_shots\s*=\s*)\d+", r"\g<1>10"),
    ]:
        m = re.search(pat, code)
        if m:
            return re.sub(pat, rep, code, count=1)
    return None


def _mut_if_test(code):
    m = re.search(r"with\s+qc\.if_test\(", code)
    if m:
        return re.sub(r"with\s+qc\.if_test\(", "if False:", code, count=1)
    return None


def mutations(checker: str) -> list:
    """Ordered mutation factories for the checker's broken-variant."""
    if checker in ("concentration", "statevector", "z_expectation", "grover", "qae", "hhl"):
        return [_mut_h_to_x, _mut_delete_h, _mut_shots]
    if checker == "stabilizer":
        return [_mut_stab_ancilla_h, _mut_h_to_x, _mut_delete_h, _mut_shots]
    if checker == "qrng":
        return [_mut_delete_h, _mut_h_to_x, _mut_shots]
    if checker == "qpe_phase":
        return [_mut_h_to_x, _mut_delete_h, _mut_shots]
    if checker == "shor":
        return [_mut_shor_swaps, _mut_h_to_x]
    if checker == "simon":
        return [_mut_h_to_x, _mut_delete_h, _mut_shots]
    if checker == "walk":
        return [_mut_walk_steps, _mut_h_to_x]
    if checker == "maxcut":
        return [_mut_maxcut_cut, _mut_maxcut_edges, _mut_shots]
    if checker == "vqe":
        return [_mut_maxiter, _mut_coeff]
    if checker == "teleport":
        return [
            _mut_if_test,
            _mut_teleport_cirq,
            _mut_teleport_cirq2,
            _mut_teleport_cirq3,
            _mut_teleport_qsharp,
            _mut_teleport_statevector,
        ]
    if checker == "bitflip":
        return [_mut_if_test, _mut_bitflip_theta]
    if checker == "qasm3":
        return [_mut_qasm3_no_h, _mut_qasm3_no_if]
    if checker == "random_benchmark":
        return [_mut_rb_p, _mut_depol]
    if checker == "loschmidt":
        return [_mut_loschmidt, _mut_h_to_x]
    if checker == "ising":
        return [_mut_ising_j]
    if checker == "xxz":
        return [_mut_steps]
    if checker == "hubbard":
        return [_mut_coulomb]
    if checker == "transpile":
        return [_mut_transpile_opt, _mut_basis]
    if checker == "ite":
        return [_mut_steps]
    if checker == "xeb":
        return [_mut_xeb, _mut_xeb2]
    if checker == "surface_code":
        return [_mut_distances, _mut_surface_rate]
    if checker == "zne":
        return [_mut_rb_p, _mut_depol]
    if checker == "swap_test":
        return [_mut_h_to_x, _mut_shots]
    if checker in ("chsh", "povm", "knapsack"):
        return [_mut_h_to_x, _mut_shots]
    return []


def _mut_walk_steps(code):
    m = re.search(r"range\(\s*steps\s*\)", code)
    if m:
        return re.sub(r"range\(\s*steps\s*\)", "range(1)", code, count=1)
    return None


def _mut_maxcut_cut(code):
    m = re.search(r"bits\[[^\]]*\]\s*!=\s*bits\[[^\]]*\]", code)
    if m:
        return re.sub(r"(bits\[[^\]]*\]\s*)!=(.*)", r"\1==\2", code, count=1)
    m = re.search(r"!=\s*.*bits", code)
    if m:
        return re.sub(r"!=", "==", code, count=1)
    return None


def _mut_maxcut_edges(code):
    m = re.search(r"edges?\s*=\s*\[[^\]]*\]", code, re.I)
    if not m:
        return None
    pairs = re.findall(r"\(\s*\d+\s*,\s*\d+\s*\)", m.group(0))
    if len(pairs) < 2:
        return None
    last = pairs[-1]
    return code.replace(last, "(0, 0)", 1)


def _mut_maxiter(code):
    m = re.search(r"['\"]maxiter['\"]\s*:\s*\d+", code)
    if m:
        return re.sub(r"(['\"]maxiter['\"]\s*:\s*)\d+", r"\g<1>2", code, count=1)
    return None


def _mut_coeff(code):
    """Drop the transverse X field: the VQE then converges to the ZZ-only
    ground state, which is far above the true ground energy."""
    m = re.search(r"(h_x|c_x0|c_x1)\s*=\s*[\d.]+", code)
    if m:
        return re.sub(r"(h_x|c_x0|c_x1)\s*=\s*[\d.]+", r"\g<1> = 0.0", code, count=1)
    m = re.search(r"add_operator\([\d.]+,\s*\"X\s+[01]\"\)", code)
    if m:
        return re.sub(
            r"add_operator\([\d.]+,\s*(\"X\s+[01]\"\))", r"add_operator(0.0, \1)", code, count=1
        )
    return None


def _mut_teleport_cirq(code):
    m = re.search(r"q_bob", code)
    if m:
        pats = [r"^\s*.*CNOT\([^)]*q_bob[^)]*\).*$", r"^\s*.*CZ\([^)]*q_bob[^)]*\).*$"]
        for pat in pats:
            mm = re.search(pat, code, re.M)
            if mm:
                return re.sub(
                    pat, "# correction removed (broken variant)", code, count=1, flags=re.M
                )
    return None


def _mut_teleport_qsharp(code):
    for pat in [
        r"^\s*Controlled\s+X\([^)]*\);\s*$",
        r"^\s*Controlled\s+Z\([^)]*\);\s*$",
        r"^\s*(?:CNOT|CZ)\((?:alice|msg), bob\);\s*$",
    ]:
        m = re.search(pat, code, re.M)
        if m:
            return re.sub(pat, "// correction removed (broken variant)", code, count=1, flags=re.M)
    return None


def _mut_teleport_cirq2(code):
    """Remove Cirq deferred-measurement corrections (classical controls)."""
    m = re.search(r"\.with_classical_controls\(", code)
    if m:
        return re.sub(
            r"^.*\.with_classical_controls\(.*$",
            "# correction removed (broken variant)",
            code,
            count=1,
            flags=re.M,
        )
    return None


def _mut_teleport_statevector(code):
    """Disable the classical corrections in a statevector teleportation."""
    m = re.search(r"^\s*q2 = (X|Z) @ q2\s*$", code, re.M)
    if m:
        return re.sub(
            r"^\s*q2 = (X|Z) @ q2\s*$",
            "# correction removed (broken variant)",
            code,
            count=1,
            flags=re.M,
        )
    return None


def _mut_teleport_cirq3(code):
    """Remove the receiver-correction gates in a plain-append Cirq
    teleportation (no classical controls, q2 = receiver)."""
    m = re.search(
        r"^\s*circuit\.append\(cirq\.(?:CNOT|CZ)\([^)]*,\s*q2\)\)" r"\s*$",
        code,
        re.M,
    )
    if m:
        return re.sub(
            r"^\s*circuit\.append\(cirq\.(?:CNOT|CZ)\([^)]*," r"\s*q2\)\)\s*$",
            "# correction removed (broken)",
            code,
            count=1,
            flags=re.M,
        )
    return None


def _mut_bitflip_theta(code):
    m = re.search(r"qc\.ry\(\s*theta\s*,", code)
    if m:
        return re.sub(r"qc\.ry\(\s*theta\s*,", "qc.ry(0.0,", code, count=1)
    m = re.search(r"qc\.ry\(\s*[\d.]+\s*,", code)
    if m:
        return re.sub(r"qc\.ry\(\s*[\d.]+\s*,", "qc.ry(0.0,", code, count=1)
    return None


def _mut_qasm3_no_h(code):
    m = re.search(r"^\s*h\s*q\[\d+\];?\s*$", code, re.M)
    if m:
        return re.sub(r"^\s*h\s*q\[\d+\];?\s*$", "# h removed (broken)", code, count=1, flags=re.M)
    return None


def _mut_qasm3_no_if(code):
    m = re.search(r"^\s*if\s*\(c\[0\]\)\s*\{\s*$", code, re.M)
    if m:
        return re.sub(
            r"^\s*if\s*\(c\[0\]\)\s*\{\s*$", "# if removed (broken)", code, count=1, flags=re.M
        )
    return None


def _mut_rb_p(code):
    m = re.search(r"^\s*(p|p_dep|p_err|noise|depolarizing)\s*=\s*0\.\d+", code, re.M)
    if m:
        return re.sub(
            r"^(\s*(?:p|p_dep|p_err|noise|depolarizing)\s*=\s*)" r"0\.\d+",
            r"\g<1>0.9",
            code,
            count=1,
            flags=re.M,
        )
    return None


def _mut_depol(code):
    m = re.search(r"depolarizing_error\(\s*p\s*,\s*\d+\)", code)
    if m:
        return re.sub(
            r"depolarizing_error\(\s*p\s*,\s*\d+\)", "depolarizing_error(0.9, 1)", code, count=1
        )
    return None


def _mut_loschmidt(code):
    m = re.search(r"append\(u_dag_ops\)", code)
    if m:
        return re.sub(
            r"^\s*.*append\(u_dag_ops\).*$",
            "# U^dagger removed (broken variant)",
            code,
            count=1,
            flags=re.M,
        )
    return None


def _mut_ising_j(code):
    m = re.search(r"^\s*(J_val|J_phys|J)\s*=\s*([\d.]+)\s*(#.*)?$", code, re.M)
    if m:
        name, val = m.group(1), m.group(2)
        return re.sub(
            rf"^(\s*{name}\s*=\s*){re.escape(val)}", rf"\g<1>-{val}", code, count=1, flags=re.M
        )
    return None


def _mut_steps(code):
    m = re.search(r"^\s*steps\s*=\s*\d+", code, re.M)
    if m:
        return re.sub(r"(^\s*steps\s*=\s*)\d+", r"\g<1>1", code, count=1, flags=re.M)
    return None


def _mut_coulomb(code):
    m = re.search(r"coulomb\s*=\s*[\d.]+", code)
    if m:
        # replace every occurrence (a function-default must not be missed)
        return re.sub(r"(coulomb\s*=\s*)[\d.]+", r"\g<1>6.0", code)
    return None


def _mut_basis(code):
    m = re.search(r"basis(?:_gates)?\s*=\s*\[[^\]]*\]", code)
    if m:
        return re.sub(
            r"basis(?:_gates)?\s*=\s*\[[^\]]*\]", "basis_gates = ['rx', 'ry']", code, count=1
        )
    return None


def _mut_transpile_opt(code):
    """Transpile every level with optimization_level=0: no improvement."""
    m = re.search(r"optimization_level\s*=\s*level", code)
    if m:
        return re.sub(r"optimization_level\s*=\s*level", "optimization_level=0", code, count=1)
    return None


def _mut_shor_swaps(code):
    """Break the modular-multiplication permutation: remove the literal-int
    swap gates (identity cmodmul -> phase 0 -> period 1 -> no factors).
    Falls back to removing the first swap line (usually inside the cmodmul
    builder) which makes factoring fail or crash."""
    m = re.search(
        r"^\s*(?:qc|U|circuit|g)\.swap\(\s*\d+\s*,\s*\d+\s*\)" r"\s*$",
        code,
        re.M,
    )
    if m:
        return re.sub(
            r"^\s*(?:qc|U|circuit|g)\.swap\(\s*\d+\s*,\s*\d+\s*\)" r"\s*$",
            "# swap removed (broken)",
            code,
            flags=re.M,
        )
    m = re.search(r"^\s*(?:qc|U|circuit)\.swap\([^)]*\)\s*$", code, re.M)
    if m:
        return re.sub(
            r"^\s*(?:qc|U|circuit)\.swap\([^)]*\)\s*$",
            "# swap removed (broken)",
            code,
            count=1,
            flags=re.M,
        )
    return None


def _mut_xeb(code):
    m = re.search(r"fidelity\s*\*=\s*\(\s*2\s*\*\*\s*n\s*\)", code)
    if m:
        return re.sub(r"fidelity\s*\*=\s*\(\s*2\s*\*\*\s*n\s*\)", "fidelity *= 1.0", code, count=1)
    return None


def _mut_xeb2(code):
    m = re.search(r"np\.mean\(p_vals\)\s*\*\s*dim", code)
    if m:
        return re.sub(r"np\.mean\(p_vals\)\s*\*\s*dim", "np.mean(p_vals)", code, count=1)
    return None


def _mut_distances(code):
    m = re.search(r"distances\s*=\s*\[[\d,\s]+\]", code)
    if m:
        return re.sub(r"distances\s*=\s*\[[\d,\s]+\]", "distances = [5, 3]", code, count=1)
    return None


def _mut_surface_rate(code):
    for pat in [r"(errs|errors|num_errors)\s*/\s*(shots|num_shots|total)", r"errs\s*/\s*shots"]:
        m = re.search(pat, code)
        if m:
            return re.sub(pat, r"\g<1>", code, count=1)
    m = re.search(
        r"total_errors\s*/\s*\(\s*num_shots\s*\*\s*" r"num_observables\s*\)",
        code,
    )
    if m:
        return re.sub(
            r"total_errors\s*/\s*\(\s*num_shots\s*\*\s*" r"num_observables\s*\)",
            "total_errors * 4",
            code,
            count=1,
        )
    m = re.search(r"np\.mean\(\s*logical_errors\s*\)", code)
    if m:
        return re.sub(
            r"np\.mean\(\s*logical_errors\s*\)", "np.mean(logical_errors) + 0.9", code, count=1
        )
    return None


# ------------------------------------------------------------------ tests.py


def helper_source() -> str:
    src = pathlib.Path(HERE / "stageb_common.py").read_text()
    start = src.find("# __STAGEB_COMMON_MAIN_START__")
    if start != -1:
        src = src[:start]
    return src


SOURCE_CONTRACTS = {
    "cirq": {
        "framework_import_roots": ["cirq"],
        "circuit_constructors": ["Circuit"],
        "simulator_constructors": ["Simulator", "DensityMatrixSimulator"],
        "execution_methods": ["run", "simulate", "run_sweep", "simulate_sweep"],
        "require_dynamic_output": True,
    },
    "qiskit": {
        "framework_import_roots": ["qiskit"],
        "circuit_constructors": ["QuantumCircuit"],
        "simulator_constructors": ["AerSimulator", "StatevectorSimulator"],
        "execution_methods": ["run", "execute"],
        "require_dynamic_output": True,
    },
}


def source_contract_for(question: str, reference_code: str) -> dict:
    """Select a broad public-framework contract without copying reference logic."""
    tree = ast.parse(reference_code)
    roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            roots.add(node.module.split(".", 1)[0])
    lowered = question.lower()
    for framework in ("cirq", "qiskit"):
        if framework in roots or framework in lowered:
            return dict(SOURCE_CONTRACTS[framework])
    quantum_roots = sorted(
        roots
        & {
            "braket",
            "pennylane",
            "projectq",
            "pyquil",
            "qutip",
            "qulacs",
            "stim",
        }
    )
    return {
        "framework_import_roots": quantum_roots,
        "require_dynamic_output": True,
    }


def build_tests(
    row_id: str,
    checker: str,
    params: dict,
    source_contract: dict | None = None,
    timeout: int = RUN_TIMEOUT,
) -> str:
    return f"""# Auto-generated semantic checker for {row_id} ({checker}).
# run_tests(candidate_path) -> {{"passed": bool, "details": [str]}}
# Executes the candidate as a standalone script and asserts SEMANTIC
# properties (distribution / energy / phase / fidelity / decoded stats)
# instead of stdout equality — the reference output is nondeterministic
# (random sampling).
import pathlib
import sys

{helper_source()}

CHECKER_NAME = {checker!r}
CHECKER_PARAMS = {params!r}
SOURCE_CONTRACT = {dict(source_contract or {})!r}


def run_tests(candidate_path: str) -> dict:
    try:
        candidate_source = pathlib.Path(candidate_path).read_text(encoding="utf-8")
    except Exception as exc:
        return {{"passed": False, "details": [f"source contract: {{exc}}"]}}
    source_ok, source_details = validate_quantum_source_contract(
        candidate_source, SOURCE_CONTRACT
    )
    if not source_ok:
        return {{"passed": False, "details": source_details}}
    rc, stdout, stderr = run_candidate(candidate_path, timeout={timeout})
    if rc != 0:
        return {{
            "passed": False,
            "details": ["exit code {{r}}" .format(r=rc) + ": " + stderr.strip()[:500]],
        }}
    details = []
    fn = globals()["check_" + CHECKER_NAME]
    passed = fn(stdout, details, **CHECKER_PARAMS)
    return {{"passed": bool(passed), "details": details}}
"""


# ------------------------------------------------------------------ workers

_RUNNER = None


def worker_init():
    global _RUNNER
    _RUNNER = f"/tmp/stageb/runner_{os.getpid()}.py"


def run_code(code: str, timeout: int = RUN_TIMEOUT):
    with open(_RUNNER, "w") as fh:
        fh.write(code)
    try:
        p = subprocess.run(
            [sys.executable, _RUNNER],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"


def run_triple(code):
    return [run_code(code) for _ in range(RUNS)]


def run_once(code):
    return run_code(code)


# ------------------------------------------------------------------ main


def load_rows() -> list:
    rows = [json.loads(line) for line in open(DATA) if line.strip()]
    cats = json.load(open(CATEGORIES)) if os.path.exists(CATEGORIES) else {}
    return rows, cats


def process_row(row_id, row, hint_cat, pool, ckpt_dir, out_dir):
    """Returns (status, payload). status in {'shipped', 'repaired'}."""
    code = row["code"]
    question = row["question"]
    triple = pool.apply(run_triple, (code,))
    stdouts = []
    for rc, out, err in triple:
        if rc != 0:
            return (
                "repaired",
                {
                    "id": row_id,
                    "category": hint_cat,
                    "reason": f"reference exit {rc}: {err.strip()[:200]}",
                    "candidates": [],
                },
            )
        stdouts.append(out)
    if not stdouts[0].strip():
        return (
            "repaired",
            {
                "id": row_id,
                "category": hint_cat,
                "reason": "empty reference stdout",
                "candidates": [],
            },
        )
    candidates = classify_row(question, stdouts[0], hint_cat)
    attempts = []
    chosen = None
    params = None
    for ck in candidates:
        p = derive_params(ck, question, stdouts, code)
        if p is None:
            attempts.append({"checker": ck, "passed": 0, "note": "params not derivable"})
            continue
        passed = 0
        dets = []
        for s in stdouts:
            d = []
            fn = getattr(sc, "check_" + ck)
            ok = fn(s, d, **p)
            dets.append({"passed": bool(ok), "details": d})
            if ok:
                passed += 1
        attempts.append({"checker": ck, "passed": passed, "details": dets})
        if passed == RUNS:
            chosen, params = ck, p
            break
    if chosen is None:
        return (
            "repaired",
            {
                "id": row_id,
                "category": hint_cat,
                "reason": "reference fails its own semantic check 3/3 (broken reference)",
                "candidates": attempts,
            },
        )
    # broken variant must fail the checker
    broken_code = None
    for mut in mutations(chosen):
        b = mut(code)
        if b is None or b == code:
            continue
        rc, out, err = pool.apply(run_once, (b,))
        d = []
        fn = getattr(sc, "check_" + chosen)
        if rc != 0:
            failed = True
            d.append(f"broken variant exit {rc}: {err.strip()[:120]}")
        else:
            failed = not fn(out, d, **params)
        if failed:
            broken_code = b
            attempts.append(
                {
                    "checker": chosen,
                    "broken_variant": f"mutation {mut.__name__}",
                    "broken_details": d,
                }
            )
            break
    if broken_code is None:
        return (
            "repaired",
            {
                "id": row_id,
                "category": hint_cat,
                "reason": "no failing broken variant found",
                "candidates": attempts,
            },
        )
    # write the task dir
    task_dir = out_dir / row_id
    task_dir.mkdir(parents=True, exist_ok=True)
    (task_dir / "task.json").write_text(
        json.dumps(
            {
                **TASK_JSON,
                "id": row_id,
                "name": question[:80],
                "task_prompt": question,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    (task_dir / "solution.py").write_text(
        f'"""Replace this stub with your solution for {row_id}."""\n'
    )
    source_contract = source_contract_for(question, code)
    (task_dir / "tests.py").write_text(
        build_tests(row_id, chosen, params, source_contract=source_contract)
    )
    return (
        "shipped",
        {
            "id": row_id,
            "category": hint_cat,
            "checker": chosen,
            "params": params,
            "candidates": attempts,
        },
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--end", type=int, default=0, help="exclusive; 0 = all")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out-dir", default=str(OUT_DIR))
    ap.add_argument("--benchmark", default=BENCHMARK_FILE)
    ap.add_argument("--repair-report", default=REPAIR_REPORT)
    ap.add_argument("--checkpoint-dir", default=CHECKPOINT_DIR)
    ap.add_argument("--workers", type=int, default=MAX_WORKERS)
    args = ap.parse_args()

    rows, cats = load_rows()
    # Only the SAMPLING rows (stage-A owns the deterministic ones): keep rows
    # whose qc-id appears in nondet_categories.json.
    rows = [(i, r) for i, r in enumerate(rows) if f"qc-{i + 1:04d}" in cats]
    if args.end > 0:
        rows = [(i, r) for i, r in rows if args.start <= i < args.end]
    elif args.limit:
        rows = rows[: args.limit]
    offset = args.start if args.end > 0 else 0

    out_dir = pathlib.Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ckpt_dir = pathlib.Path(args.checkpoint_dir)
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    ckpt_file = ckpt_dir / f"stageb_shard_{offset}_{offset + len(rows)}.jsonl"

    done = set()
    if ckpt_file.exists():
        for line in open(ckpt_file):
            if line.strip():
                done.add(json.loads(line)["id"])
    print(f"rows {offset}..{offset + len(rows)}; {len(done)} already done", flush=True)

    fresh_run = not ckpt_file.exists()
    repair_fh = open(args.repair_report, "w" if fresh_run else "a")
    shipped: list[str] = []
    shipped_checkers = Counter()
    repaired: list[dict] = []
    t0 = time.time()
    n_workers = min(args.workers, MAX_WORKERS)
    pool = multiprocessing.Pool(n_workers, initializer=worker_init)
    try:
        for i, (row_idx, row) in enumerate(rows):
            row_id = f"qc-{row_idx + 1:04d}"
            if row_id in done:
                continue
            hint_cat = cats.get(row_id, "")
            status, payload = process_row(row_id, row, hint_cat, pool, ckpt_dir, out_dir)
            payload["category"] = payload.get("category") or hint_cat
            record = {"id": row_id, "status": status, "category": payload.get("category", hint_cat)}
            if status == "shipped":
                shipped.append(row_id)
                shipped_checkers[payload["checker"]] += 1
                record["checker"] = payload["checker"]
            else:
                repaired.append(payload)
                repair_fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
                repair_fh.flush()
            with open(ckpt_file, "a") as fh:
                fh.write(json.dumps(record) + "\n")
            if (i + 1) % 10 == 0 or status == "repaired":
                print(
                    f"  ...{i + 1}/{len(rows)} "
                    f"shipped={len(shipped)} repaired={len(repaired)} "
                    f"({time.time() - t0:.0f}s)",
                    flush=True,
                )
    finally:
        pool.close()
        pool.join()
    repair_fh.close()

    shipped.sort()
    # merge with any previously-written benchmark ids (shard-safe)
    existing = set()
    if os.path.exists(args.benchmark):
        for line in open(args.benchmark):
            line = line.strip()
            if line and not line.startswith("#"):
                existing.add(line)
    all_ids = sorted(existing | set(shipped))
    with open(args.benchmark, "w") as fh:
        fh.write(
            "# RL task set auto-converted from quantum_distill v3 "
            "verified_nologit (sampling rows, semantic tests)\n"
        )
        fh.write(
            f"# {len(all_ids)} tasks total; {len(repaired)} rows needing "
            f"reference repair (this shard).\n"
        )
        fh.write("\n".join(all_ids) + "\n")

    print(
        f"DONE: {len(shipped)} shipped (this run) -> {out_dir}/ ; "
        f"{len(repaired)} repaired -> {args.repair_report}"
    )
    print("repair reasons:", Counter(r["reason"] for r in repaired))
    print("shipped checkers:", dict(shipped_checkers))
    return 0


if __name__ == "__main__":
    sys.exit(main())
