"""C-9106: Base-leg mid-leg slice-progress watch.

Fail-closed watcher for eval-leg run dirs: parses the eval_results.jsonl
step ladder (stage "step_begin" then "backward_done"), maintains a durable
per-slice status artifact, checks mtime liveness of the log, and raises a
NAMED alarm artifact (naming the run dir) on mid-leg death/stall or any
unknown state. NEVER re-launches: this module has no launch path
(C-9032 single-launch guard).

CLI:
    python3 harness/slice_watch.py --run-dir <dir> [--stale-s 900]
        [--state-dir harness/state/slice_watch] [--log-name eval_results.jsonl]

Exit codes: 0 = LIVE, 3 = ALARM (stall/death/unknown; fail closed).
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

DEFAULT_LOG_NAME = "eval_results.jsonl"
DEFAULT_STALE_S = 900  # 15 min without a new ladder line = stalled mid-leg
LADDER_BEGIN = "step_begin"
LADDER_DONE = "backward_done"


def _utc(ts):
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_ladder(log_path):
    """Return ({step: {"step_begin": bool, "backward_done": bool}}, n_lines).

    Tolerates non-JSON / partial trailing lines (buffered writer, B-222):
    they are skipped, never fatal.
    """
    slices = {}
    n = 0
    with open(log_path, encoding="utf-8", errors="replace") as f:
        for line in f:
            n += 1
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            stage = ev.get("stage")
            if stage not in (LADDER_BEGIN, LADDER_DONE):
                continue
            step = str(ev.get("step", "?"))
            sl = slices.setdefault(step, {"step_begin": False, "backward_done": False})
            if stage == LADDER_BEGIN:
                sl["step_begin"] = True
            else:
                sl["backward_done"] = True
    return slices, n


def _atomic_write_json(path, obj):
    """Durable write: fsync tmp file, then os.replace (never torn)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def watch(run_dir, state_dir, stale_s=DEFAULT_STALE_S, now=None, log_name=DEFAULT_LOG_NAME):
    """Watch one eval-leg run dir. Returns the summary dict.

    Fail-closed: a missing/unreadable log is verdict ALARM with kind
    "unknown_*" -- an unverifiable leg is never reported LIVE.
    """
    if now is None:
        now = datetime.now(timezone.utc).timestamp()
    run_name = os.path.basename(os.path.normpath(os.path.abspath(run_dir)))
    os.makedirs(state_dir, exist_ok=True)
    status_path = os.path.join(state_dir, f"leg_status_{run_name}.json")
    log_path = os.path.join(run_dir, log_name)

    base = {
        "card": "C-9106",
        "run_dir": os.path.abspath(run_dir),
        "checked_at": _utc(now),
        "stale_s": stale_s,
        "log_name": log_name,
    }

    if not os.path.isfile(log_path):
        summary = dict(
            base,
            verdict="ALARM",
            liveness="UNKNOWN",
            kind="unknown_missing_log",
            log_path=log_path,
            slices={},
            open_slices=[],
            done_slices=[],
            status_artifact=status_path,
        )
        _atomic_write_json(status_path, summary)
        _atomic_write_json(
            os.path.join(state_dir, f"ALARM_{run_name}_unknown.json"),
            dict(summary, reason="eval_results log absent; leg state unverifiable (fail closed)"),
        )
        return summary

    try:
        slices, n_lines = _parse_ladder(log_path)
        log_mtime = os.stat(log_path).st_mtime
    except OSError as exc:
        summary = dict(
            base,
            verdict="ALARM",
            liveness="UNKNOWN",
            kind="unknown_unreadable_log",
            error=str(exc),
            slices={},
            open_slices=[],
            done_slices=[],
            status_artifact=status_path,
        )
        _atomic_write_json(status_path, summary)
        _atomic_write_json(
            os.path.join(state_dir, f"ALARM_{run_name}_unknown.json"),
            dict(summary, reason=f"log unreadable: {exc}"),
        )
        return summary

    age_s = max(0.0, now - log_mtime)
    liveness = "LIVE" if age_s <= stale_s else "STALE"
    open_slices = sorted(
        s for s, sl in slices.items() if sl["step_begin"] and not sl["backward_done"]
    )
    done_slices = sorted(s for s, sl in slices.items() if sl["backward_done"])

    summary = dict(
        base,
        verdict="LIVE",
        liveness=liveness,
        kind="leg_progress",
        log_mtime=_utc(log_mtime),
        log_age_s=round(age_s, 1),
        lines=n_lines,
        slices=slices,
        open_slices=open_slices,
        done_slices=done_slices,
        status_artifact=status_path,
    )

    # Mid-leg death/stall: an open slice (step_begin with no backward_done)
    # on a log that has gone quiet past the stale bar.
    _atomic_write_json(status_path, summary)
    if open_slices and liveness == "STALE":
        summary["verdict"] = "ALARM"
        summary["kind"] = "stall_open_slice"
        joined = ",".join(open_slices)
        alarm = dict(
            summary,
            reason=(
                f"slices {joined} begun but not finished and log silent {age_s:.0f}s (> {stale_s}s)"
            ),
        )
        _atomic_write_json(os.path.join(state_dir, f"ALARM_{run_name}_stall.json"), alarm)
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="C-9106 slice-progress watch (fail-closed, never relaunches)"
    )
    default_state = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state", "slice_watch")
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--state-dir", default=default_state)
    ap.add_argument("--log-name", default=DEFAULT_LOG_NAME)
    ap.add_argument("--stale-s", type=int, default=DEFAULT_STALE_S)
    args = ap.parse_args(argv)
    summary = watch(args.run_dir, args.state_dir, stale_s=args.stale_s, log_name=args.log_name)
    opens = ",".join(summary.get("open_slices", [])) or "-"
    dones = ",".join(summary.get("done_slices", [])) or "-"
    print(
        f"C9106_WATCH verdict={summary['verdict']} kind={summary['kind']} "
        f"run_dir={summary['run_dir']} open={opens} done={dones} "
        f"liveness={summary['liveness']}"
    )
    return 0 if summary["verdict"] == "LIVE" else 3


if __name__ == "__main__":
    sys.exit(main())
