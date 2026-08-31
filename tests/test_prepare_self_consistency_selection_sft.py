"""Unit tests for scripts/prepare_self_consistency_selection_sft.py (Track N9)."""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "prepare_self_consistency_selection_sft.py"


def _run(tmp_path, max_rows=5):
    out = tmp_path / "out.jsonl"
    r = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--tasks-dir",
            str(REPO / "evals" / "tasks" / "quantum"),
            "--output",
            str(out),
            "--max-rows",
            str(max_rows),
        ],
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert r.returncode == 0, f"script failed: {r.stderr}"
    return out


def test_schema(tmp_path):
    out = _run(tmp_path)
    lines = [ln for ln in out.read_text().splitlines() if ln.strip()]
    if len(lines) == 0:
        return
    for ln in lines:
        row = json.loads(ln)
        assert "prompt" in row and "completion" in row
        assert row["completion"][: len(row["prompt"])] == row["prompt"]
        assert "best_index" in row
        assert isinstance(row["best_index"], int)
        assert 0 <= row["best_index"] < row["n_candidates"]
        assert len(row["row_id"]) == 16


def test_completion_is_an_index(tmp_path):
    out = _run(tmp_path)
    for ln in out.read_text().splitlines():
        if not ln.strip():
            continue
        row = json.loads(ln)
        completion_text = row["completion"][-1]["content"]
        assert (
            completion_text.strip().isdigit()
        ), f"completion must be an index, got {completion_text!r}"


def test_deterministic(tmp_path):
    out1 = _run(tmp_path)
    first = out1.read_text()
    out2 = _run(tmp_path / "second")
    assert out2.read_text() == first
