from __future__ import annotations

import json
import shlex
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "submit_huanxin_preflight_task.sh"


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


def test_huanxin_preflight_wrapper_targets_explicit_env_without_submit() -> None:
    command = _dry_run("--env", "yx-QITE", "--artifact-stem", "yx-qite-preflight")

    assert command[:2] == ["node", str(ROOT / "browser-automation" / "huanxin_submit_task_run.js")]
    assert "--submit" not in command

    by_flag = dict(zip(command, command[1:], strict=False))
    assert "name=yx-QITE" in by_flag["--url"]
    assert by_flag["--task-name"] == "huanxin-preflight"
    assert by_flag["--remote-root"] == "/root/work/quantum-gpt"
    assert by_flag["--launcher-script"] == str(SCRIPT)
    assert by_flag["--launcher-arg"] == "__launch-spec"
    assert by_flag["--screenshot"] == str(ROOT / "browser-automation" / "yx-qite-preflight.png")
    assert by_flag["--dump-json"] == str(ROOT / "browser-automation" / "yx-qite-preflight.json")


def test_huanxin_preflight_wrapper_accepts_exact_url() -> None:
    url = "https://example.invalid/app#/train-dev/environment/dl-custom?name=yx-QITE"
    command = _dry_run("--env", "yx-QITE", "--url", url)
    by_flag = dict(zip(command, command[1:], strict=False))
    assert by_flag["--url"] == url


def test_huanxin_preflight_launch_spec_uses_env_markers_and_newlines() -> None:
    result = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run", "__launch-spec"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={
            "HUANXIN_PREFLIGHT_ENV": "yx-QITE",
            "HUANXIN_PREFLIGHT_REMOTE_ROOT": "/remote/root",
            "HUANXIN_PREFLIGHT_MODEL_PATH": "/models/qwen",
            "HUANXIN_PREFLIGHT_BENCHMARK_FILE": "evals/benchmarks/custom.txt",
        },
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["remote_root"] == "/remote/root"
    assert payload["job_name"] == "yx-QITE-preflight"
    assert "__YX_QITE_PREFLIGHT_START__" in payload["remote_command"]
    assert "__YX_QITE_PREFLIGHT_DONE__" in payload["remote_command"]
    assert "test -d /models/qwen" in payload["remote_command"]
    assert "test -f evals/benchmarks/custom.txt" in payload["remote_command"]
    assert "yx-QITE_preflight_dependencies" in payload["remote_command"]
    assert "torch_npu" in payload["remote_command"]
    assert "accelerate" in payload["remote_command"]
    assert "&&" not in payload["execution_command"]
    assert "cd /remote/root" in payload["execution_command"]


def test_generic_task_status_probe_passes_open_pod_log_flag() -> None:
    result = subprocess.run(
        [
            "bash",
            "scripts/probe_huanxin_task_status.sh",
            "--dry-run",
            "--task-id",
            "dt-test",
            "--open-pod-log",
            "--artifact-stem",
            "probe-yx-qite",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    command = shlex.split(result.stdout.strip())
    assert "--task-id" in command
    assert "--open-pod-log" in command
    assert "--open-detail" not in command
    assert str(ROOT / "browser-automation" / "probe-yx-qite.json") in command


def test_huanxin_preflight_can_bootstrap_from_wheelhouse() -> None:
    result = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run", "__launch-spec"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={
            "HUANXIN_PREFLIGHT_ENV": "ASI1",
            "HUANXIN_PREFLIGHT_BOOTSTRAP_WHEELHOUSE": "1",
        },
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert "test -d tools/wheels" in payload["remote_command"]
    assert (
        "python3 -m pip install --no-input --no-index --find-links tools/wheels accelerate peft"
        in payload["remote_command"]
    )
    assert "&&" not in payload["execution_command"]


def test_huanxin_preflight_can_bootstrap_from_pip_index() -> None:
    result = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run", "__launch-spec"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={
            "HUANXIN_PREFLIGHT_ENV": "ASI1",
            "HUANXIN_PREFLIGHT_BOOTSTRAP_PIP_INDEX": "1",
        },
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert (
        "python3 -m pip install --no-input accelerate==1.4.0 peft==0.14.0"
        in payload["remote_command"]
    )
    assert "&&" not in payload["execution_command"]
