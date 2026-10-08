#!/usr/bin/env python3
"""Trainer-liveness POLLER (B-150 wiring half) -- the persistent-process half of the
skill 5.4.1 BUG-ZERO liveness mandate.

WHY THIS FILE EXISTS. `scripts/trainer_liveness_watchdog.py` holds the pure detection
policy (three-state classify + strike counter) and passed 14/14 at tick #382. Nothing
called it. Measured that tick: a repo-wide grep matched only the module and its own
test. A detector nobody polls detects nothing -- the exact blind spot one layer down
from the bug it was written for. Run 20260913T112337Z died at step 29 and the death
sat unnoticed for 13+ minutes.

TWO HALVES OF THE SAME MANDATE, DELIBERATELY UNEQUAL. Detection is autonomous; HEALING
IS USER-GATED. The standing order in `.sapo-loop/STATUS.md` is "Only stop/relaunch
training — harness is FULLY AUTOMATIC", so this poller has NO launch/stop surface at all -- it
raises the RED signal into a durable log and the harness auto-acts with TDD fix + relaunch.
That absence is enforced on the AST by
`tests/test_trainer_liveness_poller.py::test_poller_has_no_launch_or_stop_surface`,
because "we just will not call subprocess" is not a lock.

THREE-STATE, NEVER TWO (skill 5.4.1 false-DEAD class). A liveness probe sharing a
transport with other pollers TIMES OUT under load, and a two-state probe reads that as
death -> spurious relaunches -> co-resident duplicate trainers. So: ALIVE (a positive
signal), DEAD (a positive ABSENCE signal from every container that answered), UNKNOWN
(the transport failed, carrying no opinion). Only DEAD accumulates strikes.

PER-CONTAINER SWEEP. The trainer is not visible from every container (B-149 blocker 3,
measured 2026-09-13: absent from ASI3's procfs while resident on ASI2). ANY container
reporting a resident trainer is ALIVE; only "every reachable container says no" is a
positive absence.

PUNCH-THROUGH (B-233). UNKNOWN is the honest verdict under exec-transport
congestion, but an unbounded UNKNOWN streak is its own blind spot: measured
2026-09-14, 55 consecutive polls (~82 min) read UNKNOWN while the trainer was
verifiably ALIVE. So after DEFAULT_UNKNOWN_PUNCH_AFTER consecutive UNKNOWN
cycles the poller fires ONE long-timeout sweep (make_punch_probe) -- the same
three-state, sentinel-guarded logic with a bigger transport budget -- and lets
its definitive verdict stand. The streak resets either way, so escalation stays
bounded, and a failed punch invents no opinion: the verdict stays UNKNOWN.

Run it detached (skill 5.4.1 design rule 4):
    python3 scripts/trainer_liveness_poller.py --daemon
`--daemon` double-forks in-process (see `daemonize`): the survivor reparents to init
and leads its own session, so the launching session ending does NOT kill the poller.
The previous recipe (`nohup ... & disown`) was followed to the letter at tick #383 and
the poller was still reaped with its session -- hence doing it here, not at the call site.
"""
import json
import os
import re
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import trainer_liveness_watchdog as tlw  # noqa: E402

CONTAINER_PORTS = (20646, 19004, 20653)
BOX_ROOT = "/root/work/software/quantum-gpt"
DEFAULT_INTERVAL_S = 90.0
DEFAULT_STALE_AFTER_S = 240.0
# The regular transport timeout, and the punch-through's (B-233). Under exec
# congestion every leg of the sweep can time out at the regular budget and the
# poller then sits at UNKNOWN forever. The punch shares the regular probe's
# three-state/sentinel logic and differs ONLY in patience -- the extra wait is
# the whole mechanism.
DEFAULT_PROBE_TIMEOUT_S = 90.0
DEFAULT_PUNCH_TIMEOUT_S = 300.0
DEFAULT_UNKNOWN_PUNCH_AFTER = 6
DEFAULT_LOG = "/Users/daxu/software/quantum-gpt/.sapo-loop/trainer_liveness.log"
DEFAULT_STATE = "/Users/daxu/software/quantum-gpt/.sapo-loop/trainer_liveness_state.json"
DEFAULT_PIDFILE = "/Users/daxu/software/quantum-gpt/.sapo-loop/trainer_liveness.pid"

