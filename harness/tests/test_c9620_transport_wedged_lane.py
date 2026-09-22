#!/usr/bin/env python3
"""C-9620: the dispatch transport-wedge gate must be LANE-AWARE over box.

Root cause (recurring P0, C-9613/C-9605/C-9595/C-9589 retires): the fixer
transport_wedged() reads ONLY probes/asi3.json and returns a single GLOBAL
"wedged" verdict, which cmd_dispatch uses to gate ALL BOX_BOUND_LANES
(evaluator, trainer-ops, deploy-integrity). But the 18-task holdout EVAL legs
run on **ASI2** (scripts/run_asi2_base_adapter_rubric_eval.py, c9072 marker
canary, fast_pass_gate all dispatch to ASI2 :19004), NOT ASI3. So an ASI3-only
exec wedge (a stuck /exec busy slot -- the measured C-9613 condition) holds
the evaluator lane and no fail-closed eval leg can ever dispatch on the
healthy ASI2 box. No leg -> no 18/18.

Fix: a lane->box mapping and transport_wedged_lane(lane) that gates a lane
on the exec probe of the box that actually serves it. An ASI3 wedge must NOT
block the ASI2 evaluator; an ASI2 wedge MUST.

RED first: transport_wedged_lane does not exist yet (AttributeError) and the
ASI3-wedge-evaluator case would be mishandled by the global asi3-only gate.
"""

import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import harness.qgh as q  # noqa: E402


def _write_probe(sd, box, summary, ts=None):
    # fresh ts so the gate's stale-probe refresh (a real-daemon side effect)
    # never fires during this unit test -- we are testing the pure wedge read.
    if ts is None:
        from datetime import datetime, timezone

        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    d = os.path.join(sd, "probes")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, box + ".json"), "w", encoding="utf-8") as f:
        json.dump({"ts": ts, "summary": summary}, f)


class TestTransportWedgedLane(unittest.TestCase):
    def test_asi3_wedge_does_not_gate_asi2_evaluator(self):
        """RED/Acceptance: an ASI3-only exec wedge must NOT hold the evaluator
        lane, because eval legs run on ASI2 (healthy here)."""
        with tempfile.TemporaryDirectory() as sd:
            _write_probe(
                sd,
                "asi3",
                "UNKNOWN (ready-but-exec_wedged: busyAgeMs=330000 pendingRequestCount=487 EXEC=wedged)",
            )
            _write_probe(sd, "asi2", "READY HEALTH=ready EXEC=ok")
            self.assertFalse(
                q.transport_wedged_lane("evaluator", sd),
                "evaluator runs on ASI2; an ASI3 wedge must not block it",
            )

    def test_asi3_wedge_does_gate_trainer_ops(self):
        """trainer runs on ASI3, so an ASI3 wedge DOES block trainer-ops."""
        with tempfile.TemporaryDirectory() as sd:
            _write_probe(
                sd,
                "asi3",
                "UNKNOWN (ready-but-exec_wedged: busyAgeMs=330000 pendingRequestCount=487 EXEC=wedged)",
            )
            _write_probe(sd, "asi2", "READY HEALTH=ready EXEC=ok")
            # C-9629: the gate re-measures a young-unhealthy probe live; stub
            # the refresh (real-daemon side effect) so this unit test proves
            # the pure read: an unhealthy verdict on re-measure keeps gating.
            with mock.patch.object(q, "_refresh_box_probe_best_effort"):
                self.assertTrue(
                    q.transport_wedged_lane("trainer-ops", sd),
                    "trainer-ops runs on ASI3; an ASI3 wedge must gate it",
                )

    def test_asi2_wedge_does_gate_evaluator(self):
        """Acceptance: an ASI2 wedge MUST gate the evaluator lane (its box)."""
        with tempfile.TemporaryDirectory() as sd:
            _write_probe(sd, "asi3", "READY HEALTH=ready EXEC=ok")
            _write_probe(
                sd,
                "asi2",
                "UNKNOWN (ready-but-exec_wedged: busyAgeMs=330000 pendingRequestCount=487 EXEC=wedged)",
            )
            # C-9629: stub the live re-measure (see trainer-ops test above).
            with mock.patch.object(q, "_refresh_box_probe_best_effort"):
                self.assertTrue(
                    q.transport_wedged_lane("evaluator", sd),
                    "evaluator runs on ASI2; an ASI2 wedge must gate it",
                )

    def test_missing_probe_fails_open(self):
        """A missing probe is fail-open (same as legacy transport_wedged):
        we never dispatch against an unmeasured box anyway."""
        with tempfile.TemporaryDirectory() as sd:
            self.assertFalse(q.transport_wedged_lane("evaluator", sd))
            self.assertFalse(q.transport_wedged_lane("trainer-ops", sd))


if __name__ == "__main__":
    unittest.main()
