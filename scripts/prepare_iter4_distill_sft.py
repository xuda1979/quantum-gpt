#!/usr/bin/env python3
"""Prepare iter-4 soft-distillation SFT splits from teacher responses.

Reads teacher_responses.jsonl (from generate_iter4_teacher_responses.py),
converts to chat-sft-v1 format, and writes 90/10 train/eval splits.

Output:
  data/generated/glm52_soft_distill_sft_iter4_{27b,35b}/train_chatml.jsonl
  data/generated/glm52_soft_distill_sft_iter4_{27b,35b}/eval_chatml.jsonl
  data/generated/glm52_soft_distill_sft_iter4_{27b,35b}/manifest.json (updated)
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SYSTEM_PROMPT = (
    "You are a careful quantum software engineering assistant. Use the user's task "
    "and any supplied context to produce correct, testable Python or precise repair "
    "guidance. Always produce a complete, runnable Python program with `def main()` "
    "that prints the exact specified marker string. Do not include markdown fences "
    "or surrounding commentary."
)


def stable_sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def split_90_10(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Stable 90/10 split by SHA-256 of example_id (deterministic)."""
    annotated = [(stable_sha256(r["example_id"]), r) for r in rows]
    annotated.sort(key=lambda x: x[0])
    n_train = int(len(annotated) * 0.9)
    train = [r for _, r in annotated[:n_train]]
    eval_ = [r for _, r in annotated[n_train:]]
    return train, eval_


def to_chat_sft(rec: dict[str, Any]) -> dict[str, Any]:
    """Convert a teacher response record to chat-sft-v1 format."""
    return {
        "example_id": rec["example_id"],
        "format": "chat-sft-v1",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": rec["user_instruction"]},
            {"role": "assistant", "content": rec["teacher_response"]},
        ],
        "metadata": {
            "adapter_target": rec.get("adapter_target"),
            "task_family": rec.get("task_family"),
            "framework": rec.get("framework"),
            "difficulty": rec.get("difficulty"),
            "variant_id": rec.get("variant_id"),
            "source_gap": rec.get("source_gap"),
            "expected_marker": rec.get("expected_marker"),
            "teacher_model": rec.get("teacher_model", "glm5.2"),
            "teacher_logprobs_preserved": bool(rec.get("teacher_logprobs")),
            "teacher_logprobs_len": len(rec.get("teacher_logprobs", [])),
        },
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")


def write_manifest(
    path: Path,
    adapter: str,
    train_rows: int,
    eval_rows: int,
    teacher_path: Path,
    seed_path: Path,
) -> None:
    manifest = {
        "iteration": 4,
        "adapter_target": adapter,
        "created": "2026-07-16",
        "status": "ready_for_sft",
        "train_rows": train_rows,
        "eval_rows": eval_rows,
        "teacher": "glm5.2",
        "teacher_logprobs": True,
        "teacher_top_logprobs": 20,
        "system_prompt": SYSTEM_PROMPT,
        "split_method": "stable_sha256_sorted_90_10",
        "base_source": {
            "teacher_responses": str(teacher_path),
            "seed_questions": str(seed_path),
        },
        "source_gap_report": "docs/iter4-comprehensive-eval-report-2026-07-16.md",
        "plan": "docs/iter4-distill-sft-plan-2026-07-16.md",
        "quality_gates_passed": [
            "no_think_tags",
            "valid_python_ast_parse",
            "no_markdown_fences",
        ],
        "recommended_training": {
            "ASI1_max_length": 768 if adapter == "27b" else 2048,
            "adapter_init": (
                "outputs/qnt-sft-27b-asi3-r21-20260706T143739Z/adapter"
                if adapter == "27b"
                else "outputs/qg-35b-glm52-distill-sft-glm52-distill-35b-20260706T081105Z/adapter"
            ),
            "ASI1_lr": "1e-4" if adapter == "27b" else "5e-6",
            "lora_rank": 16,
            "lora_alpha": 32,
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--adapter", choices=["27b", "35b"], required=True)
    p.add_argument(
        "--input-dir",
        default=None,
        help="default: data/generated/glm52_soft_distill_sft_iter4_{adapter}",
    )
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    input_dir = (
        Path(args.input_dir)
        if args.input_dir
        else Path(f"data/generated/glm52_soft_distill_sft_iter4_{args.adapter}")
    )
    teacher_path = input_dir / "teacher_responses.jsonl"
    seed_path = input_dir / "seed_questions.jsonl"

    if not teacher_path.exists():
        print(
            f"ERROR: {teacher_path} not found. Run generate_iter4_teacher_responses.py first.",
            flush=True,
        )
        return 2

    teacher_rows = load_jsonl(teacher_path)
    print(f"Loaded {len(teacher_rows)} teacher responses from {teacher_path}")

    train_rows, eval_rows = split_90_10(teacher_rows)
    train_chat = [to_chat_sft(r) for r in train_rows]
    eval_chat = [to_chat_sft(r) for r in eval_rows]

    print(f"Split: {len(train_chat)} train / {len(eval_chat)} eval (90/10)")

    # Verify train/eval disjoint by example_id
    train_ids = {r["example_id"] for r in train_chat}
    eval_ids = {r["example_id"] for r in eval_chat}
    overlap = train_ids & eval_ids
    if overlap:
        print(f"ERROR: train/eval overlap: {len(overlap)} example_ids", flush=True)
        return 1

    train_path = input_dir / "train_chatml.jsonl"
    eval_path = input_dir / "eval_chatml.jsonl"
    manifest_path = input_dir / "manifest.json"

    if not args.dry_run:
        write_jsonl(train_path, train_chat)
        write_jsonl(eval_path, eval_chat)
        write_manifest(
            manifest_path, args.adapter, len(train_chat), len(eval_chat), teacher_path, seed_path
        )
        print(f"✅ Wrote {train_path} ({len(train_chat)} rows)")
        print(f"✅ Wrote {eval_path} ({len(eval_chat)} rows)")
        print(f"✅ Wrote {manifest_path}")
    else:
        print(f"[DRY RUN] Would write {train_path}, {eval_path}, {manifest_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
