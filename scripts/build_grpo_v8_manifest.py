#!/usr/bin/env python3
"""build_grpo_v8_manifest.py — regenerate the SAPO holdout-adjacent training
manifest (quantum_grpo_training_v8_holdout_adjacent.txt).

v8 = v7 (quantum_grpo_training_v7_targeted_integrity.txt, untouched) plus the
10 holdout-adjacent curriculum tasks. The header follows the v7 conventions:
  # source=<v7 path> sha256=<sha256 of the v7 file bytes>
  # task_contract_sha256=<hash of sorted task.json + tests.py bytes>
  # targeted=<n> deterministic=0 semantic=0
  # required_import_roots=
  # reference_execution_verified=true runs=3

Deterministic: running it reproduces the checked-in manifest byte-for-byte
(locked by tests/test_sapo_curriculum_holdout_adjacent.py).

Usage:
  python3 scripts/build_grpo_v8_manifest.py [--output PATH] [--check]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

V7_MANIFEST = ROOT / "evals/benchmarks/quantum_grpo_training_v7_targeted_integrity.txt"
OUTPUT = ROOT / "evals/benchmarks/quantum_grpo_training_v8_holdout_adjacent.txt"

# The 10 holdout-adjacent tasks added by the 2026-08-24 curriculum workstream.
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


def manifest_ids(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def task_contract_hash(task_ids: list[str]) -> str:
    """Hash every task's task.json + tests.py bytes (v7 convention)."""
    task_dirs: dict[str, Path] = {}
    for task_json in (ROOT / "evals/tasks").glob("*/*/task.json"):
        meta = json.loads(task_json.read_text(encoding="utf-8"))
        task_dirs[str(meta.get("id", task_json.parent.name))] = task_json.parent
    digest = hashlib.sha256()
    for task_id in sorted(task_ids):
        task_dir = task_dirs.get(task_id)
        if task_dir is None:
            raise SystemExit(f"unable to hash missing task contract: {task_id}")
        for name in ("task.json", "tests.py"):
            path = task_dir / name
            if not path.is_file():
                raise SystemExit(f"unable to hash missing task artifact: {path}")
            digest.update(task_id.encode())
            digest.update(b"\0")
            digest.update(name.encode())
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")
    return digest.hexdigest()


def render(v7_ids: list[str]) -> str:
    ids = v7_ids + NEW_TASK_IDS
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate task id in v8 manifest")
    source_hash = hashlib.sha256(V7_MANIFEST.read_bytes()).hexdigest()
    contract_hash = task_contract_hash(ids)
    lines = [
        "# SAPO holdout-adjacent training: v7 targeted10 + 10 holdout-adjacent tasks.",
        f"# source={V7_MANIFEST.relative_to(ROOT)} sha256={source_hash}",
        f"# task_contract_sha256={contract_hash}",
        "# targeted=20 deterministic=0 semantic=0",
        "# required_import_roots=",
        "# reference_execution_verified=true runs=3",
        "# The 10 added tasks exercise the same competence classes as the 10",
        "# frozen-holdout failures (partial trace, Shor code, Trotter, 2-qubit",
        "# depolarizing, VQE, QAOA landscape, Bell basis, QFT, stabilizers, QML)",
        "# on disjoint instances and contracts. Reference candidates validated",
        "# locally; near-miss candidates get graded numeric details (shaped>0).",
        "# Frozen holdout sapo_promotion_holdout_v1_18.txt is read-only.",
        *ids,
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero if the output differs from the checked-in file",
    )
    args = parser.parse_args()

    v7_ids = manifest_ids(V7_MANIFEST)
    text = render(v7_ids)
    if args.check:
        if not args.output.is_file():
            raise SystemExit(f"missing manifest: {args.output}")
        if args.output.read_text(encoding="utf-8") != text:
            raise SystemExit(f"manifest drift: {args.output} is stale (re-run builder)")
        print(f"OK {args.output}")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8")
    print(f"wrote {args.output} ({len(manifest_ids(args.output))} tasks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
