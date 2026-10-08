"""Trainer silent-death detector (B-150) -- the DETECTION half of skill 5.4.1.

Measured failure 2026-09-13 (tick #382): run sapo-27b-ai-20260913T112337Z stopped
ungracefully at step 29 (resume_state `sigterm_save: false`, saved 13:32:27Z) and
NOTHING detected it. The trainer was absent from the /proc of all three containers,
yet the only watcher on the run -- the judge watcher -- could not flag it, because
its `live_run_dir()` CORRECTLY returns UNKNOWN for an absent trainer and so only
logged "queue-run: live run undetermined" every cycle. A correct UNKNOWN is not an
alarm. The death sat unnoticed for 13+ minutes.

This module is deliberately a pure, importable policy with no process spawning and
no launch/stop surface: relaunching training is USER-GATED by the standing order
("Harness is FULLY AUTOMATIC — trainer relaunch is auto-gated on TDD green + sha-verify", .sapo-loop/STATUS.md), so this
lane raises the RED signal and the harness auto-relaunches with TDD fix + sha-verify.

Three-state contract (skill 5.4.1 -- never let transport failure read as death):
  ALIVE   -- a resident trainer process, or metrics advancing inside the budget
  DEAD    -- no resident process AND metrics stale past the budget
  UNKNOWN -- the transport failed; carries no opinion about the trainer

Only DEAD accumulates strikes. UNKNOWN never does. Two consecutive DEAD reads
(two positive absence signals) raise the alarm; the alarm fires once per death
episode so a persistent death cannot spam the log the manager has to read.
"""
import json
import os
import tempfile

VERDICTS = ("ALIVE", "DEAD", "UNKNOWN")


def classify(metrics_age_s, proc_alive, stale_after_s, transport_error=None):
    """Map one probe to exactly one verdict (never a boolean, never a guess).

    metrics_age_s : seconds since `grpo_step_metrics.jsonl` last advanced, or None
    proc_alive    : True / False / None (None = the probe could not tell)
    stale_after_s : the liveness budget in seconds
    """
    if transport_error:
        return "UNKNOWN"
    if proc_alive is None:
        return "UNKNOWN"
    if proc_alive:
        # The process is resident: a long step legitimately holds metrics still.
        return "ALIVE"
    if proc_alive is False:
        # A POSITIVE ABSENCE about the process is stronger evidence than any
        # metrics reading, so it is DEAD on its own. Downgrading it to UNKNOWN
        # when the metrics file is unreadable handed the detector exactly the
        # blind spot it exists to close: the process is gone, the run dir may be
        # gone with it, and the one signal that knows so is the process probe.
        # Measured 2026-09-13 while wiring the poller: the first probe
        # implementation returned (False, None, None) and classified UNKNOWN.
        return "DEAD"
    if metrics_age_s is None:
        return "UNKNOWN"
    if metrics_age_s > stale_after_s:
        return "DEAD"
    return "ALIVE"


class LivenessState:
    """Consecutive-death strike counter with a once-per-episode alarm."""

    def __init__(self, stale_after_s=180.0, strikes_to_alarm=2):
        self.stale_after_s = float(stale_after_s)
        self.strikes_to_alarm = int(strikes_to_alarm)
        self.strikes = 0
        self.alarmed = False
        self.run_dir = ""
        self.last_verdict = ""
        self.last_alarm = None

    def observe(self, verdict, run_dir="", now=0.0, metrics_age_s=None):
        """Record one verdict. Returns True on the single transition that fires."""
        if verdict not in VERDICTS:
            raise ValueError(f"unknown verdict {verdict!r}")
        if verdict == "DEAD":
            if run_dir and run_dir != self.run_dir:
                # A NEW run directory is a NEW subject: never inherit its strike
                # count, and never carry an old alarm across the change.
                self.strikes = 0
                self.alarmed = False
                self.last_alarm = None
            self.run_dir = run_dir or self.run_dir
            self.strikes += 1
            fired = False
            if self.strikes >= self.strikes_to_alarm and not self.alarmed:
                self.alarmed = True
                fired = True
                self.last_alarm = {
                    "run_dir": self.run_dir,
                    "strikes": self.strikes,
                    "observed_at": now,
                    "metrics_age_s": metrics_age_s,
                    "verdict": "DEAD",
                }
        elif verdict == "ALIVE":
            if run_dir:
                self.run_dir = run_dir
            self.strikes = 0
            self.alarmed = False
            self.last_alarm = None
            fired = False
        else:  # UNKNOWN -- log it, count nothing, never fire
            if run_dir:
                self.run_dir = run_dir
            fired = False
        self.last_verdict = verdict
        return fired

    def as_dict(self):
        return {
            "run_dir": self.run_dir,
            "strikes": self.strikes,
            "strikes_to_alarm": self.strikes_to_alarm,
            "stale_after_s": self.stale_after_s,
            "alarmed": self.alarmed,
            "last_verdict": self.last_verdict,
            "last_alarm": self.last_alarm,
        }


DEFAULT_OWNERSHIP_STALE_S = 900.0


def save_state(path, state, extra=None, now_epoch=None,
               ownership_stale_s=DEFAULT_OWNERSHIP_STALE_S):
    """Atomically persist the state. A torn read must never look like 'no strikes',
    which would silently reset a death counter on restart.

    B-239: two resident pollers cached DIFFERENT subjects and each clobbered the
    ONE shared file, so the subject and the strike count flip-flopped per write.
    The write REFUSES to clobber a different LIVE subject and returns None; it
    takes over only once the on-disk writer has gone stale. Callers that can
    date their write pass now_epoch; without it the on-disk subject counts as
    live (conservative -- an undatable writer is never clobbered)."""
    try:
        with open(path, encoding="utf-8") as fh:
            disk = json.load(fh)
    except (OSError, ValueError):
        disk = {}
    disk_run = disk.get("run_dir", "")
    if disk_run and state.run_dir and disk_run != state.run_dir:
        stamp_epoch = disk.get("updated_epoch")
        if stamp_epoch is None:
            # B-239 follow-up: an OLD-format state file carries no updated_epoch,
            # and keying takeover only on that field wedges the file FOREVER --
            # a relaunch against a different live run is refused eternally with
            # no escape hatch (the refused writer never refreshes the file, so
            # it can never gain the field). Date the on-disk writer by its file
            # mtime instead: a RECENT undatable foreign writer is still refused,
            # an old one still goes stale. Only an unreadable mtime stays
            # conservative-undatable.
            try:
                stamp_epoch = os.path.getmtime(path)
            except OSError:
                stamp_epoch = None
        age = (None if stamp_epoch is None or now_epoch is None
               else now_epoch - float(stamp_epoch))
        if age is None or age < ownership_stale_s:
            return None
    payload = state.as_dict()
    if extra:
        payload.update(extra)
    directory = os.path.dirname(os.path.abspath(path)) or "."
    fd, tmp = tempfile.mkstemp(dir=directory, prefix=".liveness.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as fh:
            json.dump(payload, fh, sort_keys=True)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    return payload
