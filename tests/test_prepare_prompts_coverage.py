"""Coverage backlog (2026-08-26): evals/runner/prepare_prompts.py branches.

The run-preparation tool: task-id selection, prompt construction, and the
manifest/candidate-map artifacts whose hashes feed the frozen-contract
verification (the promotion gate trusts these aggregates). The placeholder
candidate contract (the empty-candidate detection in execute_run) is pinned
here too.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evals.runner.frozen_contract import sha256_text  # noqa: E402
from evals.runner.prepare_prompts import (  # noqa: E402
    PROMPT_STYLES,
    build_user_prompt,
    create_run_dir,
    load_task_id_file,
    select_task_files,
    write_run_artifacts,
)


def _task(tmp_path: Path, task_id: str, name: str = "T") -> Path:
    task_dir = tmp_path / "q" / task_id
    task_dir.mkdir(parents=True)
    (task_dir / "task.json").write_text(
        json.dumps(
            {
                "id": task_id,
                "name": name,
                "domain": "q",
                "category": "impl",
                "candidate_file": "candidate.py",
            }
        ),
        encoding="utf-8",
    )
    (task_dir / "tests.py").write_text(
        "def run_tests(candidate_path):\n    return {'passed': True}\n", encoding="utf-8"
    )
    return task_dir / "task.json"


def test_load_task_id_file_skips_comments_and_blanks(tmp_path: Path) -> None:
    assert load_task_id_file(None) == []
    p = tmp_path / "ids.txt"
    p.write_text("# comment\n\ntask_a\n  task_b  \n# another\ntask_c\n", encoding="utf-8")
    assert load_task_id_file(p) == ["task_a", "task_b", "task_c"]


def test_build_user_prompt_has_identity_and_style(tmp_path: Path) -> None:
    task_json = _task(tmp_path, "demo_task")
    prompt = build_user_prompt(task_json.parent, json.loads(task_json.read_text()), "direct")
    assert "Task ID: demo_task" in prompt
    assert "hidden tests will verify it" in prompt  # the direct style's suffix
    assert PROMPT_STYLES["direct"]["user_suffix"] in prompt
    # the plan_then_code style renders its own suffix
    prompt2 = build_user_prompt(
        task_json.parent, json.loads(task_json.read_text()), "plan_then_code"
    )
    assert "reason privately" in prompt2


def test_select_task_files_order_and_unknown(tmp_path: Path) -> None:
    a = _task(tmp_path, "a")
    b = _task(tmp_path, "b")
    c = _task(tmp_path, "c")
    all_files = [a, b, c]
    assert select_task_files(all_files, []) == all_files  # no filter
    assert select_task_files(all_files, ["c", "a"]) == [c, a]  # requested order
    with pytest.raises(SystemExit, match="Unknown task ids requested"):
        select_task_files(all_files, ["zzz"])


def test_create_run_dir_named_and_collision(tmp_path: Path, monkeypatch) -> None:
    runs_root = tmp_path / "runs"
    monkeypatch.setattr("evals.runner.prepare_prompts.RUNS_ROOT", runs_root)
    run_dir = create_run_dir("my-run")
    assert run_dir == runs_root / "my-run"
    assert run_dir.is_dir()
    with pytest.raises(FileExistsError):
        create_run_dir("my-run")  # exist_ok=False -> collision fails loud


def test_write_run_artifacts_manifest_contract(tmp_path: Path) -> None:
    task_json = _task(tmp_path, "demo_task")
    run_dir = tmp_path / "run"
    task_ids = tmp_path / "ids.txt"
    task_ids.write_text("demo_task\n", encoding="utf-8")
    write_run_artifacts(
        run_dir,
        prompt_style="direct",
        notes="wave-1",
        task_files=[task_json],
        task_id_file=task_ids,
    )
    manifest = json.loads((run_dir / "manifest.json").read_text())
    assert manifest["prompt_style"] == "direct"
    assert manifest["notes"] == "wave-1"
    assert manifest["system_prompt_sha256"] == sha256_text(
        PROMPT_STYLES["direct"]["system_prompt"] + "\n"
    )
    assert manifest["task_id_file"].endswith("ids.txt")
    assert manifest["task_id_file_sha256"] == sha256_text("demo_task\n")
    assert "public_eval_contract_sha256" in manifest
    assert "scorer_contract_sha256" in manifest
    assert "evaluation_runner_sha256" in manifest
    entry = manifest["tasks"][0]
    assert entry["id"] == "demo_task"
    assert entry["prompt_file"] == "prompts/demo_task.txt"
    assert entry["candidate_file"] == "candidates/demo_task.py"
    assert entry["prompt_sha256"] == sha256_text(
        (run_dir / "prompts" / "demo_task.txt").read_text()
    )
    # artifacts on disk
    assert (run_dir / "SYSTEM_PROMPT.txt").is_file()
    assert (run_dir / "README.txt").is_file()
    assert "run_eval.py --candidate-map" in (run_dir / "README.txt").read_text()
    # the placeholder candidate is the execute_run empty-candidate contract
    candidate = (run_dir / "candidates" / "demo_task.py").read_text()
    assert candidate == "# Paste model output here.\n"
    candidate_map = json.loads((run_dir / "candidate-map.json").read_text())
    assert candidate_map == {"demo_task": "candidates/demo_task.py"}


def test_write_run_artifacts_without_task_id_file(tmp_path: Path) -> None:
    task_json = _task(tmp_path, "t1")
    run_dir = tmp_path / "run2"
    write_run_artifacts(run_dir, prompt_style="repair_focused", notes=None, task_files=[task_json])
    manifest = json.loads((run_dir / "manifest.json").read_text())
    assert "task_id_file" not in manifest
    assert manifest["prompt_style"] == "repair_focused"
    assert manifest["notes"] is None
