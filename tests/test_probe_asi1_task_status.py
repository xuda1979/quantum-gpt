from __future__ import annotations

import shlex
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_task_status_probe_scripts_compile() -> None:
    bash_result = subprocess.run(
        ["bash", "-n", "scripts/probe_asi1_task_status.sh"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert bash_result.returncode == 0, bash_result.stderr

    node_result = subprocess.run(
        ["node", "-c", "browser-automation/huanxin_task_status_probe.js"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert node_result.returncode == 0, node_result.stderr


def test_probe_asi1_status_wrapper_passes_open_pod_log_flag() -> None:
    result = subprocess.run(
        [
            "bash",
            "scripts/probe_asi1_task_status.sh",
            "--dry-run",
            "--task-id",
            "dt-test",
            "--open-pod-log",
            "--artifact-stem",
            "probe-test",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    command = shlex.split(result.stdout.strip())
    assert "--task-id" in command
    by_flag = dict(zip(command, command[1:], strict=False))
    assert "name=ASI1" in by_flag["--url"]
    assert "--open-pod-log" in command
    assert "--open-detail" not in command
    assert str(ROOT / "browser-automation" / "probe-test.json") in command
