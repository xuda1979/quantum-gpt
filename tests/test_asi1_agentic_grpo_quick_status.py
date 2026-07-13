from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "asi1_agentic_grpo_quick_status.sh"


def run_status(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(SCRIPT), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_quick_status_dry_run_uses_asi1_wrappers_without_training_launch() -> None:
    result = run_status(
        "--dry-run",
        "--output-dir",
        "outputs/qwen36-agentic",
        "--log-path",
        "/tmp/qwen36-agentic.log",
        "--tail-lines",
        "40",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["environment"] == "ASI1"
    assert payload["remote_root"] == "/workspace/quantum-gpt"
    assert payload["tail_lines"] == 40
    commands = payload["commands"]
    assert len(commands) == 2
    assert commands[0][:4] == [
        "bash",
        str(ROOT / "scripts" / "show_huanxin_agentic_grpo_status.sh"),
        "--env",
        "ASI1",
    ]
    assert commands[1][:4] == [
        "bash",
        str(ROOT / "scripts" / "huanxin_env_shell.sh"),
        "--env",
        "ASI1",
    ]
    rendered = "\n".join(" ".join(command) for command in commands)
    assert "launch_qwen36_35b_a3b_agentic_grpo_asi1.sh" not in rendered
    assert "huanxin_training_job.sh" not in rendered
    assert "torchrun" not in rendered
    assert "tail -n 40 -- /tmp/qwen36-agentic.log" in commands[1][-1]


def test_quick_status_resolves_relative_log_against_remote_root() -> None:
    result = run_status(
        "--dry-run",
        "--remote-root",
        "/workspace/custom-quantum-gpt",
        "--log-path",
        "logs/run.log",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["commands"][0][3] == "ASI1"
    remote_command = payload["commands"][0][-1]
    assert "cd /workspace/custom-quantum-gpt" in remote_command
    assert "test -f /workspace/custom-quantum-gpt/logs/run.log" in remote_command
    assert "tail -n 80 -- /workspace/custom-quantum-gpt/logs/run.log" in remote_command


def test_quick_status_rejects_unbounded_tail() -> None:
    result = run_status("--dry-run", "--log-path", "/tmp/run.log", "--tail-lines", "501")

    assert result.returncode == 2
    assert "--tail-lines must be <= 500" in result.stderr
