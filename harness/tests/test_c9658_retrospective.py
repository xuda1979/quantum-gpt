"""C-9658: the harness ALWAYS reviews its work, then improves itself.

DevOps mandate (user 2026-09-23): blameless postmortems, automated. The
retrospective scans recent events and files improvement cards itself —
findings must carry evidence, become actions (cards), and dedupe within 6h.
"""

import json
import os
import sys
from pathlib import Path

import conftest  # noqa: F401

HERE = Path(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, str(HERE.parent / "scripts"))

import retrospective  # noqa: E402


def test_review_detects_tick_crash(monkeypatch, tmp_path):
    """A tick_crashed event in window -> finding asking for phase isolation."""
    ev = tmp_path / "EVENTS.jsonl"
    ev.write_text(
        json.dumps({"ts": _now_iso(60), "kind": "tick_crashed", "err": "KeyError('gates')"}) + "\n"
    )
    monkeypatch.setattr(retrospective, "STATE", tmp_path)
    res = retrospective.review(3.0, file_cards=False)
    assert any("tick crashed" in f["title"] for f in res["findings"])
    assert any("KeyError" in f["evidence"] for f in res["findings"])


def test_review_detects_bounce_pattern(monkeypatch, tmp_path):
    """A card bounced 2+ times in window -> root-cause finding."""
    ev = tmp_path / "EVENTS.jsonl"
    lines = [
        json.dumps({"ts": _now_iso(600 * (3 - i)), "kind": "card_bounced", "card": "C-999"})
        for i in range(3)
    ]
    ev.write_text("\n".join(lines) + "\n")
    monkeypatch.setattr(retrospective, "STATE", tmp_path)
    res = retrospective.review(3.0, file_cards=False)
    assert any("C-999" in f["title"] and "failed" in f["title"] for f in res["findings"])


def test_review_dedupes_within_6h(monkeypatch, tmp_path):
    """Same finding signature files at most one card per 6h (OPS ledger)."""
    ev = tmp_path / "EVENTS.jsonl"
    ev.write_text(json.dumps({"ts": _now_iso(60), "kind": "tick_crashed", "err": "x"}) + "\n")
    monkeypatch.setattr(retrospective, "STATE", tmp_path)
    calls = []

    def fake_add_card(title, evidence):
        calls.append(title)
        return True, "C-RETRO-1"

    monkeypatch.setattr(retrospective, "_add_card", fake_add_card)
    res1 = retrospective.review(3.0, file_cards=True)
    res2 = retrospective.review(3.0, file_cards=True)
    assert len(res1["cards_filed"]) == 1
    assert len(res2["cards_filed"]) == 0, "second run within 6h must dedupe"
    assert len(calls) == 1


def test_review_clean_window_has_no_findings(monkeypatch, tmp_path):
    ev = tmp_path / "EVENTS.jsonl"
    ev.write_text("")
    monkeypatch.setattr(retrospective, "STATE", tmp_path)
    res = retrospective.review(3.0, file_cards=False)
    assert res["findings"] == []


def _now_iso(offset_s=0):
    import time

    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - offset_s))
