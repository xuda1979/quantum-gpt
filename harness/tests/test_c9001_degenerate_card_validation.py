"""C-9001: card-add validation rejects degenerate placeholder cards.

Root cause: new_card() accepts any string for title/why/acceptance,
allowing junk cards (title=\'t\', why=\'w\', acceptance=[\'a\']) to be minted
and dispatched, burning a fixer slot for 25 min on content-free work.

RED first: these tests fail before the validation guard is added.
"""

import os
import sys
import unittest

TEST_DIR = os.path.dirname(__file__)
HARNESS_DIR = os.path.dirname(TEST_DIR)
REPO = os.path.dirname(HARNESS_DIR)
sys.path.insert(0, HARNESS_DIR)
import harness_lib as H  # noqa: E402


class TestDegenerateCardRejection(unittest.TestCase):
    def test_rejects_title_shorter_than_8_chars(self):
        """A 1-char title like \'t\' must be rejected."""
        with self.assertRaises(ValueError) as ctx:
            H.new_card(
                title="t",
                lane="fixer",
                why="this is a valid why string",
                acceptance=["do the thing properly"],
            )
        self.assertIn("title", str(ctx.exception).lower())

    def test_rejects_why_shorter_than_8_chars(self):
        """A 1-char why like \'w\' must be rejected."""
        with self.assertRaises(ValueError) as ctx:
            H.new_card(
                title="A real card title here",
                lane="fixer",
                why="w",
                acceptance=["do the thing properly"],
            )
        self.assertIn("why", str(ctx.exception).lower())

    def test_rejects_acceptance_item_shorter_than_8_chars(self):
        """A 1-char acceptance like \'a\' must be rejected."""
        with self.assertRaises(ValueError) as ctx:
            H.new_card(
                title="A real card title here",
                lane="fixer",
                why="this is a valid why string",
                acceptance=["a"],
            )
        self.assertIn("acceptance", str(ctx.exception).lower())

    def test_accepts_valid_card(self):
        """A card with proper-length fields must pass."""
        card = H.new_card(
            title="Fix the broken dispatch path",
            lane="fixer",
            why="dispatch burns slots on junk cards",
            acceptance=["dispatch rejects degenerate cards"],
        )
        self.assertEqual(card["title"], "Fix the broken dispatch path")

    def test_rejects_empty_title(self):
        with self.assertRaises(ValueError):
            H.new_card(
                title="",
                lane="fixer",
                why="this is a valid why string",
                acceptance=["do the thing properly"],
            )

    def test_rejects_empty_why(self):
        with self.assertRaises(ValueError):
            H.new_card(
                title="A real card title here",
                lane="fixer",
                why="",
                acceptance=["do the thing properly"],
            )


if __name__ == "__main__":
    unittest.main()
