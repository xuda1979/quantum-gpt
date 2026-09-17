#!/usr/bin/env python3
"""B-200: the chunked full-suite runner must BOUND its wait on a chunk.

MEASURED DEFECT (.sapo-loop/run_full_suite.py, tick #434, 2026-09-14 23:41Z).
`run_chunk` calls `subprocess.run(..., capture_output=True)` with NO `timeout=`.
Two consequences, both measured live on this host:

  - artifact .sapo-loop/logs/full_suite_315_79513.txt, runner pid 79513, measured on
    this host: chunk 01 = 223s, chunk 02 = 3066s, chunk 03 = 131s. Chunk 02 spent 51
    MINUTES -- 15-20x its siblings -- and for the whole of it the artifact was
    byte-identical to a wedged process.
  - the chunk's pytest child, pid 81772, was resident 49:31 with 3:40.12 of CPU time
    and STAT `S`; sampled twice 20 s apart it advanced 0.23 s of CPU (~1.2% busy).

The child had not died -- it did finish, at 3066s. The defect is that NOTHING COULD
TELL: `capture_output=True` holds the child's output until it returns and no timeout
bounds the wait, so "slow" and "hung" are the same reading from outside. This tick
read it as a hang and was wrong. That is the failure mode this file pins: the
instrument that enforces section 9.3 ("run ALL tests every tick") goes silent for
arbitrary lengths of time, and every later tick re-reads the same frozen artifact as
"still running" with no way to distinguish the two.

The bound is therefore calibrated ABOVE measured reality (3066s -> 3600s default): a
timeout that fires on a legitimately slow chunk is a false alarm, and the skill prices
a false alarm as dearly as a missed one.

CONTRACT PINNED HERE:
  1. run_chunk passes a positive `timeout=` to subprocess.run, so the wait is bounded.
  2. A chunk that exceeds it returns a NOT-MEASURED record instead of propagating
     TimeoutExpired. `parse_counts` over its output is None, which is the existing
     "never reported" fact -- not a report of zeros (B-083/B-158).
  3. The chunk is named as TIMED OUT, and the TOTAL line certifies INCOMPLETE and
     names it, so a hang can never be read as a complete suite.

SAFETY: these tests feed SYNTHETIC chunk results and a stubbed subprocess.run. They
never run the suite and never write into .sapo-loop/logs/ (a real run is in flight).
"""

from __future__ import annotations

import ast
import importlib.util
import os
import pathlib
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[1]
RUNNER = REPO / ".sapo-loop" / "run_full_suite.py"


