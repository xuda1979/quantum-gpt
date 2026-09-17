#!/usr/bin/env python3
"""Chunked full-suite runner (section 9.3) -- chunked by COLLECTED TEST ID.

B-078 (2026-09-11): the first version of this runner enumerated test FILES with
`git ls-files tests` and passed them to pytest explicitly. That is wrong twice
over, and both halves were measured:

  1. It bypassed the repo's own conftest ignore rule
     (`collect_ignore_glob = ["_legacy/*.py"]` in tests/conftest.py), because
     collect_ignore applies to RECURSIVE collection and not to a file named
     directly on the command line. Result: 7 phantom "collection errors" in
     tests/_legacy/, which then ABORTED the whole chunk -- so 18 files in that
     chunk never ran at all.
  2. `git ls-files` + basename startswith("test") found 234 files, while pytest
     actually collects 296. So even the "full" run was silently a PARTIAL suite.

The fix is to chunk the set pytest itself collects -- never a re-derived list.
MEASURED: `pytest --collect-only -o addopts= -q` -> 3846 tests in 296 files,
0 collection errors, 0 from _legacy. A runner that enumerates its own file list
is a runner that can silently disagree with the suite it claims to run.

B-083 (2026-09-11): the aggregation reported an INCOMPLETE suite as complete.
A chunk that produced NO `TESTSUITE_COUNTS` line -- SIGKILLed by the concurrent-
suite OOM class (rc=-9), crashed, or timed out -- was folded in as

    rec = dict.fromkeys(tot, 0)      # all-zero record for a chunk that never reported
    for k in tot: tot[k] += rec[k]   # ...summed as if those zeros were measurements

and the TOTAL line carried no completeness term, so a partial run was
byte-indistinguishable from a full one. MEASURED, twice:

    chunk 05/20 rc=-9 (no TESTSUITE_COUNTS line)  VACUOUS ... ids=801..1000
    TOTAL passed=3634 failed=1 errors=0 skipped=11 total=3635   (3846 collected)

200 tests (5.2% of the suite) were silently absent and the process still exited 0,
so a caller checking exit status read success. "Chunk ran and reported zeros" and
"chunk never reported" are different facts; only the second is a missing
measurement. The TOTAL line now carries chunks_expected / chunks_reported / missing
/ signalled / unmeasured / VERDICT, and main() returns non-zero when incomplete.

SAFETY: the suite-running part of this file lives behind `if __name__ == "__main__"`,
so importing the module (to test the aggregation) does NOT collect, truncate the
log, or run a single chunk.
"""

import hashlib
import os
import subprocess
import sys
import time

QG = "/Users/daxu/software/quantum-gpt"
# B-169 (2026-09-13): the default used to be the constant `full_suite_315.txt`. This
# repo runs ~13-16 tick sessions against ONE tree, and more than one invokes this
# runner, so two concurrent default runs opened the SAME path and interleaved their
# chunk lines -- measured: a 24-chunk header with only 5 chunk lines, ids 401..3200
# overwritten in place, while the runner's stdout showed all 24 chunks had run. The
# completeness accounting B-083 added cannot survive a clobbered artifact, so the
# default must be UNIQUE PER RUN. SUITE_OUT still wins verbatim; the historical
# `full_suite_` prefix is kept so existing globs, readers and docs still match.
SUITE_OUT_BASENAME = os.environ.get("SUITE_OUT") or ("full_suite_315_%d.txt" % os.getpid())
OUT = os.path.join(QG, ".sapo-loop", "logs", SUITE_OUT_BASENAME)
CHUNK = 200

