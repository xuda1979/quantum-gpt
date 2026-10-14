#!/usr/bin/env python3
"""C-10363 data-miner card: probe C-10358 gap symbols against frozen reference
solutions (evals/tasks/quantum/<dir>/candidate.py).

For each of the 13 failing tasks from the C-10358 step-322 failure-delta panel,
extract the api_gap symbols and verify each symbol appears in the corresponding
candidate.py reference solution. Fail-closed: any missing symbol aborts.

Deterministic; no training; outputs/ only.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PANEL_REL = "outputs/C10358_step322_failure_delta_panel.json"
EVAL_ROOT = ROOT / "evals" / "tasks" / "quantum"

BENCH_TO_DIR = {
    "quantum_phase_estimation_circuit": "phase_estimation_circuit",
    "quantum_qaoa_maxcut": "qaoa_maxcut",
    "quantum_density_matrix_partial_trace": "density_matrix_partial_trace",
    "quantum_error_correction_shor_9qubit": "quantum_error_correction_shor_9qubit",
    "quantum_trotterized_hamiltonian_evolution": "trotterized_hamiltonian_evolution",
    "quantum_channel_depolarizing": "quantum_channel_depolarizing",
    "quantum_ghz_state_witness": "ghz_state_witness",
    "quantum_pennylane_vqe_h2": "pennylane_vqe_h2",
    "quantum_cirq_qaoa_line": "cirq_qaoa_line",
    "quantum_braket_bell_state": "braket_bell_state",
    "quantum_qiskit_qft_entangled": "qiskit_qft_entangled",
    "quantum_qiskit_stabilizer_5qubit_code": "qiskit_stabilizer_5qubit_code",
    "quantum_pennylane_qml_iris_classification": "pennylane_qml_iris_classification",
}

MODULE_GAPS = {"pennylane", "cirq", "qiskit"}


def load_panel():
    p = ROOT / PANEL_REL
    if not p.is_file():
        raise RuntimeError("missing panel " + str(p))
    return json.loads(p.read_text())


def gap_rows_from_panel():
    panel = load_panel()
    out = []
    for t in panel["failing_tasks"]:
        gaps = [g.strip() for g in t["api_gap"].split(",") if g.strip()]
        out.append({
            "task_id": t["task_id"],
            "fault_class": t["fault_class"],
            "api_gap": t["api_gap"],
            "gaps": gaps,
            "task_dir": BENCH_TO_DIR.get(t["task_id"]),
        })
    return out


def validate(row):
    tid = row["task_id"]
    tdir = row["task_dir"]
    if tdir is None:
        return {**row, "valid": False, "reason": "no task_dir mapping"}
    cand = EVAL_ROOT / tdir / "candidate.py"
    if not cand.is_file():
        return {**row, "valid": False, "reason": "missing candidate.py " + str(cand)}
    src = cand.read_text(encoding="utf-8")
    task_json = EVAL_ROOT / tdir / "task.json"
    task_meta = {}
    if task_json.is_file():
        try:
            task_meta = json.loads(task_json.read_text(encoding="utf-8"))
        except Exception:
            task_meta = {}
    framework = str(task_meta.get("framework", ""))
    # union of candidate.py + tests.py text plus task.json metadata
    tsrc_path = EVAL_ROOT / tdir / "tests.py"
    tsrc = tsrc_path.read_text(encoding="utf-8") if tsrc_path.is_file() else ""
    alltext = src + "\n" + tsrc + "\n" + json.dumps(task_meta)
    sym_check = []
    for g in row["gaps"]:
        if g in MODULE_GAPS:
            present = bool(
                re.search(r"\bimport\s+" + re.escape(g) + r"\b", alltext) or
                re.search(r"\bfrom\s+" + re.escape(g) + r"\b", alltext) or
                re.search(r"\b" + re.escape(g) + r"\b", alltext)
            )
            kind = "(module)"
        else:
            present = bool(
                re.search(r"^def\s+" + re.escape(g) + r"\s*\(", src, re.M) or
                re.search(r"^class\s+" + re.escape(g) + r"\b", src, re.M) or
                re.search(r"^[A-Za-z_]\w*\s*=", src, re.M) and
                re.search(r"\b" + re.escape(g) + r"\b", src)
            )
            kind = "(symbol)"
        sym_check.append({"gap": g, "kind": kind, "present": present})
    missing = [s for s in sym_check if not s["present"]]
    return {
        **row,
        "valid": len(missing) == 0,
        "reason": "" if not missing
        else "missing in reference solutions: " + str([m["gap"] for m in missing]),
        "symbol_checks": sym_check,
    }


def main():
    rows = gap_rows_from_panel()
    results = [validate(r) for r in rows]
    all_ok = all(r["valid"] for r in results)
    report = {
        "card": "C-10363",
        "probe": "gap-symbol-validation",
        "panel_src": PANEL_REL,
        "n_failing_tasks": len(rows),
        "all_gap_symbols_valid_in_reference_solutions": all_ok,
        "rows": results,
    }
    out = ROOT / "outputs" / "C10363_gap_symbol_validation.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
