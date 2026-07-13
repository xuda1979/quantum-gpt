from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "fetch_asi1_agentic_run_artifacts.sh"


def test_fetch_asi1_artifacts_dry_run_uses_one_shell_call(tmp_path: Path) -> None:
    local_output = tmp_path / "run"

    result = subprocess.run(
        [
            "bash",
            str(SCRIPT),
            "--dry-run",
            "--env",
            "ASI1",
            "--remote-output-dir",
            "outputs/agentic-run",
            "--local-output-dir",
            str(local_output),
            "--log-path",
            "/tmp/agentic-run.log",
            "--tail-lines",
            "80",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["env"] == "ASI1"
    assert payload["remote_dir"] == "/workspace/quantum-gpt/outputs/agentic-run"
    assert payload["local_output_dir"] == str(local_output)
    assert payload["log_path"] == "/tmp/agentic-run.log"
    assert payload["tail_lines"] == 80

    shell_command = payload["shell_command"]
    assert shell_command[:3] == ["bash", "scripts/huanxin_env_shell.sh", "--env"]
    assert shell_command[3] == "ASI1"
    assert "__HX_ARTIFACT_BUNDLE_BEGIN__" in payload["remote_command"]
    assert "train_log_tail.txt" in payload["remote_command"]
    assert "checkpoint_history.jsonl" in payload["remote_command"]
    assert "latest_checkpoint_artifact" in payload["remote_command"]
    assert "huanxin_fetch_small_file.sh" not in payload["remote_command"]


def test_fetch_asi1_artifacts_rejects_unbounded_log_tail(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            "bash",
            str(SCRIPT),
            "--dry-run",
            "--remote-output-dir",
            "outputs/agentic-run",
            "--local-output-dir",
            str(tmp_path / "run"),
            "--tail-lines",
            "2001",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2
    assert "--tail-lines must be <= 2000" in result.stderr
