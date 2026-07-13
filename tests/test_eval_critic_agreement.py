"""Unit test for scripts/eval_critic_agreement.py.

Validates the split is task-disjoint and stratified, and that the mock
critic (returns the row's own label) achieves 100% agreement — a
self-test of the harness plumbing.
"""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts/eval_critic_agreement.py"
ROWS = REPO / "data/generated/rd_lines_2026_07_13/n2_critic_sft_rows.jsonl"


def _run(*args: str) -> tuple[int, str, str]:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    return proc.returncode, proc.stdout, proc.stderr


def test_split_is_task_disjoint_and_stratified(tmp_path):
    out = tmp_path / "split.json"
    rc, so, se = _run("--split-only", "--split-out", str(out))
    assert rc == 0, se
    data = json.loads(out.read_text())
    train_ids = {r["task_id"] for r in data["train_rows"]}
    eval_ids = {r["task_id"] for r in data["eval_rows"]}
    # Task-disjoint
    assert train_ids.isdisjoint(eval_ids), "task leaked into both splits"
    # Stratified: eval set must contain at least 1 negative
    eval_neg = [r for r in data["eval_rows"] if r["label"] == "negative"]
    assert len(eval_neg) >= 1, "eval split has no negatives"
    # Eval frac ~ 0.2
    total = len(data["train_rows"]) + len(data["eval_rows"])
    assert 0.15 <= len(data["eval_rows"]) / total <= 0.30


def test_mock_critic_100pct_agreement(tmp_path):
    out = tmp_path / "split.json"
    rc, so, se = _run("--mock-critic", "--split-out", str(out))
    # Mock critic returns the row's own label → 100% agreement → rc 0
    assert rc == 0, se
    assert "agreement = 100.00%" in so, so


def test_split_reproducible(tmp_path):
    out1 = tmp_path / "s1.json"
    out2 = tmp_path / "s2.json"
    _run("--split-only", "--split-out", str(out1))
    _run("--split-only", "--split-out", str(out2))
    assert out1.read_text() == out2.read_text(), "split not reproducible"


def test_rows_file_exists():
    assert ROWS.exists(), f"missing {ROWS} — run scripts/prepare_critic_sft.py first"
