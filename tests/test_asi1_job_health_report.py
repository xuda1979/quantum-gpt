from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "asi1_job_health_report.py"


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_sample_job_health_writes_expected_fields(tmp_path: Path) -> None:
    metric_path = tmp_path / "metrics.jsonl"
    log_path = tmp_path / "train.log"
    checkpoint_path = tmp_path / "checkpoint_state.json"
    output_path = tmp_path / "job_health.json"

    for path in (metric_path, log_path, checkpoint_path):
        path.write_text("ok\n", encoding="utf-8")

    now = time.time()
    os.utime(metric_path, (now - 30, now - 30))
    os.utime(log_path, (now - 45, now - 45))
    os.utime(checkpoint_path, (now - 60, now - 60))

    result = run_script(
        "sample",
        "--run-id",
        "asi1-smoke",
        "--pid",
        str(os.getpid()),
        "--metric-path",
        str(metric_path),
        "--log-path",
        str(log_path),
        "--checkpoint-path",
        str(checkpoint_path),
        "--disk-path",
        str(tmp_path),
        "--remote-path",
        "/workspace/quantum-gpt/outputs/asi1-smoke",
        "--output",
        str(output_path),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["run_id"] == "asi1-smoke"
    assert payload["pid_alive"] is True
    assert 0 <= payload["last_metric_age_sec"] < 120
    assert 0 <= payload["last_log_age_sec"] < 120
    assert 0 <= payload["checkpoint_age_sec"] < 120
    assert payload["disk_free"]["bytes"] > 0
    assert payload["remote_path"] == "/workspace/quantum-gpt/outputs/asi1-smoke"


def test_sample_job_health_can_use_artifact_overrides(tmp_path: Path) -> None:
    artifact = tmp_path / "remote_health.json"
    artifact.write_text(
        json.dumps(
            {
                "pid_alive": False,
                "last_metric_age_sec": 900,
                "last_log_age_sec": 901,
                "checkpoint_age_sec": None,
                "remote_path": "/workspace/remote/run",
            }
        ),
        encoding="utf-8",
    )

    result = run_script(
        "sample",
        "--run-id",
        "asi1-artifact",
        "--artifact",
        str(artifact),
        "--disk-path",
        str(tmp_path),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["pid_alive"] is False
    assert payload["last_metric_age_sec"] == 900
    assert payload["last_log_age_sec"] == 901
    assert payload["checkpoint_age_sec"] is None
    assert payload["remote_path"] == "/workspace/remote/run"
    assert payload["sources"]["artifact_path"] == str(artifact)


def test_failure_report_writer_and_validator(tmp_path: Path) -> None:
    log_path = tmp_path / "run.log"
    output_path = tmp_path / "failure_report.json"
    log_path.write_text("Traceback: context overflow\n", encoding="utf-8")

    result = run_script(
        "failure-report",
        "--run-id",
        "asi1-context-overflow",
        "--failure-kind",
        "context_overflow",
        "--message",
        "training exceeded the 1024-token context budget",
        "--log-path",
        str(log_path),
        "--disk-path",
        str(tmp_path),
        "--details-json",
        '{"max_context":1024}',
        "--output",
        str(output_path),
    )

    assert result.returncode == 0, result.stderr
    report = json.loads(output_path.read_text(encoding="utf-8"))
    assert report["status"] == "failed"
    assert report["failure_kind"] == "context_overflow"
    assert report["details"] == {"max_context": 1024}
    assert report["health"]["last_log_age_sec"] is not None

    validation = run_script("validate-failure-report", str(output_path))
    assert validation.returncode == 0, validation.stderr
    payload = json.loads(validation.stdout)
    assert payload["ok"] is True
    assert payload["errors"] == []


def test_failure_report_validator_rejects_missing_health_fields(tmp_path: Path) -> None:
    bad_report = tmp_path / "bad_failure_report.json"
    bad_report.write_text(
        json.dumps(
            {
                "timestamp_utc": "2026-05-26T00:00:00+00:00",
                "status": "failed",
                "run_id": "asi1-bad",
                "failure_kind": "missing_health",
                "message": "bad report",
                "health": {"run_id": "asi1-bad", "pid_alive": "maybe"},
            }
        ),
        encoding="utf-8",
    )

    validation = run_script("validate-failure-report", str(bad_report))
    assert validation.returncode == 1
    payload = json.loads(validation.stdout)
    assert payload["ok"] is False
    assert "health missing field: last_metric_age_sec" in payload["errors"]
    assert "health field pid_alive must be true, false, or null" in payload["errors"]
