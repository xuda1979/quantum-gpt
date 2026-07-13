from __future__ import annotations

import json
import shlex
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "submit_asi1_embedded_wheelhouse_task.sh"


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


def test_asi1_embedded_wheelhouse_defaults_to_fill_only() -> None:
    command = _dry_run()

    assert command[:2] == ["node", str(ROOT / "browser-automation" / "huanxin_submit_task_run.js")]
    assert "--submit" not in command

    by_flag = dict(zip(command, command[1:], strict=False))
    assert "name=ASI1" in by_flag["--url"]
    assert by_flag["--task-name"] == "asi1-wheel-embed"
    assert by_flag["--remote-root"] == "/workspace/quantum-gpt"
    assert by_flag["--launcher-script"] == str(SCRIPT)
    assert by_flag["--launcher-arg"] == "__launch-spec"


def test_asi1_embedded_wheelhouse_only_submits_when_requested() -> None:
    command = _dry_run("--submit")
    assert "--submit" in command


def test_asi1_embedded_wheelhouse_launch_spec_embeds_and_installs_wheels() -> None:
    result = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run", "__launch-spec"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={"ASI1_EMBEDDED_WHEELHOUSE_REMOTE_ROOT": "/remote/root"},
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["remote_root"] == "/remote/root"
    assert payload["job_name"] == "asi1-embedded-wheelhouse"
    assert "__ASI1_EMBEDDED_WHEELHOUSE_START__" in payload["remote_command"]
    assert "__ASI1_EMBEDDED_WHEELHOUSE_DONE__" in payload["remote_command"]
    assert "accelerate-1.4.0-py3-none-any.whl" in payload["remote_command"]
    assert "peft-0.14.0-py3-none-any.whl" in payload["remote_command"]
    assert "python3 scripts/append_text_file.py" in payload["remote_command"]
    assert "python3 scripts/decode_base64_file.py" in payload["remote_command"]
    assert "python3 -m zipfile -t" in payload["remote_command"]
    assert (
        "python3 -m pip install --no-cache-dir --no-input --no-index --find-links "
        "/tmp/asi1-wheelhouse/tools/wheels accelerate==1.4.0 peft==0.14.0"
    ) in payload["remote_command"]
    assert "import accelerate; import peft" in payload["remote_command"]
    assert "&&" not in payload["execution_command"]
    assert "\n" not in payload["execution_command"]
    assert ">" not in payload["execution_command"]
    assert "&" not in payload["execution_command"]
    assert "cd /remote/root" in payload["execution_command"]
