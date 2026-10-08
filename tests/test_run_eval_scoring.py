"""Coverage backlog (2026-08-26): evals/runner/run_eval.py scoring core.

classify_exception / classify_failure_details / summarize_failure_categories /
load_candidate_overrides / select_candidate_tasks / resolve_candidate_paths /
run_workspace_task / run_task — the runner's failure taxonomy (what the
scorecards record) and the candidate-path contracts (never a hidden reference
fallback). The security and reward-integrity paths are pinned end-to-end.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evals.runner.run_eval import (  # noqa: E402
    classify_exception,
    classify_failure_details,
    load_candidate_overrides,
    resolve_candidate_paths,
    run_task,
    run_workspace_task,
    select_candidate_tasks,
    summarize_failure_categories,
)

# ---------------------------------------------------------------------------
# failure taxonomy
# ---------------------------------------------------------------------------


def test_classify_exception_taxonomy() -> None:
    assert classify_exception(SyntaxError("bad")) == "syntax"
    assert classify_exception(IndentationError("indent")) == "syntax"
    assert classify_exception(ModuleNotFoundError("no qiskit")) == "dependency"
    assert classify_exception(ImportError("nope")) == "dependency"
    assert classify_exception(AssertionError("x != y")) == "assertion"
    assert classify_exception(FileNotFoundError("tests.py")) == "packaging"
    assert classify_exception(ValueError("candidate directory override")) == "packaging"
    assert classify_exception(ValueError("some other value error")) == "runtime"
    assert classify_exception(RuntimeError("boom")) == "runtime"


def test_classify_failure_details_taxonomy() -> None:
    assert classify_failure_details(["SyntaxError: bad token"]) == "syntax"
    assert classify_failure_details(["ModuleNotFoundError: no module named x"]) == "dependency"
    assert classify_failure_details(["workspace directory not found: /x"]) == "packaging"
    assert classify_failure_details(["assert 1 == 2"]) == "assertion"
    assert classify_failure_details([]) == "assertion"


def test_summarize_failure_categories_sorted_counts() -> None:
    results = [
        {"failure_category": "assertion"},
        {"failure_category": "syntax"},
        {"failure_category": "assertion"},
        {"passed": True},  # no failure_category -> excluded
        {},
    ]
    assert summarize_failure_categories(results) == {"assertion": 2, "syntax": 1}


# ---------------------------------------------------------------------------
# candidate selection — never a hidden reference fallback
# ---------------------------------------------------------------------------


def test_load_candidate_overrides_paths(tmp_path: Path) -> None:
    assert load_candidate_overrides(None) == {}
    payload = tmp_path / "map.json"
    payload.write_text(
        json.dumps({"task_a": "cands/a.py", "task_b": "/abs/b.py"}), encoding="utf-8"
    )
    overrides = load_candidate_overrides(payload)
    assert overrides["task_a"] == (tmp_path / "cands" / "a.py").resolve()
    assert overrides["task_b"] == Path("/abs/b.py")


def test_select_candidate_tasks_orders_and_rejects_unknown(tmp_path: Path) -> None:
    t1 = tmp_path / "t1.json"
    t2 = tmp_path / "t2.json"
    t1.write_text(json.dumps({"id": "a"}), encoding="utf-8")
    t2.write_text(json.dumps({"id": "b"}), encoding="utf-8")
    selected = select_candidate_tasks([t1, t2], {"b": Path("x"), "a": Path("y")})
    assert selected == [t2, t1]  # map order, not discovery order
    with pytest.raises(SystemExit, match="unknown task ids"):
        select_candidate_tasks([t1, t2], {"zzz": Path("x")})


def test_resolve_candidate_paths_contracts(tmp_path: Path) -> None:
    task_dir = tmp_path / "task"
    task_dir.mkdir()
    # workspace-style: candidate_files + override dir
    overrides_dir = tmp_path / "overrides"
    paths, source = resolve_candidate_paths(
        {"id": "t", "candidate_files": ["pkg/a.py", "pkg/b.py"]},
        task_dir,
        overrides_dir,
    )
    assert source == "override"
    assert paths["pkg/a.py"] == overrides_dir / "pkg" / "a.py"
    # a FILE where a directory is expected -> ValueError
    f = tmp_path / "file.txt"
    f.write_text("x")
    with pytest.raises(ValueError, match="expects a candidate directory override"):
        resolve_candidate_paths({"id": "t", "candidate_files": ["a.py"]}, task_dir, f)
    # reference mode: task_dir-relative
    paths, source = resolve_candidate_paths(
        {"id": "t", "candidate_files": ["a.py"]},
        task_dir,
        None,
    )
    assert source == "reference"
    assert paths["a.py"] == task_dir / "a.py"
    # single candidate_file + override
    paths, source = resolve_candidate_paths(
        {"id": "t", "candidate_file": "c.py"},
        task_dir,
        overrides_dir,
    )
    assert source == "override"
    assert paths["c.py"] == overrides_dir


def test_run_workspace_task_copies_and_prefers_workspace_tests(tmp_path: Path) -> None:
    task_dir = tmp_path / "task"
    (task_dir / "ws" / "pkg").mkdir(parents=True)
    (task_dir / "ws" / "pkg" / "core.py").write_text("VALUE = 1\n", encoding="utf-8")
    # a module with run_workspace_tests
    module_path = tmp_path / "tests_mod.py"
    module_path.write_text(
        "def run_workspace_tests(workspace_root, candidate_paths):\n"
        "    import sys, importlib.util, json\n"
        "    spec = importlib.util.spec_from_file_location('core', candidate_paths[0])\n"
        "    mod = importlib.util.module_from_spec(spec)\n"
        "    spec.loader.exec_module(mod)\n"
        "    return {'passed': mod.VALUE == 2, 'details': ['ws-ran']}\n",
        encoding="utf-8",
    )
    spec = __import__("importlib.util").util.spec_from_file_location("tests_mod", module_path)
    module = __import__("importlib.util").util.module_from_spec(spec)
    spec.loader.exec_module(module)
    override = tmp_path / "override"
    (override / "pkg").mkdir(parents=True)
    (override / "pkg" / "core.py").write_text("VALUE = 2\n", encoding="utf-8")
    result = run_workspace_task(
        module,
        task_dir,
        {"id": "t", "workspace_dir": "ws", "candidate_files": ["pkg/core.py"]},
        {"pkg/core.py": override / "pkg" / "core.py"},
    )
    assert result["passed"] is True
    assert result["details"] == ["ws-ran"]
    # the original workspace file was NOT mutated by the copy
    assert (task_dir / "ws" / "pkg" / "core.py").read_text() == "VALUE = 1\n"


def test_run_workspace_task_missing_workspace_fails_loud(tmp_path: Path) -> None:
    task_dir = tmp_path / "task"
    task_dir.mkdir()
    module_path = tmp_path / "m.py"
    module_path.write_text("def run_tests(root):\n    return {'passed': True}\n", encoding="utf-8")
    spec = __import__("importlib.util").util.spec_from_file_location("m", module_path)
    module = __import__("importlib.util").util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # declared candidate_files but NO workspace_dir -> ValueError
    with pytest.raises(ValueError, match="no workspace_dir"):
        run_workspace_task(
            module,
            task_dir,
            {"id": "t", "candidate_files": ["a.py"]},
            {"a.py": tmp_path / "a.py"},
        )
    # workspace_dir declared but missing on disk -> FileNotFoundError
    with pytest.raises(FileNotFoundError, match="Workspace directory not found"):
        run_workspace_task(
            module,
            task_dir,
            {"id": "t", "workspace_dir": "nope", "candidate_files": ["a.py"]},
            {"a.py": tmp_path / "a.py"},
        )


# ---------------------------------------------------------------------------
# run_task end-to-end
# ---------------------------------------------------------------------------


def _task_fixture(tmp_path: Path, tests_src: str, candidate_src: str) -> Path:
    task_dir = tmp_path / "task"
    task_dir.mkdir(parents=True)
    (task_dir / "task.json").write_text(
        json.dumps(
            {
                "id": "demo",
                "domain": "q",
                "category": "impl",
                "name": "Demo",
                "candidate_file": "candidate.py",
            }
        ),
        encoding="utf-8",
    )
    (task_dir / "tests.py").write_text(tests_src, encoding="utf-8")
    (task_dir / "candidate.py").write_text(candidate_src, encoding="utf-8")
    return task_dir / "task.json"


PASSING_TESTS = (
    "def run_tests(candidate_path):\n"
    "    import importlib.util\n"
    "    spec = importlib.util.spec_from_file_location('c', candidate_path)\n"
    "    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)\n"
    "    return {'passed': mod.solve() == 42, 'details': ['ok' if mod.solve() == 42 else 'bad']}\n"
)


def test_run_task_passing_and_failing() -> None:
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        task_json = _task_fixture(tmp, PASSING_TESTS, "def solve():\n    return 42\n")
        result = run_task(task_json)
        assert result["passed"] is True
        assert result["failure_category"] is None
        assert result["source"] == "reference"
        assert len(result["candidate_sha256"]) == 64
        task_json2 = _task_fixture(tmp / "f", PASSING_TESTS, "def solve():\n    return 7\n")
        result2 = run_task(task_json2)
        assert result2["passed"] is False
        assert result2["failure_category"] == "assertion"
        assert result2["error_type"] is None


def test_run_task_security_rejection() -> None:
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        task_json = _task_fixture(Path(tmp), PASSING_TESTS, 'x = eval("1")\n')
        result = run_task(task_json)
        assert result["passed"] is False
        assert result["error_type"] == "CandidateSecurityError"
        assert result["failure_category"] == "security"
        assert "policy" in result["details"][0]


def test_run_task_reward_integrity_circuit_breaker() -> None:
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        task_dir = tmp / "task"
        task_dir.mkdir()
        (task_dir / "task.json").write_text(
            json.dumps(
                {
                    "id": "sem",
                    "domain": "q",
                    "category": "distill_v3_sampling",
                    "name": "Sem",
                    "candidate_file": "candidate.py",
                }
            ),
            encoding="utf-8",
        )
        (task_dir / "tests.py").write_text(PASSING_TESTS, encoding="utf-8")
        (task_dir / "candidate.py").write_text("def solve():\n    return 42\n", encoding="utf-8")
        result = run_task(task_dir / "task.json")
        assert result["passed"] is False
        assert result["error_type"] == "RewardIntegrityCircuitBreaker"
        assert result["failure_category"] == "security"
        assert "provenance" in result["details"][0]


def test_run_task_override_source_label() -> None:
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        task_json = _task_fixture(tmp, PASSING_TESTS, "def solve():\n    return 42\n")
        override = tmp / "override.py"
        override.write_text("def solve():\n    return 42\n", encoding="utf-8")
        result = run_task(task_json, {"demo": override})
        assert result["source"] == "override"
        assert result["candidate_path"] == str(override)
