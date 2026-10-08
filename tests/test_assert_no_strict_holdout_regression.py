from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_gate(path: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "assert_no_strict_holdout_regression.py"),
            "--comparison",
            str(path),
            *extra_args,
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_gate_passes_on_non_regression_current_schema(tmp_path: Path) -> None:
    comparison = tmp_path / "comparison.json"
    comparison.write_text(
        json.dumps(
            {
                "kind": "strict_override_comparison",
                "baseline": {"label": "base"},
                "candidate": {"label": "adapter"},
                "strict_override": {
                    "base_passes": 0,
                    "base_total": 4,
                    "adapter_passes": 1,
                    "adapter_total": 4,
                    "adapter_minus_base_passes": 1,
                },
                "full_scorecard": {
                    "base_passes": 22,
                    "base_total": 26,
                    "candidate_passes": 23,
                    "candidate_total": 26,
                    "candidate_minus_base_passes": 1,
                },
            }
        ),
        encoding="utf-8",
    )

    result = run_gate(comparison)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["strict_delta_passes"] == 1


def test_gate_fails_on_regression_current_schema(tmp_path: Path) -> None:
    comparison = tmp_path / "comparison.json"
    comparison.write_text(
        json.dumps(
            {
                "kind": "strict_override_comparison",
                "baseline": {"label": "base"},
                "candidate": {"label": "adapter"},
                "strict_override": {
                    "base_passes": 3,
                    "base_total": 4,
                    "adapter_passes": 2,
                    "adapter_total": 4,
                    "adapter_minus_base_passes": -1,
                },
                "full_scorecard": {
                    "base_passes": 25,
                    "base_total": 26,
                    "candidate_passes": 25,
                    "candidate_total": 26,
                    "candidate_minus_base_passes": 0,
                },
            }
        ),
        encoding="utf-8",
    )

    result = run_gate(comparison)
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["strict_delta_passes"] == -1
    assert "strict delta -1 < required 0" in payload["failures"]


def test_gate_supports_legacy_schema(tmp_path: Path) -> None:
    comparison = tmp_path / "legacy.json"
    comparison.write_text(
        json.dumps(
            {
                "strict_override": {
                    "base_passes": 3,
                    "base_total": 4,
                    "adapter_passes": 2,
                    "adapter_total": 4,
                    "adapter_minus_base_passes": -1,
                }
            }
        ),
        encoding="utf-8",
    )

    result = run_gate(comparison)
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["schema"] == "legacy_strict_override"
    assert payload["full_delta_passes"] is None


def test_gate_can_require_non_negative_full_delta(tmp_path: Path) -> None:
    comparison = tmp_path / "comparison.json"
    comparison.write_text(
        json.dumps(
            {
                "kind": "strict_override_comparison",
                "baseline": {"label": "base"},
                "candidate": {"label": "adapter"},
                "strict_override": {
                    "base_passes": 0,
                    "base_total": 4,
                    "adapter_passes": 0,
                    "adapter_total": 4,
                    "adapter_minus_base_passes": 0,
                },
                "full_scorecard": {
                    "base_passes": 25,
                    "base_total": 26,
                    "candidate_passes": 24,
                    "candidate_total": 26,
                    "candidate_minus_base_passes": -1,
                },
            }
        ),
        encoding="utf-8",
    )

    result = run_gate(comparison, "--min-full-delta-passes", "0")
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert "full delta -1 < required 0" in payload["failures"]
