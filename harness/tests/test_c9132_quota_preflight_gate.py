"""C-9132: API-quota preflight gate for launch legs -- fail-closed.

RED first 2026-09-20: no harness/quota_preflight_gate.py existed and
cmd_dispatch had no quota gate. MEASURED (EVENTS 04:56-05:05Z): C-9029
reaped spawn_failed_env then instantly re-dispatched, 3 cycles in 9 min
on exhausted API quota (quota-exhausted CN), each cycle burned a 25-min
budget slot and a spawn. Contract under test:

  - a launch-leg card (box-bound lane) dispatched while quota is
    EXHAUSTED or UNKNOWN must result in a gate_skip with a NAMED blocker
    in harness/state/preflights/quota_block.json and NO worker spawn;
  - the probe is ONE cheap API call per dispatch run (not per card),
    injected here -- the real probe is never executed by this suite;
  - fail closed: probe exception/UNKNOWN verdict -> skip, never launch;
  - sufficient quota -> the launch leg dispatches normally;
  - non-launch lanes (fixer/planner) are NOT quota-gated;
  - a gate-skipped card stays ready and claimable (no bounce strike,
    no fleet row) so a later run with quota can dispatch it;
  - the artifact names the blocker (verdict + detail) and the card.
All state is isolated via QGH_STATE_DIR; the suite never touches live
harness state and never makes a network call.
"""

import argparse
import importlib.util
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "harness"))
import quota_preflight_gate as G  # noqa: E402

QGH_PATH = os.path.join(REPO, "harness", "qgh.py")
_counter = [0]


