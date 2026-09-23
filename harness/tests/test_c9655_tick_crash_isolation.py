"""C-9655: tick crash isolation + queue schema normalization.

Design mandate (user 2026-09-23): productive, 0-bug harness.
1. A crashing tick phase must emit tick_crashed (LOUD: report digest +
   STATUS.md) — never again a silent 50-min freeze.
2. Any card, however legacy, must carry every required field on load —
   the gates-KeyError class of bug is impossible by construction.
"""

import json
import os
import sys
from pathlib import Path

import conftest  # noqa: F401

HERE = Path(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

import harness_lib  # noqa: E402
import qgh  # noqa: E402


def test_normalize_card_fills_all_required_fields():
    """A legacy card with NO fields at all must load with every default."""
    bare = {"id": "C-LEGACY", "title": "t", "lane": "fixer", "status": "ready"}
    c = qgh._normalize_card(dict(bare))
    for k in ("deps", "gates", "acceptance"):
        assert c[k] == [], f"{k} must default to []"
    assert c["bounce_count"] == 0
    assert c["budget_min"] == 60
    assert c["priority"] == 0


def test_normalize_card_preserves_existing_values():
    """Real values are never overwritten by defaults."""
    c = qgh._normalize_card(
        {"id": "C-1", "gates": ["tdd"], "bounce_count": 2, "budget_min": 90, "priority": 5}
    )
    assert c["gates"] == ["tdd"]
    assert c["bounce_count"] == 2
    assert c["budget_min"] == 90
    assert c["priority"] == 5


def test_load_queue_normalizes_legacy_cards(tmp_path):
    """End-to-end: a QUEUE.json with schema holes loads fully healed."""
    qd = tmp_path / "QUEUE.json"
    qd.write_text(
        json.dumps(
            {
                "cards": [{"id": "C-X", "title": "t", "lane": "fixer", "status": "ready"}],
                "seq": 1,
            }
        )
    )
    q = qgh.load_queue(str(tmp_path))
    card = q["cards"][0]
    assert card["gates"] == []
    assert card["deps"] == []
    assert card["budget_min"] == 60
    # harness_lib mirror has identical behavior (workers use that import)
    q2 = harness_lib.load_queue(str(tmp_path))
    assert q2["cards"][0]["gates"] == []
    assert q2["cards"][0]["priority"] == 0


def test_tick_crashed_in_error_kinds():
    """The report digest must classify tick_crashed as ERROR-class."""
    sys.path.insert(0, str(HERE.parent / "scripts"))
    import detailed_report  # noqa: E402

    assert "tick_crashed" in detailed_report.ERROR_KINDS


def test_tick_crash_emits_event_and_status(tmp_path, monkeypatch):
    """A crashing tick body must leave a tick_crashed event + STATUS line."""
    events = []
    status_lines = []

    monkeypatch.setattr(qgh, "STATE", str(tmp_path))
    monkeypatch.setattr(qgh, "TICK_LOCK", str(tmp_path / "tick.lock"))
    monkeypatch.setattr(qgh, "TICK_STALE_SEC", 60)
    monkeypatch.setattr(qgh, "acquire_lock", lambda *a, **k: object())
    monkeypatch.setattr(qgh, "release_lock", lambda *a, **k: None)
    monkeypatch.setattr(qgh, "load_goal", lambda *a, **k: {"status": "OPEN"})
    monkeypatch.setattr(qgh, "_reap", lambda: (_ for _ in ()).throw(RuntimeError("boom-phase")))
    monkeypatch.setattr(qgh, "event", lambda sd, kind, payload=None: events.append((kind, payload)))
    monkeypatch.setattr(
        qgh,
        "append_line",
        lambda p, line: status_lines.append(line) if "STATUS" in str(p) else None,
    )

    import pytest

    with pytest.raises(RuntimeError):
        qgh.cmd_tick(None)

    kinds = [k for k, _ in events]
    assert "tick_crashed" in kinds, f"tick_crashed event missing; got {kinds}"
    assert any("TICK-CRASHED" in ln for ln in status_lines), status_lines
    payload = dict(events)["tick_crashed"]
    assert "boom-phase" in payload["err"]
    assert payload["trace"], "traceback must be recorded for diagnosis"
