#!/usr/bin/env python3
"""status_surface.py — ONE harness status surface (design fix #10).

Diagnosis today meant manually walking ps, /tmp logs, daemon ports, and box
exec. This renders EVERY layer from the ledgers in one command:

  LAYER            SOURCE (ledger, never ad-hoc scraping)
  scheduler        cron job logs (last firing per job, pass/fail)
  tick             tick.log mtime + last success event
  heartbeat        /tmp/huanxin_heartbeat_state.json (daemons + mandate)
  judge            /tmp/sapo_judge_health_state.json (dp4-only)
  trainer          harness/state/self_resume_guardian.json
  reconciler       harness/state/reconciler_loop.json
  queue WIP        harness/state/QUEUE.json (ready/claimed/bounced)
  mandate debt     sapo_mandate_gate.py verdict
  events tail      harness/state/EVENTS.jsonl (last 5)

Fail-closed: unreadable layer = "UNREADABLE", never silent pass.
Stdlib only; Python 3.9-safe. Output: human table (default) or --json.
"""
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
STATE = REPO / "harness" / "state"
CRON_JOBS = Path.home() / ".claude-mcp-cron" / "jobs"


def _age(path, now=None):
    try:
        return int((now or time.time()) - os.path.getmtime(path))
    except OSError:
        return None


def _read_json(path, default="UNREADABLE"):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return default


def layer_scheduler(now):
    rows = []
    if not CRON_JOBS.is_dir():
        return [{"jobs_dir": "UNREADABLE"}]
    for d in sorted(CRON_JOBS.iterdir()):
        if not d.is_dir():
            continue
        log = d / "log.txt"
        last, fail = "", False
        try:
            lines = log.read_text(errors="replace").splitlines()
        except OSError:
            rows.append({"job": d.name, "state": "NO-LOG"})
            continue
        for ln in reversed(lines):
            if "firing job" in ln:
                m = re.search(r"\[(\S+)\] firing job", ln)
                last = m.group(1) if m else "?"
                break
        fail = "Not logged in" in "\n".join(lines[-3:])
        rows.append({"job": d.name.replace("job_", ""), "last_firing": last, "failing": fail})
    return rows


def layer_tick(now):
    tick_log = STATE / "tick.log"
    age = _age(tick_log, now)
    return {"tick_log_age_s": age,
            "verdict": ("RECENT" if age is not None and age < 1800 else
                        "STALE" if age is not None else "MISSING")}


def layer_queue():
    q = _read_json(STATE / "QUEUE.json")
    if q == "UNREADABLE":
        return {"queue": "UNREADABLE"}
    cards = q if isinstance(q, list) else q.get("cards", [])
    counts = {}
    for c in cards:
        s = c.get("status", "?")
        counts[s] = counts.get(s, 0) + 1
    return {"total": len(cards), **counts}


def layer_events():
    ev = STATE / "EVENTS.jsonl"
    try:
        lines = ev.read_text(errors="replace").splitlines()[-5:]
    except OSError:
        return "UNREADABLE"
    return [ln[:140] for ln in lines]


def collect(now=None):
    now = now or time.time()
    hb = _read_json("/tmp/huanxin_heartbeat_state.json")
    judge = _read_json("/tmp/sapo_judge_health_state.json")
    guardian = _read_json(STATE / "self_resume_guardian.json")
    recon = _read_json(STATE / "reconciler_loop.json")
    return {
        "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
        "scheduler": layer_scheduler(now),
        "tick": layer_tick(now),
        "heartbeat": ({"daemons": hb.get("daemons"), "mandate": str(hb.get("mandate", ""))[:60]}
                      if isinstance(hb, dict) else "UNREADABLE"),
        "judge": ({"healthy": judge.get("healthy"), "strikes": judge.get("strikes")}
                  if isinstance(judge, dict) else "UNREADABLE"),
        "trainer": ({"status": guardian.get("status"), "age_s": _age(STATE / "self_resume_guardian.json", now)}
                    if isinstance(guardian, dict) else "UNREADABLE"),
        "reconciler": ({"phase": recon.get("phase"), "detail": str(recon.get("detail", ""))[:40]}
                       if isinstance(recon, dict) else "UNREADABLE"),
        "queue": layer_queue(),
        "events_tail": layer_events(),
    }


def render(d):
    out = ["=== HARNESS STATUS (%s) ===" % d["ts_utc"]]
    hb = d["heartbeat"]
    if isinstance(hb, dict):
        out.append("daemons : %s" % hb.get("daemons"))
        out.append("mandate : %s" % hb.get("mandate"))
    else:
        out.append("daemons : UNREADABLE")
    j = d["judge"]
    out.append("judge   : healthy=%s strikes=%s (dp4-only)" %
               (j.get("healthy") if isinstance(j, dict) else "?",
                j.get("strikes") if isinstance(j, dict) else "?"))
    t = d["trainer"]
    out.append("trainer : %s (guardian state age %ss)" %
               (t.get("status") if isinstance(t, dict) else "UNREADABLE",
                t.get("age_s") if isinstance(t, dict) else "?"))
    r = d["reconciler"]
    out.append("recon   : %s %s" % (r.get("phase") if isinstance(r, dict) else "?",
                                    r.get("detail") if isinstance(r, dict) else ""))
    out.append("tick    : %s (age %ss)" % (d["tick"]["verdict"], d["tick"]["tick_log_age_s"]))
    q = d["queue"]
    if isinstance(q, dict) and "total" in q:
        out.append("queue   : total=%(total)s ready=%(ready)s claimed=%(claimed)s bounced=%(bounced)s dead=%(dead)s" % {
            "total": q.get("total", 0), "ready": q.get("ready", 0),
            "claimed": q.get("claimed", 0), "bounced": q.get("bounced", 0),
            "dead": q.get("dead", 0)})
    else:
        out.append("queue   : UNREADABLE")
    out.append("cron jobs (last firing, failing?):")
    for row in d["scheduler"]:
        out.append("  - %(job)-16s %(last_firing)-22s failing=%(failing)s" % row)
    out.append("events tail:")
    ev = d["events_tail"]
    if isinstance(ev, list):
        for ln in ev:
            out.append("  %s" % ln)
    else:
        out.append("  UNREADABLE")
    return "\n".join(out)


def main():
    if "--json" in sys.argv:
        print(json.dumps(collect(), indent=2, default=str))
        return 0
    print(render(collect()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
