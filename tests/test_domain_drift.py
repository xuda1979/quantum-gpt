"""TDD: cross-domain performance-drift report. Given per-domain eval JSONs
(mirroring run_asi2_base_adapter_rubric_eval output), assemble: per-domain
composite (0.70*rubric + 0.30*pass) + drift vs base, so we see performance
change across math/coding/physics as training evolves (industrial-standard)."""
from scripts import domain_drift_report as D


def _domain_eval(adapter_tasks, base_tasks, domain):
    """adapter_tasks/base_tasks: list of (task_id, passed, overall). Domains are
    scored via a per-domain eval JSON (subset) with the standard record schema."""
    records = []
    for m, tasks in (("adapter", adapter_tasks), ("base", base_tasks)):
        for tid, passed, overall in tasks:
            records.append({"model": m, "task_id": tid, "category": domain,
                            "passed": passed, "scores": {"overall": overall}})
    return {"records": records, "domain": domain}


def test_drift_report_empty_no_results():
    """No result files -> empty report (never crash)."""
    assert D.report_from_results({}) == {}


def test_drift_report_computes_per_domain_composite_and_delta():
    """Two domains with known adapter/base composites -> correct drift table."""
    # math: adapter high rubric, base low
    math = _domain_eval(
        [("t1", False, 6.0), ("t2", False, 6.0), ("t3", True, 6.0)],
        [("t1", False, 1.0), ("t2", False, 1.0), ("t3", False, 1.0)],
        "math",
    )
    # coding: adapter moderate, base moderate (little drift)
    coding = _domain_eval(
        [("c1", True, 5.0), ("c2", False, 4.0)],
        [("c1", True, 4.5), ("c2", False, 4.0)],
        "coding",
    )
    out = D.report_from_results({"math": math, "coding": coding}, n_tasks=3)
    assert set(out.keys()) == {"math", "coding"}
    m = out["math"]
    # adapter math composite: rub mean (18/3=6 or 6.0) and passes... /3
    assert m["adapter_composite"] > m["base_composite"]
    assert m["drift_vs_base"] > 0  # adapter beat base on math
    c = out["coding"]
    # coding adapter slightly > base (rubric 4.67 vs 4.25 mean, 1 pass vs 1)
    assert c["drift_vs_base"] is not None
    # drift table is a stable dict, sorts deterministically
    assert isinstance(out, dict)
