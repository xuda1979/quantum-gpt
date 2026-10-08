"""C-0034 (2026-09-16): None-candidate TypeError crash-containment.

C-0005's replay of the real superdense candidate measured a residual
post-import TypeError (candidate callable returning None) as a failure
class DISTINCT from markdown fences. Today ``run_harness`` lets such an
exception propagate: only the subprocess ``main()`` catch-all contains
it, and as an UNCLASSED error string - any in-process caller looping
over tasks (a leg) dies on the first bad candidate, and verdict text
carries no named class token for the measurement.

Contract pinned here (crash-containment only - no scorer-semantics
change): a candidate callable returning None (or raising) grades FAIL
for that task with the underscore token ``candidate_none_graded_fail``
in details, never a skip or a pass, and the scorer boundary returns a
normal result dict so the leg continues to the remaining tasks. A
candidate that fails BEHAVIORALLY (no crash) must NOT carry the token.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER_DIR = ROOT / "evals" / "runner"
for _p in (str(ROOT), str(RUNNER_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from evals.runner.single_candidate_eval import (  # noqa: E402
    run_harness,
)

TOKEN = "candidate_none_graded_fail"

# The measured class: candidate callable returns None, task tests.py
# indexes the result -> TypeError kills run_tests mid-task.
NONE_INDEX_TESTS = """
def run_tests(candidate_path: str) -> dict:
    import importlib.util
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    failures = []
    for bits in ("00", "01"):
        opcode = mod.encode_bits(bits)
        if opcode[0] != bits[0]:
            failures.append("bad " + bits)
    return {"passed": not failures, "details": failures or ["ok"]}
"""

RAISE_TESTS = """
def run_tests(candidate_path: str) -> dict:
    import importlib.util
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if mod.encode_bits("00") != "000":
        return {"passed": False, "details": ["mismatch"]}
    return {"passed": True, "details": ["ok"]}
"""

BEHAVIORAL_FAIL_TESTS = """
def run_tests(candidate_path: str) -> dict:
    import importlib.util
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if mod.encode_bits("00") == "000":
        return {"passed": True, "details": ["ok"]}
    return {"passed": False, "details": ["encode_bits(00) mismatch"]}
"""


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _run(tmp_path: Path, tests_src: str, candidate_src: str) -> dict:
    tests_path = _write(tmp_path / "tests.py", tests_src)
    cand_path = _write(tmp_path / "candidate.py", candidate_src)
    return run_harness(str(cand_path), tests_path)


def test_none_returning_candidate_grades_fail_with_token(tmp_path):
    result = _run(
        tmp_path,
        NONE_INDEX_TESTS,
        "def encode_bits(bits):\n    return None\n",
    )
    assert result["passed"] is False
    assert TOKEN in result["details"]


def test_raising_candidate_grades_fail_with_token(tmp_path):
    result = _run(
        tmp_path,
        RAISE_TESTS,
        'def encode_bits(bits):\n    raise ValueError("boom")\n',
    )
    assert result["passed"] is False
    assert TOKEN in result["details"]


def test_leg_continues_after_bad_candidate(tmp_path):
    # Leg shape: the task loop keeps going - the bad candidate grades
    # fail, the next task's good candidate still grades pass.
    bad = _run(
        tmp_path / "t1",
        RAISE_TESTS,
        'def encode_bits(bits):\n    raise ValueError("boom")\n',
    )
    good = _run(
        tmp_path / "t2",
        RAISE_TESTS,
        "def encode_bits(bits):\n    return bits + '0'\n",
    )
    assert bad["passed"] is False and TOKEN in bad["details"]
    assert good["passed"] is True


def test_behavioral_failure_does_not_carry_crash_token(tmp_path):
    # No scorer-semantics change: the token marks the CRASH class only.
    result = _run(
        tmp_path,
        BEHAVIORAL_FAIL_TESTS,
        "def encode_bits(bits):\n    return bits\n",
    )
    assert result["passed"] is False
    assert TOKEN not in result["details"]


def test_main_subprocess_stays_exit_zero_on_none_candidate(tmp_path):
    # Producer contract: one JSON line, exit 0, fail-closed with token.
    tests_path = _write(tmp_path / "tests.py", NONE_INDEX_TESTS)
    cand_path = _write(tmp_path / "candidate.py", "def encode_bits(b):\n    return None\n")
    runner = RUNNER_DIR / "single_candidate_eval.py"
    proc = subprocess.run(
        [
            sys.executable,
            str(runner),
            "--candidate",
            str(cand_path),
            "--tests",
            str(tests_path),
            "--task-dir",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 0, proc.stderr[-400:]
    lines = [ln for ln in proc.stdout.strip().splitlines() if ln.strip()]
    assert lines, "runner produced no stdout"
    payload = json.loads(lines[-1])
    harness = payload["harness"]
    assert harness["passed"] is False
    assert TOKEN in json.dumps(harness["details"])
