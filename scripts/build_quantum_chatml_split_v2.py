#!/usr/bin/env python3
"""Rebuild train/test ChatML split from the updated quantum_finetune_10k.jsonl.

- Test set: 500 samples, stratified by `family` (proportional allocation).
- Train set: remaining 10000 samples.
- Deterministic via fixed seed; no overlap by example id.
"""

import argparse
import collections
import hashlib
import json
import random
from pathlib import Path

SYSTEM_PROMPT = (
    "You are a careful quantum software engineering assistant. "
    "Use the user's task and any supplied context to produce correct, "
    "testable Python or precise repair guidance."
)


def to_chatml(row: dict) -> dict:
    return {
        "format": "chat-sft-v1",
        "source_schema": "instruction_output_jsonl",
        "example_id": row["id"],
        "meta": {
            "family": row.get("family"),
            "framework": row.get("framework"),
            "difficulty": row.get("difficulty"),
            "domain": row.get("domain"),
            "language": row.get("language"),
        },
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": row["instruction"]},
            {"role": "assistant", "content": row["output"]},
        ],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--source", default="/Users/daxu/quantum_dataset/gen/quantum_finetune_10k.jsonl"
    )
    ap.add_argument(
        "--out-dir",
        default="/Users/daxu/software/quantum-gpt/data/generated/qwen36_quantum_finetune_10k_split_10000_500_v2",
    )
    ap.add_argument("--test-size", type=int, default=500)
    ap.add_argument("--seed", type=int, default=20260612)
    args = ap.parse_args()

    rows = []
    seen = set()
    with open(args.source, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if row["id"] in seen:
                raise SystemExit(f"duplicate id: {row['id']}")
            seen.add(row["id"])
            if not row.get("instruction") or not row.get("output"):
                raise SystemExit(f"empty instruction/output at id: {row['id']}")
            rows.append(row)

    total = len(rows)
    rng = random.Random(args.seed)

    # Stratified test sampling by family (proportional, largest-remainder).
    by_family = collections.defaultdict(list)
    for row in rows:
        by_family[row.get("family", "unknown")].append(row)
    quotas = {}
    fractional = []
    assigned = 0
    for fam, items in sorted(by_family.items()):
        exact = args.test_size * len(items) / total
        base = int(exact)
        quotas[fam] = base
        assigned += base
        fractional.append((exact - base, fam))
    fractional.sort(reverse=True)
    for _, fam in fractional[: args.test_size - assigned]:
        quotas[fam] += 1

    test_ids = set()
    for fam, items in sorted(by_family.items()):
        items_sorted = sorted(items, key=lambda r: r["id"])
        rng.shuffle(items_sorted)
        for row in items_sorted[: quotas[fam]]:
            test_ids.add(row["id"])
    assert len(test_ids) == args.test_size

    train_rows = [r for r in rows if r["id"] not in test_ids]
    test_rows = [r for r in rows if r["id"] in test_ids]
    rng.shuffle(train_rows)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    train_file = out_dir / "train_chatml.jsonl"
    test_file = out_dir / "test_chatml.jsonl"

    h = hashlib.sha256()
    for path, subset in ((train_file, train_rows), (test_file, test_rows)):
        with open(path, "w", encoding="utf-8") as f:
            for row in subset:
                line = json.dumps(to_chatml(row), ensure_ascii=False)
                f.write(line + "\n")
                h.update(line.encode("utf-8"))

    fam_test = collections.Counter(r.get("family") for r in test_rows)
    fw_test = collections.Counter(r.get("framework") for r in test_rows)
    manifest = {
        "ok": True,
        "source": args.source,
        "output_dir": str(out_dir),
        "seed": args.seed,
        "total_rows": total,
        "train_rows": len(train_rows),
        "test_rows": len(test_rows),
        "train_file": str(train_file),
        "test_file": str(test_file),
        "split_policy": "stratified_by_family_fixed_seed",
        "sha256_train_plus_test": h.hexdigest(),
        "no_overlap_by_example_id": not (test_ids & {r["id"] for r in train_rows}),
        "test_family_coverage": f"{len(fam_test)}/{len(by_family)}",
        "test_framework_counts": dict(sorted(fw_test.items())),
    }
    with open(out_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