def _load_qgh(state_dir, monkeypatch):
    """Fresh qgh module bound to an isolated state dir."""
    monkeypatch.setenv("QGH_STATE_DIR", str(state_dir))
    _counter[0] += 1
    spec = importlib.util.spec_from_file_location("qgh_c9132_%d" % _counter[0], QGH_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.cmd_init(None)
    return mod


def _card(mod, title, lane, **over):
    c = mod.H.new_card(title, lane, "goal edge", ["acceptance"], budget_min=5)
    for k, v in over.items():
        c[k] = v
    return c


def _write_queue(mod, state_dir, cards):
    q = dict(cards=cards, seq=len(cards))
    mod.H.save_json(os.path.join(str(state_dir), "QUEUE.json"), q)
    return q


class _FakeProc:
    def __init__(self):
        self.pid = 999001  # not a live process

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    returncode = 0
    args = []

    def communicate(self, *a, **k):
        return "", ""

    def poll(self):
        return self.returncode


def _fake_popen(monkeypatch, mod, spawned):
    def fake_popen(*a, **k):
        cmd = a[0]
        if isinstance(cmd, list) and cmd and cmd[0] == "/bin/bash":
            spawned.append(cmd)
        return _FakeProc()

    monkeypatch.setattr(mod.subprocess, "Popen", fake_popen)


def _patch_probe(monkeypatch, mod, probe_result_or_exc):
    """Patch the probe seam used by cmd_dispatch; record call count."""

    calls = []

    def fake_probe(*a, **k):
        calls.append(1)
        if isinstance(probe_result_or_exc, Exception):
            raise probe_result_or_exc
        return dict(probe_result_or_exc)

    monkeypatch.setattr(mod.QPG, "probe_quota", fake_probe)
    return calls


def _events(state_dir, kind):
    out = []
    try:
        with open(os.path.join(str(state_dir), "EVENTS.jsonl"), encoding="utf-8") as f:
            for line in f:
                try:
                    ev = json.loads(line)
                except ValueError:
                    continue
                if ev.get("kind") == kind:
                    out.append(ev)
    except OSError:
        pass
    return out


# ---------------------------------------------------------------- gate module
def test_gate_allows_fail_closed():
    """Only a measured 'ok' verdict dispatches; UNKNOWN never launches."""
    assert G.gate_allows(dict(verdict="ok")) is True
    for bad in ("unknown", "exhausted", "", None):
        assert G.gate_allows(dict(verdict=bad)) is False, bad
    assert G.gate_allows(None) is False  # no probe result at all


def test_probe_classification():
    """200 -> ok; quota/balance/exhausted-cn errors -> exhausted; everything
    else (bad status without quota text) -> unknown."""
    ok = G.classify_response(200, "{}")
    assert ok["verdict"] == "ok"
    for status, body in [
        (429, '{"error":"EXHAUSTED-CN, please top up"}'),
        (402, '{"error":{"message":"insufficient credit"}}'),
        (400, '{"error":{"message":"quota exceeded for key"}}'),
    ]:
        r = G.classify_response(status, body)
        assert r["verdict"] == "exhausted", (status, body)
        assert r["detail"]
    unk = G.classify_response(500, '{"error":"upstream oops"}')
    assert unk["verdict"] == "unknown"
    assert unk["detail"]


def test_probe_transport_error_is_unknown():
    """The real probe wraps transport failures as UNKNOWN (fail closed)."""

    def boom(*a, **k):
        raise OSError("network down")

    r = G.probe_quota(transport=boom, env_files=(), api_key="test-key")
    assert r["verdict"] == "unknown"
    assert "network down" in r["detail"]
    assert r["utc"]


def test_write_block_artifact_names_blocker(tmp_path):
    sd = str(tmp_path)
    probe = dict(verdict="exhausted", detail="EXHAUSTED-CN", utc="2026-09-20T05:05:00Z")
    path = G.write_quota_block(sd, probe, card="C-9029")
    assert os.path.exists(os.path.join(sd, "preflights", "quota_block.json"))
    art = json.load(open(path, encoding="utf-8"))
    assert art["blocker"].startswith("api_quota_")
    assert art["verdict"] == "exhausted"
    assert art["card"] == "C-9029"


# ------------------------------------------------------------ dispatch wiring
def test_dispatch_launch_leg_skips_on_exhausted_quota(tmp_path, monkeypatch):
    mod = _load_qgh(tmp_path, monkeypatch)
    card = _card(mod, "launch ASI3 leg", "evaluator", id="C-9029")
    _write_queue(mod, tmp_path, [card])
    spawned = []
    _fake_popen(monkeypatch, mod, spawned)
    calls = _patch_probe(
        monkeypatch,
        mod,
        dict(verdict="exhausted", detail="EXHAUSTED-CN", utc="2026-09-20T05:00:00Z"),
    )

    mod.cmd_dispatch(argparse.Namespace(lane=None))

    assert spawned == [], "spawned a worker despite exhausted quota"
    assert calls, "quota probe never ran for a launch leg"
    block = os.path.join(str(tmp_path), "preflights", "quota_block.json")
    assert os.path.exists(block), "no quota_block.json artifact"
    art = json.load(open(block, encoding="utf-8"))
    assert art["blocker"] == "api_quota_exhausted"
    skips = _events(tmp_path, "gate_skip")
    assert any(e.get("card") == "C-9029" and e.get("gate") == "api_quota" for e in skips), skips
    on_disk = mod.H.load_queue(str(tmp_path))
    assert on_disk["cards"][0]["status"] == "ready"  # no bounce strike
    assert mod.H.load_fleet(str(tmp_path))["agents"] == []


def test_dispatch_launch_leg_fails_closed_on_unknown(tmp_path, monkeypatch):
    mod = _load_qgh(tmp_path, monkeypatch)
    card = _card(mod, "launch ASI3 leg", "evaluator", id="C-9029")
    _write_queue(mod, tmp_path, [card])
    spawned = []
    _fake_popen(monkeypatch, mod, spawned)
    _patch_probe(monkeypatch, mod, dict(verdict="unknown", detail="probe down", utc="z"))

    mod.cmd_dispatch(argparse.Namespace(lane=None))

    assert spawned == [], "UNKNOWN quota must never launch (fail closed)"
    art = json.load(
        open(os.path.join(str(tmp_path), "preflights", "quota_block.json"), encoding="utf-8")
    )
    assert art["blocker"] == "api_quota_unknown"


def test_dispatch_launch_leg_fails_closed_on_probe_crash(tmp_path, monkeypatch):
    mod = _load_qgh(tmp_path, monkeypatch)
    card = _card(mod, "launch ASI3 leg", "evaluator", id="C-9029")
    _write_queue(mod, tmp_path, [card])
    spawned = []
    _fake_popen(monkeypatch, mod, spawned)
    _patch_probe(monkeypatch, mod, RuntimeError("quota service exploded"))

    mod.cmd_dispatch(argparse.Namespace(lane=None))

    assert spawned == [], "probe crash must fail closed"
    art = json.load(
        open(os.path.join(str(tmp_path), "preflights", "quota_block.json"), encoding="utf-8")
    )
    assert art["verdict"] == "unknown"


def test_dispatch_launch_leg_dispatches_on_ok_quota(tmp_path, monkeypatch):
    mod = _load_qgh(tmp_path, monkeypatch)
    card = _card(mod, "launch ASI3 leg", "evaluator", id="C-9029")
    _write_queue(mod, tmp_path, [card])
    spawned = []
    _fake_popen(monkeypatch, mod, spawned)
    calls = _patch_probe(monkeypatch, mod, dict(verdict="ok", detail="", utc="z"))

    mod.cmd_dispatch(argparse.Namespace(lane=None))

    assert calls, "quota probe never ran"
    assert spawned, "sufficient quota must dispatch normally"
    assert not os.path.exists(os.path.join(str(tmp_path), "preflights", "quota_block.json"))
    assert not _events(tmp_path, "gate_skip")


def test_probe_runs_once_per_dispatch_run(tmp_path, monkeypatch):
    """ONE cheap call per dispatch run, not one per launch card."""
    mod = _load_qgh(tmp_path, monkeypatch)
    cards = [
        _card(mod, "launch leg a", "evaluator", id="C-9029"),
        _card(mod, "launch leg b", "trainer-ops", id="C-9130"),
    ]
    _write_queue(mod, tmp_path, cards)
    spawned = []
    _fake_popen(monkeypatch, mod, spawned)
    calls = _patch_probe(monkeypatch, mod, dict(verdict="unknown", detail="d", utc="z"))

    mod.cmd_dispatch(argparse.Namespace(lane=None))

    assert len(calls) == 1, calls
    assert spawned == []


def test_non_launch_lane_not_quota_gated(tmp_path, monkeypatch):
    mod = _load_qgh(tmp_path, monkeypatch)
    card = _card(mod, "fix a bug", "fixer", id="C-9131")
    _write_queue(mod, tmp_path, [card])
    spawned = []
    _fake_popen(monkeypatch, mod, spawned)
    calls = _patch_probe(monkeypatch, mod, dict(verdict="unknown", detail="d", utc="z"))

    mod.cmd_dispatch(argparse.Namespace(lane=None))

    assert calls == [], "quota probe ran for a non-launch lane"
    assert spawned, "non-launch lanes must not be quota-gated"
    assert not os.path.exists(os.path.join(str(tmp_path), "preflights", "quota_block.json"))


def test_gate_skipped_card_yields_to_next_candidate(tmp_path, monkeypatch):
    """A quota-blocked launch leg must not starve a ready non-launch card."""
    mod = _load_qgh(tmp_path, monkeypatch)
    launch = _card(mod, "launch leg", "evaluator", id="C-9029")
    fixer = _card(mod, "fix a bug", "fixer", id="C-9131")
    _write_queue(mod, tmp_path, [launch, fixer])
    spawned = []
    _fake_popen(monkeypatch, mod, spawned)
    _patch_probe(monkeypatch, mod, dict(verdict="unknown", detail="d", utc="z"))

    mod.cmd_dispatch(argparse.Namespace(lane=None))

    assert spawned, "fixer card starved behind a quota-skipped launch leg"
    on_disk = mod.H.load_queue(str(tmp_path))
    by_id = dict()
    for c in on_disk["cards"]:
        by_id[c["id"]] = c
    assert by_id["C-9029"]["status"] == "ready"
    assert by_id["C-9131"]["status"] == "running"