# B-200 (2026-09-14, tick #434): a chunk must not be able to stall the runner
# forever. MEASURED against run pid 79513 (artifact
# .sapo-loop/logs/full_suite_315_79513.txt), which is the calibration:
#
#     chunk 01/24 elapsed=223s     chunk 02/24 elapsed=3066s     chunk 03/24 elapsed=131s
#
# Chunk 02 spent 51 MINUTES -- ~15-20x its siblings -- and for the whole of it the
# artifact was byte-identical to a wedged process: `capture_output=True` holds the
# child's output until it returns, and nothing bounds the wait, so "slow" and "hung"
# are the same reading from outside. That is how this tick first mis-read it.
#
# The bound must sit ABOVE measured reality or it becomes a false alarm, which the
# skill prices as dearly as a missed one: 3066s is a LEGITIMATE completed chunk here,
# so the floor is set at 3600s. Re-calibrate as the suite grows -- and if a chunk ever
# reports TIMEOUT, the first question is whether the bound is too tight, not whether
# the chunk hung. SAPO_SUITE_CHUNK_TIMEOUT_S overrides it.
CHUNK_TIMEOUT_S = int(os.environ.get("SAPO_SUITE_CHUNK_TIMEOUT_S") or 3600)
# Not a signal death: keeps a timed-out chunk out of the SIGNALLED bucket so the
# TOTAL line can name it as what it is.
TIMEOUT_RC = 124

COUNTS = ("passed", "failed", "errors", "skipped", "xfailed", "xpassed", "total")

# B-115 (2026-09-11): every chunk below runs under `sys.executable` -- whatever
# interpreter launched this file -- and nothing checked that this interpreter can
# import the repo's own dependencies. The shebang is `#!/usr/bin/env python3`, so the
# natural invocation runs the whole suite under a bare interpreter with no venv
# site-packages, yielding ~182 failures whose only cause is `No module named
# 'pennylane'/'qiskit'/'cirq'/...`. Those are indistinguishable in the aggregate from
# real regressions. MEASURED both directions on one tree: the same test ids fail under
# the bare interpreter and pass under `.venv/bin/python3` (see
# tests/test_suite_runner_pins_interpreter.py).
REQUIRED_SDKS = ("pennylane", "qiskit", "cirq")

VENV_PYTHON = os.path.join(QG, ".venv", "bin", "python3")

# 0 complete, 1 incomplete (B-083), 2 collection failed. A blind interpreter is a
# fourth fact: a caller checking `rc == 0` must never read it as a passing suite.
ENV_INVALID_EXIT = 3

# B-211 (2026-09-14): SINGLE-FLIGHT.  This repo runs ~13-16 tick sessions against
# ONE tree, and more than one invokes this runner.  MEASURED at tick #440: three
# concurrent runs (pids 9124, 57656, 79513) starved each other so badly that chunk
# 02 cost 2837-3066 s against 76-431 s for its neighbouring chunks -- a ~10x
# outlier that reproduces, because each run inflates the others.  No run could
# reach a TOTAL inside a 10-min tick, so every tick reported "NOT MEASURED" and a
# real regression could hide behind the contention indefinitely.
#
# The lock is an ADVISORY flock, deliberately not a pidfile: the kernel drops it
# when the holder dies, so a crashed or SIGKILLed run leaves NO stale lock to
# clear by hand.
SINGLE_FLIGHT_EXIT = 4
SUITE_LOCK = os.path.join(QG, ".sapo-loop", "suite_runner.lock")


def acquire_single_flight(lock_path=None):
    """Take the exclusive suite lock. Returns a live handle, or None if held.

    The returned handle MUST stay referenced for as long as the run lasts --
    closing it (or letting it be collected) releases the lock.
    """
    import fcntl

    path = lock_path or SUITE_LOCK
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    fh = open(path, "a+")
    try:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        fh.close()
        return None
    # Non-vacuous guard: name the holder so a refused run can say WHO to wait for.
    fh.seek(0)
    fh.truncate()
    fh.write("%d %s\n" % (os.getpid(), time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))
    fh.flush()
    return fh


def release_single_flight(handle):
    """Release the suite lock without deleting the file (the next run reuses it)."""
    if handle is None:
        return
    try:
        import fcntl

        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    finally:
        handle.close()


def sdk_probe(python_exe):
    """Names from REQUIRED_SDKS that `python_exe` cannot import. [] means all present.

    Returns None if the probe itself could not run -- which is NOT the same as "all
    present": an unmeasurable interpreter must not be treated as a usable one.
    """
    code = (
        "import importlib.util as u,sys;"
        "sys.stdout.write(','.join(m for m in %r if u.find_spec(m) is None))"
        % (tuple(REQUIRED_SDKS),)
    )
    try:
        p = subprocess.run([python_exe, "-c", code], capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError):
        return None
    if p.returncode != 0:
        return None
    out = p.stdout.strip()
    return out.split(",") if out else []


