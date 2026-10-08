#!/usr/bin/env python3
# ruff: noqa: UP038  # (X | Y) isinstance is py3.10-only; py3.9 .venv gate (precedent: training/grpo_trainer.py)
from __future__ import annotations  # py3.9-safe (PEP 604) annotations

"""sapo_wedge_watch.py — the daemon WEDGE detector (keepalive.md audit
2026-09-01: proposed detector never landed; the ASI3 busy-wedge class
recurred 23:06 with busyAgeMs 699,817 / pendingRequestCount 12).

Polls /health on the Huanxin daemon ports every poll-seconds and classifies
each daemon 3-state + wedge:

  ok      health responds, no wedge signals
  wedged  busy=true AND busyAgeMs > busy-age-ms-max (default 120000), OR
          pendingRequestCount > pending-max (default 3) — belt-and-suspenders
          over the 08-27 wedge fixes (EXEC_DEADLINE + lock watchdog)
  down    connection refused — the KEEPER's job to relaunch (never us)
  unknown health responds but the payload is unparseable — logged, never escalated

The detector ONLY ALARMS (one line per tick to /tmp/sapo_wedge_watch.log,
alarm lines also to /tmp/sapo_wedge_alarms.log). It NEVER kills or relaunches:
the ASI3 keeper auto-relaunches within ~90s; the eval agent owns ASI2.

Usage:
  python3 scripts/sapo_wedge_watch.py --ports 19005,19004,20646 \
      [--poll-seconds 60] [--once] [--log /tmp/sapo_wedge_watch.log]
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_BUSY_AGE_MS_MAX = 120_000
DEFAULT_PENDING_MAX = 3
DEFAULT_PORTS = (19005, 19004, 20646)
DEFAULT_POLL_SECONDS = 60.0
PROBE_TIMEOUT = 5.0

_TS_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


def now_ts() -> str:
    return datetime.now(timezone.utc).strftime(_TS_FORMAT)


def wedge_alarms(
    health: dict,
    busy_age_ms_max: int = DEFAULT_BUSY_AGE_MS_MAX,
    pending_max: int = DEFAULT_PENDING_MAX,
) -> list[str]:
    """Return the wedge alarm strings for one /health payload ([] = healthy).

    Conservative by design: missing/partial fields NEVER alarm (a parse
    failure is logged as UNKNOWN by the caller, not escalated into a kill).
    """
    alarms: list[str] = []
    busy = health.get("busy")
    if busy is True:
        age = health.get("busyAgeMs")
        if isinstance(age, (int, float)) and age > busy_age_ms_max:
            alarms.append(f"busy-wedge: busyAgeMs={int(age)} > {busy_age_ms_max}")
    pending = health.get("pendingRequestCount")
    if isinstance(pending, (int, float)) and pending > pending_max:
        alarms.append(f"backlog-wedge: pendingRequestCount={int(pending)} > {pending_max}")
    return alarms


def classify_health(
    health: dict,
    busy_age_ms_max: int = DEFAULT_BUSY_AGE_MS_MAX,
    pending_max: int = DEFAULT_PENDING_MAX,
) -> str:
    """\"ok\" | \"wedged\" — the only two states reachable from a parsed
    payload. (\"down\"/\"unknown\" are transport states, decided by the
    probe, not the payload.)"""
    return "wedged" if wedge_alarms(health, busy_age_ms_max, pending_max) else "ok"


def probe_health(base_url: str, timeout: float = PROBE_TIMEOUT) -> tuple[dict | None, str]:
    """GET <base_url>/health once. Returns (payload, state).

    state: \"ok\" (200 + JSON), \"down\" (connection refused),
    \"unknown\" (any other transport/parse failure). Never raises.
    """
    url = base_url.rstrip("/") + "/health"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:  # noqa: S310 - local daemon
            body = resp.read()
    except urllib.error.HTTPError as exc:
        # A real server answering with an error status = ALIVE, just not ok.
        try:
            payload = json.loads(exc.read())
            return payload, "ok"
        except Exception:
            return None, "unknown"
    except ConnectionRefusedError:
        return None, "down"
    except Exception:
        return None, "unknown"
    try:
        payload = json.loads(body)
    except Exception:
        return None, "unknown"
    if not isinstance(payload, dict):
        return None, "unknown"
    return payload, "ok"


class WedgeTracker:
    """Tracks consecutive wedge observations per port."""

    def __init__(self, consecutive_needed: int = 2) -> None:
        self.consecutive_needed = consecutive_needed
        self._counts: dict[int, int] = {}

    def should_remediate(self, port: int, is_wedged: object) -> bool:
        wedged = bool(is_wedged) or is_wedged == "unknown"
        if wedged:
            self._counts[port] = self._counts.get(port, 0) + 1
        else:
            self._counts[port] = 0
            return False
        if self._counts[port] >= self.consecutive_needed:
            self._counts[port] = 0
            return True
        return False


def remediation_command(port: int, env: str) -> str:
    """Build the kill+relaunch recipe for a wedged Huanxin daemon."""
    return (
        f"kill $(cat /tmp/huanxin-daemon-{env}.pid 2>/dev/null) 2>/dev/null; "
        f"rm -f /tmp/huanxin-daemon-{env}.pid; "
        f"FORGE_KC_CALLBACK=1 capture_chrome_fixed1 --env {env} --port {port}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ports", default=",".join(str(p) for p in DEFAULT_PORTS))
    parser.add_argument("--poll-seconds", type=float, default=DEFAULT_POLL_SECONDS)
    parser.add_argument("--once", action="store_true", help="probe every port once and exit")
    parser.add_argument("--log", default="/tmp/sapo_wedge_watch.log")
    parser.add_argument("--alarms-log", default="/tmp/sapo_wedge_alarms.log")
    args = parser.parse_args()

    ports = [int(p) for p in args.ports.split(",") if p.strip()]
    log_path = Path(args.log)
    alarms_path = Path(args.alarms_log)

    def emit(line: str, also_alarm: bool = False) -> None:
        line = f"{now_ts()} | {line}"
        print(line, flush=True)
        try:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with log_path.open("a", encoding="utf-8") as fh:
                fh.write(line + "\n")
            if also_alarm:
                with alarms_path.open("a", encoding="utf-8") as fh:
                    fh.write("ALARM " + line + "\n")
        except OSError:
            pass  # logging must never kill the watcher

    if args.once:
        for port in ports:
            payload, state = probe_health(f"http://127.0.0.1:{port}")
            alarms = wedge_alarms(payload) if payload is not None else []
            emit(f"port {port} state={state} alarms={alarms or 'none'}", also_alarm=bool(alarms))
        return 0

    emit(f"wedge watch armed: ports={ports} poll={args.poll_seconds}s (detector-only, never kills)")
    while True:
        for port in ports:
            payload, state = probe_health(f"http://127.0.0.1:{port}")
            alarms = wedge_alarms(payload) if payload is not None else []
            if alarms:
                emit(f"port {port} state={state} WEDGED: {'; '.join(alarms)}", also_alarm=True)
            else:
                emit(f"port {port} state={state} ok")
        time.sleep(max(args.poll_seconds, 5.0))


if __name__ == "__main__":
    sys.exit(main())
