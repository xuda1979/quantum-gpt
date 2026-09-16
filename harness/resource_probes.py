"""Fail-closed resource probes for the QG harness (cards C-0024/C-0008 lineage).

Three-state rule (skill §5.4.1): every probe returns ALIVE ("ready") on positive
evidence only; transport death, non-200, empty output, and parse failure are all
UNKNOWN — never "dead", never absent. A resource not reported is a resource not
verified; these probes feed harness/state/probes/*.json and the standup renderer.

Production defaults: health via urllib against the box daemon port; the trainer
probe requires an injected exec transport (the trainer-ops lane provides it via
box /exec) — without one the trainer is UNKNOWN, never assumed healthy.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request

DAEMON_PORTS = {"asi1": 20646, "asi2": 19004, "asi3": 20653}
TRAINER_PS_CMD = "ps -eo pid,etimes,args | grep -E 'grpo_trainer\\.py' | grep -v grep | head -3"

# B-263 heal-detect thresholds (C-0008): /health ready=true does NOT certify
# the /exec transport. Measured 2026-09-16: ASI1/ASI3 sat ready with a stuck
# busy exec slot while the pending queue only grew; every /exec echo timed out.
WEDGE_BUSY_AGE_MS = 120_000  # busy exec slot stuck >= 2 min with no completion
WEDGE_PENDING_MIN = 25  # pending queue flood; a healthy daemon drains it
BOOT_STUCK_UPTIME_S = 420  # normal boot is ~4-5 min; still booting past this = stuck


def classify_transport(health):
    """Classify a parsed /health body (B-263 heal-detect, C-0008).

    /health ready=true does NOT certify the /exec transport: a daemon can sit
    ready with a permanently-stuck busy exec slot while its pending queue only
    grows (measured ASI1/ASI3 2026-09-16). Returns dict(status, evidence) with
    status in: ready | exec_wedged | boot_failed | boot_stuck | booting | unknown.
    """
    ev = dict()
    try:
        ev["startupState"] = health.get("startupState")
        ev["ready"] = bool(health.get("ready"))
        ev["uptime_s"] = health.get("uptime")
        ev["busy"] = bool(health.get("busy"))
        ev["busyAgeMs"] = health.get("busyAgeMs")
        ev["pendingRequestCount"] = health.get("pendingRequestCount")
        ev["lastCommandStartedAt"] = health.get("lastCommandStartedAt")
        ev["lastCommandCompletedAt"] = health.get("lastCommandCompletedAt")
    except AttributeError:
        return dict(status="unknown", evidence=ev)
    if ev["startupState"] == "error":
        return dict(status="boot_failed", evidence=ev)
    if ev["startupState"] == "booting":
        up = ev["uptime_s"] or 0
        stuck = up > BOOT_STUCK_UPTIME_S
        return dict(status="boot_stuck" if stuck else "booting", evidence=ev)
    if not ev["ready"]:
        return dict(status="unknown", evidence=ev)
    slot_done = ev["lastCommandCompletedAt"] is not None
    age_ok = isinstance(ev["busyAgeMs"], int | float)
    stall = ev["busy"] and not slot_done and age_ok and ev["busyAgeMs"] >= WEDGE_BUSY_AGE_MS
    pend = ev["pendingRequestCount"]
    flood = isinstance(pend, int | float) and pend >= WEDGE_PENDING_MIN
    stuck = stall or flood
    if stuck:
        return dict(status="exec_wedged", evidence=ev)
    return dict(status="ready", evidence=ev)


def _default_health(port, timeout=6):
    url = f"http://127.0.0.1:{port}/health"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return {"code": resp.status, "body": resp.read(65536).decode("utf-8", "replace")}
    except (urllib.error.URLError, OSError, ValueError) as exc:
        return {"code": None, "body": "", "error": str(exc)[:120]}


def _unknown(what, detail):
    return {"status": "unknown", "summary": f"UNKNOWN ({what}: {detail})"}


def probe_daemon(name, port, health_fn=None):
    """Probe one box daemon. 200 + parseable body -> ready; anything else unknown."""
    fn = health_fn or _default_health
    try:
        r = fn(port)
    except Exception as exc:  # probe must never raise
        return _unknown("health probe raised", str(exc)[:120])
    code = r.get("code")
    body = r.get("body") or ""
    if code != 200:
        detail = "transport error" if code is None else f"HTTP {code}"
        extra = r.get("error")
        return _unknown("health non-200", detail if not extra else f"{detail} ({extra})")
    try:
        data = json.loads(body)
        ready = bool(data.get("ready"))
        pid = data.get("pid")
    except ValueError:
        ready, pid = None, None
    if ready is None:
        return _unknown("health body unparseable", body[:60])
    if not ready:
        return {"status": "unknown", "summary": "UNKNOWN (daemon reachable, ready=false)"}
    # B-263: /health liveness does not certify /exec. A ready daemon with a
    # stuck busy exec slot renders UNKNOWN (exec_wedged), never READY.
    cls = classify_transport(data)
    if cls["status"] == "exec_wedged":
        ev = cls["evidence"]
        return dict(
            status="unknown",
            transport=cls,
            summary=(
                "UNKNOWN (ready-but-exec_wedged: busyAgeMs={} pendingRequestCount={} "
                "lastCommandCompletedAt=null)"
            ).format(ev.get("busyAgeMs"), ev.get("pendingRequestCount")),
        )
    summary = f"READY /health ready=true pid={pid}" if pid else "READY /health ready=true"
    out = dict(status="ready", summary=summary, transport=cls)
    # positive liveness term (C-0030): the pid the daemon reported over the
    # wire; without one, the observed 200+ready=true is the positive term.
    out["liveness"] = dict(term="health_pid", pid=pid) if pid else dict(term="health_200_ready")
    return out


def probe_trainer(port, exec_fn=None):
    """Probe the ASI3 trainer via an exec transport. Positive ps evidence -> ready.

    Exec failure or EMPTY output -> UNKNOWN (an empty ps could be a transport
    truncation artifact; fail-closed never reports a confident 'no trainer').
    """
    if exec_fn is None:
        return _unknown("no exec transport configured", "trainer probe needs exec_fn")
    try:
        out = exec_fn(port, TRAINER_PS_CMD)
    except Exception as exc:
        return _unknown("exec transport died", str(exc)[:120])
    lines = [ln.strip() for ln in (out or "").splitlines() if ln.strip()]
    if not lines:
        return _unknown("ps empty (possible truncation)", "no trainer pid evidence")
    m = re.match(r"^(\d+)\s+(\d+)\s+(.*)$", lines[0])
    if not m:
        return _unknown("ps unparseable", lines[0][:80])
    pid = int(m.group(1))
    return {
        "status": "ready",
        "summary": f"READY trainer pid={pid} ({m.group(3)[:48]})",
        "liveness": {"term": "ps_pid", "pid": pid},
    }


def run_all(state_dir, health_fn=None, trainer_exec=None, now=None):
    """Probe every provisioned resource, write probes/<name>.json, return payloads.

    Durable-state contract: each file carries ts, status, summary; the standup
    renderer (qgh._probe_results) reads exactly these.
    """
    from harness_lib import now_iso, save_json

    payloads = {}
    for name, port in DAEMON_PORTS.items():
        payloads[name] = probe_daemon(name, port, health_fn=health_fn)
    payloads["trainer"] = probe_trainer(DAEMON_PORTS["asi3"], exec_fn=trainer_exec)
    out_dir = os.path.join(state_dir, "probes")
    os.makedirs(out_dir, exist_ok=True)
    for name, p in payloads.items():
        rec = {"ts": now or now_iso(), "status": p.get("status"), "summary": p.get("summary")}
        if "liveness" in p:
            rec["liveness"] = p["liveness"]
        save_json(os.path.join(out_dir, f"{name}.json"), rec)
    return payloads


def box_exec(port, cmd, timeout=90):
    """Real exec transport: POST to the box daemon /exec API (body key: command)."""
    payload = json.dumps(dict(command=cmd)).encode()
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/exec",
        data=payload,
        headers=dict([("Content-Type", "application/json")]),
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        d = json.loads(resp.read().decode("utf-8", "replace"))
    out = d.get("output", d)
    if isinstance(out, dict):
        out = out.get("output", "")
    return str(out)


def _default_exec_post(port, payload, timeout):
    """POST helper for probe_exec_echo; returns (status, body) for classification."""
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/exec",
        data=payload,
        headers=dict([("Content-Type", "application/json")]),
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return dict(status=resp.status, body=resp.read(65536).decode("utf-8", "replace"))


def probe_exec_echo(port, post_fn=None, timeout=10, marker=None):
    """The C-0008/B-263 acceptance instrument: POST `echo <marker>` and require
    the marker back within `timeout` seconds.

    rc=0 only on a verified roundtrip (unique marker echoed back). A timeout is
    UNKNOWN (rc=1) — never "dead"; a wrong output is FAIL (rc=1). Every call
    generates a fresh marker so a wedged daemon replaying a cached echo cannot
    pass the second probe.
    """
    import time
    import uuid

    marker = marker or (f"ECHO_{uuid.uuid4().hex[:12].upper()}")
    fn = post_fn or _default_exec_post
    payload = json.dumps(dict(command="echo " + marker)).encode()
    t0 = time.monotonic()
    try:
        r = fn(port, payload, timeout)
        elapsed = time.monotonic() - t0
        body = r.get("body", "") if isinstance(r, dict) else str(r)
        try:
            d = json.loads(body)
            out = d.get("output", d)
            if isinstance(out, dict):
                out = out.get("output", "")
        except ValueError:
            out = body
        out = str(out).strip()
        if marker in out:
            return dict(
                rc=0,
                marker=marker,
                output=out,
                elapsed_s=round(elapsed, 3),
                summary=f"OK echo roundtrip {elapsed:.2f}s marker={marker}",
            )
        return dict(
            rc=1,
            marker=marker,
            output=out,
            elapsed_s=round(elapsed, 3),
            summary=f"FAIL marker missing from output within {timeout:.1f}s",
        )
    except Exception as exc:
        elapsed = time.monotonic() - t0
        return dict(
            rc=1,
            marker=marker,
            elapsed_s=round(elapsed, 3),
            summary=f"UNKNOWN (exec echo transport: {str(exc)[:100]})",
        )


if __name__ == "__main__":
    # CLI runner so any tick/agent can refresh the standup RESOURCES probes:
    #   /usr/bin/python3 harness/resource_probes.py
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    state = os.environ.get("QGH_STATE_DIR") or os.path.join(repo, "harness", "state")
    payloads = run_all(state, trainer_exec=box_exec)
    for name in sorted(payloads):
        p = payloads[name]
        print("{} {} {}".format(name, p.get("status"), p.get("summary")))
