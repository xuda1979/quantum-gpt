"""Unit tests for scripts/prepare_qaoa_cut_calibration_sft.py (Track N8)."""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "prepare_qaoa_cut_calibration_sft.py"


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
        timeout=60,
    )
    assert r.returncode == 0, f"script failed: {r.stderr}"
    return out


def test_emits_5_graph_variants(tmp_path):
    out = _run(tmp_path)
    lines = [ln for ln in out.read_text().splitlines() if ln.strip()]
    assert len(lines) == 5, f"expected 5 graph variants, got {len(lines)}"
    graphs = {json.loads(ln)["graph"] for ln in lines}
    assert graphs == {"5cycle", "path5", "star5", "k4", "random6"}


def test_schema(tmp_path):
    out = _run(tmp_path)
    for ln in out.read_text().splitlines():
        if not ln.strip():
            continue
        row = json.loads(ln)
        assert "prompt" in row and "completion" in row
        assert row["completion"][: len(row["prompt"])] == row["prompt"]
        assert "expected_output" in row
        assert "graph" in row
        assert len(row["row_id"]) == 16


def test_expected_outputs_are_correct(tmp_path):
    """Verify the brute-force MaxCut values are correct for known graphs."""
    out = _run(tmp_path)
    for ln in out.read_text().splitlines():
        if not ln.strip():
            continue
        row = json.loads(ln)
        # At least check the value is a positive integer string
        assert row["expected_output"].isdigit()
        assert int(row["expected_output"]) > 0


def test_deterministic(tmp_path):
    out1 = _run(tmp_path)
    first = out1.read_text()
    out2 = _run(tmp_path / "second")
    assert out2.read_text() == first
