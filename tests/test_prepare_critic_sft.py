"""Unit tests for scripts/prepare_critic_sft.py."""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "prepare_critic_sft.py"


def _run(tmp_path, extra=None):
    out = tmp_path / "out.jsonl"
    cmd = [
        sys.executable,
        str(SCRIPT),
        "--tasks-dir",
        str(REPO / "evals" / "tasks" / "quantum"),
        "--recs-dir",
        str(REPO / "evals" / "subsystem" / "recommendations"),
        "--rubric",
        str(REPO / "configs" / "rl" / "reward_rubric_v1.json"),
        "--output",
        str(out),
        "--check",
    ]
    if extra:
        cmd += extra
    r = subprocess.run(cmd, capture_output=True, text=True)
    assert r.returncode == 0, f"script failed: {r.stderr}"
    rows = [json.loads(line) for line in out.read_text().splitlines() if line.strip()]
    return rows


def test_emits_positive_and_negative_rows(tmp_path):
    rows = _run(tmp_path)
    labels = [r.get("label") for r in rows]
    assert "positive" in labels, "should have at least one positive row"
    assert "negative" in labels, "should have at least one negative row"


def test_every_row_has_critic_io_contract(tmp_path):
    rows = _run(tmp_path)
    for r in rows:
        msgs = r["messages"]
        # system, user, assistant
        assert len(msgs) == 3
        assert msgs[0]["role"] == "system"
        assert msgs[1]["role"] == "user"
        assert msgs[2]["role"] == "assistant"
        # Assistant content must be JSON with pass, scores, reasoning
        parsed = json.loads(msgs[2]["content"])
        assert "pass" in parsed and isinstance(parsed["pass"], bool)
        assert "scores" in parsed and isinstance(parsed["scores"], dict)
        assert (
            "reasoning" in parsed and isinstance(parsed["reasoning"], str) and parsed["reasoning"]
        )


def test_positive_rows_have_pass_true(tmp_path):
    rows = _run(tmp_path)
    for r in rows:
        if r.get("label") == "positive":
            parsed = json.loads(r["messages"][-1]["content"])
            assert parsed["pass"] is True
            # All scores should be 1.0 for the reference candidate
            for v in parsed["scores"].values():
                assert v == 1.0


def test_negative_rows_have_pass_false(tmp_path):
    rows = _run(tmp_path)
    for r in rows:
        if r.get("label") == "negative":
            parsed = json.loads(r["messages"][-1]["content"])
            assert parsed["pass"] is False
            # All scores should be 0.0 for a failing roll-out
            for v in parsed["scores"].values():
                assert v == 0.0


def test_pair_ids_stable(tmp_path):
    rows1 = _run(tmp_path)
    rows2 = _run(tmp_path)
    ids1 = [r["pair_id"] for r in rows1]
    ids2 = [r["pair_id"] for r in rows2]
    assert ids1 == ids2, "pair_ids must be deterministic"


def test_max_positives_limits_positive_count(tmp_path):
    rows = _run(tmp_path, ["--max-positives", "5"])
    n_pos = sum(1 for r in rows if r.get("label") == "positive")
    assert n_pos <= 5, f"max-positives=5 should limit positives to 5, got {n_pos}"
