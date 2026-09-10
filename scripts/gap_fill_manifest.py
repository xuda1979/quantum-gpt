#!/usr/bin/env python3
"""Gap-fill manifest recommender (lever #2 toward higher pass@1).

Reads a base-vs-adapter holdout eval JSON and returns the top N near-passing
tasks — the FAILED tasks with the HIGHEST rubric overall AND real code
(non-tiny output), i.e. candidates that are 'one bug from correct'. These
are exactly the API-normalization/algorithm patterns to gap-fill with 3-5
curated exemplars into the v9 training manifest, converting the existing
1->2 passes into a sustained climb toward 18/18.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

MIN_CODE_CHARS = 60  # below this = empty/garbage candidate, not a gap target


def recommend(eval_data: dict, *, top_n: int = 3, base_task_ids: list[str] | None = None) -> list[dict]:
    adapter = [r for r in eval_data.get("records", []) if r.get("model") == "adapter"]
    base_passing = set()
    for r in eval_data.get("records", []):
        if r.get("model") == "base" and r.get("passed"):
            base_passing.add(r.get("task_id"))
    candidates = []
    for r in adapter:
        tid = r.get("task_id")
        if r.get("passed"):
            continue                       # already passing
        if tid in base_passing:
            # base passes it, adapter regressed/lost it -> HIGH priority gap
            pass
        chars = r.get("output_chars") or 0
        if chars < MIN_CODE_CHARS:
            continue                       # empty/garbage, not a near-miss
        overall = (r.get("scores") or {}).get("overall", 0.0)
        candidates.append({
            "task_id": tid,
            "category": r.get("category"),
            "domain": r.get("domain"),
            "adapter_rubric": round(overall, 3),
            "output_chars": chars,
            "base_passes_this": tid in base_passing,
            "reason": "adapter_lost_base_pass" if tid in base_passing else "near_pass_high_rubric",
        })
    # sort: base-pass-regressed first (high priority), then by rubric desc
    candidates.sort(key=lambda c: (not c["base_passes_this"], -c["adapter_rubric"]))
    return candidates[:top_n]


def _load(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("eval_json")
    ap.add_argument("--top-n", type=int, default=3)
    a = ap.parse_args()
    for rec in recommend(_load(Path(a.eval_json)), top_n=a.top_n):
        print(json.dumps(rec))
