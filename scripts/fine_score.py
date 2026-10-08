#!/usr/bin/env python3
"""Fine-grained continuous scorer for the SAPO 18-task holdout.

The binary pass/fail holdout cannot separate tied arms (base 8/18, warm 6/18,
run-1 s2/s7 8/18 with identical pass sets, run-2 s4 8/18). This instrument
grades every task continuously in [0, 1] by REUSING the shaped-reward progress
math from ``training/grpo_utils.py`` (single source of truth):

    fine_grade = 1.0                     if the candidate passed
                 0.5 + 0.5 * progress    numeric near-miss band [0.5, 0.9)
                                         (progress from _detail_progress,
                                         capped at 0.9 exactly like the
                                         training reward, so a near miss
                                         never ties a pass)
                 0.0                     crash / syntax / import failure /
                                         None-stub / no numeric evidence
                                         (exactly what shaped assigns)

Per task: best candidate's grade (``mode="best"``, the primary ranking) or the
mean over candidates (``mode="mean"`` — both are computed and the difference is
reported; with pass@1 deterministic eval each task has a single candidate and
the two coincide).

Second axis — numeric ERROR DISTANCE for the assertion-class tasks:
|actual - expected| normalized by |expected| (or by the printed ``tol=`` when
present), extracted from the same harness detail strings (arrow form
``-> v, expected T``, comparator form ``v < T`` / ``v > T`` / ``v != T``,
threshold form ``key=v need>=T`` / ``need<=T``).  ``None`` means no numeric
actual exists (None-stub, crash, pure-text assertion).

CLI (also the ready-command for run-3's upcoming holdout leg):

    python3 scripts/fine_score.py <run-dir> [<run-dir> ...] [--mode best|mean]

Reads ``scorecard.json`` (schema eval-scorecard-v2) from each run dir and
prints the per-task fine grades, per-task error distances, arm means, and a
per-task delta table relative to the first run dir.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

# Running as ``python3 scripts/fine_score.py`` puts scripts/ on sys.path[0];
# make the repo root importable so ``training.grpo_utils`` resolves whether
# invoked as a script or imported as a module.
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from training.compat import strict_zip
from training.grpo_utils import (
    _DETAIL_ARROW_RE,
    _DETAIL_CMP_RE,
    _DETAIL_KV_RE,
    _DETAIL_NEED_RE,
    _DETAIL_SKIP_KEYS,
    _DETAIL_WS_RE,
    shaped_reward_from_details,
)

# ---------------------------------------------------------------------------
# Continuous grade per candidate (reuses the shaped-reward progress math)
# ---------------------------------------------------------------------------


def fine_grade(passed: bool, details: Sequence[str]) -> float:
    """Continuous per-candidate grade in [0, 1].

    pass -> 1.0; numeric near-miss -> 0.5 + 0.5 * progress (capped at 0.9, so
    a failing candidate can never tie a passing one); crash / syntax / import
    / None-stub / no-numeric-evidence -> exactly what the shaped reward
    assigns (0.0).  Binary pass/fail is the special case at threshold 1.0.
    """
    return shaped_reward_from_details(bool(passed), list(details))


def task_grade(results: Sequence[dict[str, Any]], mode: str = "best") -> float:
    """Per-task grade from the task's candidate results.

    ``mode="best"`` -> the best candidate's grade (the primary ranking used in
    the promotion loop); ``mode="mean"`` -> the mean over candidates.  An
    empty candidate list grades 0.0.
    """
    grades = [
        fine_grade(bool(result.get("passed")), result.get("details") or []) for result in results
    ]
    if not grades:
        return 0.0
    if mode == "best":
        return max(grades)
    if mode == "mean":
        return sum(grades) / len(grades)
    raise ValueError(f"unknown aggregation mode: {mode!r} (want 'best' or 'mean')")


def _group_by_task(
    results: Sequence[dict[str, Any]],
) -> tuple[list[str], dict[str, list[dict[str, Any]]]]:
    """Group scorecard results by task id, preserving first-seen order."""
    by_task: dict[str, list[dict[str, Any]]] = {}
    order: list[str] = []
    for result in results:
        task_id = str(result.get("id"))
        if task_id not in by_task:
            by_task[task_id] = []
            order.append(task_id)
        by_task[task_id].append(result)
    return order, by_task


def arm_fine_scores(results: Sequence[dict[str, Any]], mode: str = "best") -> list[float]:
    """Per-task fine grades for a whole arm, in task order."""
    order, by_task = _group_by_task(results)
    return [task_grade(by_task[task_id], mode=mode) for task_id in order]


def arm_mean_fine_score(results: Sequence[dict[str, Any]], mode: str = "best") -> float:
    """Overall arm score: mean over the tasks of the per-task grade."""
    scores = arm_fine_scores(results, mode=mode)
    if not scores:
        return 0.0
    return sum(scores) / len(scores)


# ---------------------------------------------------------------------------
# Second axis: relative numeric error distance for assertion-class failures
# ---------------------------------------------------------------------------

_TARGET_KEYS = {"exact", "true", "theory", "expected", "ideal", "analytic", "threshold", "vs"}


def _kv_pairs(line: str) -> list[tuple[str, float]]:
    """key=value pairs on one detail line (deduped like _detail_progress)."""
    pairs: list[tuple[str, float]] = []
    for match in _DETAIL_KV_RE.finditer(line):
        key = match.group(1)
        if key.endswith("<") or key.endswith("!") or (key.endswith(">") and "<" not in key):
            continue
        pairs.append((key, float(match.group(2))))
    for match in _DETAIL_WS_RE.finditer(line):
        pairs.append((match.group(1), float(match.group(2))))
    return list(dict.fromkeys(pairs))


def _line_error_distance(line: str) -> float | None:
    """Relative |actual - expected| / norm for ONE detail line, best pair.

    norm = printed ``tol=`` value when present, else |expected| (a zero
    denominator makes the pair unmeasurable).  Returns None when the line
    carries no numeric actual (None-stub / pure-text / traceback).
    """
    pairs = _kv_pairs(line)
    targets: list[float] = []
    tolerance: float | None = None
    for key, value in pairs:
        key_lower = key.lower()
        if key_lower == "tol":
            tolerance = value
        elif key_lower in _TARGET_KEYS:
            targets.append(value)
    target = max(targets) if targets else None

    # (actual, expected, direction) triples; direction in {higher, lower, equal}
    triples: list[tuple[float, float, str]] = []

    # arrow form: "-> v, expected T" — the observed value after the arrow is
    # the actual; scored only when the line states a pass target/threshold
    if target is not None or tolerance is not None:
        for match in _DETAIL_ARROW_RE.finditer(line):
            triples.append((float(match.group(1)), target, "equal"))

    # comparator form: "v < T" -> pass wanted v >= T (higher better);
    # "v > T" -> lower better; "v != T" -> equality miss
    for match in _DETAIL_CMP_RE.finditer(line):
        value, op, threshold = float(match.group(1)), match.group(2), float(match.group(3))
        if op in ("<", "<="):
            triples.append((value, threshold, "higher"))
        elif op in (">", ">="):
            triples.append((value, threshold, "lower"))
        else:  # "!="
            triples.append((value, threshold, "equal"))

    # threshold form: "key=v need>=T" / "need<=T" with KV actuals on the line
    directions: list[str] = []
    for match in _DETAIL_NEED_RE.finditer(line):
        directions.append("higher" if match.group(1).startswith(">") else "lower")
    if directions:
        thresholds = [float(match.group(2)) for match in _DETAIL_NEED_RE.finditer(line)]
        actuals: list[float] = []
        p_by_name: dict[str, float] = {}
        for key, value in pairs:
            key_lower = key.lower()
            if key_lower in _TARGET_KEYS or key_lower == "tol" or key_lower in _DETAIL_SKIP_KEYS:
                continue
            actuals.append(value)
            name = re.search(r"P\([^)]*\)", key)
            if name and 0.0 <= value <= 1.0:
                p_by_name[name.group(0)] = value
        # concentration checks: two or more distinct P(..) values -> their sum
        if len(p_by_name) >= 2 and 0.0 <= sum(p_by_name.values()) <= 1.0:
            actuals = [sum(p_by_name.values())]
        for actual in actuals:
            for direction in directions:
                triples.append((actual, thresholds[0] if thresholds else target, direction))

    # KV-actual vs printed target without any comparator/need marker:
    # "kernel_value(x, x) = 0.213857, expected 1.0" — equality form
    if target is not None and not triples:
        for key, value in pairs:
            key_lower = key.lower()
            if key_lower in _TARGET_KEYS or key_lower == "tol" or key_lower in _DETAIL_SKIP_KEYS:
                continue
            triples.append((value, target, "equal"))

    if not triples:
        return None

    best: float | None = None
    for actual, expected, direction in triples:
        if expected is None:
            continue
        if direction == "higher":
            miss = max(0.0, expected - actual)
        elif direction == "lower":
            miss = max(0.0, actual - expected)
        else:
            miss = abs(actual - expected)
        norm = tolerance if tolerance is not None else abs(expected)
        if norm <= 0.0:
            continue
        distance = miss / norm
        best = distance if best is None else min(best, distance)
    return best


def error_distance(details: Sequence[str]) -> float | None:
    """Best (min) relative error distance across the detail lines.

    0.0 means within tolerance; None means no numeric actual exists (None-stub,
    crash, pure-text assertion).
    """
    best: float | None = None
    for detail in details or []:
        if not isinstance(detail, str):
            detail = str(detail)
        if not detail.strip():
            continue
        distance = _line_error_distance(detail)
        if distance is not None:
            best = distance if best is None else min(best, distance)
    return best


def task_error_distance(results: Sequence[dict[str, Any]]) -> float | None:
    """Per-task error distance: 0.0 when the task passed, else the min across
    the failing candidates' details (None when no numeric actual exists)."""
    distances: list[float] = []
    for result in results:
        if bool(result.get("passed")):
            return 0.0
        distance = error_distance(result.get("details") or [])
        if distance is not None:
            distances.append(distance)
    return min(distances) if distances else None


