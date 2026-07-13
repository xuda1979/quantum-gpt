"""Tests for scripts/analyze_grpo_metrics.py.

Verifies the analyzer:
- Emits a CSV with the dr_variance_correction column.
- Summarizes finite/bounded DR values correctly.
- Flags non-finite values.
- Reports the psi warmup schedule.
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "analyze_grpo_metrics.py"


def _write_jsonl(path: Path, records: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


def _run_analyzer(metrics_path: Path, out_prefix: Path) -> tuple[int, str, str]:
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--metrics",
            str(metrics_path),
            "--out-prefix",
            str(out_prefix),
        ],
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout, proc.stderr


def test_analyzer_emits_dr_variance_correction_column(tmp_path: Path) -> None:
    metrics = tmp_path / "grpo_step_metrics.jsonl"
    _write_jsonl(
        metrics,
        [
            {
                "step": 0,
                "task": "qaoa_maxcut",
                "domain": "quantum",
                "mean_reward": 0.4,
                "pass_rate": 0.5,
                "dr_psi": 0.0,
                "dr_psi_init": 0.5,
                "dr_psi_warmup_steps": 10,
                "dr_psi_current_step": 0,
                "dr_variance_correction_value": 0.0,
            },
            {
                "step": 5,
                "task": "qaoa_maxcut",
                "domain": "quantum",
                "mean_reward": 0.6,
                "pass_rate": 0.7,
                "dr_psi": 0.25,
                "dr_psi_init": 0.5,
                "dr_psi_warmup_steps": 10,
                "dr_psi_current_step": 5,
                "dr_variance_correction_value": 0.0123,
            },
            {
                "step": 10,
                "task": "qaoa_maxcut",
                "domain": "quantum",
                "mean_reward": 0.8,
                "pass_rate": 0.9,
                "dr_psi": 0.5,
                "dr_psi_init": 0.5,
                "dr_psi_warmup_steps": 10,
                "dr_psi_current_step": 10,
                "dr_variance_correction_value": -0.0045,
            },
        ],
    )
    out_prefix = tmp_path / "analysis"
    rc, stdout, stderr = _run_analyzer(metrics, out_prefix)
    assert rc == 0, f"analyzer failed: {stderr}\nstdout: {stdout}"

    csv_path = out_prefix.with_suffix(".csv")
    summary_path = out_prefix.with_suffix(".summary.json")
    assert csv_path.is_file()
    assert summary_path.is_file()

    # CSV has the dr_variance_correction_value column.
    with csv_path.open() as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert "dr_variance_correction_value" in rows[0]
    assert "dr_psi" in rows[0]
    assert "dr_psi_init" in rows[0]
    assert "dr_psi_warmup_steps" in rows[0]
    assert len(rows) == 3
    assert float(rows[0]["dr_psi"]) == 0.0
    assert abs(float(rows[1]["dr_psi"]) - 0.25) < 1e-9
    assert abs(float(rows[2]["dr_psi"]) - 0.5) < 1e-9

    # Summary reports the DR schedule and bounded/finite status.
    summary = json.loads(summary_path.read_text())
    dr = summary["dr_summary"]["dr_variance_correction"]
    assert dr["finite"] is True
    assert dr["bounded"] is True
    assert dr["steps_with_value"] == 3
    psi = summary["dr_summary"]["dr_psi"]
    assert abs(psi["psi_init"] - 0.5) < 1e-9
    assert psi["warmup_steps"] == 10
    assert psi["min"] == 0.0
    assert abs(psi["max"] - 0.5) < 1e-9


def test_analyzer_flags_non_finite_values(tmp_path: Path) -> None:
    metrics = tmp_path / "grpo_step_metrics.jsonl"
    _write_jsonl(
        metrics,
        [
            {
                "step": 0,
                "task": "qaoa_maxcut",
                "dr_psi": 0.5,
                "dr_variance_correction_value": 0.01,
            },
            {
                "step": 1,
                "task": "qaoa_maxcut",
                "dr_psi": 0.5,
                "dr_variance_correction_value": float("inf"),
            },
        ],
    )
    out_prefix = tmp_path / "analysis"
    rc, stdout, _ = _run_analyzer(metrics, out_prefix)
    assert rc == 0
    summary = json.loads(out_prefix.with_suffix(".summary.json").read_text())
    dr = summary["dr_summary"]["dr_variance_correction"]
    assert dr["finite"] is False
    # The non-finite value should not be in the bounded/finite stats.
    assert dr["steps_with_value"] == 1  # only the finite one counted
    # The CLI verdict line should mention non-finite.
    assert "NON-FINITE" in stdout


def test_analyzer_handles_empty_metrics_file(tmp_path: Path) -> None:
    metrics = tmp_path / "empty.jsonl"
    metrics.write_text("")
    out_prefix = tmp_path / "analysis"
    rc, _, stderr = _run_analyzer(metrics, out_prefix)
    assert rc != 0
    assert "no records" in stderr


def test_analyzer_handles_missing_metrics_file(tmp_path: Path) -> None:
    metrics = tmp_path / "nonexistent.jsonl"
    out_prefix = tmp_path / "analysis"
    rc, _, stderr = _run_analyzer(metrics, out_prefix)
    assert rc != 0
    assert "not found" in stderr