# Appended to every probe command so a response can be CHECKED for having carried
# our command's output at all.  The transport windows/truncates bodies over ~4.5KB
# (B-138), and a windowed body can drop the output entirely while the exec still
# SUCCEEDS -- measured 2026-09-14 tick #401 through :20653: the body contained the
# transport's own wrapper (the base64 of the command echoed back) and nothing else.
# `box_trainer_probe` counted that container as `answered`, so ASI1/ASI2's genuine
# absence plus one blank body read as DEAD for a trainer that was demonstrably live
# -- the B-165 false-DEAD generator, and skill 5.4.1 wires this verdict to the
# resurrector.  Absence of the sentinel means "this body carries no opinion".
PROBE_SENTINEL = "__SAPO_TRAINER_PROBE_EOF__"
PROBE_COMMAND = "ps -eo pid,args | grep [g]rpo_trainer.py; echo " + PROBE_SENTINEL


def _http_exec(port, cmd, timeout=DEFAULT_PROBE_TIMEOUT_S):
    """The production transport: one exec call to a Huanxin daemon port."""
    payload = json.dumps(dict(command=cmd)).encode()
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}" + "/exec",
        data=payload,
        headers=dict(**{"Content-Type": "application/json"}),
    )
    raw = urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")
    doc = json.loads(raw)
    out = doc.get("output", doc)
    if isinstance(out, dict):
        out = out.get("output", "")
    return out


RUN_DIR_SHAPE = re.compile(
    r"^" + re.escape(BOX_ROOT) + r"/outputs/sapo-27b-ai-\d{8}T\d{4,10}Z?$"
)


def _find_run_dir(exec_fn, ports):
    """Newest run dir on the box, or an empty string when no container can answer.

    Fail-closed on SHAPE (B-313, 2026-09-16): a degraded transport can return an
    interleaved/stale window, and the box itself can hold a malformed dir -- the
    poller once adopted the doubled prefix "sapo-27b-ai-sapo-27b-ai-20260915T1010"
    as its subject. An answer that does not match the single-prefix shape is a
    NO-ANSWER (keep probing / stay unresolved), never a subject.
    """
    pattern = BOX_ROOT + "/outputs/sapo-27b-ai-*"
    for port in ports:
        try:
            out = exec_fn(port, "ls -dt " + pattern + " 2>/dev/null | head -1")
        except Exception:
            continue
        lines = (out or "").strip().splitlines()
        if lines and RUN_DIR_SHAPE.match(lines[0].strip()):
            return lines[0].strip()
    return ""


def _metrics_age(exec_fn, run_dir):
    """Seconds since the run's metrics file last advanced, or None if unreadable."""
    if not run_dir:
        return None
    cmd = "date +%s; stat -c %Y " + run_dir + "/grpo_step_metrics.jsonl 2>/dev/null"
    for port in CONTAINER_PORTS:
        try:
            out = exec_fn(port, cmd)
        except Exception:
            continue
        nums = [x for x in (out or "").replace("\n", " ").split() if x.isdigit()]
        if len(nums) >= 2:
            return max(0, int(nums[0]) - int(nums[1]))
    return None


def run_dir_from_ps(out):
    """Extract the single distinct `--output-dir` from raw `ps` argv lines (B-156).

    Read from the SAME snapshot that established liveness, deliberately: a second
    transport round-trip would let the identity and the liveness verdict describe
    two different instants, and the run can change between them.

    This is NOT `ls -dt`. Which directory is NEWEST is a different question from
    which run is TRAINING, and the two were measured to disagree on 2026-09-13:
    the newest dir T123210Z had no trainer at all while the only live trainer
    carried `--output-dir ...T112337Z` -- so following the newest directory names
    the wrong subject (the defect B-145 fixed in the judge watcher).

    Ambiguous (two distinct output dirs) or absent returns "" -- an unknown
    identity is never guessed, because a guessed subject is worse than none.
    """
    found = set()
    for line in (out or "").splitlines():
        idx = line.find("--output-dir ")
        if idx < 0:
            continue
        rest = line[idx + len("--output-dir "):].split()
        if rest:
            found.add(rest[0])
    if len(found) == 1:
        return found.pop()
    return ""


