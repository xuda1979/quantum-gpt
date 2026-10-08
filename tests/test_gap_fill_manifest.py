"""TDD: gap-fill manifest tool must identify the 2-3 near-passing tasks (highest
rubric among FAILED tasks with real code, i.e. 'one-bug-from-correct') to target
in the next manifest — directly addressing the 1->2->...->18/18 pass gap."""
import json, tempfile, os
from scripts import gap_fill_manifest as G


def _eval(adapter_tasks, base_tasks, n=18):
    records = []
    for m, tasks in (("adapter", adapter_tasks), ("base", base_tasks)):
        for tid, cat, passed, overall, chars in tasks:
            records.append({"model": m, "task_id": tid, "category": cat,
                            "passed": passed, "output_chars": chars,
                            "scores": {"overall": overall}})
    seen = {r["task_id"] for r in records}
    for m in ("adapter", "base"):
        for i in range(n):
            tid = f"pad_{m}_{i}"
            if tid not in seen:
                records.append({"model": m, "task_id": tid, "category": "other",
                                "passed": False, "output_chars": 0, "scores": {"overall": 0.0}})
    return {"records": records}


def test_picks_highest_rubric_failed_task_as_gap():
    """The top gap target = the FAILED task with the highest rubric + real code."""
    adapter = [
        ("pass1", "norm", True, 5.0, 800),
        ("near1", "alg", False, 4.5, 750),   # one-bug-from-correct, high rubric
        ("far1", "alg", False, 2.0, 700),
        ("crash1", "alg", False, 1.0, 5),     # tiny/no code -> not a gap target
    ]
    base = [("pass1", "norm", False, 1.0, 800)]
    d = _eval(adapter, base)
    recs = G.recommend(d, top_n=2)
    tasks = [r["task_id"] for r in recs]
    assert "near1" in tasks, f"near-passing near1 missing: {tasks}"
    assert "far1" not in tasks[:1] or recs[0]["task_id"] == "near1", f"top pick wrong: {recs}"
    # near1 (rubric 4.5, 750 chars) must be ahead of far1 (2.0) and crash1 (tiny)


def test_excludes_passed_and_no_code():
    """Passed tasks and near-empty candidates are never gap targets."""
    adapter = [("passed", "norm", True, 5.0, 900), ("tiny", "alg", False, 2.0, 3)]
    d = _eval(adapter, [])
    recs = G.recommend(d, top_n=5)
    ids = {r["task_id"] for r in recs}
    assert "passed" not in ids
    assert "tiny" not in ids
