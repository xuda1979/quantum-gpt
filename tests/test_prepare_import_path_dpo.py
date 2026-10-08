"""Unit tests for scripts/prepare_import_path_dpo.py (Track N3)."""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "prepare_import_path_dpo.py"


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
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, f"script failed: {r.stderr}"
    return out


def test_emits_pairs_with_valid_schema(tmp_path):
    out = _run(tmp_path)
    lines = [ln for ln in out.read_text().splitlines() if ln.strip()]
    assert len(lines) > 0, "expected at least one DPO pair (tasks with quantum imports exist)"
    for ln in lines:
        row = json.loads(ln)
        assert "prompt" in row and isinstance(row["prompt"], list)
        assert "chosen" in row and isinstance(row["chosen"], list)
        assert "rejected" in row and isinstance(row["rejected"], list)
        assert row["chosen"][: len(row["prompt"])] == row["prompt"]
        assert row["rejected"][: len(row["prompt"])] == row["prompt"]
        assert row["task_id"].startswith("quantum_")
        assert row["failure_category"] == "import_error"
        assert len(row["pair_id"]) == 16
        # The rejected side must contain a mutation marker comment
        rejected_text = row["rejected"][-1]["content"]
        assert (
            "ImportError" in rejected_text
            or "NameError" in rejected_text
            or "import removed" in rejected_text
        )


def test_rejected_differs_from_chosen(tmp_path):
    out = _run(tmp_path)
    for ln in out.read_text().splitlines():
        if not ln.strip():
            continue
        row = json.loads(ln)
        chosen_text = row["chosen"][-1]["content"]
        rejected_text = row["rejected"][-1]["content"]
        assert chosen_text != rejected_text, "rejected must differ from chosen"


def test_deterministic(tmp_path):
    out1 = _run(tmp_path)
    first = out1.read_text()
    out2 = _run(tmp_path / "second")
    assert out2.read_text() == first, "output must be deterministic across runs"


def test_empty_tasks_dir(tmp_path):
    fake = tmp_path / "fake_tasks"
    fake.mkdir()
    out = tmp_path / "out.jsonl"
    r = subprocess.run(
        [sys.executable, str(SCRIPT), "--tasks-dir", str(fake), "--output", str(out)],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0
    assert out.read_text().strip() == ""