def box_trainer_probe(ports=CONTAINER_PORTS, exec_fn=None, metrics_age_fn=None):
    """Build the three-state probe over the fleet.

    Returns a callable -> (proc_alive, metrics_age_s, transport_error, run_dir).
      True / None -> a trainer is resident somewhere (ALIVE)
      run_dir     -> the live run output-dir from the same snapshot, "" unknown
      False       -> every reachable container positively says no, age is known
      None        -> the transport failed everywhere (UNKNOWN, never DEAD)
    """
    exec_fn = exec_fn or _http_exec

    def probe():
        answered = 0
        blind = 0
        for port in ports:
            try:
                out = exec_fn(port, PROBE_COMMAND)
            except Exception:
                continue
            text = out or ""
            if PROBE_SENTINEL not in text:
                # The exec succeeded but the body does not contain our command's
                # output (B-138 windowing/truncation). It is BLIND, not absent:
                # counting it as `answered` is what turns a live trainer into a
                # DEAD verdict (B-165). A blind container is NOT "saying no", so
                # it blocks the positive-absence verdict below.
                blind += 1
                continue
            answered += 1
            if text.replace(PROBE_SENTINEL, "").strip():
                # A resident trainer. Name it from its own argv, so an ALIVE
                # read says WHICH run it is alive about (B-156).
                return (True, None, None, run_dir_from_ps(text))
        if blind or not answered:
            reason = ("no container answered" if not answered else
                      f"{blind} container(s) returned an unverifiable body")
            return (None, None, reason, "")
        # A positive ABSENCE: every container that answered said "no trainer".
        # That is a DEAD signal and it must survive an unreadable metrics file --
        # degrading it to UNKNOWN would silence the very alarm this exists for.
        # The age is the EVIDENCE, carried when readable, None when not.
        run_dir = _find_run_dir(exec_fn, ports)
        age = metrics_age_fn(run_dir) if metrics_age_fn else _metrics_age(exec_fn, run_dir)
        # No trainer is resident, so no process can name the subject. The
        # last run the poller saw ALIVE is retained in state and named
        # on the alarm -- a death alarm must say WHAT died.
        return (False, age, None, "")

    return probe

def make_punch_probe(timeout_s=DEFAULT_PUNCH_TIMEOUT_S, ports=None):
    """The punch-through probe (B-233): the SAME three-state sweep, more patience.

    Deliberately NOT a second detection policy -- it reuses box_trainer_probe
    unchanged, so it can only RESOLVE an UNKNOWN into a definite verdict, never
    manufacture a DEAD the regular sweep would not have produced. Congestion is
    survived by waiting longer, once -- not by re-interpreting failure.
    """
    return box_trainer_probe(ports=ports or CONTAINER_PORTS,
                             exec_fn=lambda port, cmd: _http_exec(port, cmd,
                                                                  timeout=timeout_s))