def arm_error_distances(results: Sequence[dict[str, Any]]) -> list[float | None]:
    """Per-task error distances for a whole arm, in task order."""
    order, by_task = _group_by_task(results)
    return [task_error_distance(by_task[task_id]) for task_id in order]


# ---------------------------------------------------------------------------
# CLI: score one or more cached run dirs (+ per-task delta table vs the first)
# ---------------------------------------------------------------------------


def load_scorecard_results(run_dir: Path) -> list[dict[str, Any]]:
    scorecard = json.loads((run_dir / "scorecard.json").read_text(encoding="utf-8"))
    if scorecard.get("schema_version") != "eval-scorecard-v2":
        raise SystemExit(f"untrusted scorecard schema: {run_dir}")
    results = scorecard.get("results")
    if not isinstance(results, list) or not results:
        raise SystemExit(f"empty results: {run_dir}")
    return results


def run_report(run_dir: Path, mode: str) -> dict[str, Any]:
    results = load_scorecard_results(run_dir)
    scores = arm_fine_scores(results, mode=mode)
    distances = arm_error_distances(results)
    return {
        "run_dir": str(run_dir),
        "mode": mode,
        "n_tasks": len(scores),
        "passed": len(
            {str(result.get("id")) for result in results if result.get("passed")}
        ),  # distinct passing tasks
        "fine_mean": arm_mean_fine_score(results, mode=mode),
        "scores": scores,
        "distances": distances,
    }


