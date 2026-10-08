"""2026-09-20 (manager): the repair-source preflight became a CPU furnace.

An uncommitted change to ``load_reference_correction`` (fv_gspo_repair_stage)
started verifying every record of the ~917-line distill reference jsonl by
EXECUTING it, and the ASI3 launch preflight calls that helper once per
manifest task -- measured live at 75+ CPU-minutes for ONE preflight process,
with orphaned (PPID 1) copies piling up per suite chunk and the launcher
readiness tests hanging past the chunk timeout. The gate must be O(ms).

Contract pinned here:
  * scanning the reference jsonl NEVER executes record code (a gate must not
    run arbitrary module-level code; the repair stage's
    run_candidate_against_harness is the execution-grounded verifier);
  * a record is eligible when its non-blank code COMPILES (rejects syntax-
    broken stubs at ~ms cost); the LAST eligible record wins;
  * the task's own non-stub reference candidate wins over the jsonl (the
    committed preflight docstring: "the task's declared candidate_file,
    or -- for qc-NNNN ids -- line N of the verified distill reference jsonl");
  * a comment-only training-stub candidate still falls through to the jsonl
    (test_distill_repair_uses_questions_and_code_instead_of_stub stays law);
  * the REAL preflight over the REAL tree completes in seconds, not hours.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = str(ROOT / "scripts")
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)

from fv_gspo_repair_stage import load_reference_correction  # noqa: E402

PREFLIGHT = ROOT / "scripts" / "sapo_repair_source_preflight.py"


def _write_jsonl(path, records):
    rows = []
    for i, code in enumerate(records):
        rows.append(json.dumps(dict(question="q%d" % i, code=code)))
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return path


def test_reference_scan_never_executes_record_code(tmp_path):
    marker = tmp_path / "module_level_side_effect.marker"
    source = _write_jsonl(
        tmp_path / "ref.jsonl",
        [f"import pathlib\npathlib.Path({str(marker)!r}).write_text('fired')\n"],
    )
    task_dir = tmp_path / "qc-0001"
    task_dir.mkdir()

    correction = load_reference_correction(task_dir, dict(id="qc-0001"), source)

    assert correction is not None, "compilable record must be returned"
    assert "write_text" in correction
    assert not marker.exists(), (
        "the scan EXECUTED record code -- a launch gate must never run "
        "arbitrary module-level code"
    )


def test_last_compiling_record_wins_without_execution(tmp_path):
    source = _write_jsonl(
        tmp_path / "ref.jsonl",
        [
            "def ok_early():\n    return 1\n",
            "raise RuntimeError('compiles but would explode at exec')\n",
        ],
    )
    task_dir = tmp_path / "qc-0002"
    task_dir.mkdir()

    correction = load_reference_correction(task_dir, dict(id="qc-0002"), source)

    assert correction is not None
    assert "RuntimeError" in correction, (
        "eligibility is compile-only: the LAST compilable record wins even "
        "though executing it would raise (runtime verification belongs to "
        "run_candidate_against_harness, not to the scan)"
    )


def test_task_reference_file_wins_over_distill_jsonl(tmp_path):
    source = _write_jsonl(tmp_path / "ref.jsonl", ["def distill_generic():\n    return 2\n"])
    task_dir = tmp_path / "quantum" / "some_task"
    task_dir.mkdir(parents=True)
    (task_dir / "candidate.py").write_text(
        "def task_specific_reference():\n    return 'the-task-own-reference'\n",
        encoding="utf-8",
    )

    correction = load_reference_correction(
        task_dir,
        dict(id="some_task", candidate_file="candidate.py"),
        source,
    )

    assert correction is not None
    assert "task_specific_reference" in correction, (
        "the task's OWN non-stub reference is the correction target; the "
        "generic last distill record must not shadow it"
    )


def test_stub_candidate_falls_through_to_distill_jsonl(tmp_path):
    source = _write_jsonl(tmp_path / "ref.jsonl", ["print('verified fallback')\n"])
    task_dir = tmp_path / "qc-0003"
    task_dir.mkdir()
    (task_dir / "solution.py").write_text("# training stub\n", encoding="utf-8")

    correction = load_reference_correction(
        task_dir,
        dict(id="qc-0003", candidate_file="solution.py"),
        source,
    )

    assert correction == "print('verified fallback')\n"


def test_preflight_on_real_tree_completes_in_seconds_not_hours():
    """End-to-end regression gate: the ASI3 launch preflight (v8 manifest,
    20 tasks, real 917-record jsonl) used to burn 75+ CPU-min per process.
    Bound it. Generous wall for host load; the fix makes it sub-5s."""
    started = time.monotonic()
    completed = subprocess.run(
        [
            sys.executable,
            str(PREFLIGHT),
            "--manifest",
            str(ROOT / "evals/benchmarks/quantum_grpo_training_v8_holdout_adjacent.txt"),
            "--tasks-dir",
            str(ROOT / "evals/tasks"),
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    elapsed = time.monotonic() - started

    assert completed.returncode == 0, completed.stderr[-2000:]
    assert (
        elapsed < 60
    ), f"repair-source preflight took {elapsed:.0f}s -- it is a LAUNCH GATE, it must verify by compiling, never by executing 917 records per task"
