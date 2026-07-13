from __future__ import annotations

import json
import shlex
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "submit_asi1_preflight_task.sh"


def _dry_run(*args: str) -> list[str]:
    result = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return shlex.split(result.stdout.strip())


def test_asi1_preflight_wrapper_defaults_to_no_submit_and_browser_artifacts() -> None:
    command = _dry_run()

    assert command[:2] == ["node", str(ROOT / "browser-automation" / "huanxin_submit_task_run.js")]
    assert "--submit" not in command

    by_flag = dict(zip(command, command[1:], strict=False))
    assert "name=ASI1" in by_flag["--url"]
    assert by_flag["--task-name"] == "asi1-preflight"
    assert by_flag["--remote-root"] == "/root/work/quantum-gpt"
    assert by_flag["--cpu-cores"] == "4"
    assert by_flag["--memory-gb"] == "16"
    assert by_flag["--launcher-script"] == str(SCRIPT)
    assert by_flag["--launcher-arg"] == "__launch-spec"
    assert by_flag["--screenshot"] == str(
        ROOT / "browser-automation" / "huanxin-submit-task-run-asi1-preflight.png"
    )
    assert by_flag["--dump-html"] == str(
        ROOT / "browser-automation" / "huanxin-submit-task-run-asi1-preflight.html"
    )
    assert by_flag["--dump-json"] == str(
        ROOT / "browser-automation" / "huanxin-submit-task-run-asi1-preflight.json"
    )


def test_asi1_preflight_wrapper_only_submits_when_explicitly_requested() -> None:
    command = _dry_run("--submit")
    assert "--submit" in command


def test_asi1_preflight_launch_spec_is_non_training_remote_preflight() -> None:
    result = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run", "__launch-spec"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["remote_root"] == "/root/work/quantum-gpt"

    remote_command = payload["remote_command"]
    execution_command = payload["execution_command"]
    assert "torchrun" not in remote_command
    assert "__ASI1_PREFLIGHT_START__" in remote_command
    assert "__ASI1_PREFLIGHT_DONE__" in remote_command
    assert "test -d /root/work/filestorage/Qwen3.6-35B-A3B-W8A8" in remote_command
    assert "test -f training/agentic_grpo_trainer.py" in remote_command
    assert "test -f evals/benchmarks/agentic_coding_trajectory_training_v1.txt" in remote_command
    assert "asi1_preflight_dependencies" in remote_command
    assert "torch_npu" in remote_command
    assert "accelerate" in remote_command
    assert "importlib.util,json" not in remote_command
    assert "mods=[" not in remote_command
    assert "{m:" not in remote_command
    assert "&&" not in execution_command
    assert "cd /root/work/quantum-gpt" in execution_command
    assert "asi1_preflight_dependencies" in execution_command


def test_asi1_preflight_custom_paths_feed_launch_spec() -> None:
    env = {
        "ASI1_PREFLIGHT_REMOTE_ROOT": "/remote/custom-root",
        "ASI1_PREFLIGHT_MODEL_PATH": "/models/custom-qwen",
        "ASI1_PREFLIGHT_BENCHMARK_FILE": "evals/benchmarks/custom.txt",
    }
    result = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run", "__launch-spec"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={**env},
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["remote_root"] == "/remote/custom-root"
    assert "test -d /models/custom-qwen" in payload["remote_command"]
    assert "test -f evals/benchmarks/custom.txt" in payload["remote_command"]
    assert "cd /remote/custom-root" in payload["execution_command"]


def test_asi1_preflight_can_bootstrap_from_wheelhouse() -> None:
    env = {
        "ASI1_PREFLIGHT_BOOTSTRAP_WHEELHOUSE": "1",
    }
    result = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run", "__launch-spec"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={**env},
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert "test -d tools/wheels" in payload["remote_command"]
    assert (
        "python3 -m pip install --no-input --no-index --find-links tools/wheels accelerate peft"
        in payload["remote_command"]
    )
    assert "&&" not in payload["execution_command"]


def test_asi1_preflight_can_bootstrap_from_pip_index() -> None:
    result = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run", "__launch-spec"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={
            "ASI1_PREFLIGHT_BOOTSTRAP_PIP_INDEX": "1",
        },
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert (
        "python3 -m pip install --no-input accelerate==1.4.0 peft==0.14.0"
        in payload["remote_command"]
    )
    assert "&&" not in payload["execution_command"]
