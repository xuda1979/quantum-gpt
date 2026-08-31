"""Coverage backlog #1 (2026-08-25): evals/runner/single_candidate_eval.py.

The trainer's per-step subprocess scoring runner — every rollout candidate in
every SAPO step is scored through it — had 0% test coverage. These tests pin
the contracts the trainer depends on:
  - ``bool(result["passed"])`` truthiness: _clean must keep False a bool;
  - run_harness: pass/fail verdicts, security rejections, missing run_tests
    and non-dict returns (the runner never crashes the step);
  - run_typed: no-verifier paths return (None, None); known verifiers dispatch
    and their output is cleaned;
  - main() end-to-end as the trainer invokes it (subprocess, one JSON line).
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
RUNNER_DIR = ROOT / "evals" / "runner"
for _p in (str(ROOT), str(RUNNER_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from evals.runner.single_candidate_eval import (  # noqa: E402
    _clean,
    _load_module,
    main,
    run_harness,
    run_typed,
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

PASSING_CANDIDATE = "def solve():\n    return 42\n"
FAILING_CANDIDATE = "def solve():\n    return 7\n"


def _write(dir_: Path, name: str, text: str) -> Path:
    p = dir_ / name
    p.write_text(text, encoding="utf-8")
    return p


@pytest.fixture()
def task_fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    """(candidate, tests, task_dir) for a passing solve()-based task."""
    task_dir = tmp_path / "task"
    task_dir.mkdir()
    candidate = _write(task_dir, "candidate.py", PASSING_CANDIDATE)
    tests = _write(task_dir, "tests.py", PASSING_TESTS)
    return candidate, tests, task_dir


# ---------------------------------------------------------------------------
# _clean — the trainer's bool(result["passed"]) truthiness contract
# ---------------------------------------------------------------------------


def test_clean_preserves_bools_numbers_and_recurses() -> None:
    assert _clean(False) is False  # str(False) would be TRUTHY — verbatim is load-bearing
    assert _clean(True) is True
    assert _clean(1.5) == 1.5
    assert _clean(0) == 0
    cleaned = _clean({"passed": False, "details": [1, "x", {"n": None}]})
    assert cleaned["passed"] is False
    assert cleaned["details"] == [1, "x", {"n": "None"}]
    assert isinstance(_clean(object()), str)


# ---------------------------------------------------------------------------
# _load_module
# ---------------------------------------------------------------------------


def test_load_module_loads_real_module(tmp_path: Path) -> None:
    mod_path = _write(tmp_path, "m.py", "VALUE = 7\n")
    mod = _load_module(mod_path, "m")
    assert mod.VALUE == 7


def test_load_module_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises((ImportError, FileNotFoundError)):
        _load_module(tmp_path / "nope.py", "nope")


# ---------------------------------------------------------------------------
# run_harness — pass/fail/security/malformed verdicts
# ---------------------------------------------------------------------------


def test_run_harness_passing_candidate(task_fixture) -> None:
    candidate, tests, _ = task_fixture
    result = run_harness(str(candidate), tests)
    assert result == {"passed": True, "details": ["ok"]}


def test_run_harness_failing_candidate(task_fixture) -> None:
    candidate, tests, task_dir = task_fixture
    _write(task_dir, "candidate.py", FAILING_CANDIDATE)
    result = run_harness(str(candidate), tests)
    assert result["passed"] is False
    assert "got 7" in result["details"][0]


def test_run_harness_rejects_security_violation(tmp_path: Path) -> None:
    task_dir = tmp_path / "task"
    task_dir.mkdir()
    candidate = _write(task_dir, "candidate.py", 'x = eval("1")\n')
    tests = _write(task_dir, "tests.py", PASSING_TESTS)
    result = run_harness(str(candidate), tests)
    assert result["passed"] is False
    assert result.get("security_violation") is True
    assert any("policy" in d for d in result["details"])


def test_run_harness_requires_run_tests(tmp_path: Path) -> None:
    task_dir = tmp_path / "task"
    task_dir.mkdir()
    candidate = _write(task_dir, "candidate.py", PASSING_CANDIDATE)
    tests = _write(task_dir, "tests.py", "x = 1\n")
    with pytest.raises(AttributeError, match="run_tests"):
        run_harness(str(candidate), tests)


def test_run_harness_non_dict_return_is_fail_closed(tmp_path: Path) -> None:
    task_dir = tmp_path / "task"
    task_dir.mkdir()
    candidate = _write(task_dir, "candidate.py", PASSING_CANDIDATE)
    tests = _write(task_dir, "tests.py", "def run_tests(candidate_path):\n    return [1, 2]\n")
    result = run_harness(str(candidate), tests)
    assert result["passed"] is False
    assert "Unexpected harness return type" in result["details"][0]


# ---------------------------------------------------------------------------
# run_typed — no-verifier paths and known-verifier dispatch
# ---------------------------------------------------------------------------


def test_run_typed_no_verifier_returns_none(tmp_path: Path) -> None:
    task_dir = tmp_path / "task"
    task_dir.mkdir()
    assert run_typed("x = 1", task_dir, {}) == (None, None)
    # task.json fallback: meta lacks verifier_type but task.json has it
    _write(task_dir, "task.json", json.dumps({"verifier_type": "no_such_verifier"}))
    assert run_typed("x = 1", task_dir, {}) == (None, None)


def test_run_typed_dispatches_known_verifier(tmp_path: Path, monkeypatch) -> None:
    task_dir = tmp_path / "task"
    task_dir.mkdir()
    called: list[tuple] = []

    def _fake_verifier(code, task_dir_, merged):
        called.append((code, task_dir_, dict(merged)))
        return {"score": 0.75, "ok": True}

    monkeypatch.setitem(
        sys.modules,
        "quantum_verifiers",
        SimpleNamespace(TYPED_VERIFIERS={"fake_type": _fake_verifier}),
    )
    _write(task_dir, "task.json", json.dumps({"verifier_type": "fake_type"}))
    score, info = run_typed("def solve(): return 1", task_dir, {})
    assert score == 0.75
    assert info == {"score": 0.75, "ok": True}
    assert called[0][0] == "def solve(): return 1"
    assert called[0][2]["verifier_type"] == "fake_type"


# ---------------------------------------------------------------------------
# main() end-to-end — the trainer's exact subprocess invocation
# ---------------------------------------------------------------------------


def _run_runner(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(RUNNER_DIR / "single_candidate_eval.py"), *args],
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_main_subprocess_passing_and_failing(task_fixture) -> None:
    candidate, tests, task_dir = task_fixture
    meta = _write(task_dir, "meta.json", "{}")
    ok = _run_runner(
        [
            "--candidate",
            str(candidate),
            "--tests",
            str(tests),
            "--task-dir",
            str(task_dir),
            "--meta",
            str(meta),
        ]
    )
    assert ok.returncode == 0, ok.stderr
    payload = json.loads(ok.stdout.strip().splitlines()[-1])
    assert payload["harness"]["passed"] is True
    assert payload["error"] is None

    _write(task_dir, "candidate.py", FAILING_CANDIDATE)
    bad = _run_runner(
        [
            "--candidate",
            str(candidate),
            "--tests",
            str(tests),
            "--task-dir",
            str(task_dir),
            "--meta",
            str(meta),
        ]
    )
    assert bad.returncode == 0
    payload = json.loads(bad.stdout.strip().splitlines()[-1])
    assert payload["harness"]["passed"] is False
    assert payload["error"] is None


def test_main_subprocess_security_violation(tmp_path: Path) -> None:
    task_dir = tmp_path / "task"
    task_dir.mkdir()
    candidate = _write(task_dir, "candidate.py", 'x = eval("1")\n')
    tests = _write(task_dir, "tests.py", PASSING_TESTS)
    meta = _write(task_dir, "meta.json", "{}")
    proc = _run_runner(
        [
            "--candidate",
            str(candidate),
            "--tests",
            str(tests),
            "--task-dir",
            str(task_dir),
            "--meta",
            str(meta),
        ]
    )
    assert proc.returncode == 0
    payload = json.loads(proc.stdout.strip().splitlines()[-1])
    assert payload["harness"]["passed"] is False
    assert payload["harness"].get("security_violation") is True


def test_main_usage_error_exits_2(tmp_path: Path) -> None:
    proc = _run_runner([])  # missing required args -> argparse exit 2
    assert proc.returncode == 2


def test_main_import_error_harness_fails_closed(tmp_path: Path) -> None:
    """A candidate that crashes at import must surface as a harness failure
    (passed False), never kill the subprocess."""
    task_dir = tmp_path / "task"
    task_dir.mkdir()
    candidate = _write(task_dir, "candidate.py", "raise RuntimeError('boom at import')\n")
    tests = _write(task_dir, "tests.py", PASSING_TESTS)
    meta = _write(task_dir, "meta.json", "{}")
    proc = _run_runner(
        [
            "--candidate",
            str(candidate),
            "--tests",
            str(tests),
            "--task-dir",
            str(task_dir),
            "--meta",
            str(meta),
        ]
    )
    assert proc.returncode == 0
    payload = json.loads(proc.stdout.strip().splitlines()[-1])
    assert payload["harness"]["passed"] is False
    assert payload["error"] is None  # import failure is a harness detail, not an error


# ---------------------------------------------------------------------------
# main() dispatch — in-process, exercising the SAME code the subprocess runs
# (coverage-visible; the subprocess tests above pin the production path)
# ---------------------------------------------------------------------------


def _main_in_proc(monkeypatch, capsys, args: list[str]) -> tuple[int, dict]:
    """Call main() in-process with monkeypatched argv; return (rc, payload)."""
    monkeypatch.setattr(sys, "argv", ["single_candidate_eval.py", *args])
    rc = main()
    out = capsys.readouterr().out
    payload = json.loads(out.strip().splitlines()[-1])
    return rc, payload


def test_main_dispatch_valid_task_returns_passed_json(monkeypatch, capsys, task_fixture) -> None:
    """The dispatch contract: valid task dir -> candidate runs -> one JSON
    line with harness {passed, details}; exit 0."""
    candidate, tests, task_dir = task_fixture
    meta = _write(task_dir, "meta.json", "{}")
    rc, payload = _main_in_proc(
        monkeypatch,
        capsys,
        [
            "--candidate",
            str(candidate),
            "--tests",
            str(tests),
            "--task-dir",
            str(task_dir),
            "--meta",
            str(meta),
        ],
    )
    assert rc == 0
    assert payload["harness"]["passed"] is True
    assert payload["harness"]["details"] == ["ok"]
    assert payload["error"] is None
    # no-verifier task: run_typed's documented contract is (None, None); the
    # TRAINER side coerces null -> 0.0 (float(payload.get("typed_score") or
    # 0.0) — pinned in test_grpo_trainer_harness_subprocess.py)
    assert payload["typed_score"] is None
    assert payload["typed_info"] is None


def test_main_dispatch_missing_candidate_file_fails_closed(monkeypatch, capsys, tmp_path) -> None:
    """A missing candidate file must fail closed: harness passed False, error
    set, and the runner still exits 0 (never kills the step)."""
    task_dir = tmp_path / "task"
    task_dir.mkdir()
    missing = task_dir / "nope.py"
    tests = _write(task_dir, "tests.py", PASSING_TESTS)
    meta = _write(task_dir, "meta.json", "{}")
    rc, payload = _main_in_proc(
        monkeypatch,
        capsys,
        [
            "--candidate",
            str(missing),
            "--tests",
            str(tests),
            "--task-dir",
            str(task_dir),
            "--meta",
            str(meta),
        ],
    )
    assert rc == 0
    assert payload["harness"]["passed"] is False
    assert payload["error"] is not None
    assert "FileNotFoundError" in payload["error"]


def test_main_dispatch_candidate_syntax_error_passed_false(monkeypatch, capsys, tmp_path) -> None:
    """A candidate with a SYNTAX error must be a harness failure (passed
    False), never an exception out of the runner."""
    task_dir = tmp_path / "task"
    task_dir.mkdir()
    candidate = _write(task_dir, "candidate.py", "def solve(:\n    return\n")
    tests = _write(task_dir, "tests.py", PASSING_TESTS)
    meta = _write(task_dir, "meta.json", "{}")
    rc, payload = _main_in_proc(
        monkeypatch,
        capsys,
        [
            "--candidate",
            str(candidate),
            "--tests",
            str(tests),
            "--task-dir",
            str(task_dir),
            "--meta",
            str(meta),
        ],
    )
    assert rc == 0
    assert payload["harness"]["passed"] is False
    assert payload["error"] is None  # syntax error is a harness detail
    assert any("import failed" in d for d in payload["harness"]["details"])


def test_main_dispatch_non_dict_run_tests_fails_closed(monkeypatch, capsys, tmp_path) -> None:
    """L71-72 pin: a non-dict run_tests() return is fail-closed (the trainer
    does bool(result['passed']) — a list/str would be an AttributeError)."""
    task_dir = tmp_path / "task"
    task_dir.mkdir()
    candidate = _write(task_dir, "candidate.py", PASSING_CANDIDATE)
    tests = _write(task_dir, "tests.py", "def run_tests(candidate_path):\n    return ['a', 'b']\n")
    meta = _write(task_dir, "meta.json", "{}")
    rc, payload = _main_in_proc(
        monkeypatch,
        capsys,
        [
            "--candidate",
            str(candidate),
            "--tests",
            str(tests),
            "--task-dir",
            str(task_dir),
            "--meta",
            str(meta),
        ],
    )
    assert rc == 0
    assert payload["harness"]["passed"] is False
    assert "Unexpected harness return type: list" in payload["harness"]["details"][0]
    assert payload["error"] is None


def test_main_dispatch_security_recheck_in_main(monkeypatch, capsys, tmp_path) -> None:
    """The security gate re-runs INSIDE the subprocess main() on the raw
    candidate text — a candidate that passes any earlier gate but carries an
    eval() call must be rejected here (defense in depth)."""
    task_dir = tmp_path / "task"
    task_dir.mkdir()
    candidate = _write(task_dir, "candidate.py", 'x = eval("1")\n')
    tests = _write(task_dir, "tests.py", PASSING_TESTS)
    meta = _write(task_dir, "meta.json", "{}")
    rc, payload = _main_in_proc(
        monkeypatch,
        capsys,
        [
            "--candidate",
            str(candidate),
            "--tests",
            str(tests),
            "--task-dir",
            str(task_dir),
            "--meta",
            str(meta),
        ],
    )
    assert rc == 0
    assert payload["harness"]["passed"] is False
    assert payload["harness"].get("security_violation") is True
    assert any("policy" in d for d in payload["harness"]["details"])


def test_main_dispatch_usage_error_exits_2_in_process(monkeypatch, capsys) -> None:
    """Missing required args -> argparse exits 2 (the launcher's contract)."""
    monkeypatch.setattr(sys, "argv", ["single_candidate_eval.py"])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 2


def test_main_dispatch_timeout_flag_accepted_and_run(monkeypatch, capsys, task_fixture) -> None:
    """--timeout is parsed by the runner (the ENFORCEMENT is the trainer's
    subprocess.run timeout — _run_harness_subprocess) and must not disturb
    the run."""
    candidate, tests, task_dir = task_fixture
    meta = _write(task_dir, "meta.json", "{}")
    rc, payload = _main_in_proc(
        monkeypatch,
        capsys,
        [
            "--candidate",
            str(candidate),
            "--tests",
            str(tests),
            "--task-dir",
            str(task_dir),
            "--meta",
            str(meta),
            "--timeout",
            "1",
        ],
    )
    assert rc == 0
    assert payload["harness"]["passed"] is True


def test_main_subprocess_missing_candidate_file_fails_closed(tmp_path: Path) -> None:
    """Production path (subprocess): missing candidate file -> exit 0 with a
    fail-closed harness payload."""
    task_dir = tmp_path / "task"
    task_dir.mkdir()
    tests = _write(task_dir, "tests.py", PASSING_TESTS)
    meta = _write(task_dir, "meta.json", "{}")
    proc = _run_runner(
        [
            "--candidate",
            str(task_dir / "missing.py"),
            "--tests",
            str(tests),
            "--task-dir",
            str(task_dir),
            "--meta",
            str(meta),
        ]
    )
    assert proc.returncode == 0
    payload = json.loads(proc.stdout.strip().splitlines()[-1])
    assert payload["harness"]["passed"] is False
    assert payload["error"] is not None


def test_main_subprocess_syntax_error_candidate_passed_false(tmp_path: Path) -> None:
    """Production path (subprocess): a syntax-error candidate is a harness
    failure, not a crash."""
    task_dir = tmp_path / "task"
    task_dir.mkdir()
    candidate = _write(task_dir, "candidate.py", "def solve(:\n    return\n")
    tests = _write(task_dir, "tests.py", PASSING_TESTS)
    meta = _write(task_dir, "meta.json", "{}")
    proc = _run_runner(
        [
            "--candidate",
            str(candidate),
            "--tests",
            str(tests),
            "--task-dir",
            str(task_dir),
            "--meta",
            str(meta),
        ]
    )
    assert proc.returncode == 0
    payload = json.loads(proc.stdout.strip().splitlines()[-1])
    assert payload["harness"]["passed"] is False
    assert payload["error"] is None


# ---------------------------------------------------------------------------
# remaining fallback branches — _load_module / run_typed failure classes
# ---------------------------------------------------------------------------


def test_load_module_unloadable_spec_raises_import_error(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(importlib.util, "spec_from_file_location", lambda *a, **k: None)
    with pytest.raises(ImportError, match="cannot load module"):
        _load_module(tmp_path / "x.py", "x")


def test_run_typed_verifier_import_failure_returns_none(tmp_path: Path, monkeypatch) -> None:
    """The typed-verifier import must never crash the runner: any import
    failure -> (None, None) (verifier optional by contract)."""
    monkeypatch.setitem(sys.modules, "quantum_verifiers", None)  # import halted
    task_dir = tmp_path / "task"
    task_dir.mkdir()
    _write(task_dir, "task.json", json.dumps({"verifier_type": "x"}))
    assert run_typed("x = 1", task_dir, {}) == (None, None)


def test_run_typed_corrupt_task_json_silently_ignored(tmp_path: Path) -> None:
    """A corrupt task.json must be silently ignored (fail-open on the
    fallback, not a crash)."""
    task_dir = tmp_path / "task"
    task_dir.mkdir()
    _write(task_dir, "task.json", "{corrupt")
    assert run_typed("x = 1", task_dir, {}) == (None, None)


def test_run_typed_verifier_raising_returns_none(tmp_path: Path, monkeypatch) -> None:
    task_dir = tmp_path / "task"
    task_dir.mkdir()

    def _boom(code, task_dir_, merged):
        raise RuntimeError("verifier crash")

    monkeypatch.setitem(
        sys.modules,
        "quantum_verifiers",
        SimpleNamespace(TYPED_VERIFIERS={"t": _boom}),
    )
    _write(task_dir, "task.json", json.dumps({"verifier_type": "t"}))
    assert run_typed("x = 1", task_dir, {}) == (None, None)


def test_run_typed_verifier_returning_none_returns_none(tmp_path: Path, monkeypatch) -> None:
    task_dir = tmp_path / "task"
    task_dir.mkdir()

    def _none_verifier(code, task_dir_, merged):
        return None

    monkeypatch.setitem(
        sys.modules,
        "quantum_verifiers",
        SimpleNamespace(TYPED_VERIFIERS={"t": _none_verifier}),
    )
    _write(task_dir, "task.json", json.dumps({"verifier_type": "t"}))
    assert run_typed("x = 1", task_dir, {}) == (None, None)


def test_module_main_entry_dispatch_via_runpy(monkeypatch, capsys, task_fixture) -> None:
    """The ``if __name__ == '__main__': sys.exit(main())`` entry executes the
    dispatch exactly as the subprocess launcher does."""
    import runpy

    candidate, tests, task_dir = task_fixture
    meta = _write(task_dir, "meta.json", "{}")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "single_candidate_eval.py",
            "--candidate",
            str(candidate),
            "--tests",
            str(tests),
            "--task-dir",
            str(task_dir),
            "--meta",
            str(meta),
        ],
    )
    with pytest.raises(SystemExit) as exc_info:
        runpy.run_path(str(RUNNER_DIR / "single_candidate_eval.py"), run_name="__main__")
    assert exc_info.value.code == 0
    payload = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert payload["harness"]["passed"] is True
