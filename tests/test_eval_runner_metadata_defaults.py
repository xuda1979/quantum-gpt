from __future__ import annotations

import json
from pathlib import Path

from evals.runner import prepare_prompts, run_eval


def _write_task_bundle(task_dir: Path, *, include_test_file: bool) -> Path:
    task_dir.mkdir(parents=True)
    metadata = {
        "id": "demo_task",
        "name": "Demo Task",
        "domain": "software",
        "category": "smoke",
        "candidate_file": "candidate.py",
    }
    if include_test_file:
        metadata["test_file"] = "tests.py"

    (task_dir / "task.json").write_text(json.dumps(metadata) + "\n")
    (task_dir / "candidate.py").write_text("VALUE = 7\n")
    (task_dir / "tests.py").write_text(
        "def run_tests(candidate_path: str) -> dict:\n"
        "    namespace = {}\n"
        "    exec(open(candidate_path, 'r', encoding='utf-8').read(), namespace)\n"
        "    return {'passed': namespace['VALUE'] == 7, 'details': ['ok']}\n"
    )
    return task_dir / "task.json"


def test_run_task_defaults_missing_test_file_to_tests_py(tmp_path: Path) -> None:
    task_json = _write_task_bundle(tmp_path / "demo", include_test_file=False)

    result = run_eval.run_task(task_json)

    assert result["passed"] is True
    assert result["source"] == "reference"


def test_build_user_prompt_defaults_missing_test_file_to_tests_py(tmp_path: Path) -> None:
    task_dir = tmp_path / "demo"
    task_json = _write_task_bundle(task_dir, include_test_file=False)
    metadata = json.loads(task_json.read_text())

    prompt = prepare_prompts.build_user_prompt(task_dir, metadata, prompt_style="direct")

    assert "VALUE = 7" in prompt
    assert "def run_tests" in prompt
