"""TDD tests for the domain regression gate (scripts/domain_regression_gate.py).

Industrial-standard continuous regression gate for the domain-performance
monitor (contract: evals/domain_monitor/README.md): a NEW warm-continue launch
must NOT proceed when any monitored domain (math / coding / physics / qis)
regressed beyond the allowed composite drop (default 0.10) versus the previous
checkpoint.

Two input shapes are accepted:
  A. a domain_drift_report.py JSON (per-domain composite for baseline +
     candidate), and
  B. the raw results tree (evals/domain_monitor/results/<adapter>/
     <domain>_<date>.json), where the newest dated file per domain is the
     measurement.

The failing case must exit NONZERO so launch scripts can block on it. All
tests run locally on CPU with tiny synthetic JSON files; no model, no box.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import domain_regression_gate as gate  # noqa: E402
import pytest

GATE = ROOT / "scripts" / "domain_regression_gate.py"

DOMAINS = ("math", "coding", "physics", "qis")


def run_gate(*args):
    return subprocess.run(
        [sys.executable, str(GATE), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def domain_result(domain, adapter, rubric, passed, total):
    """One domain-monitor result file body: records + rolled-up composite."""
    records = []
    for i in range(total):
        records.append(
            dict(
                task_id=domain + "-" + format(i, "02d"),
                domain=domain,
                passed=i < passed,
                scores=dict(overall=round(rubric if i < passed else 0.0, 4)),
            )
        )
    return dict(
        domain=domain,
        adapter=adapter,
        composite=round(0.7 * rubric + 0.3 * (passed / total), 4),
        n_tasks=total,
        records=records,
    )


def write_drift_report(path, base, adapter):
    domains = dict()
    for d in DOMAINS:
        domains[d] = dict(composite_base=base[d], composite_adapter=adapter[d])
    path.write_text(
        json.dumps(
            dict(
                kind="domain_drift_report",
                baseline=dict(label="prev-checkpoint-adapter"),
                candidate=dict(label="next-checkpoint-adapter"),
                domains=domains,
            )
        ),
        encoding="utf-8",
    )
    return path


def write_results_tree(results_dir, adapter, comps):
    """results/<adapter>/<domain>_<date>.json for each domain."""
    for domain, comp in comps.items():
        ddir = results_dir / adapter
        ddir.mkdir(parents=True, exist_ok=True)
        rubric = (comp - 0.15) / 0.7  # so 0.7*rubric + 0.3*0.5 == comp
        body = domain_result(domain, adapter, rubric=rubric, passed=1, total=2)
        body["composite"] = round(comp, 4)
        body["records"][0]["scores"]["overall"] = round(rubric, 4)
        (ddir / (domain + "_20260907.json")).write_text(json.dumps(body), encoding="utf-8")
    return results_dir


def all_domains(value):
    return dict((d, value) for d in DOMAINS)


def test_gate_passes_when_all_domains_above_threshold(tmp_path):
    report = write_drift_report(
        tmp_path / "drift_report.json",
        base=dict(math=0.60, coding=0.55, physics=0.50, qis=0.45),
        adapter=dict(math=0.65, coding=0.58, physics=0.52, qis=0.44),
    )
    result = run_gate("--drift-report", str(report))
    assert result.returncode == 0, result.stderr
    assert "GATE: GREEN" in result.stdout


def test_gate_fails_nonzero_when_one_domain_below_threshold(tmp_path):
    report = write_drift_report(
        tmp_path / "drift_report.json",
        base=dict(math=0.60, coding=0.55, physics=0.50, qis=0.45),
        adapter=dict(math=0.66, coding=0.58, physics=0.52, qis=0.30),
    )
    result = run_gate("--drift-report", str(report))
    assert result.returncode != 0, "regression must BLOCK the launch (exit nonzero)"
    assert "qis" in result.stdout
    assert "GATE: RED" in result.stdout


def test_gate_from_results_dirs_newest_file_per_domain(tmp_path):
    base = write_results_tree(tmp_path / "base", "adapter-prev", all_domains(0.60))
    cand = write_results_tree(tmp_path / "cand", "adapter-next", all_domains(0.62))
    result = run_gate("--baseline-dir", str(base), "--candidate-dir", str(cand))
    assert result.returncode == 0, result.stdout + result.stderr
    assert "GATE: GREEN" in result.stdout


def test_gate_from_results_dirs_detects_single_domain_regression(tmp_path):
    base = write_results_tree(tmp_path / "base", "adapter-prev", all_domains(0.60))
    cand_scores = all_domains(0.62)
    cand_scores["coding"] = 0.44  # -0.16 on coding only
    cand = write_results_tree(tmp_path / "cand", "adapter-next", cand_scores)
    result = run_gate("--baseline-dir", str(base), "--candidate-dir", str(cand))
    assert result.returncode != 0
    assert "coding" in result.stdout
    assert "GATE: RED" in result.stdout


def test_gate_prefers_newest_dated_file(tmp_path):
    """Older file says regression, newer dated file recovers -> newest wins."""
    base = write_results_tree(tmp_path / "base", "adapter-prev", all_domains(0.60))
    cand = write_results_tree(tmp_path / "cand", "adapter-next", all_domains(0.40))
    for d in DOMAINS:
        body = domain_result(d, "adapter-next", rubric=0.62, passed=1, total=2)
        body["composite"] = 0.62
        body["records"][0]["scores"]["overall"] = 0.62
        (cand / "adapter-next" / (d + "_20260908.json")).write_text(
            json.dumps(body), encoding="utf-8"
        )
    result = run_gate("--baseline-dir", str(base), "--candidate-dir", str(cand))
    assert result.returncode == 0, result.stdout + result.stderr


# ---------------------------------------------------------------------------
# programmatic gate() API (training launch guard hook)
# ---------------------------------------------------------------------------


def test_gate_api_pass_and_block_and_boundary():
    scores = dict(math=(0.60, 0.61), coding=(0.55, 0.56), physics=(0.50, 0.50), qis=(0.45, 0.44))
    ok, failed = gate.gate(scores)
    assert ok and failed == []
    bad = dict(scores)
    bad["qis"] = (0.45, 0.30)  # -0.15 drop on qis only
    ok, failed = gate.gate(bad)
    assert not ok and failed == ["qis"]
    boundary = dict(math=(0.60, 0.50))  # exactly -0.10: not a block
    assert gate.gate(boundary) == (True, [])
    beyond = dict(math=(0.60, 0.4999))
    assert gate.gate(beyond)[0] is False


def test_gate_api_fail_closed_on_unmeasurable_domain():
    ok, failed = gate.gate(dict(x=(None, 1.0)))
    assert not ok and "x" in failed


# ---------------------------------------------------------------------------
# records-only fallback + metric-name flexibility (no precomputed composite)
# ---------------------------------------------------------------------------


def test_composite_from_records_when_composite_missing():
    rec = dict(
        records=[
            dict(passed=True, scores=dict(overall=0.8)),
            dict(passed=False, scores=dict(overall=0.2)),
        ]
    )
    assert gate.candidate_composite(rec) == pytest.approx(0.7 * 0.5 + 0.3 * 0.5)


def test_composite_from_metric_alias_when_no_records():
    for key in ("composite", "avg_composite", "mean_composite", "avg_rubric", "mean_overall"):
        assert gate.candidate_composite(dict.fromkeys([key], 0.42)) == pytest.approx(0.42), key


# ---------------------------------------------------------------------------
# fail-closed semantics
# ---------------------------------------------------------------------------


def test_gate_fails_closed_on_missing_baseline_domain(tmp_path):
    report = write_drift_report(
        tmp_path / "drift.json",
        base=dict(math=0.60, coding=0.55, physics=0.50, qis=0.45),
        adapter=dict(math=0.62, coding=0.56, physics=0.51, qis=0.46),
    )
    payload = json.loads(report.read_text(encoding="utf-8"))
    del payload["domains"]["physics"]
    report.write_text(json.dumps(payload), encoding="utf-8")
    result = run_gate("--drift-report", str(report))
    assert result.returncode != 0, "unmeasurable domain must BLOCK, not silently pass"
    assert "physics" in result.stdout


def test_gate_input_error_exits_2(tmp_path):
    missing = tmp_path / "nope.json"
    result = run_gate("--drift-report", str(missing))
    assert result.returncode == 2, "unusable inputs must fail-closed with exit 2"


def test_gate_custom_threshold_flag(tmp_path):
    report = write_drift_report(
        tmp_path / "drift.json",
        base=dict(math=0.60, coding=0.55, physics=0.50, qis=0.45),
        adapter=dict(math=0.66, coding=0.58, physics=0.52, qis=0.38),
    )
    ok = run_gate("--drift-report", str(report), "--max-composite-drop", "0.10")
    strict = run_gate("--drift-report", str(report), "--max-composite-drop", "0.05")
    assert ok.returncode == 0
    assert strict.returncode != 0


def test_gate_json_output_file_written(tmp_path):
    report = write_drift_report(
        tmp_path / "drift.json",
        base=dict(math=0.60, coding=0.55, physics=0.50, qis=0.45),
        adapter=dict(math=0.66, coding=0.58, physics=0.52, qis=0.30),
    )
    out = tmp_path / "gate.json"
    result = run_gate("--drift-report", str(report), "--output", str(out))
    assert result.returncode != 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["ok"] is False
    assert payload["failed_domains"] == ["qis"]
    assert payload["max_composite_drop"] == pytest.approx(0.10)
