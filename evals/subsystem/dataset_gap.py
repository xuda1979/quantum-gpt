#!/usr/bin/env python3
"""Analyze eval failures to recommend dataset additions for the next R&D iteration.

This is the bridge between eval results and dataset curation. It reads one or
more eval JSON outputs and produces a prioritized list of dataset gaps that
should be filled to raise the pass@1 score on the next training run.

Usage:
  # Recommend new dataset rows from a single eval:
  python3 evals/subsystem/dataset_gap.py recommend \\
      --eval outputs/eval-35b-glm52-distill-iter2-pass1-12task.json \\
      --model adapter \\
      --top-k 20

  # Compute per-framework/category coverage gaps:
  python3 evals/subsystem/dataset_gap.py coverage \\
      --eval outputs/eval-35b-glm52-distill-iter2-pass1-12task.json

  # Audit existing training dataset for category balance:
  python3 evals/subsystem/dataset_gap.py audit \\
      --dataset data/generated/glm52_soft_distill_sft_iter2/train_chatml.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Known quantum framework tags we track
QUANTUM_FRAMEWORKS = [
    "qiskit",
    "pennylane",
    "cirq",
    "tket",
    "pytket",
    "tensorcircuit",
    "braket",
    "numpy_quantum",
]

# Categories that are typically underrepresented
HIGH_PRIORITY_CATEGORIES = {
    "algorithm_implementation",
    "debug_repair",
    "api_normalization",
    "circuit_optimization",
    "reasoning",
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _is_v2(data: dict[str, Any]) -> bool:
    return data.get("schema_version", 1) >= 2


def get_records(data: dict[str, Any], model_key: str) -> list[dict[str, Any]]:
    if _is_v2(data):
        return data.get("results", {}).get(model_key, {}).get("records", [])
    # Legacy shape A: top-level `records` list with per-record `model` field.
    recs = data.get("records")
    if isinstance(recs, list):
        return [r for r in recs if r.get("model") == model_key]
    # Legacy shape B (v1 scorecard): top-level `results` list of records,
    # each keyed by `id`, no `model` field (single-model file).
    res = data.get("results")
    if isinstance(res, list):
        return list(res)
    return []


def task_passed(rec: dict[str, Any]) -> bool:
    if "pass_at_1" in rec:
        return float(rec["pass_at_1"]) > 0
    if "n_pass" in rec:
        return int(rec["n_pass"]) > 0
    return bool(rec.get("passed", False))


def _task_id(rec: dict[str, Any]) -> str:
    """Return the task identifier from a record, supporting both
    schema_version=2 (`task_id`) and the v1 scorecard (`id`) fields."""
    return rec.get("task_id") or rec.get("id") or rec.get("name") or ""


def get_failure_category(rec: dict[str, Any]) -> str | None:
    fc = rec.get("failure_category")
    if fc:
        return fc
    if rec.get("samples"):
        return rec["samples"][0].get("failure_category")
    return None


def get_details(rec: dict[str, Any]) -> list[str]:
    d = rec.get("details", [])
    if not d and rec.get("samples"):
        d = rec["samples"][0].get("details", [])
    return d


def infer_framework(rec: dict[str, Any]) -> list[str]:
    """Infer quantum frameworks from task_id, name, and failure details."""
    text = " ".join(
        [
            rec.get("task_id", ""),
            rec.get("name", ""),
            " ".join(get_details(rec)),
        ]
    ).lower()
    found = []
    for fw in QUANTUM_FRAMEWORKS:
        if fw in text or fw.replace("_", " ") in text:
            found.append(fw)
    return found or ["general"]


# ─────────────────────────────────────────────────────────────────────────────
# recommend: what to add to the training dataset
# ─────────────────────────────────────────────────────────────────────────────


def cmd_recommend(args: argparse.Namespace) -> None:
    data = _load(args.eval)
    records = get_records(data, args.model)
    failing = [r for r in records if not task_passed(r)]

    if not failing:
        print(f"All tasks pass for model={args.model}. No gaps to fill.")
        return

    print(f"\n{'='*65}")
    print(f"Dataset gap recommendations — model={args.model}")
    print(f"Eval: {args.eval.name}  |  {len(failing)}/{len(records)} tasks failing")
    print(f"{'='*65}\n")

    # Score each failing task by priority
    rows: list[dict[str, Any]] = []
    for rec in failing:
        task_id = _task_id(rec)
        domain = rec.get("domain", "unknown")
        category = rec.get("category", "unknown")
        fc = get_failure_category(rec)
        fws = infer_framework(rec)
        details = get_details(rec)

        # Priority scoring (higher = more important to fix)
        score = 0
        if domain == "quantum":
            score += 3
        if category in HIGH_PRIORITY_CATEGORIES:
            score += 2
        if fc == "assertion":
            score += 2  # model tried but wrong logic
        if fc == "syntax":
            score -= 1  # syntax = training quality issue
        if fc == "empty_output":
            score -= 2  # model didn't generate
        score += 1  # base score for being a failure

        rows.append(
            {
                "task_id": task_id,
                "domain": domain,
                "category": category,
                "failure_category": fc,
                "inferred_frameworks": fws,
                "priority_score": score,
                "recommendation": _build_recommendation(task_id, domain, category, fc, details),
            }
        )

    rows.sort(key=lambda x: -x["priority_score"])
    if args.top_k:
        rows = rows[: args.top_k]

    for i, row in enumerate(rows, 1):
        print(
            f"[{i}] {row['task_id']}  (score={row['priority_score']}, fail={row['failure_category']})"
        )
        print(f"     domain={row['domain']}  category={row['category']}")
        if row["inferred_frameworks"] != ["general"]:
            print(f"     frameworks: {', '.join(row['inferred_frameworks'])}")
        print(f"     → {row['recommendation']}")
        print()

    # also output as JSON for pipeline consumption
    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps({"recommendations": rows}, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"Saved to: {args.json_out}")


def _build_recommendation(
    task_id: str, domain: str, category: str, fc: str | None, details: list[str]
) -> str:
    detail_str = " ".join(details[:3]).lower()

    if fc == "assertion":
        if "matrix" in detail_str or "numpy" in detail_str:
            return (
                f"Add {3}-{6} matrix-math worked examples for {category} "
                f"(use numpy linalg, scipy.linalg.sqrtm, exact operator form)"
            )
        if "circuit" in detail_str or "gate" in detail_str:
            return (
                f"Add {3}-{5} worked circuit-construction examples for {category} "
                f"(show correct gate sequence and parameter handling)"
            )
        return f"Add 3-5 worked examples demonstrating correct {category} for {task_id}"

    if fc == "syntax":
        return (
            f"Add high-quality {category} examples with complete, syntactically valid Python. "
            "Ensure teacher responses use proper indentation and no truncation."
        )

    if fc == "import_error":
        fw = "the relevant framework"
        for f in QUANTUM_FRAMEWORKS:
            if f in task_id or f in detail_str:
                fw = f
                break
        return f"Add examples that import {fw} correctly; verify all imports work in the eval environment."

    if fc == "timeout":
        return (
            f"Add examples showing efficient {category} implementation (avoid exponential loops)."
        )

    return f"Add 3-5 high-quality {domain}/{category} examples targeting {task_id}."


# ─────────────────────────────────────────────────────────────────────────────
# coverage: per-framework and per-category gap analysis
# ─────────────────────────────────────────────────────────────────────────────


def cmd_coverage(args: argparse.Namespace) -> None:
    data = _load(args.eval)

    print(f"\nCoverage analysis: {args.eval.name}\n")

    for model_key in ("base", "adapter"):
        records = get_records(data, model_key)
        if not records:
            continue
        n = len(records)
        n_pass = sum(1 for r in records if task_passed(r))
        print(f"  {model_key.capitalize()}: {n_pass}/{n} pass ({100*n_pass/n:.1f}%)")

        # by domain
        by_domain: dict[str, list[bool]] = defaultdict(list)
        by_cat: dict[str, list[bool]] = defaultdict(list)
        for r in records:
            by_domain[r.get("domain", "?")].append(task_passed(r))
            by_cat[r.get("category", "?")].append(task_passed(r))

        print("    By domain:")
        for dom in sorted(by_domain):
            v = by_domain[dom]
            p = sum(v)
            print(f"      {dom:15}: {p}/{len(v)} ({100*p/len(v):.0f}%)")

        print("    By category:")
        for cat in sorted(by_cat):
            v = by_cat[cat]
            p = sum(v)
            flag = " ⚠️  gap" if p / len(v) < 0.5 else ""
            print(f"      {cat:30}: {p}/{len(v)} ({100*p/len(v):.0f}%){flag}")
        print()


# ─────────────────────────────────────────────────────────────────────────────
# audit: inspect training dataset for coverage gaps
# ─────────────────────────────────────────────────────────────────────────────


def cmd_audit(args: argparse.Namespace) -> None:
    rows: list[dict] = []
    with open(args.dataset, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    print(f"\nDataset audit: {args.dataset}")
    print(f"  Total rows: {len(rows)}\n")

    fw_counter: Counter[str] = Counter()
    cat_counter: Counter[str] = Counter()
    dom_counter: Counter[str] = Counter()
    len_dist: list[int] = []

    for row in rows:
        messages = row.get("messages") or row.get("conversations") or []
        text = " ".join(m.get("content", "") for m in messages if isinstance(m, dict)).lower()

        for fw in QUANTUM_FRAMEWORKS:
            if fw in text:
                fw_counter[fw] += 1

        # category/domain heuristics from text
        for kw in [
            "algorithm_implementation",
            "debug_repair",
            "api_normalization",
            "circuit_optimization",
            "reasoning",
            "refactor",
            "bugfix",
            "test_writing",
            "data_transforms",
        ]:
            if kw in text:
                cat_counter[kw] += 1

        if "qiskit" in text or "circuit" in text:
            dom_counter["quantum"] += 1
        else:
            dom_counter["software"] += 1

        total_chars = sum(len(m.get("content", "")) for m in messages if isinstance(m, dict))
        len_dist.append(total_chars)

    print("  Framework coverage (estimated):")
    for fw, cnt in sorted(fw_counter.items(), key=lambda x: -x[1]):
        bar = "█" * min(30, cnt)
        print(f"    {fw:20}: {cnt:4d}  {bar}")

    print("\n  Keyword-matched categories:")
    for cat, cnt in sorted(cat_counter.items(), key=lambda x: -x[1]):
        print(f"    {cat:35}: {cnt}")

    print(
        f"\n  Domain split: quantum={dom_counter.get('quantum', 0)}, software={dom_counter.get('software', 0)}"
    )

    if len_dist:
        avg = sum(len_dist) / len(len_dist)
        print(f"\n  Avg example length (chars): {avg:.0f}")
        print(f"  Min/Max: {min(len_dist)} / {max(len_dist)}")

    # Flag underrepresented frameworks
    print("\n  ⚠️  Potentially underrepresented frameworks (< 5 examples):")
    flagged = False
    for fw in QUANTUM_FRAMEWORKS:
        if fw_counter[fw] < 5:
            print(f"    - {fw}: {fw_counter[fw]} rows")
            flagged = True
    if not flagged:
        print("    (none)")


# ─────────────────────────────────────────────────────────────────────────────
# CLI wiring
# ─────────────────────────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        description="Analyze eval failures → dataset gap recommendations"
    )
    sub = root.add_subparsers(dest="cmd", required=True)

    p_rec = sub.add_parser("recommend", help="Recommend new training examples to fix failing tasks")
    p_rec.add_argument("--eval", type=Path, required=True)
    p_rec.add_argument("--model", default="adapter", choices=["base", "adapter"])
    p_rec.add_argument("--top-k", type=int, default=20)
    p_rec.add_argument("--json-out", type=str, default=None, help="Write recs JSON here")

    p_cov = sub.add_parser("coverage", help="Per-framework/category coverage analysis")
    p_cov.add_argument("--eval", type=Path, required=True)

    p_aud = sub.add_parser("audit", help="Inspect training dataset for framework balance")
    p_aud.add_argument("--dataset", type=Path, required=True)

    return root


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    dispatch = {
        "recommend": cmd_recommend,
        "coverage": cmd_coverage,
        "audit": cmd_audit,
    }
    dispatch[args.cmd](args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
