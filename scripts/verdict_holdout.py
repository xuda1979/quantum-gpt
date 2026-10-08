#!/usr/bin/env python3
"""Compute an unambiguous beats-base verdict + per-task/category drill-down
from a base-vs-adapter holdout eval JSON (run_asi2_base_adapter_rubric_eval
output schema: records[model, task_id, domain, category, passed, scores.overall]).

COMPOSITE BAR (primary, addresses the degenerate pass@1 comparison):
    composite = 0.70 * rubric_overall + 0.30 * (pass_bonus)
where rubric_overall is the mean overall across N tasks and pass_bonus = pass@1
fraction (so a higher rubric AND more passes both move it). beats-base = adapter
composite > base composite. This gives a single, non-degenerate number.

Also emits per-category and per-task drill-down so the next manifest can target
the classes the adapter loses on.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

RUBRIC_WEIGHT = 0.70
PASS_WEIGHT = 0.30


def _mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else 0.0


def load_eval(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _records_by_model(eval_data: dict) -> dict[str, list[dict]]:
    out = {}
    for r in eval_data.get("records", []):
        out.setdefault(r.get("model"), []).append(r)
    return out


def composite(records: list[dict], n_tasks: int) -> float:
    """0.70*mean(rubric overall) + 0.30*pass@1 fraction over n_tasks (unseen counts score 0)."""
    total_pts = sum((r.get("scores") or {}).get("overall", 0.0) for r in records)
    passes = sum(1 for r in records if r.get("passed"))
    len(records)
    # unseen tasks contribute their share of 0 for both rubric and pass
    rub_part = (total_pts / n_tasks) if n_tasks else 0.0
    pass_part = passes / n_tasks if n_tasks else 0.0
    return RUBRIC_WEIGHT * rub_part + PASS_WEIGHT * pass_part


def verdict(eval_data: dict, *, n_tasks: int = 18) -> dict:
    by_model = _records_by_model(eval_data)
    adapter = by_model.get("adapter", [])
    base = by_model.get("base", [])
    comp_a = composite(adapter, n_tasks)
    comp_b = composite(base, n_tasks)
    # primary: composite; also report executable pass + rubric separately
    a_pass = sum(1 for r in adapter if r.get("passed"))
    b_pass = sum(1 for r in base if r.get("passed"))
    a_rub = _mean((r.get("scores") or {}).get("overall", 0.0) for r in adapter)
    b_rub = _mean((r.get("scores") or {}).get("overall", 0.0) for r in base)
    # per-category drill-down (adapter wins/loses vs base on rubric)
    cats = sorted({r.get("category") for r in adapter} | {r.get("category") for r in base} if (adapter or base) else [])
    cat_rows = []
    for c in cats:
        ca = [r for r in adapter if r.get("category") == c]
        cb = [r for r in base if r.get("category") == c]
        ca_p = sum(1 for r in ca if r.get("passed"))
        cb_p = sum(1 for r in cb if r.get("passed"))
        ca_r = _mean((r.get("scores") or {}).get("overall", 0.0) for r in ca)
        cb_r = _mean((r.get("scores") or {}).get("overall", 0.0) for r in cb)
        cat_rows.append({"category": c, "adapter_pass": ca_p, "base_pass": cb_p,
                         "adapter_rubric": round(ca_r, 3), "base_rubric": round(cb_r, 3),
                         "adapter_wins": ca_r > cb_r})
    # per-task drill-down: tasks where adapter misses the pass the base made (loss) or vice versa (gain)
    amap = {r.get("task_id"): r for r in adapter}
    bmap = {r.get("task_id"): r for r in base}
    task_ids = sorted(set(amap) | set(bmap))
    task_rows = []
    for t in task_ids:
        a = amap.get(t)
        b = bmap.get(t)
        a_p = bool(a and a.get("passed"))
        b_p = bool(b and b.get("passed"))
        a_r = (a.get("scores") or {}).get("overall", 0.0) if a else 0.0
        task_rows.append({"task": t, "category": (a or b).get("category"),
                          "adapter_pass": a_p, "base_pass": b_p,
                          "adapter_rubric": round(a_r, 3),
                          "gain": a_p and not b_p, "loss": b_p and not a_p})
    gains = [t for t in task_rows if t["gain"]]
    losses = [t for t in task_rows if t["loss"]]
    return {
        "composite_adapter": round(comp_a, 4),
        "composite_base": round(comp_b, 4),
        "beats_base": comp_a > comp_b,
        "pass_adapter": f"{a_pass}/{n_tasks}",
        "pass_base": f"{b_pass}/{n_tasks}",
        "rubric_adapter": round(a_rub, 3),
        "rubric_base": round(b_rub, 3),
        "gains": [g["task"] for g in gains],
        "losses": [loss["task"] for loss in losses],
        "by_category": cat_rows,
        "by_task_wins": [t["task"] for t in task_rows if t["adapter_pass"]],
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("eval_json")
    ap.add_argument("--n-tasks", type=int, default=18)
    a = ap.parse_args()
    print(json.dumps(verdict(load_eval(Path(a.eval_json)), n_tasks=a.n_tasks), indent=2))