class LivenessPoller:
    """One signal: classify -> strike -> durable log + durable state."""

    def __init__(self, probe, log_path=DEFAULT_LOG, state_path=DEFAULT_STATE,
                 stale_after_s=DEFAULT_STALE_AFTER_S, now=time.time,
                 punch_probe=None, unknown_punch_after=DEFAULT_UNKNOWN_PUNCH_AFTER):
        self.probe = probe
        self.log_path = log_path
        self.state_path = state_path
        self.now = now
        self.punch_probe = punch_probe
        self.unknown_punch_after = int(unknown_punch_after)
        self.unknown_streak = 0
        self.state = tlw.LivenessState(stale_after_s=stale_after_s)
        self._load()

    def _load(self):
        try:
            with open(self.state_path, encoding="utf-8") as fh:
                raw = json.load(fh)
        except (OSError, ValueError):
            return
        self.state.strikes = int(raw.get("strikes", 0))
        self.state.alarmed = bool(raw.get("alarmed", False))
        self.state.run_dir = raw.get("run_dir", "")
        self.state.last_verdict = raw.get("last_verdict", "")
        # The durable alarm record is evidence (which run died, when, how stale).
        # Not restoring it let the next resident's first write replace the real
        # alarm with null on disk.
        self.state.last_alarm = raw.get("last_alarm")
        self.unknown_streak = int(raw.get("unknown_streak", 0))

    def _append(self, line):
        directory = os.path.dirname(os.path.abspath(self.log_path))
        if directory and not os.path.isdir(directory):
            os.makedirs(directory)
        with open(self.log_path, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    def poll_once(self):
        now = self.now()
        stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))
        proc_alive, age, err, run_dir = self.probe()
        punch_used = 0
        if err is None:
            self.unknown_streak = 0
            verdict = tlw.classify(age, proc_alive, self.state.stale_after_s)
        else:
            # UNKNOWN never accumulates strikes and never alarms on its own --
            # but an unbounded streak is its own blind spot (B-233): a poller
            # that can only say UNKNOWN during a congestion episode says nothing
            # about a trainer that died inside it. Past the threshold, fire ONE
            # long-timeout sweep and let its definitive verdict stand.
            self.unknown_streak += 1
            verdict = "UNKNOWN"
            if self.unknown_streak >= self.unknown_punch_after:
                punch_used = 1
                self._append(f"{stamp} PUNCH unknown_streak=" + str(self.unknown_streak)
                             + " timeout_s=" + str(DEFAULT_PUNCH_TIMEOUT_S)
                             + " firing long-timeout punch-through sweep")
                if self.punch_probe is None:
                    self.punch_probe = make_punch_probe()
                p_alive, p_age, p_err, p_run = self.punch_probe()
                # Backoff regardless of outcome: ONE punch per full streak,
                # mirroring the keeper watchdog bounded punch-through.
                self.unknown_streak = 0
                if p_err is None:
                    err = None
                    verdict = tlw.classify(p_age, p_alive, self.state.stale_after_s)
                    run_dir = p_run or run_dir
                    age = p_age if age is None else age
                else:
                    self._append(f"{stamp} PUNCH outcome=UNKNOWN err=" + str(p_err))
        fired = self.state.observe(verdict, run_dir=run_dir,
                                   now=now, metrics_age_s=age)
        subject = run_dir or self.state.run_dir or "UNKNOWN"
        self._append(
            f"{stamp} heartbeat verdict={verdict} strikes={self.state.strikes} "
            f"metrics_age_s={age} run=" + subject
            + " punch=" + str(punch_used)
            + " unknown_streak=" + str(self.unknown_streak)
        )
        if fired:
            alarm = self.state.last_alarm or dict()
            alarm_run = alarm.get("run_dir") or "UNKNOWN"
            self._append(
                f"{stamp} ALARM trainer DEAD run=" + alarm_run
                + " strikes=" + str(alarm.get("strikes"))
                + " metrics_age_s=" + str(alarm.get("metrics_age_s"))
                + " -> auto-relaunch with TDD fix (harness is fully automatic)"
            )
        saved = tlw.save_state(self.state_path, self.state,
                               extra=dict(updated=stamp, updated_epoch=now,
                                          verdict=verdict,
                                          unknown_streak=self.unknown_streak),
                               now_epoch=now)
        if saved is None:
            # B-239: the shared state file holds a DIFFERENT LIVE subject. Say so
            # loudly -- a silently dropped write is the exact defect class.
            self._append(f"{stamp} STATE-WRITE REFUSED subject=" + subject
                         + " on-disk state holds a different live run_dir")
        return dict(verdict=verdict, strikes=self.state.strikes, alarm=fired,
                    state_write=("refused" if saved is None else "saved"),
                    metrics_age_s=age, error=err, run_dir=run_dir,
                    punch=punch_used, unknown_streak=self.unknown_streak)

    def run_forever(self, interval_s=DEFAULT_INTERVAL_S):
        self._append(f"poller start interval_s={interval_s} "
                     f"stale_after_s={self.state.stale_after_s} "
                     f"punch_after={self.unknown_punch_after}")
        while True:
            try:
                self.poll_once()
            except Exception as exc:  # a poller that dies on an exception is dark
                self._append(f"poll error: {type(exc).__name__}: {exc}")
            time.sleep(interval_s)


def write_pidfile(pidfile, pid=None):
    """Publish the resident poller's pid.

    Skill 5.4.1: duplicate watchers are always killed (keep one) -- and a duplicate
    can only be found if the resident instance says who it is. The pidfile is also
    the liveness instrument: no pidfile while the poller is supposedly running is
    the same "declared but not verified" defect this module exists to catch.

    Deliberately NOT a kill surface: this module is forbidden from containing one
    (test_poller_has_no_launch_or_stop_surface), so de-duplication belongs to
    whichever lane owns the fleet, not here.
    """
    directory = os.path.dirname(os.path.abspath(pidfile))
    if directory and not os.path.isdir(directory):
        os.makedirs(directory)
    tmp = pidfile + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(f"{os.getpid() if pid is None else pid}\n")
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, pidfile)


