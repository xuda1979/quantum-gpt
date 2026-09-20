"""C-9512 RED: STATUS.md must be trimmed to prevent unbounded growth."""

import os
import sys
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
sys.path.insert(0, HARNESS_DIR)
import harness_lib as H  # noqa: E402
import qgh  # noqa: E402


class TestStatusTrim(unittest.TestCase):
    def setUp(self):
        self._orig_state = qgh.STATE
        qgh.STATE = os.path.join(
            os.environ.get("QGH_STATE_DIR", "/tmp/qgh-test"), "status_trim_test"
        )
        os.makedirs(qgh.STATE, exist_ok=True)

    def tearDown(self):
        qgh.STATE = self._orig_state

    def test_status_trimmed_preserves_max_tick(self):
        """STATUS.md should be trimmed to last N lines, preserving max tick#."""
        status_path = os.path.join(qgh.STATE, "STATUS.md")
        lines = []
        for i in range(1, 201):
            lines.append(f"- 2026-09-20T10:{i:02d}:00Z tick#{i} reaped=0 dispatched=0")
        with open(status_path, "w") as f:
            f.write("\n".join(lines) + "\n")

        pruned = H.trim_status_file(qgh.STATE, keep=100)
        self.assertEqual(pruned, 100, "100 old lines should be pruned")

        with open(status_path) as f:
            remaining = f.readlines()
        self.assertEqual(len(remaining), 100, "100 lines should remain")
        # max tick# should be preserved
        max_tick = 0
        for line in remaining:
            idx = line.find("tick#")
            if idx >= 0:
                import re

                m = re.search(r"tick#(\d+)", line)
                if m:
                    max_tick = max(max_tick, int(m.group(1)))
        self.assertEqual(max_tick, 200, "max tick# 200 must be preserved")


if __name__ == "__main__":
    unittest.main()
