"""C-0001: ghost card heartbeat detection (RED first).

MEASURED 2026-09-20: C-0001 was reaped DONE on 2026-09-16 but workers keep
getting dispatched under its ID (by the main session manual dispatch, which
bypasses the tick dispatcher QUEUE-based selection). The heartbeat command
happily writes to C-0001.progress with no validation, creating ghost progress
files that confuse state reconciliation.

This file locks the contract:
  - heartbeat for a card NOT in QUEUE must emit a ghost_heartbeat event
    to EVENTS.jsonl so the ghost is VISIBLE in audit history
  - the heartbeat append itself MUST still succeed (the worker needs it;
    fail-open for the write, fail-closed for detection)
  - heartbeat for a card that IS in QUEUE must NOT emit ghost_heartbeat
"""

import importlib.util
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QGH_PATH = os.path.join(REPO, "harness", "qgh.py")

_counter = [0]


def _load_qgh(state_dir, monkeypatch):
    monkeypatch.setenv("QGH_STATE_DIR", str(state_dir))
    _counter[0] += 1
    spec = importlib.util.spec_from_file_location("qgh_ghost_hb_%d" % _counter[0], QGH_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.cmd_init(None)
    return mod


def _card(mod, title, lane, **over):
    c = mod.H.new_card(title, lane, "goal edge", ["acceptance"], budget_min=5)
    for k, v in over.items():
        c[k] = v
    return c


def _write_queue(mod, state_dir, cards, seq=None):
    q = {"cards": cards, "seq": seq if seq is not None else len(cards)}
    mod.H.save_json(os.path.join(str(state_dir), "QUEUE.json"), q)
    return q


def _events(state_dir):
    path = os.path.join(str(state_dir), "EVENTS.jsonl")
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except ValueError:
                    pass
    return out


def test_ghost_heartbeat_emits_event(tmp_path, monkeypatch):
    mod = _load_qgh(tmp_path, monkeypatch)
    card = _card(mod, "real work", "fixer", id="C-9001")
    _write_queue(mod, tmp_path, [card], seq=9001)
    mod.cmd_heartbeat(type("A", (), {"card": "C-0001", "message": "ghost heartbeat test"})())
    evs = _events(tmp_path)
    ghost_evs = [e for e in evs if e.get("kind") == "ghost_heartbeat"]
    assert len(ghost_evs) == 1, "expected 1 ghost_heartbeat event, got %d; events: %s" % (
        len(ghost_evs),
        [e.get("kind") for e in evs],
    )
    assert ghost_evs[0].get("card") == "C-0001"


def test_normal_heartbeat_no_ghost_event(tmp_path, monkeypatch):
    mod = _load_qgh(tmp_path, monkeypatch)
    card = _card(mod, "real work", "fixer", id="C-9001")
    _write_queue(mod, tmp_path, [card], seq=9001)
    mod.cmd_heartbeat(type("A", (), {"card": "C-9001", "message": "normal heartbeat"})())
    evs = _events(tmp_path)
    ghost_evs = [e for e in evs if e.get("kind") == "ghost_heartbeat"]
    assert len(ghost_evs) == 0, "normal heartbeat must not emit ghost_heartbeat; events: %s" % [
        e.get("kind") for e in evs
    ]


def test_ghost_heartbeat_still_writes_progress(tmp_path, monkeypatch):
    mod = _load_qgh(tmp_path, monkeypatch)
    card = _card(mod, "real work", "fixer", id="C-9001")
    _write_queue(mod, tmp_path, [card], seq=9001)
    mod.cmd_heartbeat(type("A", (), {"card": "C-0001", "message": "ghost progress write"})())
    hb_path = os.path.join(str(tmp_path), "agents", "C-0001.progress")
    assert os.path.exists(hb_path), "ghost heartbeat must still write progress file"
    with open(hb_path) as f:
        content = f.read()
    assert "ghost progress write" in content
