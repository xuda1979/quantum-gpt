#!/usr/bin/env python3
"""Collect local Huanxin environment status for the training dashboard."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "reports" / "huanxin_environment_status.json"
COMMAND_CHANNEL_MAX_AGE_SEC = 1800.0


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json_object(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        temp_name = handle.name
        handle.write(text)
    os.replace(temp_name, path)


def run_status(
    env_name: str, *, timeout_sec: int
) -> tuple[dict[str, Any] | None, str, str, int | None]:
    try:
        completed = subprocess.run(
            ["bash", "scripts/huanxin_status.sh", env_name],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=timeout_sec,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return None, exc.stdout or "", exc.stderr or "", None

    stdout = completed.stdout.strip()
    payload: dict[str, Any] | None = None
    if stdout:
        try:
            decoded = json.loads(stdout)
            payload = decoded if isinstance(decoded, dict) else None
        except json.JSONDecodeError:
            start = stdout.find("{")
            end = stdout.rfind("}")
            if start != -1 and end != -1 and start < end:
                try:
                    decoded = json.loads(stdout[start : end + 1])
                    payload = decoded if isinstance(decoded, dict) else None
                except json.JSONDecodeError:
                    payload = None
    return payload, completed.stdout, completed.stderr, completed.returncode


def manual_mode_payload(root: Path) -> dict[str, Any]:
    lock_path = root / ".huanxin_manual_mode"
    enable_path = root / ".huanxin_automation_enabled"
    return {
        "manual_mode": lock_path.exists(),
        "automation_enabled": enable_path.exists() and not lock_path.exists(),
        "lock_path": str(lock_path),
        "enable_path": str(enable_path),
    }


def load_command_channel(env_name: str) -> dict[str, Any]:
    path = ROOT / ".huanxin_shell_connections" / f"{env_name}.json"
    payload = load_json_object(path) or {}
    timestamp = payload.get("recorded_at_utc")
    age_seconds: float | None = None
    if timestamp:
        try:
            parsed = datetime.fromisoformat(str(timestamp).replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            age_seconds = max(
                0.0, (datetime.now(timezone.utc) - parsed.astimezone(timezone.utc)).total_seconds()
            )
        except ValueError:
            age_seconds = None
    recent_success = (
        bool(payload.get("ok"))
        and bool(payload.get("command_ok"))
        and (age_seconds is None or age_seconds <= COMMAND_CHANNEL_MAX_AGE_SEC)
    )
    return {
        "recent_success": recent_success,
        "transport": payload.get("transport"),
        "age_seconds": age_seconds,
        "status_path": str(path),
    }


def summarize_env(
    env_name: str,
    status_payload: dict[str, Any] | None,
    *,
    returncode: int | None,
    stdout: str,
    stderr: str,
    command_channel_fallback: dict[str, Any] | None = None,
) -> dict[str, Any]:
    fallback = command_channel_fallback or {}
    if status_payload is None:
        return {
            "env_name": env_name,
            "summary": "status_unavailable",
            "returncode": returncode,
            "browser_daemon_operational": False,
            "auth_state": "unknown",
            "shell_endpoint_failure": False,
            "command_channel_recent_success": bool(fallback.get("recent_success")),
            "command_channel_transport": fallback.get("transport"),
            "command_channel_age_seconds": fallback.get("age_seconds"),
            "command_channel_status_path": fallback.get("status_path"),
            "keepalive_operational": False,
            "job_count": 0,
            "latest_job": None,
            "raw_status": None,
            "stdout_tail": stdout[-4000:],
            "stderr_tail": stderr[-4000:],
        }

    browser_daemon = dict(status_payload.get("browser_daemon") or {})
    command_channel = dict(status_payload.get("command_channel") or {})
    if not command_channel.get("recent_success") and fallback.get("recent_success"):
        command_channel = fallback
    keepalive = dict(status_payload.get("keepalive") or {})
    jobs = dict(status_payload.get("local_ai2_jobs") or {})
    diagnostics = dict(status_payload.get("diagnostics") or {})
    return {
        "env_name": env_name,
        "summary": status_payload.get("summary") or "unknown",
        "returncode": returncode,
        "train_dev_url": status_payload.get("train_dev_url"),
        "browser_daemon_operational": bool(browser_daemon.get("operational")),
        "browser_daemon_state": browser_daemon.get("state"),
        "startup_state": browser_daemon.get("startup_state"),
        "auth_state": browser_daemon.get("auth_state") or "unknown",
        "current_url": browser_daemon.get("current_url"),
        "shell_endpoint_failure": bool(browser_daemon.get("shell_endpoint_failure")),
        "shell_endpoint_summary": diagnostics.get("shell_endpoint_summary"),
        "command_channel_recent_success": bool(command_channel.get("recent_success")),
        "command_channel_transport": command_channel.get("transport"),
        "command_channel_age_seconds": command_channel.get("age_seconds"),
        "command_channel_status_path": command_channel.get("status_path"),
        "keepalive_operational": bool(keepalive.get("operational")),
        "keepalive_loaded": bool(keepalive.get("loaded")),
        "keepalive_recent_error": bool(keepalive.get("recent_error")),
        "job_count": jobs.get("job_count", 0),
        "recent_job_ids": jobs.get("recent_job_ids") or [],
        "latest_job": jobs.get("latest_job"),
        "latest_fast_iteration_job": jobs.get("latest_fast_iteration_job"),
        "raw_status": status_payload,
    }


def collect_environment_status(
    envs: list[str], *, timeout_sec: int, include_raw: bool
) -> dict[str, Any]:
    manual = manual_mode_payload(ROOT)
    environments: list[dict[str, Any]] = []
    for env_name in envs:
        payload, stdout, stderr, returncode = run_status(env_name, timeout_sec=timeout_sec)
        summary = summarize_env(
            env_name,
            payload,
            returncode=returncode,
            stdout=stdout,
            stderr=stderr,
            command_channel_fallback=load_command_channel(env_name),
        )
        if not include_raw:
            summary.pop("raw_status", None)
        environments.append(summary)

    return {
        "schema_version": 1,
        "generated_at_utc": utc_now_iso(),
        "manual_mode": manual,
        "environments": environments,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--env",
        action="append",
        dest="envs",
        default=[],
        help="Huanxin environment name to collect.",
    )
    parser.add_argument("--timeout-sec", type=int, default=20)
    parser.add_argument("--include-raw", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    envs = args.envs or ["ASI1", "AI"]
    payload = collect_environment_status(
        envs, timeout_sec=max(args.timeout_sec, 1), include_raw=args.include_raw
    )
    write_json_atomic(args.output, payload)
    print(json.dumps({"ok": True, "output": str(args.output), "envs": envs}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
