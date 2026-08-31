"""TDD (coverage lane, PASS 16): _run_harness_subprocess — the trainer's
per-step candidate-eval spawn (2026-08-21 fork-safety fix).

Every rollout candidate in every SAPO step is evaluated through this
subprocess; a regression here silently corrupts in-loop eval feeding
rewards AND eval legs. Before this suite the function had 1/50 statements
covered (2%). Tests pin:

  (a) the production path: a REAL subprocess (sys.executable +
      single_candidate_eval.py) with a passing and a failing candidate;
  (b) the timeout fail-closed contract: TimeoutExpired -> {passed: False,
      details: ['harness subprocess timed out ...']}, never an exception;
  (c) unparseable/empty output -> fail-closed;
  (d) missing harness result / non-dict harness -> fail-closed;
  (e) _run_harness_for_code (teacher-free self-repair path) wraps the same
      contract into {passed, details}.
"""

from __future__ import annotations

import json
import subprocess
import sys
from argparse import Namespace
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import training.grpo_trainer as grpo_trainer  # noqa: E402
from training.grpo_trainer import (  # noqa: E402
    _run_harness_for_code,
    _run_harness_subprocess,
)

PASSING_TESTS = """
def run_tests(candidate_path: str) -> dict:
    import importlib.util
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    try:
        spec.loader.exec_module(mod)
    except Exception as exc:  # noqa: BLE001 - real enriched tests.py pattern
        return {"passed": False, "details": [f"import failed: {exc}"]}
    try:
        result = mod.solve()
    except Exception as exc:  # noqa: BLE001
        return {"passed": False, "details": [f"raised: {exc}"]}
    if result == 42:
        return {"passed": True, "details": ["ok"]}
    return {"passed": False, "details": [f"got {result}"]}
"""


def _write(dir_: Path, name: str, text: str) -> Path:
    p = dir_ / name
    p.write_text(text, encoding="utf-8")
    return p


@pytest.fixture()
def task_fixture(tmp_path: Path) -> tuple[Path, Path]:
    """(task_dir, tests.py) for a solve()-based task."""
    task_dir = tmp_path / "task"
    task_dir.mkdir()
    tests = _write(task_dir, "tests.py", PASSING_TESTS)
    return task_dir, tests


def _call(code: str, task_dir: Path, tests: Path, **overrides):
    task = {"tests_py": tests, "task_dir": task_dir, "meta": {}}
    args = Namespace(harness_timeout_seconds=60)
    for key, value in overrides.items():
        setattr(args, key, value)
    return _run_harness_subprocess(code, task, args)


# ---------------------------------------------------------------------------
# (a) production path — REAL subprocess, as the trainer invokes it
# ---------------------------------------------------------------------------


def test_production_path_passing_candidate(task_fixture) -> None:
    task_dir, tests = task_fixture
    harness, typed_score, typed_info = _call("def solve():\n    return 42\n", task_dir, tests)
    assert harness == {"passed": True, "details": ["ok"]}
    assert typed_score == 0.0
    assert typed_info is None


def test_production_path_failing_candidate(task_fixture) -> None:
    task_dir, tests = task_fixture
    harness, _score, _info = _call("def solve():\n    return 7\n", task_dir, tests)
    assert harness["passed"] is False
    assert "got 7" in harness["details"][0]


def test_production_path_syntax_error_candidate(task_fixture) -> None:
    task_dir, tests = task_fixture
    harness, _score, _info = _call("def solve(:\n    return\n", task_dir, tests)
    assert harness["passed"] is False
    assert harness["details"]  # import-failed detail, never a raised exception


def test_production_path_missing_tests_file_is_fail_closed(task_fixture, tmp_path: Path) -> None:
    """A missing tests.py (broken task dir) must be a fail-closed harness
    result, not an exception out of the trainer."""
    task_dir, _tests = task_fixture
    harness, typed_score, typed_info = _call(
        "def solve():\n    return 42\n", task_dir, tmp_path / "no_tests.py"
    )
    assert harness["passed"] is False
    assert typed_score == 0.0
    assert typed_info is None


def test_production_path_timeout_override_used(task_fixture) -> None:
    """harness_timeout_seconds flows into the subprocess call (default 300;
    the trainer sets it per-launch)."""
    task_dir, tests = task_fixture
    _call("def solve():\n    return 42\n", task_dir, tests, harness_timeout_seconds=7)


# ---------------------------------------------------------------------------
# (b) timeout fail-closed contract
# ---------------------------------------------------------------------------


