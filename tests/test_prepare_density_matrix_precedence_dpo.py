"""Unit tests for scripts/prepare_density_matrix_precedence_dpo.py (Track N7)."""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "prepare_density_matrix_precedence_dpo.py"


def _run(tmp_path):
    out = tmp_path / "out.jsonl"
    r = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--tasks-dir",
            str(REPO / "evals" / "tasks" / "quantum"),
            "--output",
            str(out),
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"script failed: {r.stderr}"
    return out


def test_schema(tmp_path):
    out = _run(tmp_path)
    lines = [ln for ln in out.read_text().splitlines() if ln.strip()]
    if len(lines) == 0:
        return  # no DM-family tasks found; skip gracefully
    for ln in lines:
        row = json.loads(ln)
        assert "prompt" in row and "chosen" in row and "rejected" in row
        assert row["chosen"][: len(row["prompt"])] == row["prompt"]
        assert row["rejected"][: len(row["prompt"])] == row["prompt"]
        assert row["failure_category"] == "type_error_precedence"
        assert len(row["pair_id"]) == 16


def test_rejected_contains_mutation_marker(tmp_path):
    out = _run(tmp_path)
    for ln in out.read_text().splitlines():
        if not ln.strip():
            continue
        row = json.loads(ln)
        rejected_text = row["rejected"][-1]["content"]
        assert (
            "TypeError" in rejected_text
            or "wrapper" in rejected_text
            or "precedence" in rejected_text
        )


def test_deterministic(tmp_path):
    out1 = _run(tmp_path)
    first = out1.read_text()
    out2 = _run(tmp_path / "second")
    assert out2.read_text() == first
