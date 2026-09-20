"""C-9098: re-arm ASI2 window-open sentinel -- keep window_open.json fresh.

RED first 2026-09-18: the C-9061 sentinel is a ONE-SHOT -- after its single
bounded pass exits, nothing re-arms it, so window_open.json (07:58:46Z)
aged past the C-9071 freshness bar (1800s) and every gate pass since
04:37Z SKIPs on window=window_open_stale while ASI2 sits ready (pid 32056
ready at 04:23Z went unconsumed). Contract under test:
  - run_rearm loops the C-9020 two-signal bar until an explicit expiry and
    REWRITES window_open.json on every bar-met poll with a fresh
    generated_utc, stamping the staleness bar (window_fresh_s) and this
    loop's expiry into the artifact;
  - expiry is fail-closed: a window_not_open.json names the block
    (reason=rearm-expired); window_open.json is never written unless the
    bar was met;
  - integration: after run_rearm, the C-9071 gate evaluates the artifact
    with NO 'window' unmet (the window key no longer reads
    window_open_stale).
All daemon I/O is injected fakes: the suite never touches the network.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "harness"))
import asi2_window_sentinel as S  # noqa: E402

ECHO = "echo ALIVE"


def _body(pid=32056, ready=True, **kw):
    b = dict(ok=True, ready=ready, startupState="ready" if ready else "booting", pid=pid)
    b.update(kw)
    return b


class FakeDaemon:
    """Scripted per-poll daemon: health() advances the poll index; the last
    entry holds for all later polls; echo() is recorded."""

    def __init__(self, polls):
        self.polls = polls  # dicts: {"health": body|exc, "exec": str|exc}
        self.i = -1
        self.exec_calls = []

    def _poll(self):
        return self.polls[min(self.i, len(self.polls) - 1)]

    def health(self, port, timeout=8):
        self.i += 1
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


def mk(tmp_path, polls, rearm_budget_s=600.0, poll_s=60.0, pid_gap_s=0.0):
    f = FakeDaemon(polls)
    t = dict(now=0.0)

    def sleep(s):
        t["now"] += s

    ctx = S.make_ctx(
        artifact_dir=str(tmp_path / "c9061"),
        probes_dir=str(tmp_path / "probes"),
        port=19004,
        budget_s=100000.0,
        poll_s=poll_s,
        pid_gap_s=pid_gap_s,
        rearm_budget_s=rearm_budget_s,
        window_fresh_s=1800.0,
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


def test_rearm_rewrites_window_open_on_simulated_ready(tmp_path):
    """Always-ready daemon + stable pid: run_rearm rewrites window_open.json
    on every bar-met poll and stamps the staleness bar + expiry."""
    ctx, f = mk(tmp_path, [dict(health=_body(pid=32056), exec="ALIVE")])
    res = S.run_rearm(ctx)
    assert res["opens"] >= 2  # refreshed more than once, not a one-shot
    art = _artifact(ctx, "window_open.json")
    assert art is not None and art["artifact"] == "window_open"
    assert art["card"] == "C-9098"
    st = art.get("staleness") or {}
    assert st.get("window_fresh_s") == 1800.0  # the C-9071 bar, in-artifact
    assert st.get("expires_utc")  # expiry named, parseable
    assert f.exec_calls and all(c == ECHO for c in f.exec_calls)


def test_rearm_expires_fail_closed_and_names_block(tmp_path):
    """Daemon never ready: run_rearm must expire fail-closed -- a
    window_not_open artifact naming the block, never a window_open."""
    ctx, _f = mk(
        tmp_path,
        [dict(health=_body(ready=False))],
        rearm_budget_s=180.0,
    )
    res = S.run_rearm(ctx)
    assert res["opens"] == 0
    assert _artifact(ctx, "window_open.json") is None  # fail-closed
    block = _artifact(ctx, "window_not_open.json")
    assert block is not None
    assert block["artifact"] == "window_not_open"
    assert block["reason"] == "rearm-expired"
    assert block["card"] == "C-9098"


def test_gate_window_unmet_resolves_on_rearmed_artifact(tmp_path):
    """Integration: an artifact freshly rewritten by run_rearm must make the
    C-9071 gate's 'window' key resolve (no window_open_stale). Preflight
    artifacts are absent here -- SKIP is expected, but 'window' must be
    CLEAN (the preflights are other cards' deliverables)."""
    ctx, _f = mk(tmp_path, [dict(health=_body(pid=32056), exec="ALIVE")], rearm_budget_s=120.0)
    S.run_rearm(ctx)
    import time

    import asi2_window_preflight_gate as G

    gctx = G.make_ctx(
        tmp_path / "c9061",
        tmp_path / "preflights",  # empty: SKIP via missing preflights
        tmp_path / "gate",
        tmp_path / "state",
        clock=time.time,
    )
    verdict, _path, detail = G.evaluate(gctx)
    assert verdict == "SKIP"  # preflights missing (other cards)
    assert "window" not in detail["unmet"], detail["unmet"]


def test_cli_rearm_flag_routes_to_run_rearm(tmp_path):
    """--rearm on the CLI dispatches run_rearm (operators re-arm the
    sentinel without writing python); detect-only, rc 0."""
    ctx, _f = mk(tmp_path, [dict(health=_body(pid=32056), exec="ALIVE")], rearm_budget_s=120.0)
    rc = S.main(["--rearm"], ctx_factory=lambda args: ctx)
    assert rc == 0
    art = _artifact(ctx, "window_open.json")
    assert art is not None and art["card"] == "C-9098"
