#!/usr/bin/env python3
"""daemon_reconciler.py — THE ONE per-daemon reconciler. Replaces competing supervisors.

Failure classes → exactly ONE remedy each. Never kills a booting daemon.
This absorbs transport fragility instead of amplifying it.

Usage:
    python3 harness/scripts/daemon_reconciler.py --box ASI3            # reconcile one
    python3 harness/scripts/daemon_reconciler.py --all                 # reconcile all 3
    python3 harness/scripts/daemon_reconciler.py --all --dry-run       # classify only
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys as _sys
import time
import urllib.error
import urllib.request
from pathlib import Path
import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from harness_config import get  # noqa: E402

_sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from harness_config import get  # noqa: E402

REPO = Path(__file__).resolve().parent.parent.parent
BOX_PORTS = get("box_ports")  # single source: harness_config.py
STATE_DIR = REPO / "harness" / "state" / "reconciler"

REMEDIES = {
    "healthy": "none",
    "booting": "wait",
    "conn_refused": "relaunch_daemon",
    "browser_closed": "relaunch_daemon",
    "auth_drift": "cookie_bridge",
    "unknown_error": "relaunch_after_threshold",
}

# bad_for_s thresholds before a remedy fires (seconds continuously in that class)
THRESHOLDS = {"conn_refused": 30, "browser_closed": 120, "unknown_error": 300}


def get_health(box: str, timeout: int = 5) -> dict | None:
    """Fetch /health. None = conn_refused. <8 lines."""
    port = BOX_PORTS[box]
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=timeout) as r:
            return json.loads(r.read())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None


def classify_health(h: dict | None) -> str:
    """Map health payload to failure class. <10 lines."""
    if h is None:
        return "conn_refused"
    state = h.get("startupState", "")
    if state == "ready":
        return "healthy"
    if state == "booting":
        return "booting"
    if state == "error":
        err = str(h.get("startupError", "") or "")
        if "closed" in err or "Target page" in err:
            return "browser_closed"
        if "login" in err.lower() or "auth" in err.lower():
            return "auth_drift"
        return "unknown_error"
    return "unknown_error"


def _load_state(box: str) -> dict:
    """<5 lines."""
    f = STATE_DIR / f"{box}.json"
    if f.exists():
        try:
            return json.loads(f.read_text())
        except Exception:
            pass
    return {"class": None, "since": None}


def _save_state(box: str, state: dict) -> None:
    """<4 lines."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    (STATE_DIR / f"{box}.json").write_text(json.dumps(state, indent=2))


def bad_for_s(box: str, cls: str) -> int:
    """Seconds continuously in this class. <10 lines."""
    state = _load_state(box)
    now = time.time()
    if state.get("class") != cls or state.get("since") is None:
        _save_state(box, {"class": cls, "since": now})
        return 0
    return int(now - state["since"])


def should_relaunch(cls: str, bad_for_s: int) -> bool:
    """Remedy gate. booting NEVER relaunches. <5 lines."""
    if cls == "booting":
        return False
    return cls in ("conn_refused", "browser_closed") and bad_for_s >= THRESHOLDS.get(cls, 10**9)


def relaunch_daemon(box: str) -> dict:
    """Relaunch via the keepalive script (single canonical path). <10 lines."""
    script = "/Users/daxu/software/quantum-gpt-new/scripts/huanxin_all_keepalive.sh"
    try:
        proc = subprocess.run(["bash", script], capture_output=True, text=True, timeout=120)
        return {"action": "relaunch_daemon", "exit": proc.returncode, "tail": proc.stdout[-200:]}
    except subprocess.TimeoutExpired:
        return {"action": "relaunch_daemon", "exit": -1, "tail": "TIMEOUT"}


def cookie_bridge(box: str) -> dict:
    """Auth drift → cookie bridge (not kill). <10 lines."""
    script = REPO / "scripts" / "sapo_huanxin_heartbeat.sh"
    try:
        proc = subprocess.run(["bash", str(script)], capture_output=True, text=True, timeout=120)
        return {"action": "cookie_bridge", "exit": proc.returncode}
    except subprocess.TimeoutExpired:
        return {"action": "cookie_bridge", "exit": -1}


def reconcile(box: str, dry_run: bool = False) -> dict:
    """One reconcile cycle for one box. <15 lines."""
    h = get_health(box)
    cls = classify_health(h)
    dur = bad_for_s(box, cls)
    remedy = REMEDIES[cls]
    result = {"box": box, "class": cls, "bad_for_s": dur, "remedy": remedy}
    if dry_run or cls in ("healthy", "booting", "auth_drift"):
        return result
    if should_relaunch(cls, dur):
        result.update(relaunch_daemon(box))
    return result


def main() -> None:
    """<12 lines."""
    ap = argparse.ArgumentParser(description="The ONE daemon reconciler")
    ap.add_argument("--box", choices=list(BOX_PORTS))
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    boxes = list(BOX_PORTS) if args.all or not args.box else [args.box]
    for box in boxes:
        r = reconcile(box, args.dry_run)
        print(
            f"CLASS: {r['class']}  REMEDY: {r['remedy']}  bad_for={r['bad_for_s']}s  box={r['box']}"
        )
        if r.get("action"):
            print(f"  ACTION: {r['action']} exit={r.get('exit')}")


if __name__ == "__main__":
    main()
