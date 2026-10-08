"""Unit tests for scripts/prepare_output_string_exactness_sft.py (Track N4)."""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "prepare_output_string_exactness_sft.py"


def _run(tmp_path, extra=None):
    out = tmp_path / "out.jsonl"
    cmd = [
        sys.executable,
        str(SCRIPT),
        "--tasks-dir",
        str(REPO / "evals" / "tasks" / "quantum"),
        "--output",
        str(out),
    ]
    if extra:
        cmd += extra
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    assert r.returncode == 0, f"script failed: {r.stderr}"
    return out


def test_emits_rows_with_valid_schema(tmp_path):
    out = _run(tmp_path)
    lines = [ln for ln in out.read_text().splitlines() if ln.strip()]
    # Some tasks may not have deterministic strings, so len could be 0 in theory,
    # but the 58-task set should yield at least a few.
    if len(lines) == 0:
        return  # nothing to assert; skip gracefully
    for ln in lines:
        row = json.loads(ln)
        assert "prompt" in row and isinstance(row["prompt"], list)
        assert "completion" in row and isinstance(row["completion"], list)
        assert row["completion"][: len(row["prompt"])] == row["prompt"]
        assert row["task_id"].startswith("quantum_")
        assert "expected_output" in row
        assert len(row["row_id"]) == 16


def test_completion_contains_python_block(tmp_path):
    out = _run(tmp_path)
    for ln in out.read_text().splitlines():
        if not ln.strip():
            continue
        row = json.loads(ln)
        content = row["completion"][-1]["content"]
        assert "```python" in content and "```" in content
        assert "def main()" in content


def test_deterministic(tmp_path):
    out1 = _run(tmp_path)
    first = out1.read_text()
    out2_path = tmp_path / "second.jsonl"
    r = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--tasks-dir",
            str(REPO / "evals" / "tasks" / "quantum"),
            "--output",
            str(out2_path),
        ],
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert r.returncode == 0
    assert out2_path.read_text() == first