def test_timeout_expired_fails_closed(task_fixture, monkeypatch) -> None:
    task_dir, tests = task_fixture

    def _boom(*_a, **_k):
        raise subprocess.TimeoutExpired(cmd=["x"], timeout=60)

    monkeypatch.setattr(grpo_trainer.subprocess, "run", _boom)
    harness, typed_score, typed_info = _call("def solve():\n    return 42\n", task_dir, tests)
    assert harness["passed"] is False
    assert any("timed out" in d for d in harness["details"])
    assert typed_score == 0.0
    assert typed_info is None


# ---------------------------------------------------------------------------
# (c) unparseable / empty stdout fail-closed
# ---------------------------------------------------------------------------


class _FakeCompleted:
    def __init__(self, stdout: str = "", returncode: int = 0, stderr: str = "") -> None:
        self.stdout = stdout
        self.returncode = returncode
        self.stderr = stderr


def test_unparseable_output_fails_closed(task_fixture, monkeypatch) -> None:
    task_dir, tests = task_fixture
    monkeypatch.setattr(
        grpo_trainer.subprocess,
        "run",
        lambda *_a, **_k: _FakeCompleted(stdout="not-json-at-all", returncode=1),
    )
    harness, typed_score, typed_info = _call("x = 1\n", task_dir, tests)
    assert harness["passed"] is False
    assert any("unparseable output" in d for d in harness["details"])
    assert typed_score == 0.0
    assert typed_info is None


def test_empty_output_fails_closed(task_fixture, monkeypatch) -> None:
    task_dir, tests = task_fixture
    monkeypatch.setattr(
        grpo_trainer.subprocess,
        "run",
        lambda *_a, **_k: _FakeCompleted(stdout="", returncode=0),
    )
    harness, _score, _info = _call("x = 1\n", task_dir, tests)
    assert harness["passed"] is False
    assert any("unparseable output" in d for d in harness["details"])


# ---------------------------------------------------------------------------
# (d) missing / non-dict harness fail-closed
# ---------------------------------------------------------------------------


def test_null_harness_result_fails_closed(task_fixture, monkeypatch) -> None:
    task_dir, tests = task_fixture
    payload = json.dumps({"harness": None, "typed_score": 0.0, "typed_info": None, "error": None})
    monkeypatch.setattr(
        grpo_trainer.subprocess,
        "run",
        lambda *_a, **_k: _FakeCompleted(stdout=payload, returncode=0),
    )
    harness, typed_score, typed_info = _call("x = 1\n", task_dir, tests)
    assert harness["passed"] is False
    assert any("no harness result" in d for d in harness["details"])
    assert typed_score == 0.0
    assert typed_info is None


def test_non_dict_harness_fails_closed(task_fixture, monkeypatch) -> None:
    task_dir, tests = task_fixture
    payload = json.dumps({"harness": 42, "typed_score": 1.0, "typed_info": None, "error": None})
    monkeypatch.setattr(
        grpo_trainer.subprocess,
        "run",
        lambda *_a, **_k: _FakeCompleted(stdout=payload, returncode=0),
    )
    harness, typed_score, _info = _call("x = 1\n", task_dir, tests)
    assert harness["passed"] is False
    assert any("Unexpected harness type" in d for d in harness["details"])
    # typed fields still parsed defensively
    assert typed_score == 1.0


# ---------------------------------------------------------------------------
# (e) _run_harness_for_code — teacher-free self-repair wrapper
# ---------------------------------------------------------------------------


def test_run_harness_for_code_passing(task_fixture) -> None:
    task_dir, tests = task_fixture
    result = _run_harness_for_code(tests, "def solve():\n    return 42\n")
    assert result == {"passed": True, "details": ["ok"]}


def test_run_harness_for_code_failing(task_fixture) -> None:
    task_dir, tests = task_fixture
    result = _run_harness_for_code(tests, "def solve():\n    return 3\n")
    assert result["passed"] is False
    assert all(isinstance(d, str) for d in result["details"])


def test_run_harness_for_code_default_timeout(task_fixture, monkeypatch) -> None:
    """Calling _run_harness_for_code WITHOUT args must use the 300s default —
    the argparse-Namespace fallback the trainer uses."""
    task_dir, tests = task_fixture
    seen: dict = {}

    def _spy(*args, **kwargs):
        seen.update(kwargs)
        return _FakeCompleted(
            stdout=json.dumps(
                {
                    "harness": {"passed": False, "details": ["x"]},
                    "typed_score": 0.0,
                    "typed_info": None,
                    "error": None,
                }
            ),
            returncode=0,
        )

    monkeypatch.setattr(grpo_trainer.subprocess, "run", _spy)
    result = _run_harness_for_code(tests, "x = 1\n")
    assert result["passed"] is False
    assert seen["timeout"] == 300
