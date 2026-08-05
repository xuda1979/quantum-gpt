#!/usr/bin/env python3
"""Calibrate the frozen comprehensive judge against executable anchors.

The judge (base model or an older accepted adapter) scores every sample on five
dimensions — correctness, runnability, result_correctness, efficiency, quality.
Executable tests are authoritative, so a dimension may only contribute reward
weight once its scores demonstrably agree with the executable anchors:

    correctness        <-> full test pass (binary)
    runnability        <-> syntax validity + import hygiene (binary)
    result_correctness <-> full verifier clause pass (binary)
    efficiency         <-> measured runtime (continuous; negative correlation
                           expected — faster is better)

Enablement rule: n >= MODEL_JUDGE_CALIBRATION_MIN_N samples AND
AUC >= MODEL_JUDGE_CALIBRATION_AUC (or |Spearman rho| >= RHO for efficiency).
Enabled dimensions share the MAX_MODEL_JUDGE_WEIGHT (0.05) cap uniformly.
The output `judge_calibration.json` is consumed by
`training/grpo_trainer.py --judge-calibration`.

Input JSONL (one record per judged sample):
    {"passed": bool, "syntax_ok": bool, "verifier_rate": float,
     "runtime_ms": float|None, "model_dim_scores": {"correctness": 0.9, ...}}

Usage:
    python3 scripts/calibrate_model_judge.py \
        --records <diagnostics>.jsonl --output <run>/judge_calibration.json
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.grpo_utils import (  # noqa: E402
    MAX_MODEL_JUDGE_WEIGHT,
    MODEL_JUDGE_CALIBRATION_AUC,
    MODEL_JUDGE_CALIBRATION_MIN_N,
    MODEL_JUDGE_CALIBRATION_RHO,
)


def compute_auc(labels: list[bool], scores: list[float]) -> float | None:
    """Area under the ROC curve via the Mann-Whitney U statistic.

    AUC = (sum of positive ranks - n_pos(n_pos+1)/2) / (n_pos * n_neg).
    Returns None when either class is empty.
    """
    if len(labels) != len(scores) or not labels:
        return None
    positives = [(label, score) for label, score in zip(labels, scores, strict=True) if label]
    negatives = [(label, score) for label, score in zip(labels, scores, strict=True) if not label]
    if not positives or not negatives:
        return None
    n_pos, n_neg = len(positives), len(negatives)
    # rank all scores (average ranks for ties)
    ordered = sorted(enumerate(scores), key=lambda pair: pair[1])
    ranks = [0.0] * len(scores)
    index = 0
    while index < len(ordered):
        tie_end = index + 1
        while tie_end < len(ordered) and ordered[tie_end][1] == ordered[index][1]:
            tie_end += 1
        avg_rank = (index + 1 + tie_end) / 2.0
        for pair in ordered[index:tie_end]:
            ranks[pair[0]] = avg_rank
        index = tie_end
    rank_sum_pos = sum(ranks[i] for i, label in enumerate(labels) if label)
    auc = (rank_sum_pos - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg)
    return auc


def compute_spearman_r(xs: list[float], ys: list[float]) -> float | None:
    """Spearman rank correlation; None when fewer than 2 points."""
    if len(xs) != len(ys) or len(xs) < 2:
        return None

    def _ranks(values: list[float]) -> list[float]:
        ordered = sorted(enumerate(values), key=lambda pair: pair[1])
        ranks = [0.0] * len(values)
        index = 0
        while index < len(ordered):
            tie_end = index + 1
            while tie_end < len(ordered) and ordered[tie_end][1] == ordered[index][1]:
                tie_end += 1
            avg_rank = (index + 1 + tie_end) / 2.0
            for pair in ordered[index:tie_end]:
                ranks[pair[0]] = avg_rank
            index = tie_end
        return ranks

    rank_x = _ranks(xs)
    rank_y = _ranks(ys)
    mean_x = statistics.fmean(rank_x)
    mean_y = statistics.fmean(rank_y)
    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(rank_x, rank_y, strict=True))
    var_x = sum((x - mean_x) ** 2 for x in rank_x)
    var_y = sum((y - mean_y) ** 2 for y in rank_y)
    if var_x == 0.0 or var_y == 0.0:
        return None
    return cov / (var_x * var_y) ** 0.5


def decide_enabled_dims(
    *,
    n: int,
    aucs: dict[str, float],
    rho_efficiency: float | None,
    min_n: int = MODEL_JUDGE_CALIBRATION_MIN_N,
) -> dict[str, float]:
    """Per-dimension reward weights; {} until calibration thresholds pass.

    Efficiency is enabled when |rho| >= MODEL_JUDGE_CALIBRATION_RHO with the
    expected sign (negative: faster code scores higher). Quality has no
    executable anchor and is never auto-enabled by this calibration.
    """
    enabled: dict[str, float] = {}
    if n < min_n:
        return enabled
    for dim in ("correctness", "runnability", "result_correctness"):
        auc = aucs.get(dim)
        if auc is not None and auc >= MODEL_JUDGE_CALIBRATION_AUC:
            enabled[dim] = 1.0
    if (
        rho_efficiency is not None
        and abs(rho_efficiency) >= MODEL_JUDGE_CALIBRATION_RHO
        and rho_efficiency < 0.0
    ):
        enabled["efficiency"] = 1.0
    if not enabled:
        return {}
    per_dim = MAX_MODEL_JUDGE_WEIGHT / len(enabled)
    return {dim: per_dim for dim in enabled}


def load_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not path.is_file():
        return records
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--records", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument(
        "--min-n",
        type=int,
        default=MODEL_JUDGE_CALIBRATION_MIN_N,
        help="Minimum judged samples before any dimension can be enabled.",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    records = load_records(args.records)
    if not records:
        print("error: no records", file=sys.stderr)
        return 2

    pairs: dict[str, list[tuple[bool, float]]] = {
        "correctness": [],
        "runnability": [],
        "result_correctness": [],
    }
    efficiency_pairs: list[tuple[float, float]] = []
    for record in records:
        scores = record.get("model_dim_scores") or {}
        passed = bool(record.get("passed"))
        syntax_ok = bool(record.get("syntax_ok"))
        verifier_rate = float(record.get("verifier_rate") or 0.0)
        runtime_ms = record.get("runtime_ms")
        for dim, label in (
            ("correctness", passed),
            ("runnability", syntax_ok),
            ("result_correctness", verifier_rate >= 0.999),
        ):
            score = scores.get(dim)
            if isinstance(score, int | float) and not isinstance(score, bool):
                pairs[dim].append((label, min(1.0, max(0.0, float(score)))))
        if isinstance(runtime_ms, int | float) and runtime_ms > 0:
            eff = scores.get("efficiency")
            if isinstance(eff, int | float) and not isinstance(eff, bool):
                efficiency_pairs.append((float(runtime_ms), min(1.0, max(0.0, float(eff)))))

    aucs: dict[str, float] = {}
    for dim in ("correctness", "runnability", "result_correctness"):
        auc = compute_auc([label for label, _ in pairs[dim]], [score for _, score in pairs[dim]])
        if auc is not None:
            aucs[dim] = auc
    rho_efficiency = (
        compute_spearman_r(
            [runtime for runtime, _ in efficiency_pairs],
            [score for _, score in efficiency_pairs],
        )
        if efficiency_pairs
        else None
    )

    enabled = decide_enabled_dims(
        n=len(records), aucs=aucs, rho_efficiency=rho_efficiency, min_n=args.min_n
    )
    result = {
        "n_samples": len(records),
        "min_n": args.min_n,
        "auc": aucs,
        "spearman_rho_efficiency_vs_runtime": rho_efficiency,
        "enabled_dims": enabled,
        "note": (
            "Reward weights stay zero until per-dimension agreement with "
            "executable anchors passes calibration (AUC >= 0.85, |rho| >= 0.6, "
            "n >= 200). Total model-judge weight is capped at 0.05 and is "
            "subtracted from the shaped term, never from the pass reward."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
