"""Repair-sidecar liveness guard (guardian alarm 8, 2026-08-26).

Defect class: the repair sidecar (scripts/fv_gspo_repair_sidecar.sh) can die
SILENTLY at/near launch (SIGKILL from box-prep cleanup loops is untrappable;
SIGHUP/transport kills leave no trace), the repair queue starves, and the
``all_fail_without_repair`` circuit breaker stops the run hours later with no
operator-visible cause. Runs 11 and 12 died exactly this way (sidecar log
frozen right after the startup line, pidfile left behind, zero error output).

This module is the guard: a cheap, dependency-free check the trainer (boot +
per step) and the launcher/ops scripts (sapo_ensure_repair_sidecar.sh) call to
decide whether the sidecar is alive. "Alive" means:

* the pidfile (<OUT>/repair_sidecar.pid) exists and carries a live pid, AND
* the sidecar log heartbeats (mtime within ``max_log_age_seconds``) — the
  sidecar appends a line every poll, so a fresh log proves the loop is running.

A process that is alive but whose log went stale is "wedged" (sleep-loop
killed mid-cycle would keep the pid alive for a while, or the process is
stuck) and alarms too. A missing log is tolerated while the pid is alive
(log path conventions differ between launcher generations).

The CLI prints JSON, so bash (the ensure script) and Python (the trainer)
share one implementation.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any

# Sidecar default poll is 60s (REPAIR_POLL_SECONDS). Allow ~5 polls to lapse
# before declaring the heartbeat stale; tolerant of slow disks/lane pauses.
DEFAULT_MAX_LOG_AGE_SECONDS = 300

# Alarm marker used by the trainer log and the ensure script; grep-able.
ALARM_MARKER = "SIDECAR_DEAD_ALARM"
ALIVE_MARKER = "SIDECAR_ALIVE"

# Statuses returned in the status dict.
STATUS_ALIVE = "alive"
STATUS_MISSING_PIDFILE = "missing_pidfile"
STATUS_DEAD_PID = "dead_pid"
STATUS_STALE_LOG = "stale_log"


def _pid_is_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        # Exists but owned by another user: treat as alive (zombie pids get
        # ProcessLookupError; permission errors imply a live process).
        return True
    return True


def default_sidecar_log_path(output_dir: str | os.PathLike[str]) -> Path:
    """Best-effort default sidecar log: logs/sapo_27b_ai/repair_sidecar_<suffix>.log.

    Mirrors the launcher convention RUN_ID=<OUT basename minus the
    "sapo-27b-ai-" prefix>; falls back to <output_dir>/repair_sidecar.log.
    """
    out = Path(output_dir)
    name = out.name
    suffix = name
    for prefix in ("sapo-27b-ai-", "grpo-27b-selfeval-", "sapo-27b-asi3-"):
        if name.startswith(prefix):
            suffix = name[len(prefix) :]
            break
    candidate = Path("logs") / "sapo_27b_ai" / f"repair_sidecar_{suffix}.log"
    if candidate.exists() or candidate.parent.exists():
        return candidate
    return out / "repair_sidecar.log"


def check_sidecar_liveness(
    pid_file: str | os.PathLike[str],
    log_file: str | os.PathLike[str] | None = None,
    *,
    max_log_age_seconds: int = DEFAULT_MAX_LOG_AGE_SECONDS,
    now: float | None = None,
) -> dict[str, Any]:
    """Evaluate repair-sidecar liveness from pidfile + log heartbeat.

    Returns a dict with keys:
        status: one of STATUS_* above
        alarm: bool — True whenever the sidecar is NOT provably alive
        alive: bool — status == STATUS_ALIVE
        pid_file_exists, pid, process_alive, log_file_exists,
        log_age_seconds (None when no log), alarm_reason (human-readable)

    The check never raises: on unexpected errors it returns
    status="unknown" with alarm=False (a guard bug must not false-alarm a
    healthy run; the error is surfaced in ``alarm_reason``).
    """
    now = time.time() if now is None else now
    try:
        pid_path = Path(pid_file)
        pid_file_exists = pid_path.exists()
        pid: int | None = None
        if pid_file_exists:
            try:
                pid = int(pid_path.read_text(encoding="utf-8").strip() or "0")
            except (OSError, ValueError):
                pid = None

        log_age: float | None = None
        log_file_exists = False
        if log_file:
            log_path = Path(log_file)
            log_file_exists = log_path.exists()
            if log_file_exists:
                log_age = max(0.0, now - log_path.stat().st_mtime)

        if not pid_file_exists or pid is None:
            return _result(
                STATUS_MISSING_PIDFILE,
                alarm=True,
                pid_file_exists=pid_file_exists,
                pid=pid,
                process_alive=False,
                log_file_exists=log_file_exists,
                log_age_seconds=log_age,
                alarm_reason=(
                    f"pidfile {pid_path} missing/empty — sidecar never started "
                    "or was SIGKILLed before writing it"
                ),
            )

        process_alive = _pid_is_alive(pid)
        if not process_alive:
            return _result(
                STATUS_DEAD_PID,
                alarm=True,
                pid_file_exists=True,
                pid=pid,
                process_alive=False,
                log_file_exists=log_file_exists,
                log_age_seconds=log_age,
                alarm_reason=(
                    f"pidfile pid {pid} is not alive — silent death (SIGKILL/"
                    "hangup leaves no error); queue will starve the "
                    "all_fail_without_repair breaker"
                ),
            )

        if log_file_exists and log_age is not None and log_age > max_log_age_seconds:
            return _result(
                STATUS_STALE_LOG,
                alarm=True,
                pid_file_exists=True,
                pid=pid,
                process_alive=True,
                log_file_exists=True,
                log_age_seconds=log_age,
                alarm_reason=(
                    f"pid {pid} alive but sidecar log {log_path} last written "
                    f"{log_age:.0f}s ago (> {max_log_age_seconds}s) — wedged "
                    "or heartbeating into a different log"
                ),
            )

        return _result(
            STATUS_ALIVE,
            alarm=False,
            pid_file_exists=True,
            pid=pid,
            process_alive=True,
            log_file_exists=log_file_exists,
            log_age_seconds=log_age,
            alarm_reason=None,
        )
    except Exception as exc:  # pragma: no cover - guard must not raise
        return {
            "status": "unknown",
            "alarm": False,
            "alive": False,
            "pid_file_exists": False,
            "pid": None,
            "process_alive": False,
            "log_file_exists": False,
            "log_age_seconds": None,
            "alarm_reason": f"liveness check error: {exc!r}",
        }


def _result(
    status: str,
    *,
    alarm: bool,
    pid_file_exists: bool,
    pid: int | None,
    process_alive: bool,
    log_file_exists: bool,
    log_age_seconds: float | None,
    alarm_reason: str | None,
) -> dict[str, Any]:
    return {
        "status": status,
        "alarm": alarm,
        "alive": status == STATUS_ALIVE,
        "pid_file_exists": pid_file_exists,
        "pid": pid,
        "process_alive": process_alive,
        "log_file_exists": log_file_exists,
        "log_age_seconds": log_age_seconds,
        "alarm_reason": alarm_reason,
    }


def alarm_line(status: Mapping[str, Any]) -> str:
    """One grep-able line for the train log / ensure script."""
    if status.get("alarm"):
        return (
            f"[{ALARM_MARKER}] repair sidecar NOT alive: "
            f"status={status.get('status')} pid={status.get('pid')} "
            f"pidfile_exists={status.get('pid_file_exists')} "
            f"process_alive={status.get('process_alive')} "
            f"log_file_exists={status.get('log_file_exists')} "
            f"log_age_seconds={status.get('log_age_seconds')} — "
            f"{status.get('alarm_reason') or 'no reason'}"
        )
    return (
        f"[{ALIVE_MARKER}] repair sidecar alive: pid={status.get('pid')} "
        f"status={status.get('status')}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pidfile", required=True, help="sidecar pidfile path")
    parser.add_argument("--log", default=None, help="sidecar log path (heartbeat)")
    parser.add_argument(
        "--max-age",
        type=int,
        default=DEFAULT_MAX_LOG_AGE_SECONDS,
        help="max log age in seconds before the heartbeat is stale",
    )
    args = parser.parse_args(argv)
    status = check_sidecar_liveness(
        args.pidfile,
        args.log,
        max_log_age_seconds=args.max_age,
    )
    print(json.dumps(status, sort_keys=True))
    return 0 if status.get("alive") else 1


if __name__ == "__main__":
    raise SystemExit(main())
