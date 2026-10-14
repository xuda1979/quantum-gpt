"""C-STALE storm followup (2026-09-30, second occurrence of the C-10152b
storm class): cmd_dispatch on a tmp/fixture state dir MUST NOT launch a
real claude worker.

MEASURED 2026-09-30 09:01-09:06 CST: tests/test_c10152b_stale_budget_mark_
unmark.py::test_stale_mark_clears_when_budget_becomes_feasible calls
cmd_dispatch twice; tick-2 (budget raised 45 -> 60, feasible) reached
spawn_worker WITHOUT QGH_NO_SPAWN=1 and spawned FIVE live ghost
trainer-ops workers for card C-STALE (claude pids 90720/93635/93939/
96889/98320 + successors every ~30-60s), each burning a 60-min token
budget on a card that does not exist in QUEUE.json. Same recursion class
as the measured 2026-09-28 C-10152b storm (~390 processes / 150 pytest
runs). The 2026-09-28 fix was an opt-IN env (QGH_NO_SPAWN=1) -- new
tests forget to set it. Fail closed by DEFAULT:

  spawn_worker launches a real worker ONLY when STATE resolves to the
  repo production harness/state dir (or QGH_ALLOW_SPAWN=1 explicit
  operator override). Any other state dir gets the no-op sleep stub --
  dispatch semantics (claim, fleet entry, events) stay intact.

Contract (TDD -- RED first):
  1. cmd_dispatch on a tmp state dir with a FEASIBLE ready card must
     never Popen a real worker_command() (claude) -- only the sleep stub.
  2. _spawn_state_is_production() is False for tmp STATE, True for the
     repo production path.
  3. QGH_ALLOW_SPAWN=1 keeps the operator escape hatch (real command
     allowed even under a non-default state dir).
"""

import importlib.util
import os

_HARNESS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "harness")
QGH_PATH = os.path.join(_HARNESS_DIR, "qgh.py")
PROD_STATE = os.path.join(_HARNESS_DIR, "state")

_counter = [0]


def _load_qgh(state_dir):
    _counter[0] += 1
    os.environ["QGH_STATE_DIR"] = str(state_dir)
    modname = "qgh_cstale_spawn_" + str(_counter[0])
    spec = importlib.util.spec_from_file_location(modname, QGH_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.cmd_init(None)
    return mod


class _FakeProc:
    """Stand-in Popen result: context-manager + communicate/wait, because the
    recorder patches the shared subprocess module (subprocess.run uses Popen
    as a context manager for lane probes inside the same dispatch path)."""

    pid = 424242
    returncode = 0

    def __init__(self, args=None):
        self.args = args

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def communicate(self, *a, **k):
        return ("", "")

    def wait(self, *a, **k):
        return 0

    def poll(self, *a, **k):
        return 0


def _mkcard(mod, cid, lane, budget_min):
    c = mod.H.new_card(
        "task " + cid + " regression text",
        lane,
        "goal edge regression text",
        ["acceptance criterion for test"],
        budget_min=budget_min,
    )
    c["id"] = cid
    return c


def _dispatch_recording_popen(mod):
    real_popen = mod.subprocess.Popen
    calls = []

    def _rec(cmd, **kw):
        calls.append(str(cmd))
        return _FakeProc(cmd)

    mod.subprocess.Popen = _rec

    def _restore():
        mod.subprocess.Popen = real_popen

    return calls, _restore


def _spawn_feasible_card(mod):
    """Drive spawn_worker DIRECTLY (gate-independent): feasible ready card,
    fresh queue -- the exact call the C-STALE storm reached via tick-2."""
    card = _mkcard(mod, "C-STALE", "trainer-ops", budget_min=60)
    card["status"] = "ready"
    q = dict(cards=[card], seq=1)
    mod.H.save_json(os.path.join(str(mod.STATE), "QUEUE.json"), q)
    goal = mod.load_goal(mod.STATE)
    return mod.spawn_worker(goal, q, card, dict())


def test_tmp_state_dispatch_never_spawns_real_worker(tmp_path, monkeypatch):
    monkeypatch.delenv("QGH_NO_SPAWN", raising=False)
    monkeypatch.delenv("QGH_ALLOW_SPAWN", raising=False)
    mod = _load_qgh(tmp_path)
    calls, restore = _dispatch_recording_popen(mod)
    try:
        _spawn_feasible_card(mod)
    finally:
        restore()
    real = [c for c in calls if "claude" in c and "--print" in c]
    assert not real, (
        "cmd_dispatch under tmp state dir spawned a REAL worker command "
        "(storm class C-10152b/C-STALE): " + repr(real)
    )
    assert any(
        "/bin/sleep" in c for c in calls
    ), "tmp-state spawn must still run the no-op sleep stub (dispatch semantics intact)"


def test_spawn_state_is_production_predicate(tmp_path, monkeypatch):
    monkeypatch.delenv("QGH_ALLOW_SPAWN", raising=False)
    mod = _load_qgh(tmp_path)
    assert not mod._spawn_state_is_production(), "tmp STATE must not count as production"
    mod.STATE = PROD_STATE
    assert mod._spawn_state_is_production(), "repo harness/state must count as production"


def test_qgh_allow_spawn_operator_override(tmp_path, monkeypatch):
    monkeypatch.delenv("QGH_NO_SPAWN", raising=False)
    monkeypatch.setenv("QGH_ALLOW_SPAWN", "1")
    mod = _load_qgh(tmp_path)
    calls, restore = _dispatch_recording_popen(mod)
    try:
        _spawn_feasible_card(mod)
    finally:
        restore()
    assert any(
        "claude" in c for c in calls
    ), "operator override must permit the real worker command"
