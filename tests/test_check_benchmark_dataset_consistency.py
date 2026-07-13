from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _write_task(task_root: Path, task_id: str) -> None:
    task_root.mkdir(parents=True, exist_ok=True)
    (task_root / "task.json").write_text(
        json.dumps(
            {
                "id": task_id,
                "name": task_id,
                "domain": "quantum",
                "category": "smoke",
                "candidate_file": "candidate.py",
                "test_file": "tests.py",
            }
        )
        + "\n",
        encoding="utf-8",
    )


def test_checker_accepts_matching_benchmark_and_manifest(tmp_path: Path) -> None:
    tasks_root = tmp_path / "evals" / "tasks"
    _write_task(tasks_root / "quantum" / "task_a", "task_a")
    _write_task(tasks_root / "quantum" / "task_b", "task_b")
    _write_task(tasks_root / "quantum" / "task_c", "task_c")

    benchmark = tmp_path / "benchmark.txt"
    benchmark.write_text("task_a\ntask_b\n", encoding="utf-8")

    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "manifest_version": "template-large-v1",
                "dataset_contract": {
                    "source_task_ids": ["task_a", "task_b", "task_c"],
                    "train_task_ids": ["task_c"],
                    "eval_task_ids": ["task_a", "task_b"],
                },
                "train_summary": {"tasks": {"task_c": 2}},
                "eval_summary": {"tasks": {"task_a": 1, "task_b": 1}},
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "check_benchmark_dataset_consistency.py"),
            "--benchmark-file",
            str(benchmark),
            "--tasks-root",
            str(tasks_root),
            "--manifest",
            str(manifest),
            "--require-all-benchmark-tasks-in-manifest-eval",
            "--require-benchmark-tasks-absent-from-manifest-train",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["manifest_overlap"]["benchmark_vs_eval_task_ids"] == ["task_a", "task_b"]
    assert payload["manifest_overlap"]["benchmark_vs_train_task_ids"] == []


def test_checker_fails_when_benchmark_task_missing_from_manifest_eval(tmp_path: Path) -> None:
    tasks_root = tmp_path / "evals" / "tasks"
    _write_task(tasks_root / "quantum" / "task_a", "task_a")
    _write_task(tasks_root / "quantum" / "task_b", "task_b")

    benchmark = tmp_path / "benchmark.txt"
    benchmark.write_text("task_a\ntask_b\n", encoding="utf-8")

    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "manifest_version": "template-large-v1",
                "dataset_contract": {
                    "source_task_ids": ["task_a", "task_b"],
                    "train_task_ids": ["task_b"],
                    "eval_task_ids": ["task_a"],
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "check_benchmark_dataset_consistency.py"),
            "--benchmark-file",
            str(benchmark),
            "--tasks-root",
            str(tasks_root),
            "--manifest",
            str(manifest),
            "--require-all-benchmark-tasks-in-manifest-eval",
            "--require-benchmark-tasks-absent-from-manifest-train",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["checks"]["all_benchmark_tasks_present_in_manifest_eval"] is False
    assert payload["checks"]["benchmark_tasks_absent_from_manifest_train"] is False
