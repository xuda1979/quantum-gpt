# ---------------------------------------------------------------------------
# C-9415 RED: save_queue must run a post-write integrity check that re-reads
# the on-disk QUEUE.json and verifies the card count survives the atomic
# tmp+rename.  If a concurrent writer drops cards during the rename window,
# save_queue fails closed instead of silently persisting a vaporized queue.
# ---------------------------------------------------------------------------
import importlib
import json
import os
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "harness"))
QGH_PATH = os.path.join(REPO, "harness", "qgh.py")
_counter = [0]


def _load_qgh(state_dir, monkeypatch):
    monkeypatch.setenv("QGH_STATE_DIR", str(state_dir))
    _counter[0] += 1
    spec = importlib.util.spec_from_file_location("qgh_c9415_%d" % _counter[0], QGH_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.cmd_init(None)
    return mod


def _read_queue(mod, state_dir):
    with open(os.path.join(str(state_dir), "QUEUE.json"), encoding="utf-8") as f:
        return json.load(f)


def _card(mod, title, lane, **over):
    c = mod.H.new_card(title, lane, "goal edge long enough", ["acceptance ok"], budget_min=5)
    for k, v in over.items():
        c[k] = v
    return c


def test_save_queue_fails_closed_on_vaporized_write(tmp_path, monkeypatch):
    """If the atomic write lands with fewer cards than the caller supplied
    (a clobbering concurrent writer dropped one), save_queue must raise an
    error rather than silently persist the truncated queue."""
    mod = _load_qgh(tmp_path, monkeypatch)

    cards = [
        _card(mod, f"integrity-card-{i}", "fixer", id=f"C-{1000 + i:04d}", status="ready")
        for i in range(3)
    ]
    q = dict(cards=cards, seq=3)
    mod.H.save_queue(str(tmp_path), q)
    assert len(_read_queue(mod, tmp_path)["cards"]) == 3, "sanity: initial write ok"

    # clobbering writer: during the save_queue->save_json write, land fewer
    # cards on disk than the merged queue carries (simulate vaporization).
    real_save_json = mod.H.save_json

    def _clobber(path, obj):
        # a concurrent (independent) writer lands a DIFFERENT truncated queue
        # than this caller intended to persist -- it does not mutate our
        # in-memory copy, so the caller's intended card set keeps all 3.
        import copy

        clone = copy.deepcopy(obj)
        clone["cards"] = clone["cards"][:-1]
        return real_save_json(path, clone)

    monkeypatch.setattr(mod.H, "save_json", _clobber)

    # the queue we're about to persist still carries all 3 cards
    fresh = dict(cards=[dict(c) for c in cards], seq=3)
    try:
        with pytest.raises((ValueError, RuntimeError)):
            mod.H.save_queue(str(tmp_path), fresh)
    finally:
        monkeypatch.setattr(mod.H, "save_json", real_save_json)

    # fail-closed: save_queue must NOT have silently persisted the truncated
    # queue -- the raise above IS the fail-closed signal.  The on-disk file
    # must still be a readable, well-formed QUEUE.json (not left mid-rename).
    _after = _read_queue(mod, tmp_path)
    assert "cards" in _after and "seq" in _after, "QUEUE.json left malformed"
