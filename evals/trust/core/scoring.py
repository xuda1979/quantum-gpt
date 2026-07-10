"""Deterministic scoring and pass@k computation.

pass@k is computed via the standard unbiased estimator:

    pass@k = 1 - C(n - c, k) / C(n, k)

where ``n`` is the total number of samples and ``c`` is the number of
passing samples. We use integer arithmetic throughout to avoid floating
point drift; the result is a float in [0, 1] rounded to 4 decimal
places.

We also compute:

  - ``pass_at_1``     : 1.0 iff any sample passed (deterministic judge)
  - ``n_pass``        : count of passing samples
  - ``n_samples``     : total samples drawn
  - ``verdict_breakdown`` : per-judge pass counts

Disagreements between the deterministic judge and the LLM judge (if
present) are *never* silently averaged. The ``score_task`` function
returns both verdicts; downstream reporting is responsible for
surfacing disagreements.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TaskScore:
    task_id: str
    n_samples: int
    n_pass_det: int
    n_pass_llm: int
    pass_at_1: float           # deterministic-judge pass_at_1 (any-sample-passed)
    pass_at_k: float | None    # None if k == 1
    llm_pass_at_1: float | None
    judge_disagreement: bool   # True iff det and llm verdicts disagree on any sample
    failure_categories: dict[str, int]

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "n_samples": self.n_samples,
            "n_pass_det": self.n_pass_det,
            "n_pass_llm": self.n_pass_llm,
            "pass_at_1": self.pass_at_1,
            "pass_at_k": self.pass_at_k,
            "llm_pass_at_1": self.llm_pass_at_1,
            "judge_disagreement": self.judge_disagreement,
            "failure_categories": self.failure_categories,
        }


def _comb(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    if k == 0 or k == n:
        return 1
    k = min(k, n - k)
    num = 1
    den = 1
    for i in range(k):
        num *= (n - i)
        den *= (i + 1)
    return num // den


def pass_at_k(n: int, c: int, k: int) -> float:
    """Unbiased pass@k estimator.

    ``n``: total samples. ``c``: passing samples. ``k``: samples drawn.
    Returns 1.0 if n < k (treat as if all samples were drawn). Returns
    0.0 if c == 0. Otherwise ``1 - C(n - c, k) / C(n, k)``.
    """
    if n <= 0:
        return 0.0
    if c >= n:
        return 1.0
    if k >= n:
        return 1.0 if c > 0 else 0.0
    if c == 0:
        return 0.0
    # 1 - C(n - c, k) / C(n, k) — use floats for the ratio
    return 1.0 - _comb(n - c, k) / _comb(n, k)


def score_task(
    *,
    task_id: str,
    k: int,
    verdicts: list[dict[str, Any]],
) -> TaskScore:
    """Aggregate per-sample verdicts into a TaskScore.

    Each verdict dict has keys: ``judge`` (str), ``passed`` (bool),
    ``failure_category`` (str | None).
    """
    n_samples = 0
    n_pass_det = 0
    n_pass_llm = 0
    by_index: dict[int, dict[str, bool]] = {}
    fail_cats: dict[str, int] = {}
    for v in verdicts:
        idx = v.get("sample_index", 0)
        by_index.setdefault(idx, {})
        by_index[idx][v["judge"]] = bool(v["passed"])
        if v["judge"] == "deterministic":
            n_samples = max(n_samples, idx + 1)
            if v["passed"]:
                n_pass_det += 1
            elif v.get("failure_category"):
                fail_cats[v["failure_category"]] = fail_cats.get(v["failure_category"], 0) + 1
        elif v["judge"] == "llm":
            if v["passed"]:
                n_pass_llm += 1
    disagreement = False
    for idx, judges in by_index.items():
        if "deterministic" in judges and "llm" in judges and judges["deterministic"] != judges["llm"]:
            disagreement = True
    p1 = 1.0 if n_pass_det > 0 else 0.0
    pk = pass_at_k(n_samples, n_pass_det, k) if k > 1 else None
    llm_p1 = (n_pass_llm / n_samples) if n_samples else None
    return TaskScore(
        task_id=task_id,
        n_samples=n_samples,
        n_pass_det=n_pass_det,
        n_pass_llm=n_pass_llm,
        pass_at_1=p1,
        pass_at_k=round(pk, 4) if pk is not None else None,
        llm_pass_at_1=round(llm_p1, 4) if llm_p1 is not None else None,
        judge_disagreement=disagreement,
        failure_categories=fail_cats,
    )


def aggregate_run(scores: list[TaskScore]) -> dict[str, Any]:
    """Aggregate per-task scores into a run-level summary."""
    n_tasks = len(scores)
    if n_tasks == 0:
        return {
            "n_tasks": 0, "n_pass": 0, "pass_at_1": 0.0,
            "by_domain": {}, "by_category": {}, "by_task": [],
            "disagreements": [],
        }
    n_pass = sum(1 for s in scores if s.pass_at_1 >= 1.0)
    by_domain: dict[str, dict[str, Any]] = {}
    by_cat: dict[str, dict[str, Any]] = {}
    for s in scores:
        d = by_domain.setdefault(s.task_id.split("_")[0] or "unknown", {"n": 0, "pass": 0})
        d["n"] += 1
        if s.pass_at_1 >= 1.0:
            d["pass"] += 1
    # by_category requires the caller to supply domain/category; we use
    # a simpler key here for the aggregate, see CLI for richer grouping.
    disagreements = [s.task_id for s in scores if s.judge_disagreement]
    return {
        "n_tasks": n_tasks,
        "n_pass": n_pass,
        "pass_at_1": round(n_pass / n_tasks, 4),
        "by_domain": {k: {"n": v["n"], "pass": v["pass"],
                          "pass_at_1": round(v["pass"] / v["n"], 4) if v["n"] else 0.0}
                      for k, v in by_domain.items()},
        "by_task": [s.to_dict() for s in scores],
        "disagreements": disagreements,
    }
