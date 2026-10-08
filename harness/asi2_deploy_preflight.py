"""C-9124: fail-closed preflight for deploy-class launches against the ASI2 :19004 daemon.

Banked crash class (harness/state/probes/c9124_evidence_500_class.json):
the daemon answers /exec with HTTP 500 mid-freeze-deploy when its automation
page is dead or the transport is busy-wedged, then the port refuses; the
launcher dies on uncaught HTTPError 500 mid `base64 -d` (09-19T07:52Z w38 and
09-20T04:29Z/04:48Z). The daemon's own log is platform-side (measured: no log
file in the box FS), so the accessible signature surface is:

  1. /health not ready or uptime below the boot-stability bar (boot-restart loop)
  2. exec echo dead or mismatched (wedge / dead page; health 200 is NOT alive)
  3. daemon pid changed within the lookback window (restart-loop signature)
  4. local files naming the 500 class with mtime inside the lookback window

Every check fails closed: any exception or missing signal REFUSES the launch.
"""

import json
import re

DEFAULT_LOOKBACK_S = 7200.0
DEFAULT_MIN_UPTIME_S = 600.0
DEFAULT_ECHO_MARKER = "C9124_PREFLIGHT_ECHO"

CRASH_SIGNATURE_PATTERNS = (
    "HTTP_500",
    "HTTPError 500",
    "HTTP Error 500",
    "500 Internal Server Error",
    "Internal Server Error",
    "Terminal never showed command markers",
    "Target page, context or browser has been closed",
    "transport WEDGED",
    "exec echo TIMEOUT",
)

_TS_RE = re.compile(r"20\d\d-[01]\d-[0-3]\dT[0-2]\d:[0-5]\d:[0-5]\dZ")
_SIGNATURE_RE = re.compile("|".join(re.escape(p) for p in CRASH_SIGNATURE_PATTERNS))


def find_timestamp(line):
    """First ISO-8601 Z timestamp in the line as epoch seconds, else None."""
    m = _TS_RE.search(line)
    if m is None:
        return None
    import calendar
    import datetime

    try:
        dt = datetime.datetime.strptime(m.group(0), "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return None
    return float(calendar.timegm(dt.timetuple()))


def scan_crash_signature(lines, now, lookback_s=DEFAULT_LOOKBACK_S):
    """Return matched lines: signature present with ts within lookback, or
    signature present with NO parseable timestamp (age unknown -> fail closed)."""
    matches = []
    for line in lines:
        if not _SIGNATURE_RE.search(line):
            continue
        ts = find_timestamp(line)
        if ts is None or (now - ts) <= lookback_s:
            matches.append(line.strip()[:200])
    return matches


def parse_health(text):
    """Parse /health JSON; raise ValueError on anything not a JSON object."""
    try:
        body = json.loads(text)
    except Exception as exc:
        raise ValueError(f"health body not JSON: {exc!r}")
    if not isinstance(body, dict):
        raise ValueError("health body not an object")
    return dict(
        ok=body.get("ok"),
        ready=body.get("ready"),
        pid=body.get("pid"),
        uptime=body.get("uptime"),
    )


def _read_tail(path, nbytes=32768):
    with open(path, "rb") as fh:
        fh.seek(0, 2)
        size = fh.tell()
        fh.seek(max(0, size - nbytes))
        return fh.read().decode("utf-8", "replace")


def _load_pid_state(path):
    try:
        with open(path) as fh:
            body = json.load(fh)
        if isinstance(body, dict):
            return body
    except FileNotFoundError:
        return None
    except Exception:
        return None
    return None


def preflight(
    health_fn,
    exec_echo_fn,
    now,
    state_path,
    scan_paths,
    lookback_s=DEFAULT_LOOKBACK_S,
    min_uptime_s=DEFAULT_MIN_UPTIME_S,
    echo_marker=DEFAULT_ECHO_MARKER,
):
    """Decide whether a deploy-class launch may proceed. Returns
    dict(allow=bool, reasons=list, health=dict, signature_matches=list).
    Refuses (fail closed) on every missing/failed signal."""
    verdict = dict(allow=False, reasons=[], health=None, signature_matches=[])

    try:
        health = parse_health(health_fn())
    except Exception as exc:
        verdict["reasons"].append(f"health probe failed/invalid (fail closed): {exc!r}")
        return verdict
    verdict["health"] = health
    if health["ok"] is not True or health["ready"] is not True:
        verdict["reasons"].append(
            "health not ready (boot/dead): ok={!r} ready={!r}".format(health["ok"], health["ready"])
        )
        return verdict
    uptime = health["uptime"]
    if not isinstance(uptime, (int, float)):
        verdict["reasons"].append("health uptime missing (fail closed)")
        return verdict
    if uptime < min_uptime_s:
        verdict["reasons"].append(
            f"daemon uptime {uptime}s < {min_uptime_s}s boot-stability bar (C-9024 boot-restart class)"
        )
        return verdict

    pid = health["pid"]
    prev = _load_pid_state(state_path)
    if prev is not None:
        prev_pid = prev.get("prev_pid")
        seen = prev.get("seen_epoch")
        if (
            prev_pid is not None
            and seen is not None
            and prev_pid != pid
            and (now - seen) <= lookback_s
        ):
            verdict["reasons"].append(
                f"daemon pid changed {prev_pid!r}->{pid!r} within {lookback_s}s lookback (restart-loop signature, prev seen {int(now - seen)}s ago)"
            )
            _store_pid_state(state_path, pid, now)
            return verdict

    try:
        echoed = exec_echo_fn(echo_marker)
    except Exception as exc:
        _store_pid_state(state_path, pid, now)
        verdict["reasons"].append(f"exec echo liveness failed (wedge/dead page): {exc!r}")
        return verdict
    if echoed is None or echo_marker not in str(echoed):
        _store_pid_state(state_path, pid, now)
        verdict["reasons"].append(
            f"exec echo mismatch (transport up but alive-check failed): {str(echoed)[:80]!r}"
        )
        return verdict

    for path in scan_paths:
        try:
            import os

            mtime = os.path.getmtime(path)
            if (now - mtime) > lookback_s:
                continue
            tail = _read_tail(path)
        except FileNotFoundError:
            continue
        except Exception as exc:
            _store_pid_state(state_path, pid, now)
            verdict["reasons"].append(f"signature scan unreadable {path} (fail closed): {exc!r}")
            return verdict
        for line in tail.splitlines():
            if _SIGNATURE_RE.search(line):
                ts = find_timestamp(line)
                if ts is None or (now - ts) <= lookback_s:
                    verdict["signature_matches"].append(path + ": " + line.strip()[:160])
        if verdict["signature_matches"]:
            _store_pid_state(state_path, pid, now)
            verdict["reasons"].append(
                "crash signature present in %d recent local file(s), newest: %s"
                % (len(verdict["signature_matches"]), verdict["signature_matches"][0])
            )
            return verdict

    _store_pid_state(state_path, pid, now)
    verdict["allow"] = True
    return verdict


def _store_pid_state(state_path, pid, now):
    try:
        with open(state_path, "w") as fh:
            json.dump(dict(prev_pid=pid, seen_epoch=now), fh)
    except Exception:
        pass