def env_verdict(missing, venv_path, venv_missing=None, venv_exists=None):
    """Classify the CURRENT interpreter before it is allowed to produce a suite count.

    `missing`      -- REQUIRED_SDKS absent from the current interpreter ([] = all present).
    `venv_path`    -- candidate replacement interpreter.
    `venv_missing` -- REQUIRED_SDKS absent from the candidate; None = unable to probe.
    `venv_exists`  -- whether the candidate exists at all.

    Returns a dict with keys ok / action / executable / reason, where action is one of:
      "run"    -- this interpreter is sound; run the suite here.
      "reexec" -- it is not, but the venv is; re-exec so the count describes the tree.
      "refuse" -- no sound interpreter exists; emit no suite verdict at all.
    """
    if not missing:
        return dict(ok=True, action="run", executable=None, reason="all required SDKs present")
    if not venv_exists:
        return dict(
            ok=False,
            action="refuse",
            executable=None,
            reason="missing %s here and no venv interpreter at %s" % (",".join(missing), venv_path),
        )
    if venv_missing is None:
        return dict(
            ok=False,
            action="refuse",
            executable=None,
            reason="%s missing here and the venv interpreter at %s could not be "
            "probed" % (",".join(missing), venv_path),
        )
    if venv_missing:
        return dict(
            ok=False,
            action="refuse",
            executable=None,
            reason="missing %s here and also %s in %s"
            % (",".join(missing), ",".join(venv_missing), venv_path),
        )
    return dict(
        ok=False,
        action="reexec",
        executable=venv_path,
        reason="missing %s here; %s has them" % (",".join(missing), venv_path),
    )


def collect_ids():
    """Ask pytest what the suite contains.

    Returns (returncode, node_ids, stdout_tail). The work list is never re-derived
    from the filesystem: a runner that enumerates its own files can silently
    disagree with the suite it claims to run (B-078).
    """
    col = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "--collect-only",
            "-o",
            "addopts=",
            "-q",
            "-p",
            "no:cacheprovider",
            "-p",
            "no:warnings",
        ],
        capture_output=True,
        text=True,
        cwd=QG,
    )
    ids = [ln.strip() for ln in col.stdout.splitlines() if "::" in ln]
    return col.returncode, ids, col.stdout


class _ChunkTimeout:
    """Stand-in for CompletedProcess when a chunk outlives CHUNK_TIMEOUT_S (B-200).

    Carries whatever the child managed to write before the kill so parse_counts()
    can still see it -- `counts is None` is what makes the chunk read as NOT
    MEASURED, which is the pre-existing "never reported" fact (B-083/B-158).
    """

    def __init__(self, cmd, stdout=None, stderr=None):
        self.args = cmd
        self.returncode = TIMEOUT_RC
        self.stdout = _text(stdout)
        self.stderr = _text(stderr)
        self.timed_out = True


def _text(blob):
    """TimeoutExpired may hand back bytes even under text=True."""
    if blob is None:
        return ""
    if isinstance(blob, bytes):
        return blob.decode("utf-8", "replace")
    return blob


# B-330 (2026-09-17): chunks dominated by test_grpo_pipeline_fast.py run real
# quantum-circuit candidate evaluation per test and exceed the flat 3600s chunk
# timeout (measured chunk 07 elapsed >47min before SIGKILL, leaving 200 tests
# unmeasured). Override the timeout for such heavy chunks; mild chunks keep the
# 3600s bound.
HEAVY_TEST_PATTERN = "tests/test_grpo_pipeline_fast.py::"
HEAVY_CHUNK_TIMEOUT_S = int(os.environ.get("SAPO_SUITE_HEAVY_CHUNK_TIMEOUT_S") or 7200)


