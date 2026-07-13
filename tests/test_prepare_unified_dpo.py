"""Unit test for scripts/prepare_unified_dpo.py — the merged DPO pipeline.

Validates that the unified dataset:
  1. Contains pairs from all 5 source lines (N1,N3,N6,N7,N10).
  2. Tags every row with `source_line` and `negative_type`.
  3. Has valid ChatML structure (chosen/rejected are message lists).
  4. Covers all 7 negative types from the merged taxonomy.
"""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "prepare_unified_dpo.py"
OUT = REPO / "data/generated/rd_lines_2026_07_13/unified_dpo_pairs.jsonl"


def test_unified_dpo_exists_and_valid():
    """The unified DPO dataset has been generated and is structurally valid."""
    assert OUT.exists(), f"missing {OUT} — run scripts/prepare_unified_dpo.py"
    rows = [json.loads(line) for line in OUT.read_text().splitlines() if line.strip()]
    assert len(rows) >= 300, f"expected >=300 pairs, got {len(rows)}"

    # Every row has the required unified fields
    required = {"prompt", "chosen", "rejected", "source_line", "negative_type", "pair_id"}
    for r in rows:
        assert required.issubset(r.keys()), f"row missing fields: {required - set(r.keys())}"
        assert isinstance(r["chosen"], list), "chosen not a message list"
        assert isinstance(r["rejected"], list), "rejected not a message list"

    # All 5 source lines are represented
    lines_present = {r["source_line"] for r in rows}
    assert lines_present == {
        "N1",
        "N3",
        "N6",
        "N7",
        "N10",
    }, f"missing lines: { {'N1','N3','N6','N7','N10'} - lines_present }"

    # All 7 negative types are represented
    neg_types = {r["negative_type"] for r in rows}
    expected_neg = {
        "assertion",
        "import_error",
        "prose_only",
        "no_main",
        "no_guard",
        "type_error_precedence",
        "traceback_repair",
    }
    assert neg_types == expected_neg, f"neg type mismatch: {expected_neg ^ neg_types}"


def test_unified_dpo_smoke_subset(tmp_path):
    """Running the script with --lines N3,N7 produces a valid subset."""
    out = tmp_path / "subset.jsonl"
    r = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--lines",
            "N3,N7",
            "--output",
            str(out),
            "--workdir",
            str(tmp_path / "work"),
        ],
        capture_output=True,
        text=True,
        cwd=REPO,
        timeout=120,
    )
    assert r.returncode == 0, r.stderr
    rows = [json.loads(line) for line in out.read_text().splitlines() if line.strip()]
    assert len(rows) >= 1
    assert {r["source_line"] for r in rows} == {"N3", "N7"}
