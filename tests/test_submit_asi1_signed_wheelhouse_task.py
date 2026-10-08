from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "submit_asi1_signed_wheelhouse_task.sh"


def test_signed_wheelhouse_requires_urls_for_launch_spec() -> None:
    result = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run", "__launch-spec"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "ASI1_ACCELERATE_WHEEL_URL" in result.stderr


def test_signed_wheelhouse_launch_spec_downloads_and_installs() -> None:
    result = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run", "__launch-spec"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={
            "ASI1_SIGNED_WHEELHOUSE_REMOTE_ROOT": "/remote/root",
            "ASI1_ACCELERATE_WHEEL_URL": "https://example.invalid/accelerate.whl?sig=1",
            "ASI1_PEFT_WHEEL_URL": "https://example.invalid/peft.whl?sig=2",
        },
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["remote_root"] == "/remote/root"
    assert "__ASI1_SIGNED_WHEELHOUSE_START__" in payload["remote_command"]
    assert "__ASI1_SIGNED_WHEELHOUSE_DONE__" in payload["remote_command"]
    assert "curl -fL --retry 3" in payload["remote_command"]
    assert "https://example.invalid/accelerate.whl?sig=1" in payload["remote_command"]
    assert "https://example.invalid/peft.whl?sig=2" in payload["remote_command"]
    assert (
        "python3 -m zipfile -t /tmp/asi1-wheelhouse/tools/wheels/accelerate-1.4.0-py3-none-any.whl"
        in payload["remote_command"]
    )
    assert (
        "python3 -m pip install --no-cache-dir --no-input --no-index --find-links /tmp/asi1-wheelhouse/tools/wheels accelerate==1.4.0 peft==0.14.0"
        in payload["remote_command"]
    )
    assert "import accelerate; import peft" in payload["remote_command"]
    assert "&&" not in payload["execution_command"]