def _chunk_timeout_for(node_ids):
    """Return the timeout bound for this chunk (seconds).

    Heavy chunks are those where a majority of node ids come from the
    expensive candidate-evaluation file. A chunk is not penalized for one
    stray heavy id; it must be at least half-heavy to justify the doubled
    timeout.
    """
    heavy = sum(1 for nid in node_ids if nid.startswith(HEAVY_TEST_PATTERN))
    if node_ids and heavy >= max(1, len(node_ids) // 2):
        return HEAVY_CHUNK_TIMEOUT_S
    return CHUNK_TIMEOUT_S


def run_chunk(node_ids):
    """Run one chunk of collected node ids in a child pytest process.

    BOUNDED (B-200): a chunk that never returns is the one failure this runner could
    not report at all, so the wait is capped and the overrun is returned as a
    not-measured chunk rather than raised.
    """
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "-p",
        "no:cacheprovider",
        "--tb=no",
        "-p",
        "no:warnings",
    ] + node_ids
    timeout_s = _chunk_timeout_for(node_ids)
    try:
        return subprocess.run(cmd, capture_output=True, text=True, cwd=QG, timeout=timeout_s)
    except subprocess.TimeoutExpired as exc:
        return _ChunkTimeout(cmd, stdout=exc.stdout, stderr=exc.stderr)


def parse_counts(stdout):
    """Counts from the LAST TESTSUITE_COUNTS line of a chunk, or None if that chunk
    never produced one.

    None means NOT MEASURED -- the chunk was killed, crashed or timed out before its
    summary. That is a different fact from a chunk that ran and reported zeros (all
    skipped, say), which is a real report and is returned as a counts dict.
    """
    line = ""
    for ln in stdout.splitlines():
        if ln.startswith("TESTSUITE_COUNTS"):
            line = ln.strip()
    if not line:
        return None
    rec = dict.fromkeys(COUNTS, 0)
    seen = False
    for kv in line.split()[1:]:
        k, _, v = kv.partition("=")
        if k in rec:
            try:
                rec[k] = int(v)
                seen = True
            except ValueError:
                pass
    return rec if seen else None


def parse_failures(stdout):
    """Failing node ids pytest reported for one chunk, in output order.

    `run_chunk` passes `--tb=no`, which suppresses tracebacks but NOT pytest's
    short test summary -- so a failing chunk already prints `FAILED <nodeid> -
    <reason>` and only the TESTSUITE_COUNTS line was being kept (B-147). The count
    says how many broke; this says which, which is the part triage needs.
    """
    out = []
    for ln in stdout.splitlines():
        if not (ln.startswith("FAILED ") or ln.startswith("ERROR ")):
            continue
        node = ln.split(" ", 1)[1].split(" - ", 1)[0].strip()
        if node:
            out.append(node)
    return out


def summarize(chunks):
    """Fold per-chunk results into suite totals plus a completeness verdict.

    `chunks` holds one dict per EXPECTED chunk, in run order:
        {"chunk": int, "rc": int, "counts": dict-or-None, "tests": int}
    where `tests` is how many node ids the chunk was given and `counts` is
    parse_counts() of its output.

    A chunk whose counts are None contributed NO measurement; its zeros are not
    added to the totals (they would read as a smaller-but-fine suite). A chunk that
    was killed by a signal (rc < 0) did not finish either, so whatever counts line it
    managed to emit is partial -- the run is incomplete even though it reported.
    """
    tot = dict.fromkeys(COUNTS, 0)
    missing, signalled, errored, timed = [], [], [], []
    for ch in chunks:
        rec = ch["counts"]
        if ch.get("timed_out"):
            # B-200: a chunk that blew CHUNK_TIMEOUT_S is its own exclusive bucket.
            # "hung" and "crashed" route to different owners, so it is named separately
            # rather than folded into `missing`/`errored`. Whatever it wrote before the
            # kill is PARTIAL by definition and is deliberately NOT folded into the
            # totals -- a hung chunk must never contribute a number it did not finish.
            timed.append(ch["chunk"])
            continue
        if rec is None:
            missing.append(ch["chunk"])
        elif ch["rc"] < 0:
            signalled.append(ch["chunk"])
        elif ch["rc"] not in OK_RCS:
            # B-158: pytest exited on a usage/collection/internal error, so this chunk was
            # handed its test ids and did not run them. Only rc 0 ("ran; all good") and
            # rc 1 ("ran; some failed") are REPORTS. A chunk that reported all zeros after
            # rc=0/1 is a real (quiet) measurement and stays complete -- see
            # test_a_chunk_that_reported_zeros_is_reported_not_missing. But rc 2
            # (interrupted), 3 (internal error), 4 (usage error) and 5 (no tests
            # collected) mean the tests never ran, which is the same fact as a missing
            # chunk. Measured: t381 chunk 21/23 rc=4 total=0 certified VERDICT=COMPLETE.
            errored.append(ch["chunk"])
        if rec:
            for k in COUNTS:
                tot[k] += rec.get(k, 0)
    seen_failures = []
    for ch in chunks:
        for node in ch.get("failures") or []:
            if node not in seen_failures:
                seen_failures.append(node)
    return {
        "totals": tot,
        "failures": seen_failures,
        "expected": len(chunks),
        "reported": len(chunks) - len(missing),
        "missing": missing,
        "signalled": signalled,
        "errored": errored,
        "timed_out": timed,
        "unmeasured": sum(ch["tests"] for ch in chunks if ch["counts"] is None),
        "complete": not missing and not signalled and not errored and not timed,
    }


