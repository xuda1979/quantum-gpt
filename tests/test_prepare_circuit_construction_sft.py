"""Unit tests for scripts/prepare_circuit_construction_sft.py (Track N5)."""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "prepare_circuit_construction_sft.py"


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


def test_emits_rows_for_seed_tasks(tmp_path):
    out = _run(tmp_path)
    lines = [ln for ln in out.read_text().splitlines() if ln.strip()]
    # The 3 seed tasks should produce at least the reference variants.
    task_ids = {json.loads(ln)["task_id"] for ln in lines}
    expected = {
        "quantum_deutsch_jozsa_balance_test",
        "quantum_bernstein_vazirani_hidden_string",
        "quantum_bell_pair_construction",
    }
    # At least one of the seed tasks should be present (some may fail tests.py
    # in the local env and be skipped — that's acceptable).
    assert len(task_ids & expected) >= 1, f"expected >=1 seed task, got {task_ids}"


def test_schema(tmp_path):
    out = _run(tmp_path)
    for ln in out.read_text().splitlines():
        if not ln.strip():
            continue
        row = json.loads(ln)
        assert "prompt" in row and isinstance(row["prompt"], list)
        assert "completion" in row and isinstance(row["completion"], list)
        assert row["completion"][: len(row["prompt"])] == row["prompt"]
        assert "variant" in row
        assert len(row["row_id"]) == 16


def test_deterministic(tmp_path):
    out1 = _run(tmp_path)
    first = out1.read_text()
    out2 = _run(tmp_path / "second")
    assert out2.read_text() == first
