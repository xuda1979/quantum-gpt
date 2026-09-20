# C-9126: per-card spawn-failure circuit breaker.
# The GLOBAL consecutive_spawn_failures counter let one healthy card's success
# reset a dying card's env-death streak, so backoff NEVER armed (C-9030 burned
# 6 dispatches in 25 min against a dead API while C-9029 kept succeeding).
# Contract pinned here:
#   - a success on card X must NOT reset card Y's consecutive env-death count
#   - backoff arms at SPAWN_FAIL_THRESHOLD consecutive SAME-card env-deaths
#   - an armed backoff is cleared ONLY by that card's own successful dispatch
#   - armed backoff is visible fail-closed: OPS flag + standup line

import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import harness_lib as H  # noqa: E402


def tmp_state():
    return tempfile.mkdtemp(prefix="qgh-c9126-")


def card_state(consecutive, until):
    e = dict()
    e["consecutive"] = consecutive
    e["backoff_until_utc"] = until
    return e


class TestPerCardEnvDeathCounting(unittest.TestCase):
    def test_success_on_x_does_not_reset_y_streak(self):
        ops = H.load_ops(tmp_state())
        H.note_spawn_result(None, ops, ok=False, card="C-9030")
        self.assertEqual(H.card_consecutive_spawn_fails(ops, "C-9030"), 1)
        # C-9029 (healthy) dispatches successfully
        H.note_spawn_result(None, ops, ok=True, card="C-9029")
        # C-9030's streak must be UNTOUCHED
        self.assertEqual(H.card_consecutive_spawn_fails(ops, "C-9030"), 1)

    def test_backoff_arms_at_n_same_card_deaths(self):
        ops = H.load_ops(tmp_state())
        H.note_spawn_result(None, ops, ok=False, card="C-9030")
        self.assertFalse(H.card_backoff_active(ops, "C-9030"))  # 1: not yet
        H.note_spawn_result(None, ops, ok=False, card="C-9030")
        self.assertTrue(H.card_backoff_active(ops, "C-9030"))  # 2 same-card: ARMED
        # a healthy card has no backoff
        self.assertFalse(H.card_backoff_active(ops, "C-9029"))

    def test_only_own_success_clears_armed_backoff(self):
        ops = H.load_ops(tmp_state())
        H.note_spawn_result(None, ops, ok=False, card="C-9030")
        H.note_spawn_result(None, ops, ok=False, card="C-9030")
        self.assertTrue(H.card_backoff_active(ops, "C-9030"))
        # another card's success must NOT clear it
        H.note_spawn_result(None, ops, ok=True, card="C-9029")
        self.assertTrue(H.card_backoff_active(ops, "C-9030"))
        # only C-9030's own success clears it
        H.note_spawn_result(None, ops, ok=True, card="C-9030")
        self.assertFalse(H.card_backoff_active(ops, "C-9030"))
        self.assertEqual(H.card_consecutive_spawn_fails(ops, "C-9030"), 0)

    def test_backoff_expires_fail_closed(self):
        expired = card_state(2, "2020-01-01T00:00:00Z")
        by = dict()
        by["C-9030"] = expired
        ops = dict()
        ops[H.SPAWN_FAILURES_BY_CARD_KEY] = by
        self.assertFalse(H.card_backoff_active(ops, "C-9030"))  # expired = inactive
        self.assertFalse(H.card_backoff_active(dict(spawn_failures_by_card=dict()), "C-9030"))
        self.assertFalse(H.card_backoff_active(dict(), "C-9030"))  # absent = inactive

    def test_armed_backoff_cards_lists_only_unexpired(self):
        future = (datetime.now(timezone.utc) + timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%SZ")
        by = dict()
        by["C-9030"] = card_state(2, future)
        by["C-9029"] = card_state(0, None)
        ops = dict()
        ops[H.SPAWN_FAILURES_BY_CARD_KEY] = by
        self.assertEqual(H.armed_backoff_cards(ops), ["C-9030"])

    def test_legacy_global_path_unchanged(self):
        # card=None keeps the pre-C-9126 global semantics (compat)
        ops = H.load_ops(tmp_state())
        H.note_spawn_result(None, ops, ok=False)
        H.note_spawn_result(None, ops, ok=False)
        self.assertTrue(H.backoff_active(ops))
        self.assertIsNotNone(ops[H.BACKOFF_PATH_KEY])
        H.note_spawn_result(None, ops, ok=True)
        self.assertEqual(ops[H.CONSECUTIVE_SPAWN_FAIL_KEY], 0)
        self.assertFalse(H.backoff_active(ops))


class TestBackoffVisibility(unittest.TestCase):
    def test_standup_lists_armed_card(self):
        d = tmp_state()
        ops = H.load_ops(d)
        H.note_spawn_result(None, ops, ok=False, card="C-9030")
        H.note_spawn_result(None, ops, ok=False, card="C-9030")
        H.save_ops(d, ops)
        goal = dict(objective="test goal", status="OPEN")
        text = H.render_standup(goal, dict(cards=[]), dict(agents=[]), 1, state_dir=d)
        self.assertIn("C-9030", text, "armed per-card backoff must appear in standup")
        self.assertIn("BACKOFF ARMED", text)


if __name__ == "__main__":
    unittest.main()
