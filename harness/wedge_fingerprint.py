"""C-9062: stale-code fingerprint for the huanxin browser daemons.

Compares each daemon process start time to the cure-file mtime
(huanxin_browser_daemon.js) and fails closed:

  POST-CURE   process_start > file_mtime   (STRICT: equal is NOT cured --
              a loader at the same timestamp cannot prove it saw the new
              bytes)
  STALE-CODE  process_start <= file_mtime  (loaded pre-cure source)
  UNKNOWN     pid / start / file-mtime missing or non-numeric -- never
              guessed, never coerced

Fleet rollup: "cured-fingerprint" only when there is at least one row and
EVERY row is post-cure; STALE-CODE when any row is stale; UNKNOWN otherwise
(including the empty fleet). Callers feed rows from `ps -o pid,lstart` and
the mtime from stat(2); the serving daemon (ASI3, port 20653) is the row the
after-cure requirement binds to.
"""

POST_CURE = "post-cure"
STALE_CODE = "stale-code"
UNKNOWN = "unknown"


def _num(value):
    """Return value as float iff it is a real number (bool excluded), else None."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def fingerprint_daemon(name, pid, start_epoch, file_mtime):
    """One daemon row -> dict(name, pid, start_epoch, verdict, reason)."""
    row = dict(name=name, pid=pid, start_epoch=start_epoch)
    start = _num(start_epoch)
    mt = _num(file_mtime)
    if pid is None or start is None:
        row["verdict"] = UNKNOWN
        row["reason"] = "pid/start unmeasured or non-numeric"
        return row
    if mt is None:
        row["verdict"] = UNKNOWN
        row["reason"] = "cure-file mtime unmeasured"
        return row
    if start > mt:
        row["verdict"] = POST_CURE
        row["reason"] = f"start {start} > mtime {mt}"
    else:
        row["verdict"] = STALE_CODE
        row["reason"] = f"start {start} <= mtime {mt} (strict > required)"
    return row


def fingerprint_fleet(rows, file_mtime):
    """rows: dicts with name/pid/start_epoch. Returns dict(table, fleet,
    stale_names). Fleet verdicts per module docstring; fail-closed."""
    table = [
        fingerprint_daemon(r.get("name"), r.get("pid"), r.get("start_epoch"), file_mtime)
        for r in rows
    ]
    stale_names = [r["name"] for r in table if r["verdict"] == STALE_CODE]
    if not table:
        fleet = UNKNOWN
    elif stale_names:
        fleet = STALE_CODE
    elif all(r["verdict"] == POST_CURE for r in table):
        fleet = "cured-fingerprint"
    else:
        fleet = UNKNOWN
    return dict(table=table, fleet=fleet, stale_names=stale_names)
