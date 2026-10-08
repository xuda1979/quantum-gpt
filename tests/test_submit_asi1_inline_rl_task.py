from __future__ import annotations

import json
import shlex
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "submit_asi1_inline_rl_task.sh"


def test_inline_rl_launch_spec_defaults_to_config_probe_after_metrics_first_path() -> None:
    result = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run", "__launch-spec"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={
            "ASI1_INLINE_RL_TIMESTAMP": "20260529T090000Z",
        },
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    command = payload["remote_command"]

    assert payload["remote_root"] == "/tmp"
    assert payload["output_dir"] == "/tmp/qg-asi1-inline-rl-20260529T090000Z"
    assert "export ASI1_INLINE_RL_MODEL_NAME=/root/work/filestorage/Qwen3.6-27B" in command
    assert "export ASI1_INLINE_RL_QWEN_PROBE_MODE=config" in command
    assert "export ASI1_INLINE_RL_STEPS=64" in command
    assert "export ASI1_NPROC=1" in command
    assert "asi1_inline_rl_exec.b64" in command
    assert "python3 -m py_compile /tmp/asi1_inline_rl_exec.py" in command
    assert "python3 -c '" not in command or "python3 -c 'import pathlib;" in command


def test_inline_rl_wrapper_preserves_explicit_empty_model_and_probe_mode() -> None:
    result = subprocess.run(
        [
            "bash",
            str(SCRIPT),
            "--dry-run",
            "--task-name",
            "asi1-rl-test",
            "--model-name",
            "",
            "--qwen-probe-mode",
            "none",
            "--steps",
            "96",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    command = shlex.split(result.stdout)
    by_flag = dict(zip(command, command[1:], strict=False))

    assert by_flag["--task-name"] == "asi1-rl-test"
    assert by_flag["--launcher-script"] == str(SCRIPT)
    assert "name=ASI1" in by_flag["--url"]

    spec = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run", "__launch-spec"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={
            "ASI1_INLINE_RL_MODEL_NAME": "",
            "ASI1_INLINE_RL_QWEN_PROBE_MODE": "none",
            "ASI1_INLINE_RL_STEPS": "96",
        },
    )
    assert spec.returncode == 0, spec.stderr
    payload = json.loads(spec.stdout)
    assert "export ASI1_INLINE_RL_MODEL_NAME=''" in payload["remote_command"]
    assert "export ASI1_INLINE_RL_QWEN_PROBE_MODE=none" in payload["remote_command"]
    assert "export ASI1_INLINE_RL_STEPS=96" in payload["remote_command"]
    assert "/root/work/filestorage/Qwen3.6-27B" not in payload["remote_command"]


def test_inline_rl_wrapper_propagates_explicit_8_npu_contract() -> None:
    result = subprocess.run(
        [
            "bash",
            str(SCRIPT),
            "--dry-run",
            "--task-name",
            "asi1-rl-8p-test",
            "--accelerator-cards",
            "8",
            "--nproc-per-node",
            "8",
            "--visible-devices",
            "0,1,2,3,4,5,6,7",
            "--steps",
            "512",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    command = shlex.split(result.stdout)
    by_flag = dict(zip(command, command[1:], strict=False))

    assert by_flag["--accelerator-cards"] == "8"
    assert by_flag["--task-name"] == "asi1-rl-8p-test"

    spec = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run", "__launch-spec"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={
            "ASI1_INLINE_RL_NPROC_PER_NODE": "8",
            "ASI1_INLINE_RL_VISIBLE_DEVICES": "0,1,2,3,4,5,6,7",
            "ASI1_INLINE_RL_STEPS": "512",
        },
    )
    assert spec.returncode == 0, spec.stderr
    payload = json.loads(spec.stdout)
    remote_command = payload["remote_command"]
    assert "export ASI1_NPROC=8" in remote_command
    assert "export ASI1_INLINE_RL_STEPS=512" in remote_command
    assert "asi1_inline_rl_exec.b64" in remote_command
    assert "python3 -m py_compile /tmp/asi1_inline_rl_exec.py" in remote_command
    assert "python3 -c 'import json" not in remote_command
