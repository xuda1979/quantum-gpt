#!/usr/bin/env python3
"""Cross-domain performance-drift report (industrial-standard eval monitoring).

Assembles per-domain evaluation JSONs (each mirroring the
run_asi2_base_adapter_rubric_eval output schema) into a time-series drift
summary: for each domain, adapter/base composite (0.70*rubric_mean +
0.30*pass@1-fraction, reusing verdict_holdout's formula) and drift vs base.
This lets us see how training changes performance across math / coding / physics
(each relevant to quantum-computing coding) as adapters evolve — catching silent
domain regressions even when the frozen 18-task holdout pass@1 is flat.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

RUBRIC_WEIGHT = 0.70
PASS_WEIGHT = 0.30
RESULTS_DIR = Path(__file__).resolve().parent.parent / "evals" / "domain_monitor" / "results"


def composite(records, n_tasks):
    """0.70*mean(rubric) + 0.30*pass fraction over n_tasks (unseen score 0)."""
    total_pts = sum((r.get("scores") or {}).get("overall", 0.0) for r in records)
    passes = sum(1 for r in records if r.get("passed"))
    n = n_tasks or max(len(records), 1)
    rub = total_pts / n
    return round(RUBRIC_WEIGHT * rub + PASS_WEIGHT * (passes / n), 4)


def _by_model(records):
    out = {}
    for r in records:
        out.setdefault(r.get("model"), []).append(r)
    return out


def _domain_summary(eval_data, n_tasks):
    models = _by_model(eval_data.get("records", []))
    a = models.get("adapter", [])
    b = models.get("base", [])
    def _overall(recs):
        return (sum((r.get("scores") or {}).get("overall", 0.0) for r in recs)
                / len(recs)) if recs else 0.0
    return {
        "adapter_composite": composite(a, n_tasks),
        "base_composite": composite(b, n_tasks),
        "adapter_rubric_mean": round(_overall(a), 3),
        "base_rubric_mean": round(_overall(b), 3),
        "drift_vs_base": round(composite(a, n_tasks) - composite(b, n_tasks), 4),
    }


def report_from_results(results: dict, *, n_tasks: int = 18) -> dict:
    """results: {domain_name: eval_json_dict}. Returns {domain: summary}."""
    if not results:
        return {}
    return {dom: _domain_summary(ev, n_tasks) for dom, ev in results.items()}


def _discover_results(base: Path = RESULTS_DIR) -> dict:
    """Scan evals/domain_monitor/results/**/*.json -> {domain: eval_dict}.

    Structure: results/<domain>/<file>.json. Domain = the dir directly under
    results (so multiple adapter/date files per domain = a time series). If a
    json sits in a non-domain subdir, fall back to the file stem so a flat
    single-file layout still keys by filename.
    """
    if isinstance(base, str):
        base = Path(base)
    out = {}
    if not base.exists():
        return out
    for f in sorted(base.rglob("*.json")):
        if f.parent.parent == base:
            dom = f.parent.name  # results/<domain>/<file>.json
        else:
            dom = f.stem
        try:
            out[dom] = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir", type=Path, default=RESULTS_DIR)
    ap.add_argument("--n-tasks", type=int, default=18)
    a = ap.parse_args()
    print(json.dumps(report_from_results(
        _discover_results(a.results_dir), n_tasks=a.n_tasks), indent=2))
