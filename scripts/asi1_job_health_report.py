#!/usr/bin/env python3
"""Sample ASI1 job health fields and validate failure reports.

The module is intentionally dependency-free so it can run in local shells,
artifact fetch jobs, and constrained remote environments. It samples from
local process state plus optional artifact files, then writes stable JSON for
watchers and dashboards to consume without importing this code.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REQUIRED_HEALTH_FIELDS = (
    "pid_alive",
    "last_metric_age_sec",
    "last_log_age_sec",
    "disk_free",
    "checkpoint_age_sec",
)

REQUIRED_FAILURE_REPORT_FIELDS = (
    "timestamp_utc",
    "status",
    "run_id",
    "failure_kind",
    "message",
    "health",
)


def utc_now_iso(now: float | None = None) -> str:
    return datetime.fromtimestamp(time.time() if now is None else now, tz=timezone.utc).isoformat()


def load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        temp_name = handle.name
        handle.write(text)
    os.replace(temp_name, path)


def pid_alive(pid: int | None) -> bool | None:
    if pid is None:
        return None
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def path_age_sec(path: Path | None, *, now: float) -> float | None:
    if path is None or not path.exists():
        return None
    return max(0.0, now - path.stat().st_mtime)


def disk_free_payload(path: Path) -> dict[str, Any]:
    usage = shutil.disk_usage(path)
    return {
        "path": str(path),
        "bytes": usage.free,
        "total_bytes": usage.total,
        "used_bytes": usage.used,
        "percent_free": (usage.free / usage.total) if usage.total else None,
    }


def load_artifact_overrides(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    payload = load_json_object(path)
    allowed = set(REQUIRED_HEALTH_FIELDS) | {
        "remote_path",
        "run_id",
        "timestamp_utc",
        "source_artifact",
    }
    return {key: value for key, value in payload.items() if key in allowed}


def load_pid(path: Path | None) -> int | None:
    if path is None or not path.exists():
        return None
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return None
    try:
        return int(text)
    except ValueError as exc:
        raise ValueError(f"pid file must contain an integer: {path}") from exc


def sample_job_health(
    *,
    run_id: str,
    pid: int | None = None,
    pid_file: Path | None = None,
    metric_path: Path | None = None,
    log_path: Path | None = None,
    checkpoint_path: Path | None = None,
    disk_path: Path = Path("."),
    remote_path: str | None = None,
    artifact_path: Path | None = None,
    now: float | None = None,
) -> dict[str, Any]:
    sample_time = time.time() if now is None else now
    effective_pid = pid if pid is not None else load_pid(pid_file)
    health: dict[str, Any] = {
        "schema_version": 1,
        "timestamp_utc": utc_now_iso(sample_time),
        "run_id": run_id,
        "pid": effective_pid,
        "pid_alive": pid_alive(effective_pid),
        "last_metric_age_sec": path_age_sec(metric_path, now=sample_time),
        "last_log_age_sec": path_age_sec(log_path, now=sample_time),
        "disk_free": disk_free_payload(disk_path),
        "checkpoint_age_sec": path_age_sec(checkpoint_path, now=sample_time),
        "remote_path": remote_path,
        "sources": {
            "pid_file": str(pid_file) if pid_file is not None else None,
            "metric_path": str(metric_path) if metric_path is not None else None,
            "log_path": str(log_path) if log_path is not None else None,
            "checkpoint_path": str(checkpoint_path) if checkpoint_path is not None else None,
            "disk_path": str(disk_path),
            "artifact_path": str(artifact_path) if artifact_path is not None else None,
        },
    }

    overrides = load_artifact_overrides(artifact_path)
    if overrides:
        health.update(overrides)
        health["sources"]["artifact_path"] = str(artifact_path)
    if remote_path is not None:
        health["remote_path"] = remote_path
    return health


def validate_job_health(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_HEALTH_FIELDS:
        if field not in payload:
            errors.append(f"health missing field: {field}")
    if not isinstance(payload.get("run_id"), str) or not payload.get("run_id"):
        errors.append("health missing non-empty string field: run_id")
    if payload.get("pid_alive") not in (True, False, None):
        errors.append("health field pid_alive must be true, false, or null")
    disk_free = payload.get("disk_free")
    if not isinstance(disk_free, dict):
        errors.append("health field disk_free must be an object")
    elif not isinstance(disk_free.get("bytes"), int) or disk_free.get("bytes", -1) < 0:
        errors.append("health field disk_free.bytes must be a non-negative integer")
    for field in ("last_metric_age_sec", "last_log_age_sec", "checkpoint_age_sec"):
        value = payload.get(field)
        if value is not None and (
            not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0
        ):
            errors.append(f"health field {field} must be a non-negative number or null")
    remote_path = payload.get("remote_path")
    if remote_path is not None and not isinstance(remote_path, str):
        errors.append("health field remote_path must be a string or null")
    return errors


def build_failure_report(
    *,
    run_id: str,
    failure_kind: str,
    message: str,
    health: dict[str, Any],
    details: dict[str, Any] | None = None,
    now: float | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "timestamp_utc": utc_now_iso(now),
        "status": "failed",
        "run_id": run_id,
        "failure_kind": failure_kind,
        "message": message,
        "health": health,
        "details": details or {},
    }


def validate_failure_report(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_FAILURE_REPORT_FIELDS:
        if field not in payload:
            errors.append(f"failure_report missing field: {field}")
    if payload.get("status") != "failed":
        errors.append("failure_report field status must be 'failed'")
    for field in ("run_id", "failure_kind", "message", "timestamp_utc"):
        if not isinstance(payload.get(field), str) or not payload.get(field):
            errors.append(f"failure_report missing non-empty string field: {field}")
    health = payload.get("health")
    if not isinstance(health, dict):
        errors.append("failure_report field health must be an object")
    else:
        errors.extend(validate_job_health(health))
    if not isinstance(payload.get("details", {}), dict):
        errors.append("failure_report field details must be an object when present")
    return errors


def parse_details(raw: str | None) -> dict[str, Any] | None:
    if raw is None:
        return None
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("--details-json must decode to a JSON object")
    return payload


def add_sample_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--pid", type=int, default=None)
    parser.add_argument("--pid-file", type=Path, default=None)
    parser.add_argument("--metric-path", type=Path, default=None)
    parser.add_argument("--log-path", type=Path, default=None)
    parser.add_argument("--checkpoint-path", type=Path, default=None)
    parser.add_argument("--disk-path", type=Path, default=Path("."))
    parser.add_argument("--remote-path", default=None)
    parser.add_argument(
        "--artifact",
        type=Path,
        default=None,
        help="Optional JSON object with fetched health fields.",
    )
    parser.add_argument(
        "--output", type=Path, default=None, help="Write JSON to this path instead of stdout."
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    sample = subparsers.add_parser("sample", help="Sample job health and write JSON.")
    add_sample_args(sample)

    failure = subparsers.add_parser(
        "failure-report", help="Write a validated failure report JSON file."
    )
    add_sample_args(failure)
    failure.add_argument("--failure-kind", required=True)
    failure.add_argument("--message", required=True)
    failure.add_argument("--details-json", default=None)

    validate = subparsers.add_parser(
        "validate-failure-report", help="Validate an existing failure report JSON file."
    )
    validate.add_argument("path", type=Path)
    return parser


def emit_payload(payload: dict[str, Any], output: Path | None) -> None:
    if output is None:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        write_json_atomic(output, payload)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "validate-failure-report":
        payload = load_json_object(args.path)
        errors = validate_failure_report(payload)
        result = {"ok": not errors, "errors": errors, "path": str(args.path)}
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if not errors else 1

    health = sample_job_health(
        run_id=args.run_id,
        pid=args.pid,
        pid_file=args.pid_file,
        metric_path=args.metric_path,
        log_path=args.log_path,
        checkpoint_path=args.checkpoint_path,
        disk_path=args.disk_path,
        remote_path=args.remote_path,
        artifact_path=args.artifact,
    )
    health_errors = validate_job_health(health)
    if health_errors:
        print(
            json.dumps({"ok": False, "errors": health_errors}, indent=2, sort_keys=True),
            file=sys.stderr,
        )
        return 1

    if args.command == "sample":
        emit_payload(health, args.output)
        return 0

    if args.command == "failure-report":
        report = build_failure_report(
            run_id=args.run_id,
            failure_kind=args.failure_kind,
            message=args.message,
            health=health,
            details=parse_details(args.details_json),
        )
        errors = validate_failure_report(report)
        if errors:
            print(
                json.dumps({"ok": False, "errors": errors}, indent=2, sort_keys=True),
                file=sys.stderr,
            )
            return 1
        emit_payload(report, args.output)
        return 0

    raise AssertionError(f"unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
