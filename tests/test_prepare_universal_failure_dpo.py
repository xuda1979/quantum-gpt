"""Unit tests for scripts/prepare_universal_failure_dpo.py."""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "prepare_universal_failure_dpo.py"


def _run(tmp_path, extra=None):
    out = tmp_path / "out.jsonl"
    cmd = [
        sys.executable,
        str(SCRIPT),
        "--recs-dir",
        str(REPO / "evals" / "subsystem" / "recommendations"),
        "--tasks-dir",
        str(REPO / "evals" / "tasks" / "quantum"),
        "--output",
        str(out),
    ]
    if extra:
        cmd += extra
    r = subprocess.run(cmd, capture_output=True, text=True)
    assert r.returncode == 0, f"script failed: {r.stderr}"
    pairs = [json.loads(line) for line in out.read_text().splitlines() if line.strip()]
    return pairs


def test_emits_pairs_for_universal_tasks(tmp_path):
    pairs = _run(tmp_path)
    # There should be at least 1 universal task (per the cross-ref doc, 7)
    assert len(pairs) >= 1, f"expected >=1 universal pair, got {len(pairs)}"
    for p in pairs:
        assert "task_id" in p
        assert p["models_that_failed"]  # non-empty
        # chosen must have a python code block with the main guard. Some
        # legacy reference candidates use top-level-under-guard instead of
        # def main(); both are acceptable per docs/task-design-conventions.md
        # (older tasks predate the strict main() rule).
        chosen = p["chosen"][-1]["content"]
        assert "```python" in chosen
        assert 'if __name__ == "__main__":' in chosen


def test_rejected_exhibits_documented_failure(tmp_path):
    pairs = _run(tmp_path)
    for p in pairs:
        rejected = p["rejected"][-1]["content"]
        fc = p["failure_category"].lower()
        if "import" in fc:
            assert (
                "ImportError" in rejected or "wrong module" in rejected
            ), f"import-error rejected should mention ImportError: {rejected[:100]}"
        elif "prose" in fc:
            assert "```python" not in rejected, "prose-only rejected must not have a code block"
        # assertion failures: rejected has a code block but it prints a wrong trivial output


def test_pair_ids_stable(tmp_path):
    pairs1 = _run(tmp_path)
    pairs2 = _run(tmp_path)
    ids1 = [p["pair_id"] for p in pairs1]
    ids2 = [p["pair_id"] for p in pairs2]
    assert ids1 == ids2, "pair_ids must be deterministic across runs"


def test_skip_tasks_without_candidate(tmp_path, monkeypatch=None):
    # Use a fake tasks-dir with no matching folders -> all tasks skipped
    fake = tmp_path / "fake_tasks"
    fake.mkdir()
    out = tmp_path / "out.jsonl"
    r = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--recs-dir",
            str(REPO / "evals" / "subsystem" / "recommendations"),
            "--tasks-dir",
            str(fake),
            "--output",
            str(out),
        ],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0
    # Output file should be empty (all tasks skipped)
    assert out.read_text().strip() == ""


def test_check_runs_tests_py_against_chosen(tmp_path):
    """End-to-end: --check invokes each task's tests.py against the chosen
    candidate and confirms it passes (the reference candidate must pass).

    This is the corruption-proof guarantee from the N1 design doc: the
    chosen side is always execution-grounded, never model-judged.
    """
    out = tmp_path / "out.jsonl"
    r = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--recs-dir",
            str(REPO / "evals" / "subsystem" / "recommendations"),
            "--tasks-dir",
            str(REPO / "evals" / "tasks" / "quantum"),
            "--output",
            str(out),
            "--check",
        ],
        capture_output=True,
        text=True,
        cwd=REPO,
        timeout=180,
    )
    assert r.returncode == 0, r.stderr
    # --check prints "CHECK: N pass, 0 fail"
    assert "CHECK:" in r.stderr, r.stderr
    # Parse the pass/fail line
    import re

    m = re.search(r"CHECK:\s*(\d+)\s*pass,\s*(\d+)\s*fail", r.stderr)
    assert m, f"no CHECK line in stderr: {r.stderr}"
    n_pass, n_fail = int(m.group(1)), int(m.group(2))
    assert n_fail == 0, f"chosen candidate failed tests.py: {n_fail} failures"
    assert n_pass >= 1, "no pairs checked"
