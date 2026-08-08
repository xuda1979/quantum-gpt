#!/usr/bin/env python3
"""Inspect eval dataset rows: prompts, message roles, reference fields."""

import json

SRC = "/root/work/quantum-gpt/data/generated/quantum_dedup_1k_glm52_soft_distill_v3/eval_sft_questions_code.jsonl"


def main():
    rows = [json.loads(line) for line in open(SRC, encoding="utf-8")]
    print(f"n_rows: {len(rows)}")
    for i in (0, 1, 2, 3):
        r = rows[i]
        print(f"=== row {i} id={r['example_id']} format={r.get('format')}")
        for m in r["messages"]:
            print(f"  [{m['role']}] {(m.get('content') or '')[:300]}")
        print(f"  metadata: {json.dumps(r.get('metadata'))[:250]}")
        print()
    # any reference/answer fields anywhere?
    keys = set()
    for r in rows:
        keys.update(r.keys())
        keys.update((r.get("metadata") or {}).keys())
    print("all keys:", sorted(keys))


if __name__ == "__main__":
    main()
