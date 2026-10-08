"""Regression tests for evals/subsystem/{analyzer,dataset_gap,reporter} on
the legacy v1 scorecard format.

The v1 scorecard shape (produced by the old eval/run_eval.py score step) is:
  {
    "scored_at_utc": "...",
    "results": [ { "id": "...", "domain": "...", "category": "...",
                    "passed": true, "details": [...], ... }, ... ],
    "failure_category_summary": {...}
  }

This is distinct from:
  - schema_version=2 output from harness.py (results keyed by model -> records)
  - the older `records` list shape with per-record `model` field

These tests ensure the subsystem CLI tools can ingest v1 scorecards without
crashing and produce sensible output.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SUB = REPO / "evals" / "subsystem"

# A minimal v1 scorecard fixture based on the real
# evals/runs/qwen25-1p5b-no-rag-20260428T052701Z/scorecard.json shape.
V1_FIXTURE = {
    "scored_at_utc": "2026-04-28T05:28:32.063378+00:00",
    "backend": None,
    "prompt_style": None,
    "prompt_version": None,
    "failure_category_summary": {"runtime": 1},
    "results": [
        {
            "id": "quantum_bell_pair_construction",
            "domain": "quantum",
            "category": "circuit_construction",
            "name": "Bell pair construction",
            "passed": True,
            "details": ["state=[0.707, 0.0, 0.0, 0.707]"],
            "candidate_path": "/tmp/candidate.py",
            "candidate_paths": {"candidate.py": "/tmp/candidate.py"},
            "workspace_mode": "inline",
            "source": "qwen25-1p5b",
            "error_type": None,
            "failure_category": None,
        },
        {
            "id": "quantum_density_matrix_partial_trace",
            "domain": "quantum",
            "category": "algorithm_implementation",
            "name": "Density matrix partial trace",
            "passed": False,
            "details": ["runner_exception: AttributeError: ..."],
            "candidate_path": "/tmp/candidate2.py",
            "candidate_paths": {"candidate.py": "/tmp/candidate2.py"},
            "workspace_mode": "inline",
            "source": "qwen25-1p5b",
            "error_type": "AttributeError",
            "failure_category": "runtime",
        },
        {
            "id": "software_off_by_one_bugfix",
            "domain": "software",
            "category": "bugfix",
            "name": "Off-by-one bugfix",
            "passed": True,
            "details": [],
            "candidate_path": "/tmp/candidate3.py",
            "candidate_paths": {"candidate.py": "/tmp/candidate3.py"},
            "workspace_mode": "inline",
            "source": "qwen25-1p5b",
            "error_type": None,
            "failure_category": None,
        },
    ],
}


@pytest.fixture()
def v1_scorecard(tmp_path):
    p = tmp_path / "scorecard.json"
    p.write_text(json.dumps(V1_FIXTURE), encoding="utf-8")
    return p


def _run(mod: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SUB / f"{mod}.py"), *args],
        capture_output=True,
        text=True,
        cwd=str(REPO),
    )


def test_analyzer_compare_v1_scorecard(v1_scorecard):
    """analyzer.py compare must not crash on a v1 scorecard (regression:
    previously raised ValueError: max() iterable argument is empty)."""
    r = _run("analyzer", "compare", "--eval", str(v1_scorecard))
    assert r.returncode == 0, f"stderr:\n{r.stderr}"
    assert "Summary" in r.stdout
    # For a single-model v1 file, base and adapter both reflect all records.
    assert "2/3" in r.stdout


def test_analyzer_failures_v1_scorecard(v1_scorecard):
    """analyzer.py failures must list the single failing task."""
    r = _run("analyzer", "failures", "--eval", str(v1_scorecard), "--model", "adapter")
    assert r.returncode == 0, f"stderr:\n{r.stderr}"
    assert "quantum_density_matrix_partial_trace" in r.stdout
    assert "1 failing tasks" in r.stdout


def test_analyzer_trend_v1_scorecard(v1_scorecard):
    """analyzer.py trend must not crash across two v1 scorecards."""
    r = _run("analyzer", "trend", str(v1_scorecard), str(v1_scorecard))
    assert r.returncode == 0, f"stderr:\n{r.stderr}"
    assert "quantum_bell_pair_construction" in r.stdout


def test_dataset_gap_coverage_v1_scorecard(v1_scorecard):
    """dataset_gap.py coverage must produce domain/category breakdown
    (regression: previously produced empty output)."""
    r = _run("dataset_gap", "coverage", "--eval", str(v1_scorecard))
    assert r.returncode == 0, f"stderr:\n{r.stderr}"
    assert "By domain:" in r.stdout
    assert "quantum" in r.stdout
    assert "software" in r.stdout
    # 2/3 pass overall (the bell + software pass, density matrix fails)
    assert "2/3" in r.stdout


def test_dataset_gap_recommend_v1_scorecard(v1_scorecard):
    """dataset_gap.py recommend must identify the failing task as a gap."""
    r = _run("dataset_gap", "recommend", "--eval", str(v1_scorecard), "--model", "adapter")
    assert r.returncode == 0, f"stderr:\n{r.stderr}"
    # The fixture has exactly one failing task → one gap recommendation.
    assert "quantum_density_matrix_partial_trace" in r.stdout


def test_reporter_single_v1_scorecard(v1_scorecard):
    """reporter.py single must produce a Markdown report (regression:
    previously raised KeyError: 'task_id')."""
    r = _run("reporter", "single", "--eval", str(v1_scorecard))
    assert r.returncode == 0, f"stderr:\n{r.stderr}"
    assert "## Summary" in r.stdout
    assert "## Per-task Results" in r.stdout
    assert "quantum_bell_pair_construction" in r.stdout
    assert "quantum_density_matrix_partial_trace" in r.stdout
