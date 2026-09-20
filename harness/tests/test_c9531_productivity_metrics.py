"""C-9531 RED: work_review._events_analysis must count real completion.

The standup reported "0% completion rate" (PRODUCTIVITY section: Dispatched: 35 |
Done: 0 | Bounce: 0 | Fail: 3 | Waste: 7%) even though EVENTS.jsonl shows many
reaped-with-verdict=DONE and gate_bounced events. Root cause: _events_analysis
in harness/work_review.py matches event kinds that DO NOT EXIST ("done",
"bounce") and misses "reaped"(verdict=DONE) / "gate_bounced". This test pins the
correct mapping so productivity reflects reality.
"""

import json
import os
import sys
import tempfile
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
if HARNESS_DIR not in sys.path:
    sys.path.insert(0, HARNESS_DIR)

import work_review


def _write_events(events_path, events):
    with open(events_path, "w") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")


class TestEventsAnalysis(unittest.TestCase):
    def _analysis(self, events):
        sd = tempfile.mkdtemp(prefix="qgh-c9531-events-")
        os.environ["QGH_STATE_DIR"] = sd
        evp = os.path.join(sd, "EVENTS.jsonl")
        _write_events(evp, events)
        import importlib

        mod = importlib.reload(work_review)
        return mod._events_analysis()

    def test_counts_done_from_reaped_done(self):
        events = [
            {"ts": "2026-09-20T10:00:00Z", "kind": "dispatched", "card": "C-1000", "pid": 1},
            {
                "ts": "2026-09-20T10:30:00Z",
                "kind": "reaped",
                "card": "C-1000",
                "pid": 1,
                "verdict": "DONE",
                "outcome": "dead",
                "lane": "planner",
            },
        ]
        a = self._analysis(events)
        self.assertEqual(a["dispatch"], 1)
        self.assertEqual(a["done"], 1)

    def test_counts_bounce_from_gate_bounced(self):
        events = [
            {"ts": "2026-09-20T10:00:00Z", "kind": "dispatched", "card": "C-1001", "pid": 2},
            {
                "ts": "2026-09-20T10:30:00Z",
                "kind": "gate_bounced",
                "card": "C-1001",
                "reason": "gate evidence missing",
            },
        ]
        a = self._analysis(events)
        self.assertEqual(a["dispatch"], 1)
        self.assertEqual(a["bounce"], 1)

    def test_counts_fail_from_spawn_failed_env(self):
        events = [
            {"ts": "2026-09-20T10:00:00Z", "kind": "dispatched", "card": "C-1002", "pid": 3},
            {"ts": "2026-09-20T10:01:00Z", "kind": "spawn_failed_env", "card": "C-1002"},
        ]
        a = self._analysis(events)
        self.assertEqual(a["fail"], 1)

    def test_full_productivity_reflects_reality(self):
        events = [
            {"ts": "2026-09-20T10:00:00Z", "kind": "dispatched", "card": "C-2000", "pid": 10},
            {"ts": "2026-09-20T10:01:00Z", "kind": "dispatched", "card": "C-2001", "pid": 11},
            {"ts": "2026-09-20T10:02:00Z", "kind": "dispatched", "card": "C-2002", "pid": 12},
            {
                "ts": "2026-09-20T10:05:00Z",
                "kind": "reaped",
                "card": "C-2000",
                "pid": 10,
                "verdict": "DONE",
                "outcome": "dead",
                "lane": "planner",
            },
            {
                "ts": "2026-09-20T10:06:00Z",
                "kind": "reaped",
                "card": "C-2001",
                "pid": 11,
                "verdict": "DONE",
                "outcome": "dead",
                "lane": "evaluator",
            },
            {
                "ts": "2026-09-20T10:07:00Z",
                "kind": "gate_bounced",
                "card": "C-2002",
                "reason": "no evidence",
            },
            {"ts": "2026-09-20T10:08:00Z", "kind": "spawn_failed_env", "card": "C-2003"},
        ]
        a = self._analysis(events)
        self.assertEqual(a["done"], 2)
        self.assertEqual(a["bounce"], 1)
        self.assertEqual(a["fail"], 1)

    def test_no_false_positive_done_from_reaped_blocked(self):
        events = [
            {"ts": "2026-09-20T10:00:00Z", "kind": "dispatched", "card": "C-3000", "pid": 20},
            {
                "ts": "2026-09-20T10:30:00Z",
                "kind": "reaped",
                "card": "C-3000",
                "pid": 20,
                "verdict": "BLOCKED",
                "outcome": "dead",
                "lane": "planner",
            },
        ]
        a = self._analysis(events)
        self.assertEqual(a["done"], 0)
        self.assertEqual(a["dispatch"], 1)


if __name__ == "__main__":
    unittest.main()
