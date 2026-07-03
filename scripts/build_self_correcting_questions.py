#!/usr/bin/env python3
"""Build a unified pool of 8000 unique quantum-coding questions for the
self-correcting distillation pipeline.

Sources (in priority order):
  1. data/seed/quantum_distillation_seed_questions_asi2_v1.jsonl  (11172 rows)
  2. data/seed/quantum_rag_seed_questions.jsonl                   (27 rows)
  3. data/seed/quantum_llm_plan_seed.jsonl                        (8 rows)
  4. evals/tasks/quantum/*                                          (31 tasks)

Each output row has the uniform schema:

    {
      "question_id":   "scq_<sha8>",
      "question":      "<the instruction text the student must answer>",
      "framework":     "qiskit" | "pennylane" | ... | null,
      "category":      "circuit_construction" | ...,
      "difficulty":    "easy" | "medium" | "hard",
      "task_type":     "implementation" | "repair" | "optimization" | ...,
      "language":      "python" | null,
      "source":        "asi2_distill_seed_v1" | "rag_seed_v1" |
                       "plan_seed_v1" | "eval_task_v1",
      "source_id":     <original example_id or task_id>,
      "test_harness":  {"task_dir": "evals/tasks/quantum/<name>"} | null,
      "rag_excerpt":   "<optional grounding text>",
      "expected_signature_hints": ["def bell_pair_state() -> list[complex]", ...]
    }

The pool is deduplicated on the normalized question text and capped at
--target-count (default 8000). A reproducible shuffled order is written so
that downstream pipelines can resume from an index.

Usage:
    python3 scripts/build_self_correcting_questions.py \
        --target-count 8000 \
        --output data/generated/self_correcting_distill/questions_pool.jsonl \
        --manifest data/generated/self_correcting_distill/questions_pool_manifest.json \
        --seed 20260702
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def sha8(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:8]


def normalize_question(text: str) -> str:
    """Normalize for dedup: collapse whitespace, drop leading/trailing spaces."""
    if not isinstance(text, str):
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def from_asi2_distill_seed(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            instruction = rec.get("instruction")
            if not isinstance(instruction, str) or len(instruction.strip()) < 20:
                continue
            rows.append({
                "question": instruction.strip(),
                "framework": rec.get("framework"),
                "category": rec.get("category"),
                "difficulty": rec.get("difficulty") or "medium",
                "task_type": rec.get("task_type") or "implementation",
                "language": rec.get("language") or "python",
                "source": "asi2_distill_seed_v1",
                "source_id": rec.get("example_id"),
                "rag_excerpt": (rec.get("artifacts") or {}).get("rag_excerpt"),
            })
    return rows


def from_chatml_seed(path: Path, source_tag: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            messages = rec.get("messages") or []
            user_msg = None
            for m in messages:
                if m.get("role") == "user":
                    user_msg = m.get("content")
                    break
            if not isinstance(user_msg, str) or len(user_msg.strip()) < 20:
                continue
            meta = rec.get("metadata") or {}
            rows.append({
                "question": user_msg.strip(),
                "framework": meta.get("framework") or meta.get("target_framework"),
                "category": meta.get("category"),
                "difficulty": meta.get("difficulty") or "medium",
                "task_type": meta.get("task_type") or "implementation",
                "language": meta.get("language") or "python",
                "source": source_tag,
                "source_id": rec.get("example_id"),
                "rag_excerpt": None,
            })
    return rows


def from_eval_tasks(task_root: Path) -> list[dict[str, Any]]:
    """Convert each evals/tasks/quantum/<task> into a question.

    The question includes the task id/name/category plus the reference
    candidate interface and the tests source so the student has enough
    information to produce a candidate. The test harness is preserved as
    `test_harness.task_dir` so the pipeline can re-run tests against the
    student's code.
    """
    rows: list[dict[str, Any]] = []
    if not task_root.exists():
        return rows
    for task_dir in sorted(p for p in task_root.iterdir() if p.is_dir()):
        meta_path = task_dir / "task.json"
        if not meta_path.exists():
            continue
        meta = json.loads(meta_path.read_text())
        candidate_file = meta.get("candidate_file", "candidate.py")
        test_file = meta.get("test_file", "tests.py")
        candidate_path = task_dir / candidate_file
        test_path = task_dir / test_file
        if not candidate_path.exists() or not test_path.exists():
            continue
        candidate_src = candidate_path.read_text(encoding="utf-8")
        test_src = test_path.read_text(encoding="utf-8")
        signature_hints = _extract_signatures(candidate_src)
        question = (
            f"Task ID: {meta.get('id', task_dir.name)}\n"
            f"Task name: {meta.get('name', task_dir.name)}\n"
            f"Domain: {meta.get('domain', 'quantum')}\n"
            f"Category: {meta.get('category', 'circuit_construction')}\n\n"
            f"Implement the candidate module so that the test suite below passes.\n\n"
            f"Reference candidate interface (do NOT copy verbatim — provide a correct implementation):\n"
            f"```python\n{candidate_src.strip()}\n```\n\n"
            f"Test suite (your implementation must satisfy these tests):\n"
            f"```python\n{test_src.strip()}\n```\n\n"
            f"Return only the implementation as a single Python code block."
        )
        rows.append({
            "question": question,
            "framework": _infer_framework_from_source(candidate_src + "\n" + test_src),
            "category": meta.get("category", "circuit_construction"),
            "difficulty": "medium",
            "task_type": "implementation",
            "language": "python",
            "source": "eval_task_v1",
            "source_id": meta.get("id", task_dir.name),
            "test_harness": {"task_dir": str(task_dir.relative_to(ROOT))},
            "expected_signature_hints": signature_hints,
            "rag_excerpt": None,
        })
    return rows


def _extract_signatures(source: str) -> list[str]:
    import ast
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    hints: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            args = [a.arg for a in node.args.args]
            sig = f"def {node.name}({', '.join(args)})"
            if node.returns is not None:
                sig += f" -> {ast.unparse(node.returns)}"
            hints.append(sig)
    return hints


def _infer_framework_from_source(source: str) -> str | None:
    tokens = [
        ("qiskit", "qiskit"),
        ("pennylane", "pennylane"),
        ("cirq", "cirq"),
        ("braket", "braket"),
        ("pyquil", "pyquil"),
        ("qsharp", "qsharp"),
        ("isq", "isq"),
        ("cudaq", "cudaq"),
        ("cuda-quantum", "cudaq"),
        ("mitiq", "mitiq"),
        ("pyzx", "pyzx"),
        ("qutip", "qutip"),
    ]
    lowered = source.lower()
    for needle, framework in tokens:
        if re.search(rf"\b{re.escape(needle)}\b", lowered):
            return framework
    return None


def dedup_and_cap(rows: list[dict[str, Any]], target_count: int, seed: int) -> list[dict[str, Any]]:
    seen: dict[str, dict[str, Any]] = {}
    for row in rows:
        norm = normalize_question(row["question"])
        if not norm:
            continue
        key = sha8(norm)
        if key in seen:
            # Prefer rows that carry a test harness.
            if row.get("test_harness") and not seen[key].get("test_harness"):
                seen[key] = row
            continue
        seen[key] = row
    unique = list(seen.values())
    rng = random.Random(seed)
    rng.shuffle(unique)
    return unique[:target_count]


def write_manifest(
    manifest_path: Path,
    output_path: Path,
    rows: list[dict[str, Any]],
    target_count: int,
    seed: int,
    sources_summary: dict[str, int],
) -> None:
    manifest = {
        "schema": "self-correcting-questions-pool-v1",
        "target_count": target_count,
        "actual_count": len(rows),
        "seed": seed,
        "output_file": str(output_path.relative_to(ROOT)),
        "sources_summary": sources_summary,
        "framework_counts": dict(Counter(r.get("framework") or "unknown" for r in rows)),
        "category_counts": dict(Counter(r.get("category") or "unknown" for r in rows)),
        "difficulty_counts": dict(Counter(r.get("difficulty") or "unknown" for r in rows)),
        "task_type_counts": dict(Counter(r.get("task_type") or "unknown" for r in rows)),
        "with_test_harness": sum(1 for r in rows if r.get("test_harness")),
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-count", type=int, default=8000)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "data/generated/self_correcting_distill/questions_pool.jsonl",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "data/generated/self_correcting_distill/questions_pool_manifest.json",
    )
    parser.add_argument("--seed", type=int, default=20260702)
    args = parser.parse_args()

    sources: list[tuple[str, Path, Any]] = [
        ("asi2_distill_seed_v1", ROOT / "data/seed/quantum_distillation_seed_questions_asi2_v1.jsonl", from_asi2_distill_seed),
        ("rag_seed_v1", ROOT / "data/seed/quantum_rag_seed_questions.jsonl", lambda p: from_chatml_seed(p, "rag_seed_v1")),
        ("plan_seed_v1", ROOT / "data/seed/quantum_llm_plan_seed.jsonl", lambda p: from_chatml_seed(p, "plan_seed_v1")),
        ("eval_task_v1", ROOT / "evals/tasks/quantum", from_eval_tasks),
    ]

    all_rows: list[dict[str, Any]] = []
    sources_summary: dict[str, int] = {}
    for tag, path, loader in sources:
        if not path.exists():
            print(f"[skip] source {tag} missing: {path}")
            sources_summary[tag] = 0
            continue
        try:
            rows = loader(path)
        except Exception as exc:
            print(f"[error] source {tag} failed: {exc}")
            sources_summary[tag] = 0
            continue
        sources_summary[tag] = len(rows)
        print(f"[load] {tag}: {len(rows)} raw rows from {path}")
        all_rows.extend(rows)

    print(f"[pool] total raw rows: {len(all_rows)}")
    final = dedup_and_cap(all_rows, args.target_count, args.seed)
    print(f"[pool] unique after dedup: {len(final)} (capped at {args.target_count})")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as out:
        for row in final:
            row["question_id"] = "scq_" + sha8(row["question"] + "|" + (row.get("source_id") or ""))
            out.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    write_manifest(args.manifest, args.output, final, args.target_count, args.seed, sources_summary)

    print(f"[done] wrote {len(final)} rows to {args.output}")
    print(f"[done] manifest at {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
