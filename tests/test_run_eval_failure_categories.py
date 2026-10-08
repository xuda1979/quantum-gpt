from __future__ import annotations

import json
from pathlib import Path

from evals.runner import run_eval


def _write_task_bundle(task_dir: Path, candidate_source: str, tests_source: str) -> Path:
    task_dir.mkdir(parents=True)
    metadata = {
        "id": task_dir.name,
        "name": task_dir.name,
        "domain": "software",
        "category": "smoke",
        "candidate_file": "candidate.py",
        "test_file": "tests.py",
    }
    (task_dir / "task.json").write_text(json.dumps(metadata) + "\n", encoding="utf-8")
    (task_dir / "candidate.py").write_text(candidate_source, encoding="utf-8")
    (task_dir / "tests.py").write_text(tests_source, encoding="utf-8")
    return task_dir / "task.json"


def test_run_task_marks_assertion_failures_from_details(tmp_path: Path) -> None:
    task_json = _write_task_bundle(
        tmp_path / "assertion_case",
        "VALUE = 1\n",
        (
            "def run_tests(candidate_path: str) -> dict:\n"
            "    return {'passed': False, 'details': ['VALUE was incorrect']}\n"
        ),
    )

    result = run_eval.run_task(task_json)

    assert result["passed"] is False
    assert result["failure_category"] == "assertion"
    assert result["error_type"] is None


def test_run_task_marks_syntax_failures(tmp_path: Path) -> None:
    task_json = _write_task_bundle(
        tmp_path / "syntax_case",
        "def broken(:\n    pass\n",
        (
            "import importlib.util\n"
            "def run_tests(candidate_path: str) -> dict:\n"
            "    spec = importlib.util.spec_from_file_location('candidate', candidate_path)\n"
            "    module = importlib.util.module_from_spec(spec)\n"
            "    assert spec.loader is not None\n"
            "    spec.loader.exec_module(module)\n"
            "    return {'passed': True, 'details': ['ok']}\n"
        ),
    )

    result = run_eval.run_task(task_json)

    assert result["passed"] is False
    assert result["failure_category"] == "syntax"
    assert result["error_type"] == "SyntaxError"


def test_run_task_marks_dependency_failures(tmp_path: Path) -> None:
    task_json = _write_task_bundle(
        tmp_path / "dependency_case",
        "import definitely_missing_dependency\n",
        (
            "import importlib.util\n"
            "def run_tests(candidate_path: str) -> dict:\n"
            "    spec = importlib.util.spec_from_file_location('candidate', candidate_path)\n"
            "    module = importlib.util.module_from_spec(spec)\n"
            "    assert spec.loader is not None\n"
            "    spec.loader.exec_module(module)\n"
            "    return {'passed': True, 'details': ['ok']}\n"
        ),
    )

    result = run_eval.run_task(task_json)

    assert result["passed"] is False
    assert result["failure_category"] == "dependency"
    assert result["error_type"] == "ModuleNotFoundError"