def _load_runner(path=RUNNER):
    """Import the runner module WITHOUT executing the suite it drives.

    Same safety gate as tests/test_full_suite_runner_reports_incomplete.py: importing
    a runner whose suite code is not behind `if __name__ == "__main__"` would launch a
    real 24-chunk suite run from inside this test process.
    """
    src = pathlib.Path(path).read_text()
    tree = ast.parse(src)
    funcs = {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}
    absent = sorted({"main", "summarize", "run_chunk"} - funcs)
    assert not absent, (
        "runner %s is not importable without running the suite: %s missing (B-200)" % (path, absent)
    )
    guarded = any(isinstance(n, ast.If) and "__main__" in ast.unparse(n.test) for n in tree.body)
    assert guarded, "runner has no main guard: importing it executes the whole suite (B-200)"
    spec = importlib.util.spec_from_file_location("suite_runner_timeout_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # B-216: these tests pin CHUNK ACCOUNTING and run_chunk's timeout, not
    # co-tenancy. Neutralise the ambient process table so a real co-tenant suite
    # on this machine cannot flip their verdict.
    mod.PS_SOURCE = lambda: ""
    # B-225: the same ambient-dependency class as PS_SOURCE, one layer over. main()
    # consults the REAL SUITE_LOCK, so while ANY full-suite run is live -- including
    # the one that is running this very file -- acquire_single_flight() returns None and
    # main() returns SINGLE_FLIGHT_EXIT before a single chunk runs; every _drive() case
    # then dies with "expected N chunks, ran 0". Point the lock at a private path so the
    # flock is still exercised for real, just never against a live run. The cross-file
    # guard in tests/test_full_suite_runner_lock_hermetic.py keeps a future file honest.
    mod.SUITE_LOCK = os.path.join(tempfile.mkdtemp(prefix="suite_lock_"), "runner.lock")
    return mod


class _Proc:
    """A synthetic `subprocess.CompletedProcess`."""

    def __init__(self, rc, stdout="", timed_out=False):
        self.returncode = rc
        self.stdout = stdout
        self.stderr = ""
        self.timed_out = timed_out


def _counts_line(passed=0, failed=0):
    total = passed + failed
    return (
        "TESTSUITE_COUNTS passed=%d failed=%d errors=0 skipped=0 "
        "xfailed=0 xpassed=0 deselected=0 total=%d" % (passed, failed, total)
    )


def _pin_interpreter_verdict(mod, monkeypatch):
    """Stop main() from os.execv-ing out of the TEST process (B-173)."""
    monkeypatch.setattr(
        mod,
        "env_verdict",
        lambda *a, **k: {
            "action": "run",
            "ok": True,
            "reason": "pinned by test",
            "executable": sys.executable,
        },
    )


def _drive(mod, monkeypatch, tmp_path, plan, per_chunk=2):
    """Run main() over synthetic chunk results; returns (returncode, log text).

    `plan` has one entry per expected chunk: (rc, stdout) or (rc, stdout, timed_out).
    """
    _pin_interpreter_verdict(mod, monkeypatch)
    monkeypatch.setattr(mod, "CHUNK", per_chunk)
    ids = ["tests/test_synthetic.py::test_%03d" % i for i in range(len(plan) * per_chunk)]
    monkeypatch.setattr(mod, "collect_ids", lambda: (0, ids, ""))

    calls = []

    def _fake_run_chunk(batch):
        calls.append(list(batch))
        entry = plan[len(calls) - 1]
        return _Proc(entry[0], entry[1], timed_out=(len(entry) > 2 and entry[2]))

    monkeypatch.setattr(mod, "run_chunk", _fake_run_chunk)
    log = tmp_path / "synthetic_suite.txt"
    rc = mod.main(out_path=str(log))
    assert len(calls) == len(plan), "expected %d chunks, ran %d" % (len(plan), len(calls))
    return rc, log.read_text()


def _total_line(text):
    lines = [ln for ln in text.splitlines() if ln.startswith("TOTAL")]
    assert lines, "runner wrote no TOTAL line:\n" + text
    return lines[-1]


def _fields(total):
    return dict(kv.partition("=")[::2] for kv in total.split()[1:])


def test_run_chunk_bounds_its_wait(monkeypatch):
    """The defect itself: subprocess.run must be given a positive `timeout=`."""
    mod = _load_runner()
    seen = {}

    def _fake_run(cmd, **kwargs):
        seen["cmd"] = cmd
        seen["kwargs"] = kwargs
        raise subprocess.TimeoutExpired(cmd, kwargs.get("timeout") or 0)

    monkeypatch.setattr(mod.subprocess, "run", _fake_run)
    mod.run_chunk(["tests/test_synthetic.py::test_000"])

    assert "timeout" in seen["kwargs"], (
        "run_chunk waits on a chunk with NO timeout -- a blocked test blocks the whole "
        "suite forever and, because stdout is captured, writes nothing while it does: "
        "measured 52 min frozen at chunk 01/24 (B-200). kwargs=%r" % (seen["kwargs"],)
    )
    assert isinstance(seen["kwargs"]["timeout"], (int, float)) and seen["kwargs"]["timeout"] > 0, (
        "run_chunk's chunk timeout must be a positive number of seconds: %r"
        % (seen["kwargs"]["timeout"],)
    )


def test_a_timed_out_chunk_returns_not_measured(monkeypatch):
    """A blown timeout is a MISSING measurement, not a crash and not a zero report."""
    mod = _load_runner()

    def _fake_run(cmd, **kwargs):
        raise subprocess.TimeoutExpired(
            cmd, kwargs.get("timeout") or 0, output=_counts_line(passed=1)
        )

    monkeypatch.setattr(mod.subprocess, "run", _fake_run)
    p = mod.run_chunk(["tests/test_synthetic.py::test_000"])

    assert getattr(p, "timed_out", False) is True, (
        "a chunk that blew its timeout is not marked as timed out, so the aggregation "
        "cannot name it: %r" % (p,)
    )
    s = mod.summarize(
        [
            {
                "chunk": 1,
                "rc": p.returncode,
                "counts": mod.parse_counts(p.stdout),
                "tests": 2,
                "failures": [],
                "timed_out": True,
            }
        ]
    )
    assert s["timed_out"] == [1], "a timed-out chunk did not land in its own bucket: %r" % (s,)
    assert s["totals"]["passed"] == 0 and s["totals"]["total"] == 0, (
        "a timed-out chunk's PARTIAL counts were folded into the suite totals; it "
        "never finished, so it contributes no measurement (B-083/B-200): %r" % (s,)
    )
    assert s["complete"] is False, (
        "a run containing a timed-out chunk was certified complete: %r" % (s,)
    )


def test_a_timed_out_chunk_makes_the_run_read_incomplete(monkeypatch, tmp_path):
    """A hang must be visible from the aggregate, and name itself."""
    mod = _load_runner()
    rc, text = _drive(
        mod,
        monkeypatch,
        tmp_path,
        plan=[
            (0, _counts_line(passed=2)),  # chunk 01: reported
            (mod.TIMEOUT_RC, "", True),  # chunk 02: HUNG, no report
            (0, _counts_line(passed=2)),  # chunk 03: reported
        ],
    )
    total = _total_line(text)
    f = _fields(total)
    assert f.get("VERDICT") == "INCOMPLETE", (
        "a chunk that never returned still certified a complete suite: %r" % total
    )
    assert f.get("timed_out_chunks") == "02", (
        "the TOTAL line does not name WHICH chunk timed out: %r" % total
    )
    assert rc != 0, "the runner exited 0 with a chunk that never returned (rc=%r)" % rc
    assert "TIMEOUT" in text, (
        "the per-chunk line carries no TIMEOUT marker for the hung chunk:\n" + text
    )


def test_the_chunk_bound_sits_above_measured_chunk_times():
    """Calibration guard: the bound must not fire on a chunk that is merely SLOW.

    MEASURED 2026-09-14 (artifact .sapo-loop/logs/full_suite_315_79513.txt):
    chunk 01 = 223s, chunk 02 = 3066s, chunk 03 = 131s. 3066s is a COMPLETED,
    legitimate, reporting chunk on this host, so any bound at or below it converts a
    real measurement into a false TIMEOUT. Raising the bound is the correct response
    to a TIMEOUT report; lowering it is not.
    """
    mod = _load_runner()
    assert mod.CHUNK_TIMEOUT_S > 3066, (
        "CHUNK_TIMEOUT_S=%r would kill the 3066s chunk that this host measured and "
        "reported normally -- re-calibrate above observed chunk times before shipping "
        "(B-200)" % (mod.CHUNK_TIMEOUT_S,)
    )


def test_a_complete_run_is_unaffected_by_the_timeout_gate(monkeypatch, tmp_path):
    """Over-reach guard: the fix must not make every run look incomplete."""
    mod = _load_runner()
    rc, text = _drive(
        mod,
        monkeypatch,
        tmp_path,
        plan=[
            (0, _counts_line(passed=2)),
            (1, _counts_line(passed=1, failed=1)),
            (0, _counts_line(passed=2)),
        ],
    )
    f = _fields(_total_line(text))
    assert f.get("VERDICT") == "COMPLETE", _total_line(text)
    assert f.get("timed_out_chunks", "00") in ("00", "0"), _total_line(text)
    assert rc == 0, "the timeout gate broke a normal run (rc=%r)" % rc


def test_grpo_pipeline_chunk_uses_doubled_timeout(monkeypatch, tmp_path):
    """B-330: chunks where test_grpo_pipeline_fast.py dominates get a longer timeout."""
    mod = _load_runner()
    heavy_ids = ["tests/test_grpo_pipeline_fast.py::test_a"] * 150
    mild_ids = ["tests/test_sapo_loss.py::test_a"] * 100
    mixed_ids = ["tests/test_grpo_pipeline_fast.py::test_a"] * 80 + [
        "tests/test_sapo_loss.py::test_a"
    ] * 120
    assert mod._chunk_timeout_for(heavy_ids) == mod.HEAVY_CHUNK_TIMEOUT_S
    assert mod._chunk_timeout_for(mild_ids) == mod.CHUNK_TIMEOUT_S
    assert mod._chunk_timeout_for(mixed_ids) == mod.CHUNK_TIMEOUT_S  # <50% heavy -> normal
    assert mod._chunk_timeout_for([]) == mod.CHUNK_TIMEOUT_S
