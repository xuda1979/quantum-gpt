"""Tests for scripts/prepare_iter3_distill_sft.py build subcommand.

Verifies:
- Dry-run accounting is correct
- Gap-targeted row stubs are well-formed
- Carry-forward from iter-2 works
- Manifest structure validation
- __TEACHER_PENDING__ markers present in gap rows
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "prepare_iter3_distill_sft.py"


def _run_build(
    tmp_path: Path, dry_run: bool = True, iter2_train: Path | None = None
) -> tuple[int, str, str]:
    """Run the build subcommand with minimal args."""
    if iter2_train is None:
        # Create a minimal iter-2 train file
        iter2_train = tmp_path / "iter2_train.jsonl"
        iter2_train.write_text(
            json.dumps(
                {
                    "example_id": "iter2_test_01",
                    "format": "chat-sft-v1",
                    "messages": [
                        {"role": "system", "content": "sys"},
                        {"role": "user", "content": "usr"},
                        {"role": "assistant", "content": "asst"},
                    ],
                    "metadata": {"domain": "quantum", "framework": "qiskit"},
                    "source_schema": "dataset-v0",
                }
            )
            + "\n"
        )
    iter2_eval = tmp_path / "iter2_eval.jsonl"
    iter2_eval.write_text(
        json.dumps(
            {
                "example_id": "iter2_eval_01",
                "format": "chat-sft-v1",
                "messages": [
                    {"role": "system", "content": "sys"},
                    {"role": "user", "content": "usr"},
                    {"role": "assistant", "content": "asst"},
                ],
                "metadata": {"domain": "quantum", "framework": "qiskit"},
                "source_schema": "dataset-v0",
            }
        )
        + "\n"
    )
    gap_report = tmp_path / "gap_report.md"
    gap_report.write_text("# Gap report\n")
    out_dir = tmp_path / "iter3_out"

    cmd = [
        sys.executable,
        str(SCRIPT),
        "build",
        "--gap-report",
        str(gap_report),
        "--iter2-train",
        str(iter2_train),
        "--iter2-eval",
        str(iter2_eval),
        "--out",
        str(out_dir),
    ]
    if dry_run:
        cmd.append("--dry-run")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def test_build_dry_run_accounting(tmp_path: Path) -> None:
    """Dry-run should report carry-forward + gap row counts without writing files."""
    rc, out, err = _run_build(tmp_path, dry_run=True)
    assert rc == 0, f"rc={rc} err={err}"
    assert "carry-forward rows from iter-2: 1" in out
    assert "gap-targeted stub rows: 48" in out
    assert "no files written" in out
    # Ensure no files were written
    assert not (tmp_path / "iter3_out").exists()


def test_build_dry_run_with_real_iter2(tmp_path: Path) -> None:
    """Dry-run against the real iter-2 data should report 142 carry-forward rows."""
    iter2_train = ROOT / "data/generated/glm52_soft_distill_sft_iter2/train_chatml.jsonl"
    iter2_eval = ROOT / "data/generated/glm52_soft_distill_sft_iter2/eval_chatml.jsonl"
    if not iter2_train.exists() or not iter2_eval.exists():
        return  # skip if iter-2 data not present
    rc, out, err = _run_build(tmp_path, dry_run=True, iter2_train=iter2_train)
    # Need to also override eval
    gap_report = tmp_path / "gap_report.md"
    gap_report.write_text("# Gap report\n")
    out_dir = tmp_path / "iter3_out"
    cmd = [
        sys.executable,
        str(SCRIPT),
        "build",
        "--gap-report",
        str(gap_report),
        "--iter2-train",
        str(iter2_train),
        "--iter2-eval",
        str(iter2_eval),
        "--out",
        str(out_dir),
        "--dry-run",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert "carry-forward rows from iter-2: 142" in proc.stdout
    assert "gap-targeted stub rows: 48" in proc.stdout
    assert "target train rows: 181" in proc.stdout


def test_gap_row_structure() -> None:
    """Gap-targeted row stubs should have correct structure and __TEACHER_PENDING__ marker."""
    sys.path.insert(0, str(ROOT))
    from scripts.prepare_iter3_distill_sft import _GAP_TASK_FAMILIES, TEACHER_PENDING, _make_gap_row

    rows = _make_gap_row(_GAP_TASK_FAMILIES[0], examples_per_family=3)
    assert len(rows) == 3
    for i, r in enumerate(rows, 1):
        assert r["example_id"].startswith("iter3_gap_")
        assert r["format"] == "chat-sft-v1"
        assert len(r["messages"]) == 3
        assert r["messages"][0]["role"] == "system"
        assert r["messages"][1]["role"] == "user"
        assert r["messages"][2]["role"] == "assistant"
        assert r["messages"][2]["content"] == TEACHER_PENDING
        assert r["metadata"]["teacher_status"] == "pending"
        assert r["metadata"]["distillation_phase"] == "iter3"
        assert r["metadata"]["evolution_kind"] == "gap_targeted"
        assert "task_id" in r["metadata"]
        assert "gap_row_id" in r["metadata"]


def test_all_16_families_have_prompts() -> None:
    """All 16 task families should have non-empty prompts and valid metadata."""
    sys.path.insert(0, str(ROOT))
    from scripts.prepare_iter3_distill_sft import _GAP_TASK_FAMILIES

    assert len(_GAP_TASK_FAMILIES) == 16
    for fam in _GAP_TASK_FAMILIES:
        assert fam["prompt"], f"Empty prompt for {fam['row']}"
        assert fam["task_id"], f"Empty task_id for {fam['row']}"
        assert fam["domain"] in ("quantum", "software"), f"Bad domain for {fam['row']}"
        assert fam["framework"] in (
            "qiskit",
            "cirq",
            "pennylane",
            "braket",
            "none",
        ), f"Bad framework for {fam['row']}"
        assert fam["category"], f"Empty category for {fam['row']}"


def test_manifest_check_passes_on_stub() -> None:
    """The manifest stub should pass validation."""
    manifest = ROOT / "data/generated/glm52_soft_distill_sft_iter3/manifest.json"
    if not manifest.exists():
        return
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "check", "--manifest", str(manifest)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert "PASS" in proc.stdout


def test_build_refuses_without_iter2_eval_marker(tmp_path: Path) -> None:
    """Real build (no --dry-run) should refuse without the iter-2 eval marker file."""
    rc, out, err = _run_build(tmp_path, dry_run=False)
    # Should refuse with rc=2
    assert rc == 2, f"expected rc=2, got rc={rc} out={out} err={err}"
    assert "REFUSED" in err
