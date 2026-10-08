#!/usr/bin/env python3
"""Re-evaluate the existing 100+100 standalone emissions with robust extraction.

Reads /root/work/quantum-gpt/outputs/eval_standalone_details.json, runs
extract_code_robust + run_code per sample, prints aggregates + writes a
re-eval JSONL for the judge phase.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval_100_reeval import extract_code_robust, run_code  # noqa: E402

SRC = "/root/work/quantum-gpt/outputs/eval_standalone_details.json"
OUT = "/root/work/quantum-gpt/outputs/reeval_emitted.jsonl"
EVAL_FILE = "/root/work/quantum-gpt/data/generated/quantum_dedup_1k_glm52_soft_distill_v3/eval_sft_questions_code.jsonl"


def load_task_map():
    """Map example_id -> first user message (task context for the judge)."""
    m = {}
    with open(EVAL_FILE, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            ex = json.loads(line)
            for msg in ex.get("messages", []):
                if msg.get("role") == "user":
                    m[ex.get("example_id")] = (msg.get("content") or "")[:400]
                    break
    return m


def main():
    task_map = load_task_map()
    details = json.load(open(SRC))
    with open(OUT, "w", encoding="utf-8") as out:
        for tag in ("base", "adapter"):
            rows = details[tag]
            stats = {"n": len(rows), "methods": {}, "exec": {}, "pass": 0, "resp_len": 0}
            for r in rows:
                resp = r.get("code") or ""
                stats["resp_len"] += len(resp)
                code, method = extract_code_robust(resp)
                res = run_code(code)
                stats["methods"][method] = stats["methods"].get(method, 0) + 1
                reason = res.get("reason", res.get("error", "passed"))
                stats["exec"][reason] = stats["exec"].get(reason, 0) + 1
                if res.get("passed"):
                    stats["pass"] += 1
                rec = {
                    "idx": r.get("idx"),
                    "sample_idx": r.get("idx"),
                    "id": r.get("id"),
                    "example_id": r.get("id"),
                    "which": tag,
                    "response": resp,
                    "extracted_code": code,
                    "extract_method": method,
                    "exec": res,
                    "task_context": task_map.get(r.get("id"), "unknown"),
                }
                out.write(json.dumps(rec) + "\n")
            print(
                f"{tag}: n={stats['n']} pass={stats['pass']} methods={stats['methods']} "
                f"exec={stats['exec']} mean_resp_len={stats['resp_len'] // max(1, stats['n'])}"
            )
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
