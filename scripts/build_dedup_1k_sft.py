#!/usr/bin/env python3
"""Build a deduplicated ~1k SFT subset from the verified 10k quantum train split.

The verified train split (10000 rows) has no exact duplicates, but ~6811 rows
are *parameter variants* of each other: identical task/code except for numeric
constants (e.g. gamma=0.355 vs gamma=0.41). Collapsing numbers to a placeholder
reveals only ~3189 distinct task structures.

This script:
  1. Groups train rows by a number-collapsed normalized signature of
     (prompt + code), keeping ONE representative per group (the longest/most
     complete assistant code). This removes the parameter-variant redundancy.
  2. Drops any train group whose signature also appears in the eval split, so
     the held-out 495 eval cannot leak into training.
  3. Stratifies the survivors down to the target (~1000) proportionally by
     framework so diversity is preserved.

Deterministic (seeded). Source files are untouched. Outputs to a new dir +
manifest with full distribution accounting.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

DEFAULT_TRAIN = Path("data/generated/quantum_finetune_verified_chat_sft/train_chatml.jsonl")
DEFAULT_EVAL = Path("data/generated/quantum_finetune_verified_chat_sft/eval_chatml.jsonl")
DEFAULT_OUTPUT_DIR = Path("data/generated/quantum_finetune_verified_chat_sft_dedup_1k")

_NUM_RE = re.compile(r"-?\d+\.?\d*(?:[eE][-+]?\d+)?")
_PUNCT_RE = re.compile(r"[^\w\s]")
_WS_RE = re.compile(r"\s+")


def _texts(row):
    u = a = ""
    for m in row.get("messages", []):
        if m.get("role") == "user" and not u:
            u = m.get("content", "")
        if m.get("role") == "assistant" and not a:
            a = m.get("content", "")
    return u, a


def signature(row):
    """Number-collapsed, case/whitespace/punct-normalized (prompt+code) hash.

    Two rows share a signature iff they are the same task/code up to numeric
    parameter values -> this is exactly the parameter-variant redundancy.
    """
    u, a = _texts(row)
    t = (u + " || " + a).lower()
    t = _NUM_RE.sub(" <num> ", t)
    t = _PUNCT_RE.sub(" ", t)
    t = _WS_RE.sub(" ", t).strip()
    return hashlib.blake2b(t.encode(), digest_size=16).hexdigest()


def load_jsonl(path):
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--train-file", type=Path, default=DEFAULT_TRAIN)
    ap.add_argument("--eval-file", type=Path, default=DEFAULT_EVAL)
    ap.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    ap.add_argument("--target-rows", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=20260622)
    args = ap.parse_args()

    rng = random.Random(args.seed)
    train = load_jsonl(args.train_file)
    eval_rows = load_jsonl(args.eval_file)
    print(f"loaded train={len(train)} eval={len(eval_rows)}", flush=True)

    eval_sigs = {signature(r) for r in eval_rows}

    # 1) group train by signature; keep longest-code representative per group.
    groups = defaultdict(list)
    for idx, row in enumerate(train):
        groups[signature(row)].append(idx)

    leaked_groups = 0
    reps = []
    for sig, members in groups.items():
        if sig in eval_sigs:
            leaked_groups += 1
            continue  # anti-leak: this task structure exists in eval
        best = max(members, key=lambda i: len(_texts(train[i])[1]))
        reps.append(best)

    print(
        f"distinct task-structures={len(groups)} "
        f"dropped_eval_overlap_groups={leaked_groups} "
        f"selectable_reps={len(reps)}",
        flush=True,
    )

    # 2) stratify reps down to target by framework (proportional + round-robin).
    by_fw = defaultdict(list)
    for i in reps:
        by_fw[train[i].get("metadata", {}).get("framework", "unknown")].append(i)
    for fw in by_fw:
        rng.shuffle(by_fw[fw])

    target = min(args.target_rows, len(reps))
    total = len(reps)
    quota = {fw: max(1, round(target * len(ix) / total)) for fw, ix in by_fw.items()}
    selected = []
    for fw, ids in by_fw.items():
        selected.extend(ids[: quota[fw]])
    if len(selected) > target:
        rng.shuffle(selected)
        selected = selected[:target]
    elif len(selected) < target:
        sel = set(selected)
        pool = [i for i in reps if i not in sel]
        rng.shuffle(pool)
        selected.extend(pool[: target - len(selected)])

    selected_rows = [train[i] for i in selected]
    rng.shuffle(selected_rows)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "train_chatml.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in selected_rows)
    )
    (args.output_dir / "eval_chatml.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in eval_rows)
    )

    sel_ids = {r["example_id"] for r in selected_rows}
    eval_ids = {r["example_id"] for r in eval_rows}
    sel_sigs = {signature(r) for r in selected_rows}
    manifest = {
        "source_train": str(args.train_file),
        "source_eval": str(args.eval_file),
        "method": "number_collapsed_signature_dedup_stratified",
        "seed": args.seed,
        "train_in": len(train),
        "distinct_task_structures": len(groups),
        "dropped_eval_overlap_groups": leaked_groups,
        "selectable_reps": len(reps),
        "train_out": len(selected_rows),
        "eval_out": len(eval_rows),
        "id_overlap_train_eval": len(sel_ids & eval_ids),
        "signature_overlap_train_eval": len(sel_sigs & eval_sigs),
        "framework_distribution": dict(
            sorted(Counter(r.get("metadata", {}).get("framework", "unknown") for r in selected_rows).items())
        ),
        "family_count": len({r.get("metadata", {}).get("family", "?") for r in selected_rows}),
    }
    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(json.dumps(manifest, indent=2), flush=True)
    assert manifest["id_overlap_train_eval"] == 0, "LEAK: train/eval example_id overlap!"
    assert manifest["signature_overlap_train_eval"] == 0, "LEAK: train/eval signature overlap!"
    print(f"\nOK wrote {len(selected_rows)} train + {len(eval_rows)} eval rows to {args.output_dir}")


if __name__ == "__main__":
    main()
