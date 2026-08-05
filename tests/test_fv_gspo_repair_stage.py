"""Tests for scripts/fv_gspo_repair_stage.py.

Verifies the repair lane end-to-end: queue record (failing candidate + exact
failures) -> verified correction via the task's reference candidate.py ->
repair_converted.jsonl (readable by the trainer's circuit breaker) plus
repair_sft.jsonl / repair_dpo.jsonl in the repository pair schema.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from training.grpo_utils import count_repair_conversions

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "fv_gspo_repair_stage.py"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _make_task(tmp_path: Path, *, reference_ok: bool = True) -> Path:
    task_dir = tmp_path / "evals" / "tasks" / "quantum" / "synthetic_repair_task"
    reference = (
        "def f():\n    return 42\n"
        if reference_ok
        else "def f():\n    return 0\n"  # verified reference that FAILS the harness
    )
    _write(
        task_dir / "candidate.py",
        reference,
    )
    _write(
        task_dir / "task.json",
        json.dumps(
            {
                "id": "quantum_synthetic_repair_task",
                "name": "Synthetic repair task",
                "domain": "quantum",
                "category": "synthetic",
                "candidate_file": "candidate.py",
                "description": "Return the integer 42 from f().",
            }
        ),
    )
    _write(
        task_dir / "tests.py",
        """import importlib.util


def _load(candidate_path):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    if module.f() == 42:
        return {"passed": True, "details": []}
    return {"passed": False, "details": ["AssertionError: f() != 42"]}
""",
    )
    return task_dir


def _write_queue(queue_path: Path, records: list[dict]) -> None:
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    with queue_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")


def _run_stage(tmp_path: Path, queue: Path) -> dict:
    out = tmp_path / "repair_stage"
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--queue",
            str(queue),
            "--tasks-dir",
            str(tmp_path / "evals" / "tasks"),
            "--output",
            str(out),
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


def test_repair_stage_converts_via_reference_and_emits_sft_dpo(tmp_path: Path) -> None:
    _make_task(tmp_path)
    queue = tmp_path / "run" / "repair_queue.jsonl"
    _write_queue(
        queue,
        [
            {
                "timestamp_utc": "2026-08-05T00:00:00Z",
                "step": 7,
                "task_id": "quantum_synthetic_repair_task",
                "domain": "quantum",
                "category": "synthetic",
                "best_code": "def f():\n    return 0",
                "failures": ["AssertionError: f() != 42"],
                "pass_rate": 0.0,
                "verifier_rate": 0.0,
            }
        ],
    )
    report = _run_stage(tmp_path, queue)
    assert report["converted"] == 1
    assert report["rejected"] == 0

    out = tmp_path / "repair_stage"
    converted = out / "repair_converted.jsonl"
    assert count_repair_conversions(converted) == 1
    record = json.loads(converted.read_text(encoding="utf-8").splitlines()[0])
    assert record["converted"] is True
    assert record["corrected_by"] == "reference"
    assert record["task_id"] == "quantum_synthetic_repair_task"

    sft_records = [
        json.loads(line)
        for line in (out / "repair_sft.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert len(sft_records) == 1
    assert sft_records[0]["chosen"][0]["content"].strip() == "def f():\n    return 42"
    assert sft_records[0]["failure_category"] == "assertion_failure"
    assert "EXACT TEST FAILURES" in sft_records[0]["prompt"][1]["content"]
    assert "def f():\n    return 0" in sft_records[0]["prompt"][1]["content"]

    dpo_records = [
        json.loads(line)
        for line in (out / "repair_dpo.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert len(dpo_records) == 1
    assert dpo_records[0]["rejected"][0]["content"].strip() == "def f():\n    return 0"


def test_repair_stage_rejects_unverified_correction(tmp_path: Path) -> None:
    # Reference candidate itself fails the harness -> the "correction" must be
    # rejected and recorded as unconverted (feeds the repair-conversion breaker).
    _make_task(tmp_path, reference_ok=False)
    queue = tmp_path / "run" / "repair_queue.jsonl"
    _write_queue(
        queue,
        [
            {
                "step": 3,
                "task_id": "quantum_synthetic_repair_task",
                "domain": "quantum",
                "best_code": "def f():\n    return 0",
                "failures": ["AssertionError: f() != 42"],
                "pass_rate": 0.0,
            }
        ],
    )
    report = _run_stage(tmp_path, queue)
    assert report["converted"] == 0
    assert report["rejected"] == 1
    converted = tmp_path / "repair_stage" / "repair_converted.jsonl"
    assert count_repair_conversions(converted) == 0
    record = json.loads(converted.read_text(encoding="utf-8").splitlines()[0])
    assert record["converted"] is False


def test_repair_stage_dedupes_converted_records(tmp_path: Path) -> None:
    _make_task(tmp_path)
    queue = tmp_path / "run" / "repair_queue.jsonl"
    record = {
        "step": 5,
        "task_id": "quantum_synthetic_repair_task",
        "domain": "quantum",
        "best_code": "def f():\n    return 0",
        "failures": ["AssertionError: f() != 42"],
        "pass_rate": 0.0,
        "dedup_key": "quantum_synthetic_repair_task:abc123",
    }
    _write_queue(queue, [record, record])
    report = _run_stage(tmp_path, queue)
    # Second identical record is skipped via the dedup_key.
    assert report["converted"] == 1
    converted = tmp_path / "repair_stage" / "repair_converted.jsonl"
    assert len(converted.read_text(encoding="utf-8").splitlines()) == 1
    assert count_repair_conversions(converted) == 1