def _name(nums):
    """Chunk numbers, zero padded like the per-chunk lines, capped for readability."""
    head = ",".join("%02d" % n for n in nums[:10])
    return head + (",..." if len(nums) > 10 else "")


# pytest exit codes that mean "the tests RAN": 0 = all good, 1 = some tests failed.
# Anything else (2 interrupted, 3 internal error, 4 usage error, 5 no tests collected)
# means the chunk did not execute the ids it was given -- see summarize()/B-158.
OK_RCS = (0, 1)


def chunk_flags(rc, counts, timed_out=False):
    """Per-chunk verdict markers: UNMEASURED (never reported), VACUOUS (reported but
    ran nothing), SIGNALLED (killed by a signal), TIMEOUT (outlived CHUNK_TIMEOUT_S)."""
    flags = []
    if timed_out:
        flags.append("TIMEOUT")
    if counts is None:
        flags.append("UNMEASURED")
    elif sum(counts[k] for k in ("passed", "failed", "errors")) == 0:
        flags.append("VACUOUS")
    if rc < 0:
        flags.append("SIGNALLED")
    return ("  " + " ".join(flags)) if flags else ""


def running_ps():
    """A `ps -eo pid,args` transcript, or None if it cannot be read.

    None (never "") on failure: an unreadable ps is UNKNOWN co-tenancy, and UNKNOWN
    must not fall through to "no co-tenants" -- that is the fail-OPEN trap.
    """
    try:
        proc = subprocess.run(["ps", "-eo", "pid,args"], capture_output=True, text=True, timeout=30)
    except Exception:
        return None
    return proc.stdout if isinstance(proc.stdout, str) else None


# Injectable so a test can neutralise the AMBIENT process table: without this a
# real co-tenant suite on the machine would flip an unrelated test's verdict.
PS_SOURCE = running_ps


def co_tenant_pids(ps_text, self_pids=()):
    """Pids of OTHER suite trees visible in a `ps` transcript. B-216.

    The single-flight lock (B-211) only stops runners that PARTICIPATE in it. A tree
    started BEFORE the lock existed never takes it, so it can be neither refused nor
    evicted -- it can only be SEEN. Seeing one must gate the verdict: a TOTAL produced
    while another suite starves the same tree is not a measurement.

    REFUTED FIX (recorded so it is not re-run): evicting a "stale" lock inside
    acquire_single_flight() is a NO-OP here. That function only rewrites the lock body
    on a SUCCESSFUL flock, and the body was stamped with the live holder while three
    co-tenant trees ran -- so the flock was FREE and there was nothing to evict.

    KNOWN LIMIT (deliberate, not hidden): this counts pytest/run_full_suite COMMAND
    LINES. A `grep pytest` is excluded as an instrument artifact; a suite invoked via a
    wrapper that hides those strings would be missed.
    """
    me = set(int(x) for x in self_pids)
    found = []
    for line in (ps_text or "").splitlines():
        parts = line.split(None, 1)
        if len(parts) < 2 or not parts[0].isdigit():
            continue
        pid, cmd = int(parts[0]), parts[1]
        if pid in me:
            continue
        # MEASURED false-positive class (tick #445): a tick session's PROMPT TEXT
        # contains the literal "pytest" -- the standing brief names the command --
        # so a substring test on the whole argv counts every claude process as a
        # suite. Live, that read 14 "co-tenants" of which only 10 were real, which
        # would have made EVERY run CONTAMINATED and the verdict worthless.
        # Require a REAL invocation: an interpreter, and an actual pytest/runner arg.
        if "Python" not in cmd and "python" not in cmd:
            continue
        if " -m pytest" not in cmd and "run_full_suite.py" not in cmd:
            continue
        if "claude" in cmd or "grep" in cmd:
            continue
        found.append(pid)
    return sorted(found)


