from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "huanxin_upload_small_file.sh"


def test_upload_small_file_dry_run_renders_verified_command(tmp_path: Path) -> None:
    source = tmp_path / "probe.txt"
    source.write_text("hello ASI1\n", encoding="utf-8")

    result = subprocess.run(
        [
            "bash",
            str(SCRIPT),
            "--dry-run",
            "--env",
            "ASI1",
            "--source",
            str(source),
            "--remote-path",
            "/workspace/probes/probe.txt",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["env"] == "ASI1"
    assert payload["source"] == str(source)
    assert payload["remote_path"] == "/workspace/probes/probe.txt"
    assert payload["bytes"] == len("hello ASI1\n")
    assert len(payload["sha256"]) == 64
    assert payload["chunk_commands"] >= 3
    assert payload["remote_commands"]
    assert "mkdir -p /workspace/probes" in payload["remote_command"]
    assert "probe.txt.b64tmp" in payload["remote_commands"][1]
    assert (
        "base64 -d /workspace/probes/probe.txt.b64tmp > /workspace/probes/probe.txt"
        in payload["remote_commands"][-1]
    )
    assert "__HX_UPLOAD_LOCAL_SHA__" in payload["remote_commands"][-1]
    assert "__HX_UPLOAD_REMOTE_SHA__" in payload["remote_commands"][-1]
    assert "sha256sum /workspace/probes/probe.txt" in payload["remote_commands"][-1]


def test_upload_small_file_refuses_large_source(tmp_path: Path) -> None:
    source = tmp_path / "too-large.bin"
    source.write_bytes(b"x" * 5)

    result = subprocess.run(
        [
            "bash",
            str(SCRIPT),
            "--dry-run",
            "--env",
            "ASI1",
            "--source",
            str(source),
            "--remote-path",
            "/workspace/probes/too-large.bin",
            "--max-bytes",
            "4",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    assert "Refusing upload" in result.stderr
