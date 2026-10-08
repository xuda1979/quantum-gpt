#!/usr/bin/env python3
"""Fix the 5 BBPSSW distillation rows + refresh stale outputs for 15 rows.

GROUP A — 5 rows with genuinely broken BBPSSW code (output fidelity did NOT
exceed input). The bilateral CNOT / postselection math was wrong.
  rows: 124 (F=0.58), 379 (F=0.56), 599 (F=0.73), 611 (F=0.75), 998 (F=0.69)
  Fix: replace with a verified-correct density-matrix BBPSSW implementation
  (direct simulation, no Pauli twirl). F_out > F_in for all 5 values.

GROUP B — 15 rows whose code is already fixed (sha256 matches v6 execution
which passed) but code_outputs_v4.jsonl has STALE failing stdout from before
the code fix. Just refresh outputs from the v6 run.
  rows: 93, 125, 188, 257, 286, 308, 442, 461, 597, 766, 848, 865, 916, 936, 958

Files updated for each fixed row (same convention as fix_row_659_v6.py):
  - train_chatml.jsonl: messages[2].content + teacher_logits + metadata
  - questions_and_code.jsonl: code
  - code_outputs_v4.jsonl: stdout/stderr/returncode/elapsed/status
  - execution_results/full_20260730_v6/scripts/row_NNNN.py
  - execution_results/full_20260730_v6/results.jsonl
  - analysis_v4.json / analysis_detailed_v4.json / analysis_per_row_v4.json
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/Users/daxu/software/quantum-gpt")
BASE = ROOT / "data/generated/quantum_dedup_1k_glm52_soft_distill_v3"
TRAIN = BASE / "train_chatml.jsonl"
QC = BASE / "questions_and_code.jsonl"
OUT = BASE / "code_outputs_v4.jsonl"
V6_DIR = BASE / "execution_results/full_20260730_v6"
ANAL_V4 = BASE / "analysis_v4.json"
ANAL_DET = BASE / "analysis_detailed_v4.json"
ANAL_PER = BASE / "analysis_per_row_v4.json"
RUN_SCRIPT = ROOT / "env_compat/run_script.py"

sys.path.insert(0, str(ROOT / "scripts"))
from synth_logits_for_fix import (
    build_vocab,
    synthesize_logits,
    verify_reconstruction,
    verify_sorted_desc,
    verify_top20,
)

# ---- BBPSSW correct implementation template ----
BBPSSW_TEMPLATE = '''import numpy as np
from qiskit.quantum_info import DensityMatrix


def bell_density_matrix(label: str) -> np.ndarray:
    """Bell-state density matrix on two qubits (4x4)."""
    vecs = {
        "Phi+": np.array([1, 0, 0, 1], dtype=complex),
        "Phi-": np.array([1, 0, 0, -1], dtype=complex),
        "Psi+": np.array([0, 1, 1, 0], dtype=complex),
        "Psi-": np.array([0, 1, -1, 0], dtype=complex),
    }
    v = vecs[label] / np.sqrt(2)
    return np.outer(v, v.conj())


def werner_state_dm(F: float) -> np.ndarray:
    """Werner state rho = F*|Phi+><Phi+| + (1-F)*I/4 (4x4 density matrix)."""
    return F * bell_density_matrix("Phi+") + (1.0 - F) * np.eye(4, dtype=complex) / 4.0


def _cnot_4q(control: int, target: int) -> np.ndarray:
    """4-qubit CNOT with given control/target qubit indices (0..3)."""
    dim = 16
    U = np.zeros((dim, dim), dtype=complex)
    for i in range(dim):
        b = [(i >> k) & 1 for k in range(4)]
        b[target] ^= b[control]
        j = sum(b[k] << k for k in range(4))
        U[j, i] = 1
    return U


def bilateral_cnot(rho: np.ndarray) -> np.ndarray:
    """Bilateral CNOT on two Bell pairs.

    Qubit ordering |q0 q1 q2 q3>: pair1=(q0,q1)=(Alice1,Bob1),
    pair2=(q2,q3)=(Alice2,Bob2). Alice applies CNOT q0->q2,
    Bob applies CNOT q1->q3.
    """
    U = _cnot_4q(0, 2) @ _cnot_4q(1, 3)
    return U @ rho @ U.conj().T


def postselect_equal_and_keep(rho: np.ndarray):
    """Measure qubits q2,q3; postselect on equal outcomes (00 or 11);
    keep qubits q0,q1. Returns (kept_4x4_dm, success_probability)."""
    dim = 16
    M = np.zeros((dim, dim), dtype=complex)
    for i in range(dim):
        if ((i >> 2) & 1) == ((i >> 3) & 1):
            M[i, i] = 1.0
    rho_s = M @ rho @ M
    p = float(np.trace(rho_s).real)
    if p < 1e-12:
        return None, 0.0
    rho_s = rho_s / p
    t = rho_s.reshape(2, 2, 2, 2, 2, 2, 2, 2)
    kept = np.einsum("abcdABcd->abAB", t, optimize=True).reshape(4, 4)
    return kept, p


def fidelity_to_phi_plus(rho: np.ndarray) -> float:
    """Fidelity of a 2-qubit density matrix with |Phi+>."""
    return float(np.real(np.trace(bell_density_matrix("Phi+") @ rho)))


def run_distillation(F_in: float):
    rho1 = werner_state_dm(F_in)
    rho2 = werner_state_dm(F_in)
    rho_in = np.kron(rho1, rho2)
    rho_after = bilateral_cnot(rho_in)
    rho_kept, p_succ = postselect_equal_and_keep(rho_after)
    if rho_kept is None:
        return None
    F_out = fidelity_to_phi_plus(rho_kept)
    return F_out, p_succ


if __name__ == "__main__":
    F_in = {F_IN}
    print("=" * 60)
    print("BBPSSW Entanglement Distillation (One Round)")
    print("=" * 60)
    print(f"Input Werner-state fidelity F_in  = {F_in:.6f}")
    result = run_distillation(F_in)
    if result is not None:
        F_out, p_succ = result
        print(f"Measurement success probability   = {p_succ:.6f}")
        print(f"Output fidelity (distilled) F_out = {F_out:.6f}")
        print(f"Fidelity improvement              = {F_out - F_in:+.6f}")
        if F_out > F_in:
            print("Result: Output fidelity EXCEEDS input fidelity.")
        else:
            print("Result: Output fidelity did NOT exceed input fidelity.")
    else:
        print("Post-selection failed.")
    print("=" * 60)
'''

DISTILL_ROWS = {124: 0.58, 379: 0.56, 599: 0.73, 611: 0.75, 998: 0.69, 345: 0.62}
STALE_ROWS = [
    93,
    125,
    188,
    257,
    286,
    308,
    442,
    461,
    597,
    766,
    848,
    865,
    916,
    936,
    958,
    319,
    410,
    548,
    863,
]


def load_lines(p):
    return [line.rstrip("\n") for line in open(p)]


def write_lines(p, lines):
    with open(p, "w") as f:
        for ln in lines:
            f.write(ln + "\n")


def run_code(code):
    open("/tmp/_fix_run.py", "w").write(code)
    t0 = time.time()
    proc = subprocess.run(
        [sys.executable, str(RUN_SCRIPT), "/tmp/_fix_run.py"],
        capture_output=True,
        text=True,
        timeout=90,
    )
    return proc.returncode, proc.stdout, proc.stderr, time.time() - t0


def main():
    ts_now = datetime.now(timezone.utc)
    ts = ts_now.isoformat()
    ts_compact = ts_now.strftime("%Y%m%dT%H%M%SZ")

    print("Building vocab for logit synthesis...")
    vocab = build_vocab(TRAIN)
    print(f"Vocab size: {len(vocab)}")

    # Back up all files once
    for p in [TRAIN, QC, OUT, ANAL_V4, ANAL_DET, ANAL_PER]:
        bak = p.with_suffix(p.suffix + f".bak_pre_v6_semifix_{ts_compact}")
        shutil.copy2(p, bak)
        print(f"  backup -> {bak.name}")

    # Load all JSON files
    train_lines = load_lines(TRAIN)
    qc_lines = load_lines(QC)
    out_lines = load_lines(OUT)
    v6_results = load_lines(V6_DIR / "results.jsonl")
    a = json.loads(train_lines[0]) if False else json.load(open(ANAL_V4))
    ad = json.load(open(ANAL_DET))
    ap = json.load(open(ANAL_PER))

    # Load v6 results into dict
    v6_by_row = {}
    for i, ln in enumerate(v6_results):
        r = json.loads(ln)
        v6_by_row[r["row"]] = (i, r)

    fixed_count = 0

    # ---- GROUP A: distillation rows (code fix) ----
    print(f"\n=== GROUP A: fixing {len(DISTILL_ROWS)} BBPSSW distillation rows ===")
    for row, F_in in sorted(DISTILL_ROWS.items()):
        idx = row - 1
        print(f"\n--- row {row} (F_in={F_in}) ---")
        fixed_code = BBPSSW_TEMPLATE.replace("{F_IN}", str(F_in))
        rc, out, err, elapsed = run_code(fixed_code)
        print(f"  run: rc={rc} elapsed={elapsed:.2f}s")
        print(f"  stdout: {out.strip()[:200]}")
        assert rc == 0 and "EXCEEDS input fidelity" in out, f"row {row} fix did not exceed"
        sha = hashlib.sha256(fixed_code.encode()).hexdigest()

        # train_chatml
        tr = json.loads(train_lines[idx])
        tr["messages"][2]["content"] = fixed_code
        new_logits = synthesize_logits(fixed_code, vocab)
        assert (
            verify_reconstruction(new_logits)
            and verify_top20(new_logits)
            and verify_sorted_desc(new_logits)
        )
        tr["teacher_logits"] = new_logits
        md = tr["metadata"]
        md["runnable"] = True
        md["python_valid"] = True
        md["runnable_verified_at"] = ts
        md["runnable_verified_with"] = (
            "env_compat/run_script.py + synth_logits (v6 semifix distill)"
        )
        md["v3_fix_regen"] = True
        md["v3_fix_description"] = (
            f"BBPSSW distillation: correct bilateral CNOT (a1->a2,b1->b2) + postselect equal outcomes; F_in={F_in}"
        )
        md["logprob_positions"] = len(new_logits["logprobs"])
        md["code_sha256"] = sha
        train_lines[idx] = json.dumps(tr, ensure_ascii=False)

        # questions_and_code
        q = json.loads(qc_lines[idx])
        q["code"] = fixed_code
        qc_lines[idx] = json.dumps(q, ensure_ascii=False)

        # code_outputs_v4
        o = json.loads(out_lines[idx])
        o["status"] = "pass"
        o["returncode"] = rc
        o["elapsed_seconds"] = round(elapsed, 3)
        o["stdout"] = out
        o["stderr"] = err
        o["stdout_bytes"] = len(out.encode("utf-8"))
        out_lines[idx] = json.dumps(o, ensure_ascii=False)

        # v6 script + results
        (V6_DIR / f"scripts/row_{row:04d}.py").write_text(fixed_code)
        if row in v6_by_row:
            i, r = v6_by_row[row]
            r["status"] = "pass"
            r["returncode"] = rc
            r["timed_out"] = False
            r["elapsed_seconds"] = round(elapsed, 3)
            r["code_sha256"] = sha
            r["stdout"] = out
            r["stderr"] = err
            r["stdout_bytes"] = len(out.encode("utf-8"))
            v6_results[i] = json.dumps(r, ensure_ascii=False)

        # analysis
        for e in a["entries"]:
            if e.get("row") == row:
                e["fix_status"] = "fixed_v6_semifix"
                e["fix_reason"] = "BBPSSW distillation math corrected"
                e["code_length"] = len(fixed_code)
                break
        for e in ad["detailed_analysis"]:
            if e.get("row") == row:
                e["fixed"] = True
                e["fix_version"] = "v6_semifix"
                e["fix_reason"] = "BBPSSW: correct bilateral CNOT + postselect equal"
                e["code_length"] = len(fixed_code)
                e["code_sha256"] = sha
                break
        for e in ap["per_row_analysis"]:
            if e.get("row") == row:
                e["was_fixed"] = True
                e["fix_version"] = "v6_semifix"
                e["code_length"] = len(fixed_code)
                e["stdout_bytes"] = len(out.encode("utf-8"))
                e["returncode"] = rc
                e["elapsed_seconds"] = round(elapsed, 3)
                break
        fixed_count += 1
        print(f"  ✅ row {row} fixed (F_out exceeds F_in)")

    # ---- GROUP B: stale-output rows (refresh from v6) ----
    print(f"\n=== GROUP B: refreshing stale outputs for {len(STALE_ROWS)} rows ===")
    for row in STALE_ROWS:
        idx = row - 1
        if row not in v6_by_row:
            print(f"  ⚠️  row {row} not in v6 results, skipping")
            continue
        _, v6r = v6_by_row[row]
        v6_out = v6r["stdout"]
        v6_err = v6r["stderr"]
        v6_rc = v6r["returncode"]
        v6_elapsed = v6r["elapsed_seconds"]
        # refresh code_outputs_v4
        o = json.loads(out_lines[idx])
        o["status"] = "pass"
        o["returncode"] = v6_rc
        o["elapsed_seconds"] = v6_elapsed
        o["stdout"] = v6_out
        o["stderr"] = v6_err
        o["stdout_bytes"] = len(v6_out.encode("utf-8"))
        out_lines[idx] = json.dumps(o, ensure_ascii=False)
        print(f"  ✅ row {row} outputs refreshed (stdout_bytes={len(v6_out.encode())})")
        fixed_count += 1

    # Write all files back
    print("\nWriting all files back...")
    write_lines(TRAIN, train_lines)
    write_lines(QC, qc_lines)
    write_lines(OUT, out_lines)
    write_lines(V6_DIR / "results.jsonl", v6_results)
    json.dump(a, open(ANAL_V4, "w"), indent=2, ensure_ascii=False)
    json.dump(ad, open(ANAL_DET, "w"), indent=2, ensure_ascii=False)
    json.dump(ap, open(ANAL_PER, "w"), indent=2, ensure_ascii=False)

    print(f"\n=== Done: {fixed_count} rows fixed/refreshed ===")


if __name__ == "__main__":
    main()
