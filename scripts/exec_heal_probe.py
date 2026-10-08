#!/usr/bin/env python3
"""C-0008 (B-263): fail-closed /exec transport probe + heal-detect.

Four-state exec classification (healthy / wedged / down / unknown), the
health-ready-exec-wedged class name for the B-263 signature, and a durable
heal-detect state file recording HEALED / DEGRADED transitions between
invocations. UNKNOWN measurements are inert: they never create transitions
and never overwrite the last real state (fail closed).

CLI:
    python3 scripts/exec_heal_probe.py 20646 19004 20653 [--exec-timeout 10]
        [--state .sapo-loop/exec_heal_state.json]
Prints one JSON line per fleet member, then any transition record.
"""

from __future__ import annotations

import json
import pathlib
import socket
import sys
import time
import urllib.error
import urllib.request
import uuid

MARKER = "HXECHO-" + uuid.uuid4().hex[:12]
NAMES = dict([(20646, "ASI1"), (19004, "ASI2"), (20653, "ASI3")])
RC_TIMEOUT = 28
RC_REFUSED = 7


def echo_marker():
    return MARKER


def _rc_of(exc):
    if isinstance(exc, urllib.error.HTTPError):
        return int(exc.code)
    if isinstance(exc, urllib.error.URLError):
        reason = getattr(exc, "reason", None)
        if isinstance(reason, ConnectionRefusedError):
            return RC_REFUSED
        if isinstance(reason, socket.timeout) or isinstance(reason, TimeoutError):
            return RC_TIMEOUT
    if isinstance(exc, socket.timeout) or isinstance(exc, TimeoutError):
        return RC_TIMEOUT
    text = str(exc)
    if "timed out" in text or "timed out" in text.lower():
        return RC_TIMEOUT
    return -1


def _request(req, timeout):
    t0 = time.time()
    try:
        r = urllib.request.urlopen(req, timeout=timeout)
        return dict(
            rc=0, body=r.read().decode("utf-8", "replace"), latency_s=round(time.time() - t0, 3)
        )
    except Exception as e:
        return dict(rc=_rc_of(e), body="", err=repr(e)[:200], latency_s=round(time.time() - t0, 3))


def exec_roundtrip(port, exec_timeout=10.0, marker=None):
    marker = marker or MARKER
    payload = json.dumps(dict(command="echo " + marker)).encode()
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/exec",
        data=payload,
        headers=dict([("Content-Type", "application/json")]),
    )
    r = _request(req, exec_timeout)
    out = dict(rc=r["rc"], latency_s=r["latency_s"], marker=marker)
    if r["rc"] == 0:
        ok = marker in r["body"]
        out.update(dict(echo_ok=ok, body=r["body"][:200], state="healthy" if ok else "unknown"))
    elif r["rc"] == RC_TIMEOUT:
        out.update(dict(echo_ok=False, state="wedged"))
    elif r["rc"] == RC_REFUSED:
        out.update(dict(echo_ok=False, state="down"))
    else:
        out.update(dict(echo_ok=False, state="unknown", err=r.get("err", "")))
    return out


def health_probe(port, timeout=5.0):
    r = _request(f"http://127.0.0.1:{port}/health", timeout)
    out = dict(rc=r["rc"], latency_s=r["latency_s"])
    if r["rc"] == 0:
        try:
            parsed = json.loads(r["body"])
            out.update(
                dict(
                    body=parsed,
                    ready=bool(parsed.get("ready")),
                    startupState=parsed.get("startupState"),
                )
            )
        except Exception:
            out.update(dict(body=r["body"][:200], ready=None, startupState=None))
    else:
        out["err"] = r.get("err", "")
    return out


def probe_fleet_member(port, name=None, exec_timeout=10.0):
    h = health_probe(port)
    e = exec_roundtrip(port, exec_timeout=exec_timeout)
    if e["state"] == "healthy":
        klass = "healthy"
    elif e["state"] == "wedged" and h.get("ready"):
        klass = "health-ready-exec-wedged"
    elif e["state"] == "down" and h.get("rc") == RC_REFUSED:
        klass = "daemon-down"
    else:
        klass = "transport-degraded"
    out = dict(name=name or NAMES.get(port, str(port)), port=port, health=h, exec=e)
    out["class"] = klass
    return out


def record_state(path, states):
    """states: port-string -> state. Return first transition record or None.
    UNKNOWN is inert: no transition, no clobber of the last real state."""
    path = pathlib.Path(path)
    last = dict()
    history = []
    if path.exists():
        try:
            prior = json.loads(path.read_text(encoding="utf-8"))
            last = prior.get("last", dict()) or dict()
            history = prior.get("transitions", []) or []
        except Exception:
            last = dict()
    transitions = []
    for port in sorted(states, key=str):
        key = str(port)
        new = states[port]
        if new == "unknown":
            continue
        old = last.get(key)
        if old is not None and old != new:
            ttype = "HEALED" if new == "healthy" else "DEGRADED"
            transitions.append(
                dict(type=ttype, port=key, old=old, new=new, ts=round(time.time(), 3))
            )
        last[key] = new
    history = (history + transitions)[-50:]
    path.write_text(json.dumps(dict(last=last, transitions=history), indent=1), encoding="utf-8")
    return transitions[0] if transitions else None


def main(argv):
    ports = []
    exec_timeout = 10.0
    state_path = None
    i = 0
    args = list(argv)
    while i < len(args):
        a = args[i]
        if a == "--exec-timeout":
            i += 1
            exec_timeout = float(args[i])
        elif a == "--state":
            i += 1
            state_path = args[i]
        else:
            try:
                ports.append(int(a))
            except ValueError:
                print("bad port arg:", a)
                return 2
        i += 1
    if not ports:
        ports = [20646, 19004, 20653]
    states = dict()
    for p in ports:
        snap = probe_fleet_member(p, exec_timeout=exec_timeout)
        snap["ts"] = round(time.time(), 3)
        states[str(p)] = snap["exec"]["state"]
        print(json.dumps(snap))
    if state_path:
        t = record_state(state_path, states)
        if t:
            print(json.dumps(t))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
