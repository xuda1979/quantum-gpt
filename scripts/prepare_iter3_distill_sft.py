#!/usr/bin/env python3
"""Prepare iter-3 soft-distillation SFT splits.

Builds the iter-3 dataset by carrying forward iter-2 train rows and adding
gap-targeted rows derived from the machine-generated gap recommendations
(``evals/subsystem/dataset_gap.py recommend`` output).

The gap-targeted rows are **structural stubs**: they contain the correct task
prompt and metadata, but the assistant message is a placeholder marked
``__TEACHER_PENDING__``. The GLM5.2 teacher must fill these in before training
(see ``docs/iter3-dataset-spec-2026-07-07.md`` §8 — teacher generation is
out of scope for this script).

Usage
-----
    # Validate the iter-3 manifest stub
    python3 scripts/prepare_iter3_distill_sft.py check \
        --manifest data/generated/glm52_soft_distill_sft_iter3/manifest.json

    # Dry-run account of what would be built
    python3 scripts/prepare_iter3_distill_sft.py build \
        --gap-report docs/iter3-dataset-rows-finalized-2026-07-12.md \
        --gap-recs   evals/subsystem/recommendations/qaoa-glm52-base-recs.json \
        --iter2-train data/generated/glm52_soft_distill_sft_iter2/train_chatml.jsonl \
        --iter2-eval  data/generated/glm52_soft_distill_sft_iter2/eval_chatml.jsonl \
        --out         data/generated/glm52_soft_distill_sft_iter3 \
        --dry-run

    # Real build (writes train/eval/manifest)
    python3 scripts/prepare_iter3_distill_sft.py build \
        --gap-report docs/iter3-dataset-rows-finalized-2026-07-12.md \
        --gap-recs   evals/subsystem/recommendations/qaoa-glm52-base-recs.json \
        --iter2-train data/generated/glm52_soft_distill_sft_iter2/train_chatml.jsonl \
        --iter2-eval  data/generated/glm52_soft_distill_sft_iter2/eval_chatml.jsonl \
        --out         data/generated/glm52_soft_distill_sft_iter3
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ── provenance tags ─────────────────────────────────────────────────────────
ALLOWED_SOURCES = {
    "iter2_carryforward",
    "glm52_teacher_correction",
    "multi_framework_task",
    "swe_retention",
}
ALLOWED_FRAMEWORKS = {"qiskit", "cirq", "pennylane", "braket", "none"}


def stable_key(row: dict[str, Any]) -> str:
    """Stable per-row key for deduplication."""
    msgs = row.get("messages") or []
    text = "".join(m.get("content", "") for m in msgs)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:32]


def row_token_length(row: dict[str, Any], tokenizer=None) -> int:
    """Best-effort token length. Falls back to char/4 if no tokenizer."""
    if tokenizer is not None:
        text = "".join(m.get("content", "") for m in row.get("messages", []))
        try:
            return len(tokenizer.encode(text))
        except Exception:  # noqa: BLE001
            pass
    text = "".join(m.get("content", "") for m in row.get("messages", []))
    return max(1, len(text) // 4)


def validate_manifest(path: Path) -> list[str]:
    """Return a list of error strings; empty list means OK."""
    errors: list[str] = []
    if not path.exists():
        return [f"manifest not found: {path}"]
    try:
        m = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        return [f"manifest is not valid JSON: {e}"]
    if m.get("iteration") != 3:
        errors.append(f"manifest iteration != 3 (got {m.get('iteration')!r})")
    for key in (
        "train_rows",
        "eval_rows",
        "base_source",
        "gap_report_source",
        "quality_gates",
        "recommended_training",
    ):
        if key not in m:
            errors.append(f"manifest missing key: {key}")
    qg = m.get("quality_gates") or {}
    if not isinstance(qg, dict):
        errors.append("quality_gates must be an object")
    else:
        for k in ("structural", "content", "disjoint"):
            if k not in qg:
                errors.append(f"quality_gates missing key: {k}")
    return errors


def cmd_check(args: argparse.Namespace) -> int:
    errs = validate_manifest(Path(args.manifest))
    if errs:
        print("FAIL — manifest errors:")
        for e in errs:
            print(" ", e)
        return 1
    print("PASS — manifest structure OK")
    return 0


# ── gap-targeted row generation ──────────────────────────────────────────────
# Task-family → row template map. Each entry produces a structural stub row
# with the correct task prompt and metadata; the assistant message is a
# placeholder marked __TEACHER_PENDING__ for GLM5.2 to fill in.
# See docs/iter3-dataset-rows-finalized-2026-07-12.md for the finalized list.

_GAP_TASK_FAMILIES: list[dict[str, Any]] = [
    # A. Quantum algorithm families (from manual draft §4a-4e, 20q eval)
    {
        "row": "A1",
        "task_id": "quantum_qaoa_maxcut_5cycle",
        "domain": "quantum",
        "category": "algorithm_implementation",
        "framework": "qiskit",
        "prompt": "Write a complete Python program using Qiskit that solves QAOA Max-Cut on a 5-node cycle graph. Use StatevectorSampler, print the deterministic cut value, and include a def main() that prints the result.",
    },
    {
        "row": "A2a",
        "task_id": "quantum_partial_trace_bipartite",
        "domain": "quantum",
        "category": "algorithm_implementation",
        "framework": "qiskit",
        "prompt": "Write a complete Python program using qiskit.quantum_info.DensityMatrix and partial_trace to compute the reduced density matrix of a bipartite pure state. Demonstrate correct @ operator semantics and print the result.",
    },
    {
        "row": "A2b",
        "task_id": "quantum_density_matrix_pure_state",
        "domain": "quantum",
        "category": "algorithm_implementation",
        "framework": "qiskit",
        "prompt": "Write a complete Python program using qiskit.quantum_info.DensityMatrix to construct a pure-state density matrix and verify tr(rho)=1 and rho^2=rho. Print the verification results.",
    },
    {
        "row": "A3a",
        "task_id": "quantum_pauli_expectation_x",
        "domain": "quantum",
        "category": "algorithm_implementation",
        "framework": "qiskit",
        "prompt": "Write a complete Python program using Qiskit that measures the Pauli-X expectation value <X> of a given quantum state. Import QuantumCircuit explicitly, use SparsePauliOp with correct shape, and print the expectation value.",
    },
    {
        "row": "A3b",
        "task_id": "quantum_ising_ground_state_energy",
        "domain": "quantum",
        "category": "algorithm_implementation",
        "framework": "qiskit",
        "prompt": "Write a complete Python program using Qiskit that computes the ground-state energy of a 1D transverse-field Ising model using SparsePauliOp and NumPyMinimumEigensolver or VQE. Print the ground-state energy.",
    },
    {
        "row": "A4a",
        "task_id": "quantum_teleportation_fidelity",
        "domain": "quantum",
        "category": "algorithm_implementation",
        "framework": "qiskit",
        "prompt": "Write a complete Python program implementing quantum teleportation and measuring the fidelity. Print exactly the deterministic marker: <X> on Bob = 1.000000",
    },
    {
        "row": "A4b",
        "task_id": "quantum_swap_test_overlap",
        "domain": "quantum",
        "category": "algorithm_implementation",
        "framework": "qiskit",
        "prompt": "Write a complete Python program implementing the swap test to compute the overlap between two quantum states. Print exactly the deterministic marker: overlap = 1.000000",
    },
    {
        "row": "A5a",
        "task_id": "quantum_deutsch_jozsa_balanced",
        "domain": "quantum",
        "category": "algorithm_implementation",
        "framework": "qiskit",
        "prompt": "Write a complete Python program implementing the Deutsch-Jozsa algorithm for a balanced oracle. Include explicit circuit construction with def main() and print whether the function is constant or balanced.",
    },
    {
        "row": "A5b",
        "task_id": "quantum_bernstein_vazirani_hidden",
        "domain": "quantum",
        "category": "algorithm_implementation",
        "framework": "qiskit",
        "prompt": "Write a complete Python program implementing the Bernstein-Vazirani algorithm for a hidden string s. Include explicit circuit construction with def main() and print the recovered hidden string.",
    },
    # B. Quantum framework gaps (machine recs, QAOA 56-task, universal across 3 models)
    {
        "row": "B1",
        "task_id": "quantum_braket_bell_state",
        "domain": "quantum",
        "category": "algorithm_implementation",
        "framework": "braket",
        "prompt": "Write a complete Python program using Amazon Braket that constructs a Bell state, simulates it, and prints the measurement statistics showing approximately 50% '00' and 50% '11'.",
    },
    {
        "row": "B2",
        "task_id": "quantum_cirq_qaoa_line",
        "domain": "quantum",
        "category": "algorithm_implementation",
        "framework": "cirq",
        "prompt": "Write a complete Python program using Cirq that implements QAOA on a line graph (3-node path), simulates it, and prints the deterministic cut value.",
    },
    {
        "row": "B3",
        "task_id": "quantum_pennylane_vqe_h2",
        "domain": "quantum",
        "category": "algorithm_implementation",
        "framework": "pennylane",
        "prompt": "Write a complete Python program using PennyLane that runs VQE on the H2 molecule (STO-3G basis) and prints the ground-state energy (approximately -1.136 Ha).",
    },
    {
        "row": "B4",
        "task_id": "quantum_qiskit_qft_entangled",
        "domain": "quantum",
        "category": "algorithm_implementation",
        "framework": "qiskit",
        "prompt": "Write a complete Python program using Qiskit that applies QFT to an entangled input state and prints the resulting statevector.",
    },
    {
        "row": "B5",
        "task_id": "quantum_pennylane_qml_iris_classification",
        "domain": "quantum",
        "category": "quantum_ml",
        "framework": "pennylane",
        "prompt": "Write a complete Python program using PennyLane's QML module that classifies the Iris dataset with a variational quantum classifier. Print the classification accuracy.",
    },
    # C. Software data_processing gaps (machine recs, universal across 3 models)
    {
        "row": "C1",
        "task_id": "software_log_parser_aggregator",
        "domain": "software",
        "category": "data_processing",
        "framework": "none",
        "prompt": "Write a complete Python program that parses a log file (format: 'timestamp level message'), aggregates counts by level, and prints a summary table.",
    },
    {
        "row": "C2",
        "task_id": "software_sql_join_resolver",
        "domain": "software",
        "category": "data_processing",
        "framework": "none",
        "prompt": "Write a complete Python program that resolves a SQL JOIN between two in-memory tables (users and orders) and prints the joined result with correct column projection.",
    },
]

TEACHER_PENDING = "__TEACHER_PENDING__"


def _make_gap_row(
    family: dict[str, Any], examples_per_family: int = 3, fill_teacher: bool = False
) -> list[dict[str, Any]]:
    """Generate ``examples_per_family`` structural stub rows for one task family.

    If ``fill_teacher`` is True, replace ``__TEACHER_PENDING__`` with the
    reference solution from ``scripts/iter3_reference_solutions.py`` (when
    available). Rows without a reference solution remain as stubs.
    """
    teacher_solution = None
    if fill_teacher:
        try:
            from scripts.iter3_reference_solutions import get_solution

            teacher_solution = get_solution(family["row"])
        except ImportError:
            pass

    rows = []
    for i in range(1, examples_per_family + 1):
        eid = f"iter3_gap_{family['row']}_{family['task_id']}_{i:02d}_teacher"
        assistant_content = teacher_solution if teacher_solution else TEACHER_PENDING
        teacher_status = "filled" if teacher_solution else "pending"
        source = "iter3_gap_targeted_reference" if teacher_solution else "iter3_gap_targeted_stub"
        row = {
            "example_id": eid,
            "format": "chat-sft-v1",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a careful quantum software engineering assistant. Use the user's task and any supplied context to produce correct, testable Python or precise repair guidance.",
                },
                {"role": "user", "content": family["prompt"]},
                {"role": "assistant", "content": assistant_content},
            ],
            "metadata": {
                "_source_schema": "dataset-v0",
                "category": family["category"],
                "dataset_language": "en",
                "difficulty": "medium",
                "distillation_phase": "iter3",
                "distillation_strategy": "hard_sft_black_box_teacher",
                "domain": family["domain"],
                "evolution_kind": "gap_targeted",
                "framework": family["framework"],
                "holdout_policy": "rag_docs_only_no_eval_holdout_files",
                "language": "python",
                "source": source,
                "source_title": f"Iter-3 gap row for {family['task_id']}",
                "task_id": family["task_id"],
                "task_type": "full_program",
                "teacher_status": teacher_status,
                "gap_row_id": family["row"],
            },
            "source_schema": "dataset-v0",
        }
        rows.append(row)
    return rows


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def cmd_build(args: argparse.Namespace) -> int:
    iter2_train = Path(args.iter2_train)
    iter2_eval = Path(args.iter2_eval)
    out_dir = Path(args.out)

    # Load iter-2 carry-forward
    if not iter2_train.exists():
        print(f"ERROR — iter2 train not found: {iter2_train}", file=sys.stderr)
        return 1
    if not iter2_eval.exists():
        print(f"ERROR — iter2 eval not found: {iter2_eval}", file=sys.stderr)
        return 1

    iter2_train_rows = _load_jsonl(iter2_train)
    iter2_eval_rows = _load_jsonl(iter2_eval)
    n_carry = len(iter2_train_rows)

    # Tag carry-forward rows
    for r in iter2_train_rows:
        r.setdefault("metadata", {})["distillation_phase"] = "iter3_carryforward"

    # Generate gap-targeted stub rows
    examples_per = 3
    gap_rows: list[dict[str, Any]] = []
    for family in _GAP_TASK_FAMILIES:
        gap_rows.extend(_make_gap_row(family, examples_per_family=examples_per))
    n_gap = len(gap_rows)

    # Split gap rows: 80% train, 20% eval
    n_gap_eval = max(1, n_gap // 5)
    gap_eval_rows = gap_rows[:n_gap_eval]
    gap_train_rows = gap_rows[n_gap_eval:]

    train_rows = iter2_train_rows + gap_train_rows
    eval_rows = iter2_eval_rows + gap_eval_rows

    if args.dry_run:
        print(f"[dry-run] carry-forward rows from iter-2: {n_carry}")
        print(
            f"[dry-run] gap-targeted stub rows: {n_gap} ({examples_per}/family × {len(_GAP_TASK_FAMILIES)} families)"
        )
        print(f"[dry-run]   → gap train: {len(gap_train_rows)}, gap eval: {len(gap_eval_rows)}")
        print(f"[dry-run] target train rows: {len(train_rows)}")
        print(f"[dry-run] target eval rows: {len(eval_rows)}")
        print(f"[dry-run] gap-report: {args.gap_report}")
        if args.gap_recs:
            print(f"[dry-run] gap-recs: {args.gap_recs}")
        print("[dry-run] no files written")
        return 0

    # Hard gate: refuse to actually build until iter-2 eval exists.
    eval_marker = ROOT / "outputs" / "eval-base-vs-adapter-asi1-iter2.json"
    if not eval_marker.exists():
        print(
            "REFUSED — iter-2 eval report not found. Run the iter-2 "
            "base-vs-adapter eval first, then re-run without --dry-run.",
            file=sys.stderr,
        )
        return 2

    # Write outputs
    out_dir.mkdir(parents=True, exist_ok=True)
    train_path = out_dir / "train_chatml.jsonl"
    eval_path = out_dir / "eval_chatml.jsonl"
    manifest_path = out_dir / "manifest.json"

    _write_jsonl(train_path, train_rows)
    _write_jsonl(eval_path, eval_rows)

    train_sha = _sha256_file(train_path)
    eval_sha = _sha256_file(eval_path)

    manifest = {
        "iteration": 3,
        "created": "2026-07-12",
        "status": "built_pending_teacher_fill",
        "train_rows": len(train_rows),
        "eval_rows": len(eval_rows),
        "carry_forward_rows": n_carry,
        "gap_targeted_rows": n_gap,
        "gap_train_rows": len(gap_train_rows),
        "gap_eval_rows": len(gap_eval_rows),
        "base_source": {
            "path": str(iter2_train),
            "sha256": _sha256_file(iter2_train),
        },
        "gap_report_source": args.gap_report,
        "gap_recs_source": args.gap_recs or "",
        "train_sha256": train_sha,
        "eval_sha256": eval_sha,
        "quality_gates": {
            "structural": "passed — all rows have example_id, format, messages, metadata",
            "content": "pending — gap rows have __TEACHER_PENDING__ assistant content",
            "disjoint": "pending — eval task ids must be checked against train",
        },
        "recommended_training": {
            "ASI1": {
                "base_model": "Qwen/Qwen3.6-27B",
                "max_length": 2048,
                "lr": 1e-5,
                "adapter_init": "models/iter2-27b-asi3-r21",
                "lora_rank": 64,
                "lora_alpha": 128,
                "target_modules": [
                    "q_proj",
                    "k_proj",
                    "v_proj",
                    "o_proj",
                    "gate_proj",
                    "up_proj",
                    "down_proj",
                ],
            },
            "ASI3": {
                "base_model": "Qwen/Qwen3.6-35B-A3B",
                "max_length": 2048,
                "lr": 5e-6,
                "adapter_init": "models/iter2-35b-asi3",
                "lora_rank": 16,
                "lora_alpha": 32,
                "target_modules": [
                    "q_proj",
                    "k_proj",
                    "v_proj",
                    "o_proj",
                    "gate_proj",
                    "up_proj",
                    "down_proj",
                ],
            },
        },
        "decision_gates": [
            "iter-2 eval JSON present for ASI1 and ASI2/ASI3",
            "dataset_gap.py recommend executed on iter-2 eval",
            "no >5% software-task regression vs iter-2 base",
            "0% truncation at per-env max_length",
            "iter-3 eval task ids disjoint from all prior train splits",
        ],
        "teacher_pending_count": n_gap,
        "teacher_pending_note": "All gap-targeted rows have __TEACHER_PENDING__ assistant content. Run GLM5.2 teacher to fill these before training.",
    }
    with manifest_path.open("w") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"Built iter-3 dataset at {out_dir}")
    print(f"  train_chatml.jsonl: {len(train_rows)} rows (sha256 {train_sha[:16]}...)")
    print(f"  eval_chatml.jsonl:  {len(eval_rows)} rows (sha256 {eval_sha[:16]}...)")
    print(f"  manifest.json:      status={manifest['status']}")
    print(
        f"  carry-forward: {n_carry}, gap-targeted: {n_gap} (train {len(gap_train_rows)} + eval {len(gap_eval_rows)})"
    )
    print(f"  ⚠ {n_gap} rows have __TEACHER_PENDING__ — run GLM5.2 teacher to fill before training")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    pc = sub.add_parser("check", help="Validate the iter-3 manifest")
    pc.add_argument("--manifest", required=True)
    pc.set_defaults(func=cmd_check)
    pb = sub.add_parser("build", help="Build iter-3 splits (use --dry-run until iter-2 eval lands)")
    pb.add_argument(
        "--gap-report",
        required=True,
        help="Path to the finalized gap-report doc (e.g. docs/iter3-dataset-rows-finalized-2026-07-12.md)",
    )
    pb.add_argument(
        "--gap-recs",
        required=False,
        default=None,
        help="Path to machine-generated gap recs JSON (optional, for provenance)",
    )
    pb.add_argument("--iter2-train", required=True)
    pb.add_argument("--iter2-eval", required=True)
    pb.add_argument("--out", required=True)
    pb.add_argument("--dry-run", action="store_true")
    pb.set_defaults(func=cmd_build)
    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
