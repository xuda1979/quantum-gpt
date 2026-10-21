"""C-10571 RED: RETRO 'box_exec_dead' fired 11x in window — add automatic
detection+fix (watcher card).

Measured incident (filing window 2026-10-21T11:49:35Z->14:26:07Z, harness/
state/EVENTS.jsonl): 13 box_exec_dead events across ASI1/ASI2/ASI3, EVERY
ONE carrying `autofix: true` — the in-tick C-9702 DETECTION->FIX path
(box_exec_autofix -> daemon_reconciler kick) already auto-remediated each
box before the retrospective ran. Yet retrospective._error_kind_findings
counts RAW ERROR-kind events, so the fully-handled burst still tripped the
>=5 watchdog-gap threshold and auto-filed this card asking to add automatic
detection+fix for a failure mode that already has it — a false watcher card
minted while the loop was fully self-healing.

Systemic fix (C-10247 residual model, NOT a blanket allowlist): a
box_exec_dead event is auto-remediated iff its OWN `autofix` field is
truthy — that flag is emitted in the SAME in-tick call that performs the
kick (qgh.py event(STATE, "box_exec_dead", {"box": _name, "autofix":
bool(_kick)})). All 13 measured events prove remediation. If the C-9702
auto-fixer regresses (kick write failing, dead re-firing per tick), events
carry autofix=False and still surface -> watcher card still files. Proof
ABSENT (missing autofix field) always counts fail-open (cannot prove
resolution).
"""
import json
import os
import sys
import time
from pathlib import Path

import conftest  # noqa: F401

HERE = Path(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, str(HERE.parent / "scripts"))

import retrospective  # noqa: E402


def _now_iso(offset_s=0):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - offset_s))


def _write_events(tmp_path, events):
    lines = []
    for off, box, autofix in events:
        ev = dict(ts=_now_iso(600 + off), kind="box_exec_dead", box=box)
        if autofix is not None:
            ev["autofix"] = autofix
        lines.append(json.dumps(ev) + chr(10))
    (tmp_path / "EVENTS.jsonl").write_text("".join(lines))


def _errkind_findings(res):
    return [f for f in res["findings"] if f["sig"].startswith("errkind:box_exec_dead")]


# The REAL 2026-10-21 filing window, frozen verbatim from harness/state/EVENTS.jsonl:
# (offset_s, box) of every box_exec_dead; each carries autofix=true (C-9702 kick fired).
REAL_TRAIL = [
    (0, "ASI1"),
    (8, "ASI3"),
    (638, "ASI3"),
    (2388, "ASI2"),
    (2393, "ASI3"),
    (5200, "ASI2"),
    (6800, "ASI3"),
    (7193, "ASI2"),
    (7725, "ASI1"),
    (7736, "ASI3"),
    (8192, "ASI2"),
]


def test_real_window_autofixed_boxes_file_no_watcher_card(monkeypatch, tmp_path):
    """Replaying the frozen REAL trail (11 auto-fixed box_exec_dead events)
    must NOT file an errkind:box_exec_dead card."""
    monkeypatch.setattr(retrospective, "STATE", tmp_path)
    _write_events(tmp_path, [(off, box, True) for off, box in REAL_TRAIL])
    res = retrospective.review(3.0, file_cards=False)
    got = _errkind_findings(res)
    assert not got, "auto-fixed box_exec_dead burst must not file a watcher card: " + repr(got)


def test_unautofixed_box_exec_dead_still_files_watcher_card(monkeypatch, tmp_path):
    """Regression guard: if the C-9702 auto-fixer regresses (autofix=False),
    the box_exec_dead watcher card MUST still file (the detector is broken)."""
    monkeypatch.setattr(retrospective, "STATE", tmp_path)
    _write_events(tmp_path, [(i * 10, "ASI" + str(i % 2 + 1), False) for i in range(6)])
    res = retrospective.review(3.0, file_cards=False)
    got = _errkind_findings(res)
    assert got, "6 unautofixed box_exec_dead events must still file a watcher card"


def test_residual_counting_below_threshold_no_card(monkeypatch, tmp_path):
    """7 auto-fixed + 3 unautofixed -> residual 3 < 5 threshold -> no card;
    the finder must count the RESIDUAL, not the raw burst."""
    monkeypatch.setattr(retrospective, "STATE", tmp_path)
    evs = [(i * 10, "ASI" + str(i % 2 + 1), True) for i in range(7)] + [
        (100 + i * 10, "ASI" + str(i % 2 + 1), False) for i in range(3)
    ]
    _write_events(tmp_path, evs)
    res = retrospective.review(3.0, file_cards=False)
    got = _errkind_findings(res)
    assert not got, "residual=3 must stay below the >=5 threshold: " + repr(got)


def test_autofix_field_missing_counts_fail_open(monkeypatch, tmp_path):
    """A box_exec_dead event with no autofix field cannot be proven
    auto-remediated -- it must still count (fail open to counting, never
    silently suppress)."""
    monkeypatch.setattr(retrospective, "STATE", tmp_path)
    _write_events(tmp_path, [(i * 10, "ASI1", None) for i in range(6)])
    res = retrospective.review(3.0, file_cards=False)
    got = _errkind_findings(res)
    assert got, "autofix-less box_exec_dead events must count fail-open"


if __name__ == "__main__":
    raise SystemExit(__import__("pytest").main([__file__, "-v", "--tb=short"]))
