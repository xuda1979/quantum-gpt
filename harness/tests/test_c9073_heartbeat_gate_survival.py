"""C-9073 regression: the worker heartbeat must survive session write gates.

Gate-degraded sessions deny shell redirection (te/echo appends) at the
permission layer (live 2026-09-17: C-9070 lost appends, tee AND Write-tool
on its .progress file; C-9065 disclosed the same gate the prior hour; this
card's own first heartbeat `echo ... >> file` was BLOCKED the same way).
The brief's documented recipe was that echo append, so a gate-stranded
worker goes heartbeat-silent and the reaper kills it as STALLED (>20 min)
despite real progress -- burned dispatch throughput for a working worker.

Fix under test: the heartbeat route is a python append via
`harness/qgh.py heartbeat` (harness_lib.append_heartbeat), never shell
redirection, and spawn_worker pre-creates agents/<card>.progress so the
file exists and its freshness clock starts before the worker runs.
"""

import os
import subprocess
import time

from harness import harness_lib as H
from harness import qgh

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _card(cid="C-9073"):
    return {
        "id": cid,
        "lane": "fixer",
        "title": "t",
        "why": "w",
        "acceptance": ["a"],
        "gates": [],
        "deps": [],
        "budget_min": 20,
        "status": "ready",
        "claimed_by": None,
        "claimed_utc": None,
        "deadline_utc": None,
        "priority": 1,
    }


def _brief_hb_command(brief):
    """The heartbeat command line the brief instructs the worker to run."""
    lines = brief.splitlines()
    for i, ln in enumerate(lines):
        if ln.startswith("HEARTBEAT (mandatory):"):
            return lines[i + 1].strip()
    raise AssertionError("brief has no HEARTBEAT instruction")


def test_brief_never_teaches_shell_redirection():
    # RED: the documented recipe was the echo double-chevron append,
    # denied at the permission layer in gate-degraded sessions.
    brief = H.compose_brief({"objective": "g"}, _card())
    assert ">>" not in brief, (
        "brief still teaches a shell >> heartbeat (denied in gate-degraded sessions)"
    )
    assert "qgh.py heartbeat" in brief, "brief must name the python-append heartbeat route"


def test_instructed_heartbeat_records_progress_without_redirection():
    # Simulate the gate mechanically: the instructed command itself must
    # contain no redirection operator, and running it exactly as instructed
    # (subprocess, no shell append anywhere) must record progress.
    brief = H.compose_brief({"objective": "g"}, _card())
    cmd = _brief_hb_command(brief)
    assert ">" not in cmd, f"instructed heartbeat uses redirection: {cmd!r}"
    marker = "c9073-probe-marker"
    proc = subprocess.run(
        cmd.replace("what you just did", marker),
        shell=True,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
        env={**os.environ, "QGH_STATE_DIR": qgh.STATE},  # pin the seam: a
        # sibling module in the same pytest run may perturb os.environ, and
        # the child must write exactly the dir this test asserts on
    )
    assert proc.returncode == 0, f"heartbeat command failed: {proc.stderr}"
    hb_path = os.path.join(qgh.STATE, "agents", "C-9073.progress")
    assert os.path.exists(hb_path), "heartbeat did not record progress"
    body = open(hb_path, encoding="utf-8").read()
    assert marker in body
    assert time.time() - os.path.getmtime(hb_path) < H.STALL_MIN * 60, (
        "recorded heartbeat is already stale"
    )


def test_spawn_precreates_progress_file_before_worker_starts(monkeypatch):
    state = qgh.STATE
    for sub in ("briefs", "agents", "locks"):
        os.makedirs(os.path.join(state, sub), exist_ok=True)
    card = _card("C-9073A")
    queue = {"cards": [card], "seq": 1}
    # qgh imports bare "import harness_lib as H": patch THAT module object,
    # not the harness.harness_lib package twin (distinct sys.modules entry).
    monkeypatch.setattr(qgh.H, "process_lstart", lambda pid: 1.0)

    class FakeProc:
        def __init__(self):
            self.pid = 424242

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    monkeypatch.setattr(qgh.subprocess, "Popen", lambda *a, **k: FakeProc())
    hb_path = os.path.join(state, "agents", "C-9073A.progress")
    assert not os.path.exists(hb_path), "test precondition: no progress file yet"
    entry = qgh.spawn_worker({"objective": "g"}, queue, card, [])
    assert entry and entry["card"] == "C-9073A"
    assert os.path.exists(hb_path), (
        "dispatch did not pre-create agents/<card>.progress; a worker that "
        "never heartbeats skips the stall check (missing-file fail-open) and "
        "a gate-stranded worker has no file to append to"
    )
    age = time.time() - os.path.getmtime(hb_path)
    assert age < H.STALL_MIN * 60, "pre-created file already stale at spawn"
