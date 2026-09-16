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
    summary = f"READY /health ready=true pid={pid}" if pid else "READY /health ready=true"
    return {"status": "ready", "summary": summary}


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
