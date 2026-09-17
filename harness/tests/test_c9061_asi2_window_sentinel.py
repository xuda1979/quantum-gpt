"""C-9061: ASI2 window-open sentinel -- detect-only, bounded, fail-closed.

RED first 2026-09-17: no harness/asi2_window_sentinel.py existed. C-0051
(combined detect+fire watcher) bounced 3x on "no RESULT verdict" because it
waited for the window inside its own budget; this card splits detect from
launch. Contract under test:
  - the C-9020 two-signal bar: :19004 /health ready=true AND the SAME pid
    held >=5 min apart (C-9020 boot-restart loop shows a NEW pid every
    probe) AND an ACTIVE /exec "echo ALIVE" round-trip (C-9021: a clean
    health body alone cannot distinguish ready from wedged);
  - bounded single pass: writes EXACTLY ONE terminal artifact --
    window_open.json or window_not_open.json (with the last probe JSON) --
    then exits DONE; never waits past budget;
  - on window-open the artifact names its consumer (C-9029 requeue path);
    the sentinel NEVER dispatches, launches, or requeues by itself (neither
    path launches any leg);
  - every probe banked under harness/state/probes/; any probe error is
    fail-closed (unknown is never open).
All daemon I/O is injected fakes: the suite never touches the network.

Supersedes: C-0051 (detect half; the fire half stays with the C-9029
requeue path).
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "harness"))
import asi2_window_sentinel as S  # noqa: E402

ECHO = "echo ALIVE"


def _body(pid=99, ready=True, **kw):
    b = dict(ok=True, ready=ready, startupState="ready" if ready else "booting", pid=pid)
    b.update(kw)
    return b


class FakeDaemon:
    """Scripted per-poll daemon. health() advances the poll index; echo() is
    recorded -- the sentinel may call it ONLY with the echo ALIVE command."""

    def __init__(self, polls):
        self.polls = polls  # dicts: {"health": body|exc, "exec": str|exc}
        self.i = -1
        self.health_calls = 0
        self.exec_calls = []

    def _poll(self):
        return self.polls[min(self.i, len(self.polls) - 1)]

    def health(self, port, timeout=8):
        self.i += 1
        self.health_calls += 1
        h = self._poll().get("health")
        if isinstance(h, Exception):
            raise h
        return dict(code=200, body=json.dumps(h))

    def echo(self, port, command, wait_ms=15000):
        self.exec_calls.append(command)
        e = self._poll().get("exec", "ALIVE")
        if isinstance(e, Exception):
            raise e
        return dict(rc=0, output=e + "\n")


def mk(tmp_path, polls, budget_s=100000.0, poll_s=60.0, pid_gap_s=300.0):
    f = FakeDaemon(polls)
    t = dict(now=0.0)

    def sleep(s):
        t["now"] += s

    ctx = S.make_ctx(
        artifact_dir=str(tmp_path / "c9061"),
        probes_dir=str(tmp_path / "probes"),
        port=19004,
        budget_s=budget_s,
        poll_s=poll_s,
        pid_gap_s=pid_gap_s,
        health_fn=f.health,
        exec_fn=f.echo,
        clock=lambda: t["now"],
        sleep=sleep,
    )
    return ctx, f


def _artifact(ctx, name):
    p = Path(ctx["artifact_dir"]) / name
    if not p.is_file():
        return None
    return json.loads(p.read_text())


def _probes(ctx):
    return sorted(Path(ctx["probes_dir"]).glob("C-9061-*.json"))


# ------------------------------------------------------------ the bar is MET
def test_bar_met_writes_exactly_one_window_open_artifact(tmp_path):
    stable = [{"health": _body(pid=99)} for _ in range(7)]
    ctx, f = mk(tmp_path, stable)
    verdict, rc = S.run_sentinel(ctx)
    assert (verdict, rc) == ("window_open", 0)
    art = _artifact(ctx, "window_open.json")
    assert art is not None and art["card"] == "C-9061"
    assert art["bar"]["health_ready"] is True
    assert art["bar"]["pid"] == 99
    assert art["bar"]["pid_stable_s"] >= 300
    assert art["bar"]["exec"] == "ALIVE"
    # consumer named; sentinel never dispatches by itself
    assert art["consumer"]["card"] == "C-9029"
    assert art["consumer"]["action"] == "requeue"
    assert "C-0051" in art["supersedes"]
    # exactly ONE terminal artifact; every probe banked
    assert _artifact(ctx, "window_not_open.json") is None
    assert len(_probes(ctx)) >= 6


def test_bar_confirms_only_after_full_pid_gap_no_early_echo(tmp_path):
    # pid stable only ~240s inside a 240s budget: the exec confirm must NEVER
    # run early (the C-9020 boot-restart signature needs the full gap).
    stable = [{"health": _body(pid=99)} for _ in range(10)]
    ctx, f = mk(tmp_path, stable, budget_s=240.0)
    verdict, rc = S.run_sentinel(ctx)
    assert verdict == "window_not_open"
    assert f.exec_calls == []  # no confirm before 300s of pid stability
    assert _artifact(ctx, "window_open.json") is None
    notopen = _artifact(ctx, "window_not_open.json")
    assert notopen is not None and notopen["last_probe"] is not None


# --------------------------------------------------------- the bar is NOT met
def test_budget_exhausted_writes_window_not_open_with_last_probe(tmp_path):
    ctx, f = mk(tmp_path, [{"health": _body(ready=False)}], budget_s=120.0)
    verdict, rc = S.run_sentinel(ctx)
    assert (verdict, rc) == ("window_not_open", 0)  # bounded DONE, not a hang
    art = _artifact(ctx, "window_not_open.json")
    assert art is not None and art["reason"] == "budget-exhausted-window-not-open"
    assert art["last_probe"]["ready"] is False
    assert _artifact(ctx, "window_open.json") is None


def test_pid_churn_boot_restart_loop_never_opens(tmp_path):
    # C-9020 measured signature: ready=true under a NEW pid every probe.
    churn = [{"health": _body(pid=p)} for p in (99, 99, 99, 99, 100, 101, 102, 103)]
    ctx, f = mk(tmp_path, churn, budget_s=480.0)
    verdict, rc = S.run_sentinel(ctx)
    assert verdict == "window_not_open"
    assert f.exec_calls == []  # stability never held long enough to confirm
    assert _artifact(ctx, "window_open.json") is None
    assert len(_probes(ctx)) >= 8  # every probe banked


def test_exec_wedge_fail_closed_never_open(tmp_path):
    # C-9021: clean ready body + wedged /exec is NOT a window.
    wedge = [{"health": _body(pid=99), "exec": TimeoutError("exec timed out")}] * 3
    ctx, f = mk(tmp_path, wedge, budget_s=420.0)
    verdict, rc = S.run_sentinel(ctx)
    assert verdict == "window_not_open"
    assert f.exec_calls  # confirm attempted after the full gap...
    assert _artifact(ctx, "window_open.json") is None  # ...and fail-closed
    art = _artifact(ctx, "window_not_open.json")
    assert "timed out" in json.dumps(art["last_probe"])


def test_health_error_fail_closed(tmp_path):
    ctx, f = mk(tmp_path, [{"health": OSError("conn refused")}], budget_s=120.0)
    verdict, rc = S.run_sentinel(ctx)
    assert verdict == "window_not_open"
    recs = [json.loads(p.read_text()) for p in _probes(ctx)]
    assert recs and all(r.get("error") for r in recs)
    assert _artifact(ctx, "window_open.json") is None


# ------------------------------------------------------------- never launches
def test_neither_path_launches_any_leg(tmp_path):
    stable = [{"health": _body(pid=99)} for _ in range(7)]
    ctx, f = mk(tmp_path, stable)
    S.run_sentinel(ctx)  # the OPEN path
    assert f.exec_calls == [ECHO]  # the ONLY exec ever sent is the echo probe
    src = Path(S.__file__).read_text()
    for marker in ("nohup", "qg_launch", "subprocess", "system("):
        assert marker not in src, "sentinel source carries a launch surface: " + marker


def test_not_open_path_launches_nothing(tmp_path):
    ctx, f = mk(tmp_path, [{"health": _body(ready=False)}], budget_s=120.0)
    S.run_sentinel(ctx)
    assert f.exec_calls == []
    assert f.health_calls >= 1


# ------------------------------------------------------------ docs / main()
def test_poll_interval_documented():
    assert S.POLL_S == 60.0
    assert "poll interval" in (S.__doc__ or "").lower()


def test_main_bounded_pass_returns_done_rc_with_artifact(tmp_path):
    f = FakeDaemon([{"health": _body(ready=False)}])
    ctx = S.make_ctx(
        artifact_dir=str(tmp_path / "c9061"),
        probes_dir=str(tmp_path / "probes"),
        port=19004,
        budget_s=0.0,
        health_fn=f.health,
        exec_fn=f.echo,
        clock=lambda: 0.0,
        sleep=lambda s: None,
    )
    rc = S.main(
        ["--artifact-dir", str(tmp_path / "c9061"), "--probes-dir", str(tmp_path / "probes")],
        ctx_factory=lambda args: ctx,
    )
    assert rc == 0  # DONE: bounded pass produced its terminal artifact
    assert _artifact(ctx, "window_not_open.json") is not None
