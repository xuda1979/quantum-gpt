#!/usr/bin/env python3
"""C-9620 hold: an evaluator-box transport MUST gate the evaluator lane
fail-closed when the box is NOT dispatchable, not only on the literal
'exec_wedged' marker.

Prior C-9620 lane-fix read the PER-LANE box probe (evaluator->asi2) but
transport_wedged_lane only treated a summary containing 'exec_wedged' as wedged.
An alive-but-unready box reports 'UNKNOWN (daemon reachable, ready=false)'; a
broken transport reports 'health non-200'. NONE carry 'exec_wedged', so the gate
FAILS OPEN and dispatches an eval leg onto an ASI2 that cannot serve it -> the
recurring stall/kill this card exists to end. Fail-closed: never dispatch an eval
leg onto a box whose exec transport is unhealthy. RED here.
"""

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import harness.qgh as q


def _fresh(sd, box, summ):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    os.makedirs(os.path.join(sd, "probes"), exist_ok=True)
    path = os.path.join(sd, "probes", box + ".json")
    rec = dict()
    rec["ts"] = ts
    rec["summary"] = summ
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rec, f)


class TestEvalLaneFailClosedOnUnhealthy(unittest.TestCase):
    def test_asi2_ready_false_gates_evaluator(self):
        with tempfile.TemporaryDirectory() as sd:
            _fresh(sd, "asi2", "UNKNOWN (daemon reachable, ready=false)")
            _fresh(sd, "asi3", "READY HEALTH=ready EXEC=ok")
            # C-9629: the gate now re-measures a young-unhealthy probe live;
            # stub the refresh (a real-daemon side effect) to a no-op so this
            # unit test proves the pure read: an unhealthy re-measure verdict
            # keeps the lane gated fail-closed.
            with mock.patch.object(q, "_refresh_box_probe_best_effort"):
                self.assertTrue(
                    q.transport_wedged_lane("evaluator", sd),
                    "an unready ASI2 must fail-closed the evaluator lane",
                )

    def test_asi2_transport_broken_gates_evaluator(self):
        with tempfile.TemporaryDirectory() as sd:
            _fresh(sd, "asi2", "UNKNOWN (health non-200: transport error (HTTP 500))")
            _fresh(sd, "asi3", "READY HEALTH=ready EXEC=ok")
            # C-9629: stub the live re-measure (see test_asi2_ready_false above).
            with mock.patch.object(q, "_refresh_box_probe_best_effort"):
                self.assertTrue(
                    q.transport_wedged_lane("evaluator", sd),
                    "an /exec-broken ASI2 must fail-closed the evaluator lane",
                )

    def test_asi2_healthy_opens_evaluator(self):
        with tempfile.TemporaryDirectory() as sd:
            _fresh(sd, "asi2", "READY HEALTH=ready EXEC=ok")
            _fresh(sd, "asi3", "READY HEALTH=ready EXEC=ok")
            self.assertFalse(
                q.transport_wedged_lane("evaluator", sd),
                "a healthy ASI2 must allow the evaluator lane",
            )


if __name__ == "__main__":
    unittest.main()
