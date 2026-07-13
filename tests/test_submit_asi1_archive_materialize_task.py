from __future__ import annotations

import json
import shlex
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "submit_asi1_archive_materialize_task.sh"


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


def test_asi1_archive_materialize_wrapper_accepts_runtime_bundle_options() -> None:
    command = _dry_run(
        "--task-name",
        "asi1-bdl-test",
        "--remote-root",
        "/root/work",
        "--dest-dir",
        "/root/work/quantum-gpt",
        "--archive-object",
        "software/quantum-gpt/artifacts/runtime-bundles/qg.tar.gz",
        "--archive-name",
        "qg.tar.gz",
        "--archive-sha256",
        "abc123",
        "--extract-mode",
        "direct",
    )

    by_flag = dict(zip(command, command[1:], strict=False))
    assert command[:2] == ["node", str(ROOT / "browser-automation" / "huanxin_submit_task_run.js")]
    assert "--submit" not in command
    assert "name=ASI1" in by_flag["--url"]
    assert by_flag["--task-name"] == "asi1-bdl-test"
    assert by_flag["--remote-root"] == "/root/work"
    assert by_flag["--launcher-script"] == str(SCRIPT)
    assert by_flag["--launcher-arg"] == "__launch-spec"


def test_asi1_archive_materialize_direct_launch_spec_has_no_head_precheck() -> None:
    env = {
        "ASI1_ARCHIVE_REMOTE_ROOT": "/root/work",
        "ASI1_ARCHIVE_DEST_DIR": "/root/work/quantum-gpt",
        "ASI1_ARCHIVE_OBJECT": "software/quantum-gpt/artifacts/runtime-bundles/qg_asi1_training_bundle.tar.gz",
        "ASI1_ARCHIVE_NAME": "qg_asi1_training_bundle.tar.gz",
        "ASI1_ARCHIVE_SHA256": "dc2605c3da9f222bc69636e534430e3311e1a4a7b31b40a55da50f0ab247c0f7",
        "ASI1_ARCHIVE_EXTRACT_MODE": "direct",
        "ASI1_ARCHIVE_SIGNED_URL": "https://example.invalid/qg_asi1_training_bundle.tar.gz?sig=1",
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
    assert payload["remote_root"] == "/root/work"
    assert payload["extract_mode"] == "direct"
    command = payload["remote_command"]
    assert "curl -fsSI" not in command
    assert "--retry 5 --connect-timeout 30 --max-time 300" in command
    assert "tar -xzf qg_asi1_training_bundle.tar.gz -C /root/work/quantum-gpt" in command
    assert 'mv -f "$f" scripts/' in command
    assert "cp -R benchmarks/. evals/benchmarks/" in command
    assert "test -f scripts/run_asi1_agentic_grpo_from_env.sh" in command
    assert "test -f training/agentic_grpo_trainer.py" in command
    assert "test -f evals/benchmarks/agentic_coding_trajectory_training_v1.txt" in command
    assert "du -sh extracted" not in command
