"""Regression tests for the fine-grained continuous scorer (SAPO loop).

The binary 18-task pass/fail holdout cannot distinguish tied arms (base 8/18,
warm 6/18, run-1 s2/s7 8/18 with identical pass sets, run-2 s4 8/18). This
instrument turns each task into a continuous grade in [0, 1] by reusing the
shaped-reward progress math from ``training/grpo_utils.py``
(``shaped_reward_from_details`` / ``_detail_progress`` / ``_has_runtime_failure``):

    grade = 1.0                     if passed
            0.5 + 0.5 * progress    near-miss band [0.5, 0.9)  (capped at 0.9)
            0.0                     crash / syntax / import / None-stub /
                                    no numeric evidence

plus a second axis: relative numeric error distance |actual - expected| /
|expected| (or / tolerance) for the assertion-class failures, extracted from
the same harness detail strings.

Invariants pinned here (directive 2026-08-24):
- pass == 1.0;
- near-miss band is monotone in progress and strictly below 1.0;
- crash / syntax / None-stub == the exact values shaped_reward_from_details
  assigns (single source of truth; the None-stub "fidelity(...) = None,
  expected 1.0" fixture grades 0.0);
- binary pass/fail is the special case of the continuous grade at threshold
  1.0 (grade == 1.0  <==>  passed);
- per-task aggregation (best-of-candidates and mean-of-candidates) and the
  arm-level mean over the 18 tasks;
- error-distance extraction for arrow / comparator / need-threshold forms,
  tolerance normalization, and None when no numeric actual exists.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.fine_score import (  # noqa: E402
    arm_error_distances,
    arm_fine_scores,
    arm_mean_fine_score,
    error_distance,
    fine_grade,
    format_report,
    run_report,
    task_error_distance,
    task_grade,
)
from training.grpo_utils import shaped_reward_from_details  # noqa: E402

# ---------------------------------------------------------------------------
# Fine grade: pass / near-miss band / crash / stub
# ---------------------------------------------------------------------------


def test_pass_grades_1_0() -> None:
    assert fine_grade(True, ["all checks green"]) == 1.0
    assert fine_grade(True, []) == 1.0


def test_near_miss_band_monotone_in_progress() -> None:
    # P(00)=v need>=0.80 -> progress = v / 0.80, grade = 0.5 + 0.5*progress
    low = fine_grade(False, ["P(00)=0.30 need>=0.80"])
    mid = fine_grade(False, ["P(00)=0.60 need>=0.80"])
    high = fine_grade(False, ["P(00)=0.79 need>=0.80"])
    assert 0.5 <= low < mid < high < 1.0
    assert low == pytest.approx(0.5 + 0.5 * (0.30 / 0.80))
    assert mid == pytest.approx(0.5 + 0.5 * (0.60 / 0.80))
    assert high == pytest.approx(0.9)  # capped: a near miss never ties a pass


def test_near_miss_band_floor_is_half() -> None:
    # vanishingly small numeric closeness still gets 0.5+epsilon, never 0
    grade = fine_grade(False, ["-> cost 100, expected 1"])  # exp(-99/0.25) ~ 0
    assert 0.5 <= grade < 1.0


def test_crash_grades_zero() -> None:
    crash = [
        "Traceback (most recent call last):",
        '  File "evals/tasks/quantum/.../tests.py", line 42, in test_thing',
        "TypeError: object of type 'NoneType' has no len()",
    ]
    assert fine_grade(False, crash) == 0.0


def test_syntax_failure_grades_zero() -> None:
    assert fine_grade(False, ["SyntaxError: invalid syntax (line 3)"]) == 0.0
    assert fine_grade(False, ["IndentationError: unexpected indent"]) == 0.0


def test_import_failure_grades_zero() -> None:
    assert fine_grade(False, ["ModuleNotFoundError: No module named 'pennylane'"]) == 0.0
    assert fine_grade(False, ["ImportError: cannot import name 'run_openqasm'"]) == 0.0


def test_none_stub_consistent_with_shaped_and_zero() -> None:
    # The None-stub must take exactly the value shaped assigns (single source
    # of truth) — and for the canonical stub fixture that value is 0.0, i.e. a
    # stub is NOT a near miss even though an "expected" number is printed.
    details = ["assertion: fidelity(...) = None, expected 1.0"]
    assert fine_grade(False, details) == shaped_reward_from_details(False, details)
    assert fine_grade(False, details) == 0.0


def test_missing_function_stub_grades_zero() -> None:
    details = ["assertion: candidate missing required function(s): purity"]
    assert fine_grade(False, details) == 0.0
    assert fine_grade(False, details) == shaped_reward_from_details(False, details)


def test_no_numeric_evidence_grades_zero() -> None:
    assert fine_grade(False, ["assertion: gate alias wrong for X"]) == 0.0
    assert fine_grade(False, []) == 0.0


# ---------------------------------------------------------------------------
# Binary pass/fail is a special case of the continuous grade (threshold 1.0)
# ---------------------------------------------------------------------------


def test_binary_pass_is_special_case_of_continuous() -> None:
    fixtures: list[tuple[bool, list[str]]] = [
        (True, ["ok"]),
        (False, ["P(00)=0.30 need>=0.80"]),
        (False, ["P(00)=0.79 need>=0.80"]),
        (False, ["-> 3, expected 2"]),
        (False, ["Traceback (most recent call last):", "TypeError: x"]),
        (False, ["SyntaxError: invalid syntax"]),
        (False, ["assertion: fidelity(...) = None, expected 1.0"]),
        (False, ["assertion: plain mismatch"]),
    ]
    for passed, details in fixtures:
        grade = fine_grade(passed, details)
        assert (grade == 1.0) == passed
        assert 0.0 <= grade <= 1.0


# ---------------------------------------------------------------------------
# Per-task aggregation and arm-level mean
# ---------------------------------------------------------------------------


def _result(task_id: str, passed: bool, details: list[str]) -> dict:
    return {
        "id": task_id,
        "passed": passed,
        "details": details,
        "failure_category": None if passed else "assertion",
        "error_type": None,
        "source": "override",
        "candidate_sha256": "0" * 64,
    }


def test_task_grade_best_vs_mean_aggregation() -> None:
    task = [
        _result("t1", False, ["P(00)=0.30 need>=0.80"]),  # 0.6875
        _result("t1", False, ["assertion: crash -> 0.0"]),  # 0.0
        _result("t1", True, ["ok"]),  # 1.0
    ]
    assert task_grade(task, mode="best") == 1.0
    assert task_grade(task, mode="mean") == pytest.approx((0.6875 + 0.0 + 1.0) / 3.0)
    assert 0.0 <= task_grade(task, mode="mean") <= 1.0


def test_task_grade_all_fail_best_is_max_near_miss() -> None:
    task = [
        _result("t1", False, ["P(00)=0.30 need>=0.80"]),  # 0.6875
        _result("t1", False, ["P(00)=0.60 need>=0.80"]),  # 0.875
    ]
    assert task_grade(task, mode="best") == pytest.approx(0.875)
    assert task_grade(task, mode="mean") == pytest.approx((0.6875 + 0.875) / 2.0)


def test_task_grade_empty_candidates_is_zero() -> None:
    assert task_grade([], mode="best") == 0.0
    assert task_grade([], mode="mean") == 0.0


def test_arm_fine_scores_mean_over_tasks() -> None:
    results = [
        _result("t01", True, ["ok"]),  # 1.0
        _result("t02", True, ["ok"]),  # 1.0
        _result("t03", False, ["P(00)=0.30 need>=0.80"]),  # 0.6875
        _result("t04", False, ["assertion: plain"]),  # 0.0
        _result("t05", False, ["crash"] + ["TypeError: x"]),  # 0.0
    ]
    per_task = arm_fine_scores(results, mode="best")
    assert per_task == pytest.approx([1.0, 1.0, 0.6875, 0.0, 0.0])
    assert arm_mean_fine_score(results, mode="best") == pytest.approx(
        (1.0 + 1.0 + 0.6875 + 0.0 + 0.0) / 5.0
    )
    assert arm_mean_fine_score(results, mode="mean") == pytest.approx(
        arm_mean_fine_score(results, mode="best")
    )  # one candidate per task -> modes coincide


def test_arm_fine_scores_orders_tasks_and_reports_delta() -> None:
    # Two arms with identical pass sets must still separate numerically.
    base = [
        _result("t01", True, ["ok"]),
        _result("t02", False, ["P(00)=0.30 need>=0.80"]),
        _result("t03", False, ["assertion: plain"]),
    ]
    other = [
        _result("t01", True, ["ok"]),
        _result("t02", False, ["P(00)=0.60 need>=0.80"]),  # nearer miss
        _result("t03", False, ["assertion: plain"]),
    ]
    base_scores = arm_fine_scores(base, mode="best")
    other_scores = arm_fine_scores(other, mode="best")
    # plain zip: equal length is guaranteed by arm_fine_scores (one score per
    # candidate id); strict=True is py3.10-only and the venv is py3.9.
    deltas = [o - b for b, o in zip(base_scores, other_scores)]
    assert [d == 0.0 for d in deltas] == [True, False, True]
    assert deltas[1] == pytest.approx(0.875 - 0.6875)
    assert arm_mean_fine_score(other, mode="best") > arm_mean_fine_score(base, mode="best")


def test_format_report_deltas_use_py39_safe_zip(tmp_path: Path) -> None:
    """The report-deltas path (zip(base, report["scores"])) must be py3.9-safe.

    2026-08-25 (Deploy Integrity py3.9 gate): format_report shipped
    ``zip(base, report["scores"])`` — py3.10-only; it would
    TypeError in the box's py3.9 venv when the evaluator's leg runs fine
    scoring. The source-level guard catches ANY future strict= regression
    (a runtime test cannot, because the local host is py3.14)."""
    import inspect

    import scripts.fine_score as fine_score_mod

    # the strict= KEYWORD itself is py3.10-only (even strict=False) — any
    # occurrence, in code or comments, is a deploy-gate failure
    assert "strict=" not in inspect.getsource(fine_score_mod)
    assert "from __future__ import annotations" in inspect.getsource(
        fine_score_mod
    )  # PEP 604 safety
    base_dir = tmp_path / "base"
    other_dir = tmp_path / "other"
    base_dir.mkdir()
    other_dir.mkdir()
    for run_dir, results in (
        (
            base_dir,
            [
                _result("t01", True, ["ok"]),
                _result("t02", False, ["P(00)=0.30 need>=0.80"]),
                _result("t03", False, ["assertion: plain"]),
            ],
        ),
        (
            other_dir,
            [
                _result("t01", True, ["ok"]),
                _result("t02", False, ["P(00)=0.60 need>=0.80"]),  # nearer miss
                _result("t03", False, ["assertion: plain"]),
            ],
        ),
    ):
        (run_dir / "scorecard.json").write_text(
            json.dumps({"schema_version": "eval-scorecard-v2", "results": results}),
            encoding="utf-8",
        )
    base_report = run_report(base_dir, mode="best")
    other_report = run_report(other_dir, mode="best")
    text = format_report([base_report, other_report])
    delta_line = next(line for line in text.splitlines() if line.startswith("  [1] moved="))
    assert "moved=1 tasks" in delta_line
    assert "+0.1875" in delta_line  # t02 nearer-miss delta 0.875 - 0.6875


def test_format_report_fails_loud_on_task_count_mismatch(tmp_path: Path) -> None:
    """2026-08-26 code-review finding: the py3.9 plain-zip conversion dropped
    the strict-zip LENGTH GUARD — a partial scorecard (truncated results
    list, e.g. a crashed leg) would silently truncate the cross-arm deltas
    (a partial-leg comparison that looks complete). Must fail loud."""
    base_dir = tmp_path / "base"
    partial_dir = tmp_path / "partial"
    base_dir.mkdir()
    partial_dir.mkdir()
    full_results = [
        _result("t01", True, ["ok"]),
        _result("t02", False, ["assertion: plain"]),
        _result("t03", False, ["assertion: plain"]),
    ]
    (base_dir / "scorecard.json").write_text(
        json.dumps({"schema_version": "eval-scorecard-v2", "results": full_results}),
        encoding="utf-8",
    )
    # the partial leg scored only 2 of the 3 tasks (crashed mid-run)
    (partial_dir / "scorecard.json").write_text(
        json.dumps({"schema_version": "eval-scorecard-v2", "results": full_results[:2]}),
        encoding="utf-8",
    )
    base_report = run_report(base_dir, mode="best")
    partial_report = run_report(partial_dir, mode="best")
    with pytest.raises(SystemExit, match="task count mismatch"):
        format_report([base_report, partial_report])


# ---------------------------------------------------------------------------
# Error distance axis
# ---------------------------------------------------------------------------


def test_error_distance_arrow_expected() -> None:
    assert error_distance(["phase_estimation(0.25, 3) -> 3, expected 2"]) == pytest.approx(
        0.5
    )  # |3-2| / |2|
    assert error_distance(["-> cost 1, expected 2"]) == pytest.approx(0.5)


def test_error_distance_arrow_with_tolerance() -> None:
    # tol= normalizes by the tolerance instead of |expected|
    assert error_distance(["-> 2.5, expected 2.0, tol=0.5"]) == pytest.approx(1.0)


def test_error_distance_comparator_higher_better() -> None:
    # fidelity 0.8765 < 0.9000: pass wanted v >= 0.9 -> miss (0.9-0.8765)/0.9
    assert error_distance(["xeb: fidelity=0.8765 need>=0.9000"]) == pytest.approx(
        (0.9000 - 0.8765) / 0.9000
    )
    assert error_distance(["fidelity 0.8765 < 0.9000"]) == pytest.approx((0.9000 - 0.8765) / 0.9000)


def test_error_distance_comparator_lower_better() -> None:
    # error 0.0521 > 0.0500: pass wanted v <= 0.05 -> miss (0.0521-0.05)/0.05
    assert error_distance(["hhl: max abs error=0.0521 need<=0.0500"]) == pytest.approx(
        (0.0521 - 0.0500) / 0.0500
    )
    assert error_distance(["error 0.0521 > 0.0500"]) == pytest.approx((0.0521 - 0.05) / 0.05)


def test_error_distance_equality_miss() -> None:
    assert error_distance(["optimize_circuit lost gates: 3 != 5"]) == pytest.approx(2.0 / 5.0)


def test_error_distance_no_numeric_actual_is_none() -> None:
    # A passing candidate's detail line carries no numeric evidence, and a
    # pure-text assertion carries none either — at the detail level that is
    # "no numeric actual" (None), not a distance.
    assert error_distance(["Gate alias normalization handles casing"]) is None
    assert error_distance([]) is None
    assert error_distance(["assertion: plain mismatch"]) is None


def test_error_distance_none_stub_returns_none() -> None:
    assert error_distance(["assertion: fidelity(...) = None, expected 1.0"]) is None
    assert error_distance(["assertion: missing trotter_evolve"]) is None
    assert error_distance(["Traceback (most recent call last):", "TypeError: x"]) is None


def test_error_distance_kv_actual_expected() -> None:
    # key=actual, expected T on the same line (the iris near-miss form)
    assert error_distance(["kernel_value(x, x) = 0.213857, expected 1.0"]) == pytest.approx(
        abs(0.213857 - 1.0) / 1.0
    )


def test_error_distance_best_line_wins() -> None:
    details = [
        "P(00)=0.10 need>=0.80",  # (0.8-0.1)/0.8 = 0.875
        "P(00)=0.60 need>=0.80",  # (0.8-0.6)/0.8 = 0.25
    ]
    assert error_distance(details) == pytest.approx(0.25)


def test_task_error_distance_min_across_candidates() -> None:
    task = [
        _result("t1", False, ["P(00)=0.10 need>=0.80"]),  # 0.875
        _result("t1", False, ["P(00)=0.70 need>=0.80"]),  # 0.125
    ]
    assert task_error_distance(task) == pytest.approx(0.125)
    # a passing task is within tolerance -> distance 0.0
    assert task_error_distance([_result("t1", True, ["ok"])]) == 0.0
    assert task_error_distance([_result("t1", False, ["assertion: stub = None"])]) is None


def test_arm_error_distances_per_task() -> None:
    results = [
        _result("t01", True, ["ok"]),
        _result("t02", False, ["P(00)=0.60 need>=0.80"]),  # 0.25
        _result("t03", False, ["assertion: fidelity(...) = None, expected 1.0"]),
    ]
    dists = arm_error_distances(results)
    assert dists[0] == 0.0
    assert dists[1] == pytest.approx(0.25)
    assert dists[2] is None
    assert len(dists) == 3


def test_format_report_distances_dedupe_multi_candidate_tasks(tmp_path: Path) -> None:
    """2026-08-26 code-review finding: the distances table zipped RAW scorecard
    rows against per-UNIQUE-task distances — a multi-candidate task duplicated
    its id and mislabeled the following rows. Rows must dedupe to one per
    task id (first-seen order)."""
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    results = [
        _result("t01", True, ["ok"]),
        _result("t01", False, ["P(00)=0.30 need>=0.80"]),  # second candidate
        _result("t02", True, ["ok"]),
    ]
    (run_dir / "scorecard.json").write_text(
        json.dumps({"schema_version": "eval-scorecard-v2", "results": results}),
        encoding="utf-8",
    )
    report = run_report(run_dir, mode="best")
    assert len(report["scores"]) == 2  # one per unique task
    assert len(report["distances"]) == 2
    text = format_report([report])
    distance_lines = [line for line in text.splitlines() if line.startswith("    ")]
    assert len(distance_lines) == 2  # t01 once, t02 once — not 3 rows
    assert "t01" in distance_lines[0] and "t02" in distance_lines[1]


def test_run_report_passed_counts_distinct_tasks(tmp_path: Path) -> None:
    """2026-08-26 code-review finding: 'passed' counted RESULTS, so a task
    with two passing candidates inflated the pass=N/M ratio past 1.0. Pass
    counts DISTINCT passing task ids."""
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    results = [
        _result("t01", True, ["ok"]),
        _result("t01", True, ["ok"]),  # both candidates pass
        _result("t02", False, ["assertion: plain"]),
    ]
    (run_dir / "scorecard.json").write_text(
        json.dumps({"schema_version": "eval-scorecard-v2", "results": results}),
        encoding="utf-8",
    )
    report = run_report(run_dir, mode="best")
    assert report["n_tasks"] == 2
    assert report["passed"] == 1  # one distinct passing task, not 2
