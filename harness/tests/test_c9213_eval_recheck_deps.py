"""C-9213: C-9195 (re-eval with fixed sanitizer) must depend on C-9201
(deploy sanitize fix to box) AND C-9198 (token cap fix) in addition to
C-9168 (local sanitize fix).

RED (measured 2026-09-20 against live QUEUE.json): C-9195 deps == ["C-9168"]
only. But the eval runs box-side on ASI2, so it also needs:
  - C-9201: deploy candidate_sanitize.py fix to the ASI2 box (local fix
    alone is insufficient; the box uses its own copy)
  - C-9198: max_new_tokens=1536 causes truncation in 12/15 failures; the
    re-eval must use the raised cap

If C-9195 dispatches before C-9201 and C-9198 complete, it will reproduce
3/18 with the old broken sanitizer and token cap on the box.
"""

import json
import os
import sys
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
sys.path.insert(0, HARNESS_DIR)

QUEUE_PATH = os.path.join(HARNESS_DIR, "state", "QUEUE.json")


def _load_card(card_id):
    with open(QUEUE_PATH) as f:
        q = json.load(f)
    for c in q.get("cards", []):
        if c.get("id") == card_id:
            return c
    return None


class TestC9195DepsComplete(unittest.TestCase):
    """C-9195 must depend on C-9168, C-9201, and C-9198."""

    def test_c9195_deps_include_c9201(self):
        card = _load_card("C-9195")
        if card is None:
            self.skipTest("C-9195 purged from QUEUE.json (completed or superseded)")
        self.assertIn(
            "C-9201",
            card.get("deps", []),
            "C-9195 deps must include C-9201 (box deploy of sanitize fix)",
        )

    def test_c9195_deps_include_c9198(self):
        card = _load_card("C-9195")
        if card is None:
            self.skipTest("C-9195 purged from QUEUE.json (completed or superseded)")
        self.assertIn(
            "C-9198", card.get("deps", []), "C-9195 deps must include C-9198 (token cap fix)"
        )

    def test_c9195_deps_include_c9168(self):
        card = _load_card("C-9195")
        if card is None:
            self.skipTest("C-9195 purged from QUEUE.json (completed or superseded)")
        self.assertIn(
            "C-9168",
            card.get("deps", []),
            "C-9195 deps must still include C-9168 (local sanitize fix)",
        )


if __name__ == "__main__":
    unittest.main()
