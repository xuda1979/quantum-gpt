#!/usr/bin/env python3
"""status_collectors.py — small focused collectors for system_status.

Each function <30 lines, returns a dict, finishes fast.
Box execs run in parallel to stay under 30s total.
"""

from __future__ import annotations

import concurrent.futures
import json
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
STATE = REPO / "harness" / "state"
BOX_PORTS = {"ASI1": 20646, "ASI2": 19004, "ASI3": 20653}


def _box_exec(box: str, cmd: str, timeout: int = 8) -> dict:
    """Single box exec round-trip. <8s timeout."""
    port = BOX_PORTS.get(box)
    if not port:
        return {"box": box, "status": "UNKNOWN"}
    try:
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/exec",
            data=json.dumps({"command": cmd}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            d = json.loads(r.read())
            return {"box": box, "status": "ALIVE" if d.get("commandOk") else "DEAD"}
    except Exception:
        return {"box": box, "status": "DOWN"}


def collect_boxes() -> dict:
    """All 3 box liveness in parallel. <10s total."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        futures = {pool.submit(_box_exec, box, "echo ALIVE"): box for box in BOX_PORTS}
        return {box: fut.result() for fut, box in futures.items()}


def collect_keeper() -> dict:
    """Keeper state from /tmp. <1s."""
    kp = Path("/tmp/session_keeper_state.json")
    if not kp.exists():
        return {"pid": None, "status": "NOT_FOUND"}
    try:
        d = json.loads(kp.read_text())
        return {"pid": d.get("pid"), "status": d.get("status"), "daemons": d.get("daemons")}
    except Exception:
        return {"pid": None, "status": "PARSE_FAILED"}


def collect_training() -> dict:
    """Training probe + stale detection. <1s."""
    tp = STATE / "probes" / "train.json"
    if not tp.exists():
        return {"probe_status": "NO_PROBE", "probe_stale": True}
    try:
        probe = json.loads(tp.read_text())
    except Exception:
        return {"probe_status": "PARSE_FAILED", "probe_stale": True}
    stale = _check_stale(probe.get("ts", ""))
    return {
        "probe_status": probe.get("status", "N/A"),
        "probe_stale": stale,
        "last_step": probe.get("last_checkpoint_step", "N/A"),
        "last_loss": probe.get("last_checkpoint_loss", "N/A"),
        "benchmark": probe.get("benchmark", "N/A").split("/")[-1]
        if probe.get("benchmark")
        else "N/A",
        "v10_gate": probe.get("fail_closed_gate", {}).get("v10_launch", "N/A"),
    }


def _check_stale(ts: str) -> bool:
    """Check if probe timestamp is >1h old. <6 lines."""
    if not ts:
        return True
    try:
        t = time.mktime(time.strptime(ts, "%Y-%m-%dT%H:%M:%SZ"))
        return time.time() - t > 3600
    except Exception:
        return True


def collect_queue() -> dict:
    """Queue stats from QUEUE.json. <1s."""
    qpath = STATE / "QUEUE.json"
    if not qpath.exists():
        return {"total_cards": 0, "by_status": {}, "running_cards": []}
    try:
        cards = json.loads(qpath.read_text()).get("cards", [])
    except Exception:
        return {"total_cards": 0, "by_status": {}, "running_cards": []}
    statuses: dict[str, int] = {}
    for c in cards:
        s = c.get("status", "?")
        statuses[s] = statuses.get(s, 0) + 1
    running = [
        {"id": c["id"], "lane": c["lane"], "title": c["title"][:80]}
        for c in cards
        if c.get("status") == "running"
    ]
    return {"total_cards": len(cards), "by_status": statuses, "running_cards": running}


def collect_eval() -> dict:
    """Best eval pass from verdicts. <1s."""
    vdir = STATE / "verdicts"
    best_n = 0
    total = 0
    if vdir.exists():
        for f in vdir.glob("*.json"):
            total += 1
            try:
                d = json.loads(f.read_text())
                m = re.match(r"(\d+)/", str(d.get("pass_adapter", "0/")))
                if m and int(m.group(1)) > best_n:
                    best_n = int(m.group(1))
            except Exception:
                pass
    return {"best_pass": f"{best_n}/18", "total_verdicts": total}


def _count_agents() -> int:
    """Count active claude agent processes. <8 lines."""
    proc = subprocess.run(["ps", "aux"], capture_output=True, text=True, timeout=5)
    return sum(
        1
        for line in proc.stdout.splitlines()
        if "claude" in line
        and ("--print" in line or "--bare" in line or "-p " in line)
        and "grep" not in line
    )


def _count_commits() -> tuple[int, list[str]]:
    """Count today's commits + recent 5. <8 lines."""
    today = time.strftime("%Y-%m-%d")
    proc = subprocess.run(
        ["git", "log", "--oneline", f"--since={today}T00:00:00"],
        capture_output=True,
        text=True,
        cwd=str(REPO),
        timeout=5,
    )
    count = len(proc.stdout.strip().splitlines()) if proc.stdout.strip() else 0
    recent = subprocess.run(
        ["git", "log", "--oneline", "-5"], capture_output=True, text=True, cwd=str(REPO), timeout=5
    )
    return count, recent.stdout.strip().splitlines()


def collect_activity() -> dict:
    """Commits + agents. <5s."""
    commits, recent = _count_commits()
    return {"commits_today": commits, "recent_commits": recent, "active_agents": _count_agents()}


def collect_tests() -> str:
    """Quick harness script test sample. <20s."""
    try:
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/test_harness_scripts.py",
                "-q",
                "--no-header",
                "--timeout",
                "15",
            ],
            capture_output=True,
            text=True,
            cwd=str(REPO),
            timeout=25,
        )
        for line in proc.stdout.splitlines():
            if "TESTSUITE_COUNTS" in line:
                return line.replace("TESTSUITE_COUNTS ", "")
        return "N/A"
    except Exception:
        return "TIMEOUT"
