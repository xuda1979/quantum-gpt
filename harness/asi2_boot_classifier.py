"""C-9024: ASI2 :19004 stuck-boot classifier (deploy-integrity lane).

Classifies the eval-box boot failure from >=10 min of /health snapshots:
  STALL_SAME_PID     same daemon pid, uptime monotonic and consistent with
                     the wall-clock span -> one resident process stuck
                     booting (not restarting).
  BOOT_RESTART_LOOP  pid changed, or uptime reset -> daemon/env restarting
                     in a loop. Platform signature 170022 (B-187): console-
                     gated, no local restart cures it.
  READY              ready=true observed.
  UNKNOWN            transport gap, window < min span, or malformed /
                     inconsistent snapshot. Fail-closed: never guess.

Precedent (SAPO standup #430): ASI2 loop confirmed by pid 73113->51740 with
uptime reset to 1s; ASI1 same-pid monotonic uptime classified NOT a loop.
"""

import argparse
import json
import time
import urllib.request

MIN_SPAN_S = 600
READY = "READY"
STALL_SAME_PID = "STALL_SAME_PID"
BOOT_RESTART_LOOP = "BOOT_RESTART_LOOP"
UNKNOWN = "UNKNOWN"


def probe_health(port, timeout=6):
    """One /health snapshot, or None when transport is unavailable."""
    url = "http://127.0.0.1:" + str(port) + "/health"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            d = json.loads(r.read().decode("utf-8", "replace"))
    except Exception:
        return None
    return {
        "ts": time.time(),
        "pid": d.get("pid"),
        "uptime": d.get("uptime"),
        "ready": bool(d.get("ready")),
        "startupState": d.get("startupState"),
    }


def classify(probes, min_span_s=MIN_SPAN_S):
    """Classify a probe series. Fail-closed to UNKNOWN on any doubt."""
    if not probes or any(p is None for p in probes):
        return UNKNOWN
    if len(probes) < 2 or any(not isinstance(p, dict) for p in probes):
        return UNKNOWN
    first, last = probes[0], probes[-1]
    for p in (first, last):
        for k in ("ts", "pid", "uptime"):
            if p.get(k) is None:
                return UNKNOWN
    span = last["ts"] - first["ts"]
    if span < min_span_s:
        return UNKNOWN
    if last["ready"]:
        return READY
    if last["pid"] != first["pid"]:
        return BOOT_RESTART_LOOP
    if last["uptime"] < first["uptime"]:
        return BOOT_RESTART_LOOP
    # Same pid: uptime must advance with the wall clock, else the counter
    # (and therefore the same-pid evidence) is unreliable.
    if last["uptime"] - first["uptime"] >= span * 0.5:
        return STALL_SAME_PID
    return UNKNOWN


def main(argv=None):
    ap = argparse.ArgumentParser(description="classify ASI2 stuck-boot vs restart loop")
    ap.add_argument("--port", type=int, default=19004)
    ap.add_argument("--state", default=None, help="snapshot json (prior probe in, new probe out)")
    ap.add_argument("--min-span", type=int, default=MIN_SPAN_S)
    args = ap.parse_args(argv)

    now = probe_health(args.port)
    prev = None
    if args.state:
        try:
            with open(args.state) as f:
                prev = json.load(f)
        except Exception:
            prev = None
        if now is not None:
            with open(args.state, "w") as f:
                json.dump(now, f)
    probes = [p for p in (prev, now) if p is not None]
    span = (probes[-1]["ts"] - probes[0]["ts"]) if len(probes) == 2 else 0
    verdict = classify(probes, args.min_span)
    print(
        json.dumps(
            {
                "verdict": verdict,
                "port": args.port,
                "prev": prev,
                "now": now,
                "span_s": round(span, 1),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
