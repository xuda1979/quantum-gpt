"""C-0001 ghost dispatch guard (RED first).

MEASURED 2026-09-16 through 2026-09-20: card C-0001 was reaped DONE
(terminal) on 2026-09-16T11:20:00Z but kept appearing in dispatch contexts.
Workers were dispatched under C-0001 even though the card was not in
QUEUE.json, not in FLEET.json, and had a terminal reap in EVENTS.jsonl.

Root cause: while C-9127 prevents re-MINTING a terminal id via add_card,
there is no guard preventing an external/manual dispatch from giving a
worker a ghost card ID. A worker launched with a terminal card ID has
no way to detect it is working on a non-existent card.

This test locks the contract:
  - is_terminal_card_id() must return True for ids in EVENTS.jsonl with
    terminal reap outcomes (DONE/dead)
  - is_terminal_card_id() must return False for ids never seen terminal
  - dispatch_target_ok must reject a card not in the queue (already tested
    in test_qgh_dispatch_integrity.py, but this test adds the terminal-id
    angle)
"""

import importlib.util
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QGH_PATH = os.path.join(REPO, "harness", "qgh.py")

_counter = [0]


def _load_qgh(state_dir, monkeypatch):
    """Fresh qgh module bound to an isolated state dir."""
    monkeypatch.setenv("QGH_STATE_DIR", str(state_dir))
    _counter[0] += 1
    spec = importlib.util.spec_from_file_location("qgh_ghost_%d" % _counter[0], QGH_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.cmd_init(None)
    return mod


def _card(mod, title, lane, **over):
    c = mod.H.new_card(title, lane, "goal edge reason", ["acceptance here"], budget_min=5)
    for k, v in over.items():
        c[k] = v
    return c


def _write_queue(mod, state_dir, cards, seq=None):
    q = {"cards": cards, "seq": seq if seq is not None else len(cards)}
    mod.H.save_json(os.path.join(str(state_dir), "QUEUE.json"), q)
    return q


def _write_events(mod, state_dir, events):
    """Append events to EVENTS.jsonl in the state dir."""
    path = os.path.join(str(state_dir), "EVENTS.jsonl")
    with open(path, "a") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")


def test_terminal_card_id_detected_from_history(tmp_path, monkeypatch):
    """is_terminal_card_id must return True for a card reaped DONE in EVENTS."""
    mod = _load_qgh(tmp_path, monkeypatch)
    _write_events(
        mod,
        tmp_path,
        [
            {
                "ts": "2026-09-16T11:06:15Z",
                "kind": "dispatched",
                "card": "C-0001",
                "lane": "planner",
                "pid": 23869,
                "budget_min": 20,
            },
            {
                "ts": "2026-09-16T11:20:00Z",
                "kind": "reaped",
                "card": "C-0001",
                "outcome": "dead",
                "verdict": "DONE",
            },
        ],
    )

    assert mod.H.is_terminal_card_id(str(tmp_path), "C-0001") is True, (
        "C-0001 was reaped DONE -- is_terminal_card_id must return True"
    )


def test_non_terminal_card_id_not_flagged(tmp_path, monkeypatch):
    """is_terminal_card_id must return False for a card never reaped terminal."""
    mod = _load_qgh(tmp_path, monkeypatch)
    _write_events(
        mod,
        tmp_path,
        [
            {
                "ts": "2026-09-16T11:06:15Z",
                "kind": "dispatched",
                "card": "C-0099",
                "lane": "fixer",
                "pid": 999,
                "budget_min": 10,
            },
        ],
    )

    assert mod.H.is_terminal_card_id(str(tmp_path), "C-0099") is False, (
        "C-0099 was never reaped terminal -- is_terminal_card_id must return False"
    )


def test_unknown_card_id_not_terminal(tmp_path, monkeypatch):
    """is_terminal_card_id must return False for a card never seen in history."""
    mod = _load_qgh(tmp_path, monkeypatch)

    assert mod.H.is_terminal_card_id(str(tmp_path), "C-9999") is False, (
        "C-9999 never appeared in EVENTS -- is_terminal_card_id must return False"
    )


def test_environmental_reap_not_terminal(tmp_path, monkeypatch):
    """A reap with verdict=null (environmental death) is NOT terminal -- the
    card was re-armed to ready, not closed."""
    mod = _load_qgh(tmp_path, monkeypatch)
    _write_events(
        mod,
        tmp_path,
        [
            {
                "ts": "2026-09-16T11:06:15Z",
                "kind": "dispatched",
                "card": "C-0005",
                "lane": "fixer",
                "pid": 123,
                "budget_min": 10,
            },
            {
                "ts": "2026-09-16T11:08:32Z",
                "kind": "reaped",
                "card": "C-0005",
                "outcome": "dead",
                "verdict": None,
            },
        ],
    )

    assert mod.H.is_terminal_card_id(str(tmp_path), "C-0005") is False, (
        "C-0005 was reaped with verdict=null (environmental) -- NOT terminal"
    )


def test_reaped_bounced_is_terminal(tmp_path, monkeypatch):
    """A bounced verdict after exhausted retries is terminal."""
    mod = _load_qgh(tmp_path, monkeypatch)
    _write_events(
        mod,
        tmp_path,
        [
            {
                "ts": "2026-09-16T12:00:00Z",
                "kind": "reaped",
                "card": "C-0010",
                "outcome": "dead",
                "verdict": "BOUNCED",
            },
        ],
    )

    assert mod.H.is_terminal_card_id(str(tmp_path), "C-0010") is True, (
        "C-0010 was reaped with verdict=BOUNCED -- terminal"
    )


def test_card_purged_is_terminal(tmp_path, monkeypatch):
    """A card_purged event must be detected as terminal by
    is_terminal_card_id.  card_purged uses 'id' field, not 'card'."""
    mod = _load_qgh(tmp_path, monkeypatch)
    _write_events(
        mod,
        tmp_path,
        [
            {
                "ts": "2026-09-20T06:02:00Z",
                "kind": "card_purged",
                "id": "C-9001",
                "reason": "duplicate",
            },
        ],
    )
    assert mod.H.is_terminal_card_id(str(tmp_path), "C-9001") is True, (
        "C-9001 was purged -- is_terminal_card_id must return True"
    )


def test_card_purged_in_history_terminal_ids(tmp_path, monkeypatch):
    """history_terminal_card_ids must include ids with card_purged events.
    Without this, save_queue could resurrect a purged card from disk."""
    mod = _load_qgh(tmp_path, monkeypatch)
    _write_events(
        mod,
        tmp_path,
        [
            {
                "ts": "2026-09-20T06:02:00Z",
                "kind": "card_purged",
                "id": "C-9211",
                "reason": "duplicate of C-9195",
            },
        ],
    )
    terminal_ids = mod.H.history_terminal_card_ids(str(tmp_path))
    assert "C-9211" in terminal_ids, (
        "C-9211 was purged -- history_terminal_card_ids must include it"
    )


def test_card_done_is_terminal(tmp_path, monkeypatch):
    """A card_done event must be detected as terminal by is_terminal_card_id."""
    mod = _load_qgh(tmp_path, monkeypatch)
    _write_events(
        mod,
        tmp_path,
        [
            {
                "ts": "2026-09-20T08:00:00Z",
                "kind": "card_done",
                "card": "C-0050",
            },
        ],
    )
    assert mod.H.is_terminal_card_id(str(tmp_path), "C-0050") is True, (
        "C-0050 has card_done event -- is_terminal_card_id must return True"
    )


def test_card_voided_is_terminal(tmp_path, monkeypatch):
    """A card_voided event must be detected as terminal by is_terminal_card_id."""
    mod = _load_qgh(tmp_path, monkeypatch)
    _write_events(
        mod,
        tmp_path,
        [
            {
                "ts": "2026-09-20T08:00:00Z",
                "kind": "card_voided",
                "card": "C-0060",
            },
        ],
    )
    assert mod.H.is_terminal_card_id(str(tmp_path), "C-0060") is True, (
        "C-0060 has card_voided event -- is_terminal_card_id must return True"
    )
