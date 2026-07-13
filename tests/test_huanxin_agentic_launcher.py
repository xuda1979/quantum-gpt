from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRAINING_BENCHMARK = ROOT / "evals" / "benchmarks" / "agentic_software_engineering_training_v1.txt"
HOLDOUT_BENCHMARK = ROOT / "evals" / "benchmarks" / "agentic_software_engineering_holdout_v1.txt"


def _load_benchmark_ids(path: Path) -> set[str]:
    ids: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            ids.add(line)
    return ids


def _task_ids_on_disk() -> set[str]:
    ids: set[str] = set()
    for task_json in ROOT.glob("evals/tasks/*/*/task.json"):
        meta = json.loads(task_json.read_text(encoding="utf-8"))
        ids.add(str(meta.get("id") or task_json.parent.name))
    return ids


def test_generic_huanxin_agentic_launcher_rejects_blocked_asi1_w8a8_override() -> None:
    result = subprocess.run(
        [
            "bash",
            "scripts/launch_huanxin_agentic_grpo.sh",
            "--env",
            "ASI1",
            "--remote-root",
            "/root/work/quantum-gpt",
            "--model-name",
            "/root/work/filestorage/Qwen3.6-35B-A3B-W8A8",
            "--benchmark-file",
            "evals/benchmarks/agentic_coding_trajectory_training_v1.txt",
            "--dry-run",
            "--group-size",
            "8",
            "--grpo-steps",
            "64",
            "--max-turns",
            "30",
            "--max-new-tokens",
            "32768",
            "--max-seq-length",
            "32768",
            "--visible-devices",
            "0,1,2,3,4,5,6,7",
            "--nproc-per-node",
            "8",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2
    payload = json.loads(result.stderr)
    assert payload["status"] == "blocked"
    assert "aclnnMm" in payload["message"]


def test_generic_huanxin_agentic_launcher_accepts_asi1_27b_override() -> None:
    result = subprocess.run(
        [
            "bash",
            "scripts/launch_huanxin_agentic_grpo.sh",
            "--env",
            "ASI1",
            "--remote-root",
            "/root/work/quantum-gpt",
            "--model-name",
            "/root/work/filestorage/Qwen3.6-27B",
            "--benchmark-file",
            "evals/benchmarks/agentic_coding_trajectory_training_v1.txt",
            "--dry-run",
            "--group-size",
            "8",
            "--grpo-steps",
            "64",
            "--max-turns",
            "30",
            "--max-new-tokens",
            "32768",
            "--max-seq-length",
            "32768",
            "--visible-devices",
            "0,1,2,3,4,5,6,7",
            "--nproc-per-node",
            "8",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["remote_root"] == "/root/work/quantum-gpt"
    assert payload["job_name"] == "qwen36-35b-a3b-agentic-grpo-asi1-fast"
    assert "evals/benchmarks/agentic_coding_trajectory_training_v1.txt" in payload["remote_command"]
    assert "Qwen3.6-27B" in payload["remote_command"]


def test_direct_ai3_launcher_accepts_model_and_benchmark_overrides() -> None:
    result = subprocess.run(
        [
            "bash",
            "scripts/launch_qwen36_35b_a3b_agentic_grpo_ai3.sh",
            "--dry-run",
            "--model-name",
            "/tmp/custom-model",
            "--benchmark-file",
            "evals/benchmarks/custom.txt",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert "evals/benchmarks/custom.txt" in payload["remote_command"]


def test_agentic_software_engineering_benchmarks_are_disjoint_and_resolvable() -> None:
    training_ids = _load_benchmark_ids(TRAINING_BENCHMARK)
    holdout_ids = _load_benchmark_ids(HOLDOUT_BENCHMARK)
    task_ids = _task_ids_on_disk()

    assert training_ids
    assert holdout_ids
    assert training_ids.isdisjoint(holdout_ids)
    assert not (training_ids | holdout_ids) - task_ids