def total_line(summary):
    """The aggregate line. It names how much of the suite is accounted for, so an
    incomplete run can never be read as a complete one (B-083)."""
    tot = dict(summary["totals"])
    tot.update(
        chunks_expected=summary["expected"],
        chunks_reported=summary["reported"],
        missing=len(summary["missing"]),
        signalled=len(summary["signalled"]),
        errored=len(summary["errored"]),
        timed_out=len(summary.get("timed_out") or []),
        unmeasured=summary["unmeasured"],
        verdict=(
            "UNMEASURED-CO-TENANCY"
            if summary.get("co_tenants") is None
            else "CONTAMINATED"
            if summary.get("co_tenants")
            else "COMPLETE"
            if summary["complete"]
            else "INCOMPLETE"
        ),
    )
    named = []
    if summary["missing"]:
        named.append("missing_chunks=%s" % _name(summary["missing"]))
    if summary["signalled"]:
        named.append("signalled_chunks=%s" % _name(summary["signalled"]))
    if summary["errored"]:
        named.append("errored_chunks=%s" % _name(summary["errored"]))
    if summary.get("timed_out"):
        named.append("timed_out_chunks=%s" % _name(summary["timed_out"]))
    if summary.get("co_tenants"):
        named.append("co_tenants=%s" % ",".join(str(x) for x in summary["co_tenants"]))
    tot["named"] = (" " + " ".join(named)) if named else ""
    return (
        "TOTAL passed=%(passed)d failed=%(failed)d errors=%(errors)d "
        "skipped=%(skipped)d xfailed=%(xfailed)d xpassed=%(xpassed)d "
        "total=%(total)d chunks_expected=%(chunks_expected)d "
        "chunks_reported=%(chunks_reported)d missing=%(missing)d "
        "signalled=%(signalled)d errored=%(errored)d timed_out=%(timed_out)d "
        "unmeasured=%(unmeasured)d "
        "VERDICT=%(verdict)s%(named)s" % tot
    )


