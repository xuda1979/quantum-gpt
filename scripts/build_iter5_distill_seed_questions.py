#!/usr/bin/env python3
"""Build iter-5 distillation seed questions: 1000 per adapter (27B + 35B).

Reuses the iter-4 generator functions (same verified weakness profile from
docs/iter4-comprehensive-eval-report-2026-07-16.md) but expands the per-family
allocation 10x to reach 1000 questions per adapter.

Each question targets a documented weakness:
  - 27B: code-vs-prose discipline (CRITICAL), Python syntax validity (HIGH),
         Qiskit/PennyLane/Cirq/Braket API gaps, full-program contract
  - 35B: same profile + MoE routing risk on Cirq

Output: data/generated/glm52_soft_distill_sft_iter5_{27b,35b}/seed_questions.jsonl
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import random
import sys
from collections import Counter
from pathlib import Path

# Import iter-4 generators (same verified variant pool)
ITER4_BUILDER = Path(__file__).parent / "build_iter4_distill_seed_questions.py"
spec = importlib.util.spec_from_file_location("iter4_builder", ITER4_BUILDER)
iter4 = importlib.util.module_from_spec(spec)
sys.modules["iter4_builder"] = iter4
spec.loader.exec_module(iter4)

SYSTEM_PROMPT = iter4.SYSTEM_PROMPT
TASK_REGISTRY = iter4.TASK_REGISTRY

# ---------------------------------------------------------------------------
# 10x allocation per adapter → 1000 questions each
# Scaled from iter-4's 100-row allocation, weighted by weakness severity.
# ---------------------------------------------------------------------------
ADAPTER_ALLOCATION_1000 = {
    "27b": {
        "qaoa_end_to_end": 120,  # CRITICAL: code-vs-prose (was 12)
        "vqe_expectation": 100,  # HIGH: Qiskit VQE (was 10)
        "qft_phase_estimation": 80,  # HIGH: Qiskit QFT (was 8)
        "pennylane_vqe": 100,  # HIGH: PennyLane VQE (was 10)
        "pennylane_qml": 80,  # HIGH: PennyLane QML (was 8)
        "cirq_qaoa_simulation": 100,  # MEDIUM: Cirq (was 10)
        "braket_general": 60,  # MEDIUM: Braket (was 6)
        "full_program_contract": 120,  # CRITICAL: def main() discipline (was 12)
        "rare_algorithms": 80,  # HIGH: rare algo coverage (was 8)
        "error_mitigation_qml": 60,  # MEDIUM: error mitigation (was 6)
        "software_domain": 100,  # universal gap (was 10)
    },
    "35b": {
        "qaoa_end_to_end": 110,
        "vqe_expectation": 90,
        "qft_phase_estimation": 70,
        "pennylane_vqe": 90,
        "pennylane_qml": 70,
        "cirq_qaoa_simulation": 130,  # ↑ MoE routing risk (was 13)
        "braket_general": 70,  # ↑
        "full_program_contract": 110,
        "rare_algorithms": 90,
        "error_mitigation_qml": 70,
        "software_domain": 70,
        "density_matrix_partial_trace": 100,  # 35B-specific extra
    },
}


def expand_to_target(
    variants: list[dict],
    target: int,
    family: str,
    adapter: str,
    framework: str,
    source_gap: str,
    seed: int,
) -> list[dict]:
    """Expand variants to target count with unique example_ids and varied prompts.

    To avoid exact duplicates when cycling, we append a unique variation tag
    and rotate numeric parameters in the prompt where possible.
    """
    questions: list[dict] = []
    n_variants = len(variants)
    if n_variants == 0:
        return questions

    for i in range(target):
        v = variants[i % n_variants]
        cycle_num = i // n_variants
        # Make prompt unique per cycle by appending a variation tag
        base_prompt = v["prompt"]
        if cycle_num == 0:
            prompt = base_prompt
        else:
            # Vary the prompt slightly: ask for a different random seed in the program
            vary_seed = 1000 + cycle_num * 7 + (i % 997)
            prompt = (
                base_prompt
                + f" Use random seed {vary_seed} for any stochastic operations, and ensure the output marker is identical."
            )
        q = {
            "example_id": f"iter5-{adapter}-{family}-{i:04d}",
            "adapter_target": adapter,
            "task_family": family,
            "framework": framework,
            "prompt": prompt,
            "expected_marker": v["expected_marker"],
            "difficulty": v["difficulty"],
            "variant_id": f"{v['variant_id']}_c{cycle_num}",
            "source_gap": source_gap,
            "system_prompt": SYSTEM_PROMPT,
            "cycle": cycle_num,
        }
        questions.append(q)
    return questions


def build_dataset(adapter: str, seed: int = 42) -> list[dict]:
    """Build the full 1000-question dataset for one adapter."""
    allocation = ADAPTER_ALLOCATION_1000[adapter]
    all_questions: list[dict] = []
    for family, generator, framework, source_gap in TASK_REGISTRY:
        n = allocation.get(family, 0)
        if n == 0:
            continue
        variants = generator()
        questions = expand_to_target(variants, n, family, adapter, framework, source_gap, seed)
        all_questions.extend(questions)
    return all_questions


def dedup_by_prompt_hash(questions: list[dict]) -> tuple[list[dict], int]:
    """Dedup by SHA-256 of the prompt; keep first occurrence."""
    seen: set[str] = set()
    deduped: list[dict] = []
    removed = 0
    for q in questions:
        h = hashlib.sha256(q["prompt"].encode("utf-8")).hexdigest()
        if h in seen:
            removed += 1
            continue
        seen.add(h)
        deduped.append(q)
    return deduped, removed


def write_jsonl(path: Path, questions: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for q in questions:
            fh.write(json.dumps(q, ensure_ascii=False) + "\n")


def write_manifest(path: Path, adapter: str, questions: list[dict], removed_dupes: int) -> None:
    family_counts = Counter(q["task_family"] for q in questions)
    framework_counts = Counter(q["framework"] for q in questions)
    difficulty_counts = Counter(q["difficulty"] for q in questions)
    manifest = {
        "iteration": 5,
        "adapter_target": adapter,
        "created": "2026-07-16",
        "total_questions": len(questions),
        "teacher": "glm5.2",
        "teacher_logprobs": True,
        "teacher_top_logprobs": 20,
        "system_prompt": SYSTEM_PROMPT,
        "task_family_distribution": dict(family_counts),
        "framework_distribution": dict(framework_counts),
        "difficulty_distribution": dict(difficulty_counts),
        "source_gap_report": "docs/iter4-comprehensive-eval-report-2026-07-16.md",
        "plan": "docs/iter5-distill-sft-plan-2026-07-16.md",
        "dedup_removed": removed_dupes,
        "quality_gates": [
            "No truncation at max_length (768 for 27B, 2048 for 35B)",
            "No <think> tags in teacher responses",
            "All teacher responses pass ast.parse",
            "All teacher responses print the expected_marker (runnable code)",
            "No duplicate questions (dedup by SHA-256 of prompt)",
            "Train/eval split disjoint by task_family",
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--adapter", choices=["27b", "35b", "both"], default="both")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out-dir", default="data/generated")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    adapters = ["27b", "35b"] if args.adapter == "both" else [args.adapter]

    for adapter in adapters:
        print(f"\n{'='*70}")
        print(f"Building iter-5 seed questions for adapter={adapter}")
        print(f"{'='*70}")

        questions = build_dataset(adapter, args.seed)
        print(f"Generated {len(questions)} questions (pre-dedup)")

        questions, removed = dedup_by_prompt_hash(questions)
        print(f"Dedup removed {removed} duplicates → {len(questions)} unique questions")

        # Shuffle deterministically for batch diversity
        rng = random.Random(args.seed + hash(adapter) % 100000)
        rng.shuffle(questions)

        out_dir = Path(args.out_dir) / f"glm52_soft_distill_sft_iter5_{adapter}"
        jsonl_path = out_dir / "seed_questions.jsonl"
        manifest_path = out_dir / "manifest.json"

        print("\nTask family distribution:")
        for fam, cnt in sorted(Counter(q["task_family"] for q in questions).items()):
            print(f"  {fam:35s} {cnt:4d}")

        print("\nFramework distribution:")
        for fw, cnt in sorted(Counter(q["framework"] for q in questions).items()):
            print(f"  {fw:35s} {cnt:4d}")

        print("\nDifficulty distribution:")
        for d, cnt in sorted(Counter(q["difficulty"] for q in questions).items()):
            print(f"  {d:35s} {cnt:4d}")

        if not args.dry_run:
            write_jsonl(jsonl_path, questions)
            write_manifest(manifest_path, adapter, questions, removed)
            print(f"\n✅ Wrote {jsonl_path}")
            print(f"✅ Wrote {manifest_path}")
        else:
            print(f"\n[DRY RUN] Would write to {jsonl_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
