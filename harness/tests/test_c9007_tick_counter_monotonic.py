"""C-9007: tick-counter reset -- _next_standup_no() must never go backwards.

RED (measured 2026-09-16): the tick number is derived ONLY from the
standup-*.md filenames (qgh._next_standup_no). The 2026-09-17 event-log
recovery recreated the standup dir empty and the counter fell off a cliff
(STATUS.md: 18:40:01Z tick#127 -> 18:40:27Z tick#1), re-climbing 1..51
afterwards. Any standup-dir wipe (recovery, cleanup, prune bug) resets the
numbering and collides new standup numbers with every pre-wipe number that
durable card text references (C-9017 why cites "standup #1" from the
pre-reset era -- ambiguous since the reset).

Fix under test: the highest tick#N ever recorded in STATUS.md (durable,
append-only history that survives standup-dir wipes) floors the counter;
a file-derived number above the floor still wins; a missing STATUS.md
degrades to the file-derived number.
"""

import os
import sys
import tempfile
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
sys.path.insert(0, HARNESS_DIR)
import qgh  # noqa: E402  (conftest seam binds STATE to a temp dir)


class TickCounterMonotonic(unittest.TestCase):
    def setUp(self):
        self.state = tempfile.mkdtemp(prefix="qgh-c9007-")
        os.makedirs(os.path.join(self.state, "standup"), exist_ok=True)

    def standup(self, n):
        with open(os.path.join(self.state, "standup", "standup-%d.md" % n), "w") as f:
            f.write("x")

    def status(self, text):
        with open(os.path.join(self.state, "STATUS.md"), "w") as f:
            f.write(text)

    def test_wiped_standup_dir_does_not_reset_counter(self):
        # the measured live shape: pre-wipe era reached tick#127 (STATUS.md kept
        # the history), the dir was wiped, the post-wipe climb recreated 1..51.
        # Next must be 128 -- never 52, never a reuse of 1..127.
        self.status(
            "- 2026-09-16T18:40:01Z tick#127 reaped=1 dispatched 3 workers\n"
            "- 2026-09-16T21:14:43Z tick#51 reaped=2 dispatched 2 workers\n"
        )
        for n in range(1, 52):
            self.standup(n)
        self.assertEqual(qgh._next_standup_no(state_dir=self.state), 128)

    def test_file_derived_above_floor_still_wins(self):
        self.status("- 2026-09-16T11:06:15Z tick#3 reaped=0 dispatched 0 workers\n")
        self.standup(9)
        self.assertEqual(qgh._next_standup_no(state_dir=self.state), 10)

    def test_missing_status_degrades_to_file_derived(self):
        self.standup(4)
        self.assertEqual(qgh._next_standup_no(state_dir=self.state), 5)

    def test_empty_standup_dir_with_history_also_floored(self):
        # dir wiped entirely (the recovery exact shape): counter must still
        # continue past the historical max, not restart at 1
        self.status("- 2026-09-16T18:40:01Z tick#127 reaped=1 dispatched 3 workers\n")
        self.assertEqual(qgh._next_standup_no(state_dir=self.state), 128)


if __name__ == "__main__":
    unittest.main()