def main(out_path=None):
    """Run the whole suite in chunks. Returns the process exit code:
    0 complete, 1 incomplete (a chunk never reported or was killed), 2 collection
    failed. An incomplete suite MUST NOT exit 0."""
    out = out_path or OUT
    # B-178: capture the source identity BEFORE any chunk runs. Whatever is on
    # disk later cannot retroactively become what this process loaded.
    boot_src = source_identity()
    # B-216: snapshot FOREIGN suite trees BEFORE any chunk of ours exists, so our
    # own chunk children can never read as co-tenants of ourselves.
    _boot_ps = PS_SOURCE()
    boot_co_tenants = (
        None if _boot_ps is None else co_tenant_pids(_boot_ps, self_pids=(os.getpid(),))
    )

    # B-115: classify the interpreter BEFORE it is allowed to produce a suite count.
    # A count from an interpreter that cannot import the repo's dependencies describes
    # the environment, not the tree -- it must never be folded into the totals.
    _venv_exists = os.path.exists(VENV_PYTHON)
    verdict_env = env_verdict(
        sdk_probe(sys.executable),
        VENV_PYTHON,
        venv_missing=(sdk_probe(VENV_PYTHON) if _venv_exists else None),
        venv_exists=_venv_exists,
    )
    if verdict_env["action"] == "reexec":
        sys.stderr.write(
            "SUITE INTERPRETER: %s; re-exec into %s\n"
            % (verdict_env["reason"], verdict_env["executable"])
        )
        os.execv(
            verdict_env["executable"],
            [verdict_env["executable"], os.path.abspath(__file__)] + sys.argv[1:],
        )
    if not verdict_env["ok"]:
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "a") as fh:
            fh.write(
                "ENV-INVALID interpreter=%s reason=%s\n" % (sys.executable, verdict_env["reason"])
            )
            fh.write(
                "TOTAL VERDICT=ENV-INVALID -- no suite count was measured; this "
                "run must not be read as a regression\n"
            )
        sys.stderr.write(
            "SUITE ENV-INVALID: %s -- refusing to report a suite count\n" % verdict_env["reason"]
        )
        return ENV_INVALID_EXIT

    # B-211: single-flight.  Taken AFTER the env re-exec above, because Python
    # opens fds non-inheritable (PEP 446), so a lock held across os.execv would be
    # silently dropped and the re-exec'd run would hold nothing.
    global _SINGLE_FLIGHT_HANDLE
    _SINGLE_FLIGHT_HANDLE = acquire_single_flight()
    if _SINGLE_FLIGHT_HANDLE is None:
        holder = ""
        try:
            holder = open(SUITE_LOCK).read().strip()
        except OSError:
            pass
        sys.stderr.write(
            "SUITE SINGLE-FLIGHT: another full-suite run holds %s (holder %s) -- "
            "refusing to start a concurrent run against the same tree (B-211)\n"
            % (SUITE_LOCK, holder or "unknown")
        )
        return SINGLE_FLIGHT_EXIT

    rc, ids, tail = collect_ids()
    if rc != 0 or not ids:
        sys.stderr.write("COLLECTION FAILED rc=%s ids=%d\n%s\n" % (rc, len(ids), tail[-2000:]))
        return 2

    os.makedirs(os.path.dirname(out), exist_ok=True)
    fh = open(out, "w")
    nchunks = (len(ids) + CHUNK - 1) // CHUNK
    fh.write(
        "SUITE tests=%d chunks=%d chunk_size=%d started=%s\n"
        % (len(ids), nchunks, CHUNK, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    )
    write_source_stamp(fh, boot_src)
    fh.flush()

    chunks = []
    for i in range(0, len(ids), CHUNK):
        batch = ids[i : i + CHUNK]
        n = i // CHUNK + 1
        t0 = time.time()
        p = run_chunk(batch)
        counts = parse_counts(p.stdout)
        line = ""
        for ln in p.stdout.splitlines():
            if ln.startswith("TESTSUITE_COUNTS"):
                line = ln.strip()
        failures = parse_failures(p.stdout)
        timed_out = bool(getattr(p, "timed_out", False))
        chunks.append(
            {
                "chunk": n,
                "rc": p.returncode,
                "counts": counts,
                "tests": len(batch),
                "failures": failures,
                "timed_out": timed_out,
            }
        )
        fh.write(
            "chunk %02d/%02d rc=%d %s%s elapsed=%.0fs ids=%d..%d\n"
            % (
                n,
                nchunks,
                p.returncode,
                line or "(no TESTSUITE_COUNTS line)",
                chunk_flags(p.returncode, counts, timed_out),
                time.time() - t0,
                i + 1,
                i + len(batch),
            )
        )
        # B-175: the names must be durable the moment the chunk ENDS, not only at
        # end of run. A suite takes ~76 min against a 10-min standup cadence, so an
        # end-of-run-only block leaves the ids resident in memory but unwritten for
        # ~7 consecutive ticks. Distinct prefix so a consumer counting `FAILING `
        # lines cannot double-count; the end-of-run block stays authoritative.
        for node in failures:
            fh.write("chunk %02d/%02d FAILED %s\n" % (n, nchunks, node))
        fh.flush()
        print("chunk %d/%d done" % (n, nchunks), flush=True)

    summary = summarize(chunks)
    summary["co_tenants"] = boot_co_tenants
    verdict = total_line(summary)
    fh.write(verdict + "\n")
    failures = summary["failures"]
    fh.write("FAILING_TESTS count=%d\n" % len(failures))
    for node in failures:
        fh.write("FAILING %s\n" % node)
    fh.write("finished=%s\n" % time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    write_source_end(fh, boot_src, source_identity())
    fh.close()
    print(verdict, flush=True)
    if not summary["complete"]:
        sys.stderr.write(
            "SUITE INCOMPLETE: %d/%d chunks reported, %d test ids never ran "
            "(missing chunks: %s; errored chunks: %s; timed-out chunks: %s) -- this "
            "run does NOT satisfy section 9.3\n"
            % (
                summary["reported"],
                summary["expected"],
                summary["unmeasured"],
                _name(summary["missing"] + summary["signalled"]) or "none",
                _name(summary["errored"]) or "none",
                _name(summary.get("timed_out") or []) or "none",
            )
        )
        return 1
    return 0


USAGE = """usage: run_full_suite.py [-h]

Run the full pytest suite in chunks and write the completeness-checked TOTAL line
to .sapo-loop/logs/<SUITE_OUT or full_suite_315_<pid>.txt>.

Options:
  -h, --help  print this help and exit 0 WITHOUT running any chunk.

The runner takes no other arguments. An unrecognised argument is refused rather
than run (B-172: a sibling's `--help` probe started a real 24-chunk suite).
"""


def source_identity(path=None):
    """sha256 + mtime of this runner's OWN source, or Nones when unreadable (B-178).

    A chunked suite runs ~76 min against a 10-min standup cadence, so the runner
    routinely outlives the code that produced its verdict. Measured 2026-09-13:
    runner pid 10677 booted 17:12:01Z, `run_full_suite.py` was modified 17:47:04Z,
    and the artifact then reported chunks 08 (errors=9), 10 and 11 (failed=1) with
    ZERO failure names -- not because the naming code was missing (B-175 is present
    in the file) but because the process had already loaded its in-memory copy 35
    minutes before that code existed. Editing a file cannot reach a running
    interpreter; only a stamp written INTO the artifact can say so.

    Returns dict(sha256=<hex|None>, mtime=<int|None>). An unreadable path is
    UNKNOWN, never silently CURRENT.
    """
    target = path or os.path.abspath(__file__)
    try:
        with open(target, "rb") as fh:
            digest = hashlib.sha256(fh.read()).hexdigest()
        return dict(sha256=digest, mtime=int(os.stat(target).st_mtime))
    except OSError:
        return dict(sha256=None, mtime=None)


def source_verdict(boot, later):
    """STALE when the source changed mid-run; UNKNOWN when either side is unstamped.

    Three-state on purpose (fail-closed): a missing reading is UNKNOWN, and UNKNOWN
    is never allowed to decay into CURRENT -- the same rule the resource probes use.
    """
    if not boot.get("sha256") or not later.get("sha256"):
        return "UNKNOWN"
    return "STALE" if boot["sha256"] != later["sha256"] else "CURRENT"


def write_source_stamp(fh, ident):
    """Emit the boot-time source stamp as the artifact's second line (B-178)."""
    fh.write("SOURCE sha256=%s mtime=%s\n" % (ident.get("sha256"), ident.get("mtime")))


def write_source_end(fh, boot, later):
    """Emit the end-of-run source verdict + a loud line when the source drifted."""
    verdict = source_verdict(boot, later)
    fh.write("SOURCE_END sha256=%s SOURCE_VERDICT=%s\n" % (later.get("sha256"), verdict))
    if verdict != "CURRENT":
        fh.write(
            "SOURCE_DRIFT this artifact was produced by source sha256=%s, "
            "which is %s the source at end of run (sha256=%s) -- the counts "
            "above describe the code as of BOOT and must not be read as a "
            "verdict on the current tree (B-178)\n"
            % (boot.get("sha256"), verdict, later.get("sha256"))
        )


def parse_argv(argv):
    """Classify argv BEFORE any work happens (B-172).

    Returns ("help",) / ("error", bad) / ("run",). `-h` and `--help` win over any
    other argument so an inspection can never fall through into a run; anything
    else is unrecognised, because the runner takes no positional or flag
    arguments today.
    """
    for arg in argv:
        if arg in ("-h", "--help"):
            return ("help",)
    if argv:
        return ("error", argv[0])
    return ("run",)


if __name__ == "__main__":
    _mode = parse_argv(sys.argv[1:])
    if _mode[0] == "help":
        sys.stdout.write(USAGE)
        sys.exit(0)
    if _mode[0] == "error":
        sys.stderr.write("unrecognised argument: %s\n\n%s" % (_mode[1], USAGE))
        sys.exit(2)
    sys.exit(main())
