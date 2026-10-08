#!/usr/bin/env python3
import json
import os
import random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data", "generated", "quantum_dedup_1k_glm52_soft_distill_v3")
OUT_DIR = DATA_DIR + "_verified_nologit"

with open(os.path.join(DATA_DIR, "verified_pass_ids.json")) as f:
    verified = set(json.load(f))
print("Verified IDs:", len(verified))

all_rows = []
with open(os.path.join(DATA_DIR, "train_chatml.jsonl")) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        all_rows.append(json.loads(line))

verified_rows = [r for r in all_rows if r["example_id"] in verified]
print("Total rows:", len(all_rows), "| Verified:", len(verified_rows))

nologit_rows = []
for r in verified_rows:
    clean = dict(
        example_id=r["example_id"],
        format=r["format"],
        messages=r["messages"],
        metadata=r.get("metadata", dict()),
    )
    nologit_rows.append(clean)

random.seed(42)
random.shuffle(nologit_rows)

train_rows = nologit_rows[:900]
eval_rows = nologit_rows[900:937]
print("Train:", len(train_rows), "| Eval:", len(eval_rows))
assert len(train_rows) == 900
assert len(eval_rows) == 37

os.makedirs(OUT_DIR, exist_ok=True)

for fname, rows in [("train_chatml.jsonl", train_rows), ("eval_chatml.jsonl", eval_rows)]:
    path = os.path.join(OUT_DIR, fname)
    with open(path, "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    print("Wrote", fname, ":", path, "(", len(rows), "rows)")

for fname in ["train_chatml.jsonl", "eval_chatml.jsonl"]:
    path = os.path.join(OUT_DIR, fname)
    with open(path) as f:
        for line in f:
            d = json.loads(line.strip())
            assert "teacher_logits" not in d
            assert len(d["messages"]) == 3
    print(fname, ": clean")

manifest = dict(
    dataset="quantum_dedup_1k_glm52_soft_distill_v3_verified_nologit",
    description="Verified-PASS-only subset. 937 rows, 900 train / 37 eval. No teacher_logits.",
    total_verified=937,
    train_rows=900,
    eval_rows=37,
    shuffle_seed=42,
    format="chat-sft-v1",
    no_teacher_logits=True,
)
with open(os.path.join(OUT_DIR, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=2)
print("DONE")