def format_report(reports: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for index, report in enumerate(reports):
        tag = f"[{index}]"
        lines.append(
            f"{tag} {report['run_dir']} mode={report['mode']} "
            f"pass={report['passed']}/{report['n_tasks']} "
            f"fine_mean={report['fine_mean']:.4f}"
        )
    base = reports[0]["scores"]
    lines.append("task deltas (fine score - base, per task):")
    for index, report in enumerate(reports[1:], start=1):
        # Length EQUALITY is a hard contract: a partial scorecard (truncated
        # results, e.g. a crashed leg) would otherwise silently truncate the
        # cross-arm deltas — a partial comparison that looks complete
        # (2026-08-26 code-review finding). Fail loud: the SystemExit keeps a
        # friendly CLI message, and the strict pairing (training.compat)
        # hardens the zip itself for the same class.
        if len(report["scores"]) != len(base):
            raise SystemExit(
                f"fine-score task count mismatch: base {len(base)} vs "
                f"{report['run_dir']} {len(report['scores'])} — refusing a "
                f"partial-leg comparison"
            )
        deltas = [value - base_value for base_value, value in strict_zip(base, report["scores"])]
        moved = sum(1 for delta in deltas if abs(delta) >= 1e-9)
        lines.append(
            f"  [{index}] moved={moved} tasks: " + ", ".join(f"{delta:+.4f}" for delta in deltas)
        )
    for index, report in enumerate(reports):
        lines.append(f"[{index}] error distances (None = no numeric actual):")
        # Distances are one-per-scorecard-result (same task list) — equal by
        # construction, but strict pairing keeps it that way: a mismatch
        # raises instead of silently dropping rows. The ids are deduped to one
        # row per UNIQUE task id (first-seen order, matching
        # _group_by_task/arm_error_distances): a multi-candidate task would
        # otherwise duplicate its id and mislabel the following rows
        # (2026-08-26 code-review finding).
        report_ids = list(
            dict.fromkeys(str(r.get("id")) for r in load_scorecard_results(Path(report["run_dir"])))
        )
        for task_id, distance in strict_zip(report_ids, report["distances"]):
            value = "None" if distance is None else f"{distance:.4f}"
            lines.append(f"    {task_id}: {value}")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dirs", nargs="+", type=Path, help="cached eval run dirs")
    parser.add_argument("--mode", choices=("best", "mean"), default="best")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    reports = [run_report(run_dir, mode=args.mode) for run_dir in args.run_dirs]
    if len(reports) > 1:
        mean_reports = [run_report(run_dir, mode="mean") for run_dir in args.run_dirs]
        lines = [format_report(reports), "best-vs-mean arm means:"]
        for index, report in enumerate(reports):
            lines.append(
                f"  [{index}] {Path(report['run_dir']).name} best={report['fine_mean']:.4f} "
                f"mean={mean_reports[index]['fine_mean']:.4f} "
                f"diff={report['fine_mean'] - mean_reports[index]['fine_mean']:+.4f}"
            )
        print("\n".join(lines))
    else:
        print(format_report(reports))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
