"""Unit tests for scripts/prepare_traceback_repair_dpo.py (Track N10)."""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "prepare_traceback_repair_dpo.py"


def _run(tmp_path, max_rows=10):
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
        assert "prompt" in row and "chosen" in row and "rejected" in row
        assert row["chosen"][: len(row["prompt"])] == row["prompt"]
        assert row["rejected"][: len(row["prompt"])] == row["prompt"]
        assert row["failure_category"] == "traceback_repair"
        assert "traceback_tail" in row
        assert len(row["pair_id"]) == 16


def test_prompt_contains_traceback(tmp_path):
    out = _run(tmp_path)
    for ln in out.read_text().splitlines():
        if not ln.strip():
            continue
        row = json.loads(ln)
        user_msg = row["prompt"][-1]["content"]
        assert "Traceback" in user_msg or "Error" in user_msg


def test_chosen_differs_from_rejected(tmp_path):
    out = _run(tmp_path)
    for ln in out.read_text().splitlines():
        if not ln.strip():
            continue
        row = json.loads(ln)
        assert row["chosen"][-1]["content"] != row["rejected"][-1]["content"]


def test_deterministic(tmp_path):
    out1 = _run(tmp_path)
    first = out1.read_text()
    out2 = _run(tmp_path / "second")
    assert out2.read_text() == first
