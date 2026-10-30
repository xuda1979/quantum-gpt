#!/usr/bin/env python3
"""C-10610 — watch the IBM baseline battery on ASI2 and report progress.

Polls the box-side battery artifacts every POLL_S; appends a compact JSON
line to logs/c10610_battery_watch.log. Exits when DONE marker appears
(all 4 runs finished) or after MAX_POLL_H hours (fail-closed note).

Read-only on the box; never restarts anything.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "harness" / "scripts"))
from run_and_report import run_box  # noqa: E402

BOX = "ASI2"
BOX_ROOT = "/root/work/quantum-gpt"
OUT_BOX = BOX_ROOT + "/outputs/ibm_baseline_c10610"
LOG = REPO / "logs" / "c10610_battery_watch.log"
POLL_S = 900
MAX_POLL_H = 72
# Battery liveness: the inner bash chain stays alive across all 4 runs.
# If it is gone AND no DONE marker for STALE_ABSENT_POLLS consecutive
# successful polls, the battery died (e.g. another container restart)
# and no further progress is possible without operator relaunch.
STALE_ABSENT_POLLS = 3

RUNS = ["base_qhe", "base_hard", "champ_qhe", "champ_hard"]


def now_utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def emit(**kw) -> None:
    line = json.dumps(dict(ts_utc=now_utc(), **kw), ensure_ascii=False)
    print(line, flush=True)
    with LOG.open("a") as f:
        f.write(line + "\n")


def poll_once() -> dict | None:
    cmd = (
        f"ls {OUT_BOX}/DONE 2>/dev/null && echo BATTERY_DONE; "
        f"grep -c task_done {OUT_BOX}/battery.log 2>/dev/null; "
        f'grep -h \'"stage": "envelope_written"\' {OUT_BOX}/battery.log 2>/dev/null | wc -l; '
        f"tail -1 {OUT_BOX}/battery.log 2>/dev/null | head -c 200; "
        f"echo ---; "
        f"pgrep -f c10610_battery_inner.sh >/dev/null && echo BATTERY_ALIVE || echo BATTERY_GONE"
    )
    res = run_box(BOX, cmd, timeout=120)
    if res.get("status") != "PASS":
        return None
    out = (res.get("stdout") or "").strip().splitlines()
    alive = any("BATTERY_ALIVE" in ln for ln in out)
    done = any("BATTERY_DONE" in ln for ln in out[:1])
    tasks = 0
    envelopes = 0
    for ln in out:
        ln = ln.strip()
        if ln.isdigit() and int(ln) < 100000:
            if tasks == 0:
                tasks = int(ln)
            else:
                envelopes = int(ln)
                break
    last = ""
    for ln in out:
        if ln.strip() == "---":
            break
        last = ln
    return {
        "battery_done": done,
        "battery_alive": alive,
        "task_events": tasks,
        "envelopes": envelopes,
        "last": last[-160:],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--max-poll-h",
        type=float,
        default=MAX_POLL_H,
        help="give up after this many hours (default %(default)s)",
    )
    args = ap.parse_args()
    emit(stage="watch_start", box=BOX, poll_s=POLL_S, max_poll_h=args.max_poll_h)
    deadline = time.time() + args.max_poll_h * 3600
    absent_streak = 0
    last_tasks = -1
    while time.time() < deadline:
        d = poll_once()
        if d is None:
            emit(stage="poll_transport_flap")
        else:
            emit(stage="poll", **d)
            if d["battery_done"]:
                emit(stage="battery_complete")
                return 0
            if d["battery_alive"]:
                absent_streak = 0
            else:
                absent_streak += 1
                if absent_streak >= STALE_ABSENT_POLLS:
                    emit(stage="battery_stale_dead", absent_polls=absent_streak)
                    return 1
            if d["task_events"] == last_tasks and not d["battery_alive"]:
                # covered by absent_streak above; keep log explicit
                pass
            last_tasks = d["task_events"]
        time.sleep(POLL_S)
    emit(stage="watch_timeout_no_done_marker")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
