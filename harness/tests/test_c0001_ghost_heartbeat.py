"""C-0001 regression: ghost-card dispatch must emit a ghost_heartbeat event.

A worker dispatched under a terminal/removed card ID (the "ghost card"
failure mode) must remain VISIBLE in audit history AND keep heartbeating.
The heartbeat append MUST succeed (fail-open for the write, or the stall
reaper kills a healthy worker) while ghost detection is best-effort
(fail-closed for detection: it must not unwind a successful heartbeat).
"""

import os

import qgh


def _args(card, message):
    class A:
        pass

    a = A()
    a.card = card
    a.message = message
    a.gate_mode = "normal"
    return a


def _write_queue(state_tmp, cards):
    os.makedirs(state_tmp, exist_ok=True)
    qgh.save_queue(state_tmp, {"cards": cards, "seq": 0})


def _events(state_tmp):
    p = os.path.join(state_tmp, "EVENTS.jsonl")
    if not os.path.exists(p):
        return ""
    with open(p) as fh:
        return fh.read()


def test_ghost_card_emits_ghost_heartbeat_and_still_heartbeats(tmp_path, monkeypatch):
    state_tmp = str(tmp_path / "state")
    monkeypatch.setattr(qgh, "STATE", state_tmp)
    # Ghost card C-GHOST is NOT in the queue.
    _write_queue(state_tmp, [{"id": "C-REAL", "status": "ready"}])
    hb = os.path.join(state_tmp, "agents", "C-GHOST.progress")

    qgh.cmd_heartbeat(_args("C-GHOST", "first beat"))

    # Heartbeat must still land (fail-open: the worker survives the reaper).
    assert os.path.exists(hb), "ghost heartbeat did not write progress file"
    with open(hb) as fh:
        assert "first beat" in fh.read()
    # Ghost detection must be visible in audit history.
    assert "ghost_heartbeat" in _events(state_tmp)
    assert '"card": "C-GHOST"' in _events(state_tmp)


def test_real_queued_card_no_ghost_heartbeat(tmp_path, monkeypatch):
    state_tmp = str(tmp_path / "state")
    monkeypatch.setattr(qgh, "STATE", state_tmp)
    _write_queue(state_tmp, [{"id": "C-REAL", "status": "ready"}])
    hb = os.path.join(state_tmp, "agents", "C-REAL.progress")

    qgh.cmd_heartbeat(_args("C-REAL", "real beat"))

    assert os.path.exists(hb)
    assert "ghost_heartbeat" not in _events(
        state_tmp
    ), "no ghost_heartbeat expected for a card that IS in the queue"


def test_detection_failopen_never_unwinds_heartbeat(tmp_path, monkeypatch):
    state_tmp = str(tmp_path / "state")
    monkeypatch.setattr(qgh, "STATE", state_tmp)
    os.makedirs(state_tmp, exist_ok=True)

    # Corrupt/missing queue -> load_queue raises; heartbeat must still succeed.
    def boom(*a, **k):
        raise RuntimeError("queue unreadable")

    monkeypatch.setattr(qgh, "load_queue", boom)
    hb = os.path.join(state_tmp, "agents", "C-X.progress")

    qgh.cmd_heartbeat(_args("C-X", "beat despite failure"))

    assert os.path.exists(hb), "fail-open violated: heartbeat unwound on detection error"
    with open(hb) as fh:
        assert "beat despite failure" in fh.read()
