#!/usr/bin/env python3
"""C-9625: box-bound trainer-ops dispatch must stay fail-closed when a stale
exec_wedged probe is refreshed and the box's /health lies ready but its /exec
channel is still wedged.

C-9620 fixed the lane->box mapping (evaluator on ASI2, trainer-ops on ASI3)
but the stale-probe refresh (_refresh_box_probe_best_effort) re-measures the
box with a HEALTH-ONLY probe (no exec positive control). A /health 'ready=true'
can LIE (C-9021 / d59579a7): the exec channel may still be wedged. A health-only
refresh then overwrites the stale 'exec_wedged' summary with 'READY' and the
dispatch gate FAILS OPEN - dispatching box-bound trainer-ops workers onto a box
whose /exec is still wedged. Those workers immediately env_block -> C-9616 botting.

RED: with a stale wedged ASI3 probe and a /health that says ready (but an exec
echo that still fails), the trainer-ops gate must stay CLOSED (still wedged).
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import harness.qgh as q  # noqa: E402

STALE_TS = "2026-09-20T00:00:00Z"  # far past -> always stale
WEDGED_SUMMARY = (
    "UNKNOWN (ready-but-exec_wedged: busyAgeMs=330000 pendingRequestCount=487 EXEC=wedged)"
)


def _write_probe(sd, box, summary, ts=STALE_TS):
    d = os.path.join(sd, "probes")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, box + ".json"), "w", encoding="utf-8") as f:
        json.dump({"ts": ts, "summary": summary}, f)


class _FakeHealthReady:
    """A /health that LIES: reports ready=true, pid, busy=false (so the
    health-only classifier would return 'ready'). The exec channel is really
    wedged (exec echo fails)."""

    def __call__(self, port):
        body = json.dumps(
            {
                "startupState": "ready",
                "ready": True,
                "pid": 999,
                "busy": False,
                "busyAgeMs": 0,
                "pendingRequestCount": 0,
                "lastCommandCompletedAt": "2026-09-20T00:00:00Z",
            }
        )
        return {"code": 200, "body": body}


def _fake_exec_wedged(port, *a, **k):
    """The active exec echo positive control FAILS (rc=1) -> still wedged."""
    return {"rc": 1, "summary": "UNKNOWN (exec echo transport ...)"}


class TestTrainerDispatchStaysFailClosed(unittest.TestCase):
    def test_stale_wedged_probe_stays_closed_with_lying_health(self):
        """RED: a stale exec_wedged ASI3 probe refreshed via a health-only
        probe that lies ready=true must NOT re-open the trainer-ops dispatch
        gate while the exec channel is still wedged."""
        import resource_probes as RP

        with tempfile.TemporaryDirectory() as sd:
            _write_probe(sd, "asi3", WEDGED_SUMMARY)
            orig_daemon = RP.probe_daemon
            orig_exec = RP.probe_exec_echo
            try:
                # Wrap the REAL probe_daemon with a lying /health and a wedged
                # exec echo, so its C-9021 positive-control path is exercised.
                # NOTE (C-9629 test-bug fix): the wrapper must NOT forward a
                # caller-supplied exec_probe_fn in **k — the gate passes its
                # own exec_probe_fn kwarg, and the duplicate keyword raised a
                # TypeError that the refresh helper swallowed, so the probe
                # never rewrote and the first test passed vacuously.
                RP.probe_daemon = lambda name, port, *a, **k: orig_daemon(
                    name, port, health_fn=_FakeHealthReady(), exec_probe_fn=_fake_exec_wedged
                )
                self.assertTrue(
                    q.transport_wedged_lane("trainer-ops", sd),
                    "trainer-ops runs on ASI3; a lying /health must not re-open "
                    "the gate while the exec channel is still wedged (fail-closed)",
                )
            finally:
                RP.probe_daemon = orig_daemon
                RP.probe_exec_echo = orig_exec

    def test_healthy_exec_refresh_opens_gate(self):
        """Acceptance: when the exec positive control also passes, a stale
        wedge probe legitimately recovers and the trainer-ops gate opens."""
        import resource_probes as RP

        with tempfile.TemporaryDirectory() as sd:
            _write_probe(sd, "asi3", WEDGED_SUMMARY)
            orig_daemon = RP.probe_daemon
            orig_exec = RP.probe_exec_echo
            try:
                # Lying /health but a PASSING exec echo -> the wedge legitimately
                # recovered; the stale probe may refresh to ready and open.
                RP.probe_daemon = lambda name, port, *a, **k: orig_daemon(
                    name,
                    port,
                    health_fn=_FakeHealthReady(),
                    exec_probe_fn=lambda port, *a, **k: {"rc": 0, "summary": "OK echo roundtrip"},
                )
                self.assertFalse(
                    q.transport_wedged_lane("trainer-ops", sd),
                    "exec echo passed: the stale wedge legitimately recovered, gate opens",
                )
            finally:
                RP.probe_daemon = orig_daemon
                RP.probe_exec_echo = orig_exec


if __name__ == "__main__":
    unittest.main()
