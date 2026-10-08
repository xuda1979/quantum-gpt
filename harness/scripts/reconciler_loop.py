#!/usr/bin/env python3
"""reconciler_loop.py — run daemon_reconciler every 30s. THE standing supervisor.

Replaces: session_keeper daemon-restart role, heartbeat daemon-restart role,
keepalive restarts. One reconciler, failure-class remedies, never storms.

Usage:
    nohup python3 harness/scripts/reconciler_loop.py &
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO / "harness" / "scripts" / "daemon_reconciler.py"
STATE = REPO / "harness" / "state" / "reconciler_loop.json"


def write_state(phase: str, detail: str = "") -> None:
    """<4 lines."""
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(
        json.dumps({"phase": phase, "detail": detail, "ts": time.strftime("%H:%M:%S")})
    )


def main() -> None:
    """<12 lines."""
    write_state("starting")
    cycle = 0
    while True:
        cycle += 1
        try:
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "--all"], capture_output=True, text=True, timeout=180
            )
            write_state("running", f"cycle={cycle} exit={proc.returncode}")
        except subprocess.TimeoutExpired:
            write_state("reconcile_timeout", f"cycle={cycle}")
        except Exception as e:
            write_state("error", str(e)[:100])
        time.sleep(30)


if __name__ == "__main__":
    main()