def duplicate_poller_detected(state_path=DEFAULT_STATE,
                              now_epoch=None,
                              max_age_s=3 * DEFAULT_STALE_AFTER_S):
    """True when a RESIDENT poller demonstrably owns the role already (B-310).

    A fleet re-arm double-fired this poller (two resident copies, 2026-09-16
    14:43) because nothing refused the second start; duplicate transport
    pollers multiply /exec queue load on a wedge-sensitive channel. The
    refusal keys on the resident instance's OUTPUT heartbeat -- it rewrites
    the state file every poll -- so liveness of OUTPUT, not of PROCESS (the
    5.4.1 hang rule): a hung or dead writer's state goes stale and a new
    instance may take over. No signal is ever sent to the resident process:
    refusing to become the duplicate is not a kill surface.

    The 3x-stale_after window tolerates transport congestion (punch-through
    escalates at 6 unknowns ~= 9 min) without admitting a second poller
    mid-congestion: while the old owner still cycles, its state stays fresh.
    """
    if now_epoch is None:
        now_epoch = time.time()
    stamp = None
    # The writer's date is the FRESHER of the stamped field and the file
    # mtime (B-310 live case 2026-09-16 15:06Z: field 1100s old while mtime
    # was 9s fresh -- a writer that does not stamp the field; field-only
    # reading false-admitted a third poller). Missing file: no proof anyone
    # owns the role. Corrupt content: never an ownership proof, and (B-239
    # lesson) it must not wedge the role forever -- admit the takeover;
    # save_state publishes via atomic replace, so garbage is external
    # corruption, not a mid-write resident.
    try:
        mtime = os.path.getmtime(state_path)
    except OSError:
        return False
    try:
        with open(state_path, encoding="utf-8") as fh:
            stamp = json.load(fh).get("updated_epoch")
    except (OSError, ValueError, TypeError):
        stamp = None
    try:
        stamp = max(float(stamp), mtime) if stamp is not None else mtime
    except (TypeError, ValueError):
        stamp = mtime
    try:
        age = now_epoch - float(stamp)
    except (TypeError, ValueError):
        return False
    return age < max_age_s


def log_duplicate_refusal(pidfile=DEFAULT_PIDFILE, log_path=DEFAULT_LOG):
    """Record WHY this instance exited without polling (visible non-start)."""
    resident = None
    if pidfile:
        try:
            with open(pidfile, encoding="utf-8") as fh:
                resident = fh.read().strip()
        except OSError:
            resident = None
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    directory = os.path.dirname(os.path.abspath(log_path))
    if directory and not os.path.isdir(directory):
        os.makedirs(directory)
    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write(f"{stamp} refusing duplicate start: resident poller heartbeat fresh"
                 f" (pidfile={resident or 'none'})\n")


def daemonize(pidfile=None):
    """Detach into a persistent background process (skill 5.4.1 design rule 4).

    WHY (B-157, measured 2026-09-13): the poller was launched as a SESSION CHILD at
    tick #383, logged two heartbeats, fired its alarm and then vanished -- no third
    poll, no error line -- because it was reaped when the launching tick session
    ended. Skill 5.4.1 requires the opposite in as many words: watchers are
    "persistent background processes, NOT a child of the manager's session" and
    "must survive the session ending". `nohup ... & disown` was the documented
    recipe and it was not enough, so the detach is done here, in-process, where it
    cannot be forgotten by a caller.

    Double-fork: the second fork guarantees the survivor is NOT a session leader,
    so it can never reacquire a controlling terminal, and it reparents to init --
    killing the launcher's session no longer touches it. Only the surviving
    grandchild returns from this call; the intermediate processes exit immediately.
    """
    if os.fork() > 0:
        os._exit(0)
    os.setsid()
    if os.fork() > 0:
        os._exit(0)
    devnull = os.open(os.devnull, os.O_RDWR)
    for fd in (0, 1, 2):
        os.dup2(devnull, fd)
    if devnull > 2:
        os.close(devnull)
    if pidfile:
        write_pidfile(pidfile)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    interval = DEFAULT_INTERVAL_S
    pidfile = DEFAULT_PIDFILE
    detach = False
    punch_after = DEFAULT_UNKNOWN_PUNCH_AFTER
    punch_timeout = DEFAULT_PUNCH_TIMEOUT_S
    rest = []
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--daemon":
            detach = True
        elif arg == "--no-detach":
            detach = False
        elif arg == "--pidfile":
            i += 1
            pidfile = argv[i]
        elif arg.startswith("--pidfile="):
            pidfile = arg.split("=", 1)[1]
        elif arg.startswith("--interval="):
            interval = float(arg.split("=", 1)[1])
        elif arg.startswith("--punch-after="):
            punch_after = int(arg.split("=", 1)[1])
        elif arg.startswith("--punch-timeout="):
            punch_timeout = float(arg.split("=", 1)[1])
        elif arg == "--no-pidfile":
            pidfile = None
        else:
            rest.append(arg)
        i += 1
    if rest:
        interval = float(rest[0])
    if duplicate_poller_detected():
        log_duplicate_refusal(pidfile, DEFAULT_LOG)
        return 0
    if detach:
        daemonize(pidfile)
    elif pidfile:
        write_pidfile(pidfile)
    LivenessPoller(probe=box_trainer_probe(),
                   punch_probe=make_punch_probe(timeout_s=punch_timeout),
                   unknown_punch_after=punch_after).run_forever(interval)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
