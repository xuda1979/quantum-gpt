"""TDD: the composite beats-base bar + per-category/per-task drill-down must be
unambiguous and correct (addresses degenerate pass@1 + measurement depth)."""
import json, tempfile, os
from scripts import verdict_holdout as V


def _eval(adapter_tasks, base_tasks, n=18):
    """Build a minimal eval JSON. adapter_tasks/base_tasks: list of
    (task_id, category, passed, overall). Fill to n tasks with zeros."""
    records = []
    for i, (tid, cat, passed, overall) in enumerate(adapter_tasks):
        records.append({"model": "adapter", "task_id": tid, "category": cat,
                        "passed": passed, "scores": {"overall": overall}})
    for i, (tid, cat, passed, overall) in enumerate(base_tasks):
        records.append({"model": "base", "task_id": tid, "category": cat,
                        "passed": passed, "scores": {"overall": overall}})
    # pad to n tasks each with zero-scored unseen tasks
    seen_t = {r["task_id"] for r in records}
    for m in ("adapter", "base"):
        for i in range(n):
            tid = f"pad_{m}_{i}"
            if tid not in seen_t:
                records.append({"model": m, "task_id": tid, "category": "other",
                                "passed": False, "scores": {"overall": 0.0}})
    return {"records": records}


def test_composite_favors_more_passes_AND_higher_rubric():
    """Adapter with 1 more pass and same rubric beats base; composite is primary and
    not degenerate (a rubric win alone also moves it)."""
    base = [(f"t{i}", "alg", False, 3.0) for i in range(3)] + [("t9", "norm", True, 3.0)]
    adapter = [("tA", "alg", True, 3.0), ("t0", "alg", False, 3.0), ("t1", "alg", False, 3.0), ("t9", "norm", True, 3.0)]
    d = _eval(adapter, base)
    r = V.verdict(d)
    assert r["beats_base"] is True, f"expected adapter to beat base, got {r}"
    assert r["composite_adapter"] > r["composite_base"]
    assert r["pass_adapter"] == "2/18" and r["pass_base"] == "1/18", r
    # drill-down shows the gain task
    assert r["gains"] == ["tA"], r


def test_rubric_win_alone_beatso_check():
    """Even with equal (tied) passes, a large rubric win flips composite (non-degenerate)."""
    base = [(f"t{i}", "alg", False, 4.0) for i in range(3)] + [("tx", "norm", True, 4.0)]
    adapter = [(f"t{i}", "alg", False, 2.0) for i in range(3)] + [("tx", "norm", True, 4.0)]  # same passes, LOWER rubric
    d = _eval(adapter, base)
    r = V.verdict(d)
    # same passes -> composite driven by rubric: adapter lower rubric -> NOT beats
    assert r["pass_adapter"] == r["pass_base"] == "1/18"
    assert r["beats_base"] is False, "lower rubric with tied passes must NOT beat"


def test_per_category_drilldown():
    """by_category must list each category with adapter/base rubric + pass and a wins flag."""
    d = _eval([("a1", "norm", True, 5.0), ("a2", "alg", False, 2.0)],
              [("a1", "norm", False, 1.0), ("a2", "alg", False, 1.0)])
    r = V.verdict(d)
    cats = {c["category"]: c for c in r["by_category"]}
    assert "norm" in cats and "alg" in cats, cats.keys()
    assert cats["norm"]["adapter_rubric"] == 5.0
    assert cats["norm"]["adapter_wins"] is True  # 5.0 > 1.0
