from __future__ import annotations

import json
import subprocess
from pathlib import Path

import scripts.collect_huanxin_environment_status as collector


def test_collect_environment_status_summarizes_huanxin_payload(monkeypatch) -> None:
    def fake_run(*args, **kwargs):  # type: ignore[no-untyped-def]
        payload = {
            "env_name": "ASI1",
            "summary": "safari_keepalive_and_browser_daemon_healthy",
            "train_dev_url": "https://example.invalid/train-dev/environment?name=ASI1",
            "keepalive": {"operational": True, "loaded": True, "recent_error": False},
            "browser_daemon": {
                "operational": True,
                "state": "healthy",
                "startup_state": "ready",
                "auth_state": "authenticated",
                "shell_endpoint_failure": False,
                "current_url": "https://example.invalid/train-dev/environment?name=ASI1",
            },
            "command_channel": {
                "recent_success": True,
                "transport": "standalone",
                "age_seconds": 12.0,
                "status_path": "/tmp/ASI1.json",
            },
            "local_ai2_jobs": {
                "job_count": 2,
                "recent_job_ids": ["job-a", "job-b"],
                "latest_job": {"job_id": "job-b"},
            },
            "diagnostics": {"shell_endpoint_summary": ""},
        }
        return subprocess.CompletedProcess(args[0], 0, json.dumps(payload), "")

    monkeypatch.setattr(collector.subprocess, "run", fake_run)

    payload = collector.collect_environment_status(["ASI1"], timeout_sec=1, include_raw=False)

    env = payload["environments"][0]
    assert env["env_name"] == "ASI1"
    assert env["browser_daemon_operational"] is True
    assert env["auth_state"] == "authenticated"
    assert env["command_channel_recent_success"] is True
    assert env["command_channel_transport"] == "standalone"
    assert env["keepalive_operational"] is True
    assert env["job_count"] == 2
    assert env["latest_job"] == {"job_id": "job-b"}
    assert "raw_status" not in env


def test_collect_environment_status_handles_timeout(monkeypatch) -> None:
    def fake_run(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise subprocess.TimeoutExpired(args[0], timeout=1, output="partial", stderr="slow")

    monkeypatch.setattr(collector.subprocess, "run", fake_run)

    payload = collector.collect_environment_status(["ASI1"], timeout_sec=1, include_raw=False)

    env = payload["environments"][0]
    assert env["summary"] == "status_unavailable"
    assert env["returncode"] is None
    assert env["browser_daemon_operational"] is False
    assert env["stdout_tail"] == "partial"
    assert env["stderr_tail"] == "slow"


def test_timeout_preserves_recent_command_channel_evidence(monkeypatch) -> None:
    def fake_run(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise subprocess.TimeoutExpired(args[0], timeout=1, output="", stderr="")

    monkeypatch.setattr(collector.subprocess, "run", fake_run)
    monkeypatch.setattr(
        collector,
        "load_command_channel",
        lambda env_name: {
            "recent_success": True,
            "transport": "standalone",
            "age_seconds": 9.0,
            "status_path": f"/tmp/{env_name}.json",
        },
    )

    payload = collector.collect_environment_status(["ASI1"], timeout_sec=1, include_raw=False)

    env = payload["environments"][0]
    assert env["summary"] == "status_unavailable"
    assert env["command_channel_recent_success"] is True
    assert env["command_channel_transport"] == "standalone"


def test_main_writes_status_json(tmp_path: Path, monkeypatch) -> None:
    def fake_collect(envs, *, timeout_sec, include_raw):  # type: ignore[no-untyped-def]
        return {
            "schema_version": 1,
            "generated_at_utc": "2026-05-26T00:00:00+00:00",
            "manual_mode": {"manual_mode": False, "automation_enabled": True},
            "environments": [{"env_name": envs[0], "summary": "ok"}],
        }

    output = tmp_path / "huanxin_environment_status.json"
    monkeypatch.setattr(collector, "collect_environment_status", fake_collect)
    monkeypatch.setattr(
        collector,
        "parse_args",
        lambda: type(
            "Args",
            (),
            {"envs": ["ASI1"], "timeout_sec": 1, "include_raw": False, "output": output},
        )(),
    )

    assert collector.main() == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["environments"][0]["env_name"] == "ASI1"
