# ---------------------------------------------------------------------------
# C-9427 RED: bounce_dead_running_cards direct save_json bypasses the
# lost-update merge, vaporizing concurrently-added ready cards.
# ---------------------------------------------------------------------------
import importlib
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "harness"))
QGH_PATH = os.path.join(REPO, "harness", "qgh.py")
_counter = [0]


def _load_qgh(state_dir, monkeypatch):
    monkeypatch.setenv("QGH_STATE_DIR", str(state_dir))
    _counter[0] += 1
    spec = importlib.util.spec_from_file_location("qgh_c9427_%d" % _counter[0], QGH_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.cmd_init(None)
    return mod


def _read_queue(mod, state_dir):
    with open(os.path.join(str(state_dir), "QUEUE.json"), encoding="utf-8") as f:
        return json.load(f)


def _card(mod, title, lane, **over):
    c = mod.H.new_card(title, lane, "goal edge", ["acceptance"], budget_min=5)
    for k, v in over.items():
        c[k] = v
    return c


def _write_queue(mod, state_dir, cards, seq=None):
    q = dict(cards=cards, seq=seq if seq is not None else len(cards))
    mod.H.save_json(os.path.join(str(state_dir), "QUEUE.json"), q)
    return q


def test_bounce_never_vaporizes_concurrent_ready_adds(tmp_path, monkeypatch):
    """bounce_dead_running_cards writes QUEUE.json via save_json directly
    (harness_lib.py:519), skipping save_queue's lost-update merge.  If a
    concurrent worker adds ready cards after bounce loaded its (stale)
    snapshot but before it saves, those cards are silently vaporized.

    Reproduced deterministically: bounce sees a 5-card stale snapshot while
    the disk already holds 7 cards (2 concurrent adds).  After bounce saves,
    the 2 concurrently-added cards must STILL be present."""
    mod = _load_qgh(tmp_path, monkeypatch)

    expired = "2026-09-09T01:00:00Z"  # long in the past
    cards = [
        _card(
            mod,
            "runner-dead",
            "fixer",
            id="C-0001",
            status="running",
            deadline_utc=expired,
            claimed_by=99999,
        ),
        _card(mod, "ready-0002", "fixer", id="C-0002", status="ready"),
        _card(mod, "ready-0003", "fixer", id="C-0003", status="ready"),
        _card(mod, "ready-0004", "fixer", id="C-0004", status="ready"),
        _card(mod, "ready-0005", "fixer", id="C-0005", status="ready"),
    ]
    _write_queue(mod, tmp_path, cards, seq=5)
    # empty history so the merge does not treat these as terminal
    evt = os.path.join(str(tmp_path), "EVENTS.jsonl")
    with open(evt, "w", encoding="utf-8") as f:
        f.write("")

    # --- concurrent writer adds two ready cards to disk ---
    q_disk = mod.H.load_queue(str(tmp_path))
    add_a = _card(mod, "concurrent-add-A", "fixer", id="C-0006", status="ready")
    add_b = _card(mod, "concurrent-add-B", "fixer", id="C-0008", status="ready")
    mod.H.add_card(q_disk, add_a, state_dir=str(tmp_path))
    mod.H.add_card(q_disk, add_b, state_dir=str(tmp_path))
    mod.H.save_queue(str(tmp_path), q_disk)
    assert "C-0006" in {c["id"] for c in _read_queue(mod, tmp_path)["cards"]}

    # --- bounce runs against a STALE 5-card snapshot (loaded before the adds) ---
    stale = {
        "cards": [dict(c) for c in cards],
        "seq": 5,
    }
    real_load = mod.H.load_json

    def _stale_load(path, default=None):
        return stale if str(path).endswith("QUEUE.json") else real_load(path, default)

    monkeypatch.setattr(mod.H, "load_json", _stale_load)

    try:
        bounced = mod.H.bounce_dead_running_cards(str(tmp_path), pid_alive_fn=lambda pid: False)
    finally:
        monkeypatch.setattr(mod.H, "load_json", real_load)

    assert bounced == ["C-0001"], f"expected C-0001 bounced, got {bounced}"

    ids = {c["id"] for c in _read_queue(mod, tmp_path)["cards"]}
    assert "C-0006" in ids, "bounce vaporized concurrently-added C-0006"
    assert "C-0008" in ids, "bounce vaporized concurrently-added C-0008"
