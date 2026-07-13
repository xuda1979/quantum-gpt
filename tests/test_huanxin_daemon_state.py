from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "huanxin_daemon_state.py"
SPEC = importlib.util.spec_from_file_location("huanxin_daemon_state", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_inspect_detects_stale_state_when_pid_and_processing_exist(tmp_path: Path) -> None:
    env = "AI"
    pid_file = tmp_path / f"huanxin-daemon-{env}.pid"
    port_file = tmp_path / f"huanxin-daemon-{env}.port"
    ipc_dir = tmp_path / f"huanxin-daemon-{env}.ipc"
    ipc_dir.mkdir()
    pid_file.write_text("999999\n", encoding="utf-8")
    port_file.write_text("59006\n", encoding="utf-8")
    (ipc_dir / "123.processing.json").write_text(
        '{"command":"echo hi","waitMs":1000}', encoding="utf-8"
    )

    payload = MODULE.inspect_state(env, tmp_path, 0.01)

    assert payload["stale_state_detected"] is True
    assert payload["daemon_process_alive"] is False
    assert payload["daemon_health_ok"] is False
    assert len(payload["processing_files"]) == 1


def test_cleanup_stale_moves_claim_and_writes_response(tmp_path: Path) -> None:
    env = "AI"
    pid_file = tmp_path / f"huanxin-daemon-{env}.pid"
    port_file = tmp_path / f"huanxin-daemon-{env}.port"
    ipc_dir = tmp_path / f"huanxin-daemon-{env}.ipc"
    ipc_dir.mkdir()
    pid_file.write_text("999999\n", encoding="utf-8")
    port_file.write_text("59006\n", encoding="utf-8")
    claim_path = ipc_dir / "123.processing.json"
    claim_path.write_text('{"command":"echo hi","waitMs":1000}', encoding="utf-8")

    payload = MODULE.cleanup_stale(env, tmp_path, 0.01)

    assert payload["action"] == "cleanup-stale"
    response_path = ipc_dir / "123.response.json"
    assert response_path.exists()
    response_payload = json.loads(response_path.read_text(encoding="utf-8"))
    assert response_payload["error"] == "stale_daemon_state_recovered"
    assert response_payload["command"] == "echo hi"
    assert not pid_file.exists()
    assert not port_file.exists()
    assert not claim_path.exists()
