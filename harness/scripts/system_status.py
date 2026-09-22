#!/usr/bin/env python3
"""system_status.py — one-shot full system status. Reusable, never write again.

Usage:
    python3 harness/scripts/system_status.py            # human-readable
    python3 harness/scripts/system_status.py --json      # machine-readable
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
STATE = REPO / "harness" / "state"
BOX_PORTS = {"ASI1": 20646, "ASI2": 19004, "ASI3": 20653}


def box_exec(box: str, cmd: str, timeout: int = 10) -> dict:
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
            return {
                "box": box,
                "status": "ALIVE" if d.get("commandOk") else "DEAD",
                "output": (d.get("output") or "").strip()[:200],
            }
    except Exception:
        return {"box": box, "status": "DOWN"}


def collect():
    # --- BOXES ---
    boxes = {}
    for box in BOX_PORTS:
        boxes[box] = box_exec(box, "echo ALIVE")

    # --- KEEPER ---
    keeper = {}
    kp = Path("/tmp/session_keeper_state.json")
    if kp.exists():
        try:
            keeper = json.loads(kp.read_text())
        except Exception:
            pass

    # --- TRAINING PROBE ---
    probe = {}
    tp = STATE / "probes" / "train.json"
    if tp.exists():
        try:
            probe = json.loads(tp.read_text())
        except Exception:
            pass
    train_stale = False
    if probe.get("ts"):
        try:
            ts = time.mktime(time.strptime(probe["ts"], "%Y-%m-%dT%H:%M:%SZ"))
            if time.time() - ts > 3600:
                train_stale = True
        except Exception:
            pass

    # --- QUEUE ---
    q = {}
    cards = []
    if (STATE / "QUEUE.json").exists():
        try:
            q = json.loads((STATE / "QUEUE.json").read_text())
            cards = q.get("cards", [])
        except Exception:
            pass

    statuses = {}
    for c in cards:
        s = c.get("status", "?")
        statuses[s] = statuses.get(s, 0) + 1

    running = [c for c in cards if c.get("status") == "running"]

    # --- VERDICTS ---
    best_pass = "0/18"
    vdir = STATE / "verdicts"
    if vdir.exists():
        best_n = 0
        for f in vdir.glob("*.json"):
            try:
                d = json.loads(f.read_text())
                m = re.match(r"(\d+)/", str(d.get("pass_adapter", "0/")))
                if m and int(m.group(1)) > best_n:
                    best_n = int(m.group(1))
            except Exception:
                pass
        if best_n:
            best_pass = f"{best_n}/18"

    # --- COMMITS ---
    today = time.strftime("%Y-%m-%d")
    proc = subprocess.run(
        ["git", "log", "--oneline", f"--since={today}T00:00:00"],
        capture_output=True,
        text=True,
        cwd=str(REPO),
    )
    commits = len(proc.stdout.strip().splitlines()) if proc.stdout.strip() else 0
    recent = (
        subprocess.run(
            ["git", "log", "--oneline", "-5"], capture_output=True, text=True, cwd=str(REPO)
        )
        .stdout.strip()
        .splitlines()
    )

    # --- AGENTS ---
    proc = subprocess.run(["ps", "aux"], capture_output=True, text=True)
    agents = sum(
        1
        for line in proc.stdout.splitlines()
        if "claude" in line
        and ("--print" in line or "--bare" in line or "-p " in line)
        and "grep" not in line
    )

    # --- TESTS (quick sample) ---
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
    )
    test_line = "N/A"
    for line in proc.stdout.splitlines():
        if "TESTSUITE_COUNTS" in line:
            test_line = line.replace("TESTSUITE_COUNTS ", "")
            break

    return {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "boxes": boxes,
        "keeper": {
            "pid": keeper.get("pid"),
            "status": keeper.get("status"),
            "daemons": keeper.get("daemons"),
        },
        "training": {
            "probe_status": probe.get("status", "N/A"),
            "probe_stale": train_stale,
            "last_step": probe.get("last_checkpoint_step", "N/A"),
            "last_loss": probe.get("last_checkpoint_loss", "N/A"),
            "benchmark": probe.get("benchmark", "N/A").split("/")[-1]
            if probe.get("benchmark")
            else "N/A",
            "v10_gate": probe.get("fail_closed_gate", {}).get("v10_launch", "N/A"),
        },
        "queue": {
            "total_cards": len(cards),
            "by_status": statuses,
            "running_cards": [
                {"id": c["id"], "lane": c["lane"], "title": c["title"][:80]} for c in running
            ],
        },
        "eval": {
            "best_pass": best_pass,
            "total_verdicts": sum(1 for _ in vdir.glob("*.json")) if vdir.exists() else 0,
        },
        "commits_today": commits,
        "recent_commits": recent,
        "active_agents": agents,
        "harness_script_tests": test_line,
    }


def render(d: dict) -> str:
    lines = []
    lines.append("=" * 60)
    lines.append(f"SYSTEM STATUS — {d['timestamp']}")
    lines.append("=" * 60)

    lines.append("\n--- BOXES ---")
    for box, info in d["boxes"].items():
        lines.append(f"  {box}: {info['status']}")

    lines.append("\n--- KEEPER ---")
    k = d["keeper"]
    lines.append(f"  pid={k.get('pid')} status={k.get('status')} daemons={k.get('daemons')}")

    lines.append("\n--- TRAINING ---")
    t = d["training"]
    stale_flag = " ⚠️ STALE" if t["probe_stale"] else ""
    lines.append(f"  status: {t['probe_status']}{stale_flag}")
    lines.append(f"  last_step: {t['last_step']}  loss: {t['last_loss']}")
    lines.append(f"  benchmark: {t['benchmark']}")
    lines.append(f"  v10_gate: {t['v10_gate']}")

    lines.append("\n--- QUEUE ---")
    q = d["queue"]
    lines.append(f"  total: {q['total_cards']}  by_status: {q['by_status']}")
    for c in q["running_cards"]:
        lines.append(f"  RUNNING: {c['id']} [{c['lane']}] {c['title']}")

    lines.append("\n--- EVAL ---")
    lines.append(f"  best_pass: {d['eval']['best_pass']}  verdicts: {d['eval']['total_verdicts']}")

    lines.append("\n--- ACTIVITY ---")
    lines.append(f"  commits_today: {d['commits_today']}")
    lines.append(f"  active_agents: {d['active_agents']}")
    lines.append(f"  harness_tests: {d['harness_script_tests']}")
    lines.append("  recent_commits:")
    for c in d["recent_commits"]:
        lines.append(f"    {c}")

    lines.append("\n" + "=" * 60)
    # Health verdict
    all_alive = all(v["status"] == "ALIVE" for v in d["boxes"].values())
    verdict = "🟢 HEALTHY" if all_alive and not t["probe_stale"] else "🟡 DEGRADED"
    if not all_alive:
        verdict = "🔴 BOX DOWN"
    lines.append(f"VERDICT: {verdict}")
    lines.append("=" * 60)
    return "\n".join(lines)


if __name__ == "__main__":
    d = collect()
    if "--json" in sys.argv:
        print(json.dumps(d, indent=2, default=str))
    else:
        print(render(d))
