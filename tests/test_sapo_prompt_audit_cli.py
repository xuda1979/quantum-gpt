"""Coverage backlog (2026-08-26): sapo_prompt_audit.py CLI mains (smoke).

The prompt-integrity audit's CLI: manifest/holdout hash contracts, overlap
detection, the JSON report file, and the pass/fail exit codes the monitoring
fleet watches. Uses the same synthetic task fixtures as the audit's own
regression suite.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

from tests.test_sapo_prompt_audit import (  # noqa: E402
    SYNTH_CANDIDATE_PY,
    SYNTH_TASK_JSON,
    SYNTH_TESTS_PY,
)


@pytest.fixture()
def audit_fixture(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    """(manifest, holdout, tasks_dir, metrics) for a clean audit."""
    tasks_dir = tmp_path / "evals" / "tasks" / "quantum"
    task_dir = tasks_dir / "quantum_fake_synth"
    task_dir.mkdir(parents=True)
    (task_dir / "task.json").write_text(json.dumps(SYNTH_TASK_JSON), encoding="utf-8")
    (task_dir / "candidate.py").write_text(SYNTH_CANDIDATE_PY, encoding="utf-8")
    (task_dir / "tests.py").write_text(SYNTH_TESTS_PY, encoding="utf-8")
    manifest = tmp_path / "manifest.txt"
    manifest.write_text("quantum_fake_synth\n", encoding="utf-8")
    holdout = tmp_path / "holdout.txt"
    holdout.write_text("quantum_fake_holdout_alpha\nquantum_fake_holdout_beta\n", encoding="utf-8")
    metrics = tmp_path / "grpo_step_metrics.jsonl"
    metrics.write_text('{"step": 1, "task": "quantum_fake_synth"}\n', encoding="utf-8")
    # the tasks ROOT is evals/tasks (domain dirs directly underneath)
    return manifest, holdout, tasks_dir.parent, metrics


def test_prompt_audit_module_has_future_annotations() -> None:
    """r10 depmatrix F2: PEP 604 annotations require the future import for
    py3.9-safe imports."""
    import sapo_prompt_audit as spa_mod

    source = Path(spa_mod.__file__).read_text(encoding="utf-8")
    assert "from __future__ import annotations" in source


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / "sapo_prompt_audit.py"), *args],
        capture_output=True,
        text=True,
        timeout=120,
    )


def test_cli_clean_audit_passes(audit_fixture) -> None:
    manifest, holdout, tasks_dir, metrics = audit_fixture
    expected_manifest = hashlib.sha256(manifest.read_bytes()).hexdigest()
    expected_holdout = hashlib.sha256(holdout.read_bytes()).hexdigest()
    json_out = manifest.parent / "report.json"
    proc = _run_cli(
        "--manifest",
        str(manifest),
        "--holdout",
        str(holdout),
        "--tasks-dir",
        str(tasks_dir),
        "--metrics",
        str(metrics),
        "--expected-manifest-sha256",
        expected_manifest,
        "--expected-holdout-sha256",
        expected_holdout,
        "--json-out",
        str(json_out),
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "RESULT PASS" in proc.stdout
    report = json.loads(json_out.read_text())
    assert report["ok"] is True
    assert report["violations"] == []


def test_cli_manifest_hash_mismatch_fails(audit_fixture) -> None:
    manifest, holdout, tasks_dir, metrics = audit_fixture
    proc = _run_cli(
        "--manifest",
        str(manifest),
        "--holdout",
        str(holdout),
        "--tasks-dir",
        str(tasks_dir),
        "--metrics",
        str(metrics),
        "--expected-manifest-sha256",
        "0" * 64,
    )
    assert proc.returncode == 1
    assert "VIOLATION [manifest_hash]" in proc.stdout
    assert "RESULT FAIL (1 violations)" in proc.stdout


def test_cli_holdout_overlap_fails(audit_fixture) -> None:
    manifest, holdout, tasks_dir, metrics = audit_fixture
    # poison the manifest with a holdout id
    manifest.write_text("quantum_fake_synth\nquantum_fake_holdout_alpha\n", encoding="utf-8")
    proc = _run_cli(
        "--manifest",
        str(manifest),
        "--holdout",
        str(holdout),
        "--tasks-dir",
        str(tasks_dir),
        "--metrics",
        str(metrics),
    )
    assert proc.returncode == 1
    assert "VIOLATION [manifest_holdout_overlap]" in proc.stdout
    assert "quantum_fake_holdout_alpha" in proc.stdout


def test_cli_json_report_written_on_failure(audit_fixture) -> None:
    manifest, holdout, tasks_dir, metrics = audit_fixture
    manifest.write_text("quantum_fake_synth\nquantum_fake_holdout_alpha\n", encoding="utf-8")
    json_out = manifest.parent / "fail.json"
    proc = _run_cli(
        "--manifest",
        str(manifest),
        "--holdout",
        str(holdout),
        "--tasks-dir",
        str(tasks_dir),
        "--metrics",
        str(metrics),
        "--json-out",
        str(json_out),
    )
    assert proc.returncode == 1
    report = json.loads(json_out.read_text())
    assert report["ok"] is False
    assert any(v["kind"] == "manifest_holdout_overlap" for v in report["violations"])
