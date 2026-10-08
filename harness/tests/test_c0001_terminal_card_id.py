"""C-0001: is_terminal_card_id detects terminal events regardless of
JSON field serialization order or which field carries the card id.
"""

import json
import os
import sys
import tempfile
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
sys.path.insert(0, HARNESS_DIR)
import harness_lib  # noqa: E402

NL = chr(10)


def _state_with(events):
    state = tempfile.mkdtemp(prefix="qgh-c0001-")
    with open(os.path.join(state, "EVENTS.jsonl"), "w") as f:
        for ev in events:
            f.write(json.dumps(ev) + NL)
    return state


class TerminalCardId(unittest.TestCase):
    def test_reap_verdict_before_card(self):
        state = _state_with(
            [
                {"ts": "1", "kind": "reaped", "verdict": "PARTIAL", "card": "C-0123", "pid": 9},
            ]
        )
        self.assertTrue(harness_lib.is_terminal_card_id(state, "C-0123"))

    def test_reap_id_field(self):
        state = _state_with(
            [
                {"ts": "1", "kind": "reaped", "id": "C-0999", "pid": 9, "verdict": "DONE"},
            ]
        )
        self.assertTrue(harness_lib.is_terminal_card_id(state, "C-0999"))

    def test_null_verdict_reap_still_not_terminal(self):
        state = _state_with(
            [
                {
                    "ts": "1",
                    "kind": "reaped",
                    "card": "C-0789",
                    "pid": 3,
                    "outcome": "env",
                    "verdict": None,
                },
            ]
        )
        self.assertFalse(harness_lib.is_terminal_card_id(state, "C-0789"))

    def test_other_terminal_kind_id_field(self):
        state = _state_with(
            [
                {"ts": "1", "kind": "card_done", "id": "C-0456", "note": "ok"},
            ]
        )
        self.assertTrue(harness_lib.is_terminal_card_id(state, "C-0456"))


if __name__ == "__main__":
    unittest.main()
