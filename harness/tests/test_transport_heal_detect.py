"""C-0008 heal-detect: /health liveness must NOT certify the /exec transport.

B-263 signatures measured live 2026-09-16:
  - ASI1/ASI3: /health 200 ready=true, but busy=true with a stuck exec slot
    (lastCommandStartedAt set, lastCommandCompletedAt null, busyAgeMs growing)
    and a pending queue that only grows (80 / 487). Every /exec echo times out.
    The old probe_daemon called this plain READY -- a false liveness signal.
  - ASI2: startupState booting -> error at uptime ~1306s (normal boot is
    ~4-5 min) = failed boot / auth-capture loop; console cure is user-gated.

RED first: these tests fail against resource_probes without classify_transport /
probe_exec_echo and without the wedge downgrade in probe_daemon.
"""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import resource_probes as RP  # noqa: E402


def _health(**kw):
    body = dict(
        ok=True,
        ready=True,
        startupState="ready",
        startupError=None,
        env="ASI3",
        pid=98203,
        port=20653,
        uptime=88586,
        commandCount=1473,
        busy=False,
        busyAgeMs=0,
        pendingRequestCount=0,
        lastCommand="echo hi",
        lastCommandStartedAt=None,
        lastCommandCompletedAt=None,
    )
    body.update(kw)
    return body


class TestClassifyTransport(unittest.TestCase):
    def test_ready_not_busy_is_ready(self):
        out = RP.classify_transport(_health())
        self.assertEqual(out["status"], "ready")

    def test_ready_but_stuck_exec_slot_is_exec_wedged(self):
        out = RP.classify_transport(
            _health(
                busy=True,
                busyAgeMs=330000,
                pendingRequestCount=487,
                lastCommandStartedAt="2026-09-16T15:41:21.177Z",
                lastCommandCompletedAt=None,
            )
        )
        self.assertEqual(out["status"], "exec_wedged")
        self.assertIn("pendingRequestCount", out["evidence"])

    def test_pending_flood_is_exec_wedged_even_with_reset_busy_age(self):
        # measured 2026-09-16: each stuck command is superseded by the next
        # probe (busyAgeMs resets ~60s) but NOTHING ever completes and the
        # pending queue floods 80/487 -- a healthy daemon drains its queue
        out = RP.classify_transport(
            _health(
                busy=True,
                busyAgeMs=4000,
                pendingRequestCount=487,
                lastCommandStartedAt="2026-09-16T15:42:16.391Z",
                lastCommandCompletedAt=None,
            )
        )
        self.assertEqual(out["status"], "exec_wedged")

    def test_small_pending_queue_is_not_a_flood(self):
        out = RP.classify_transport(
            _health(
                busy=True,
                busyAgeMs=4000,
                pendingRequestCount=5,
                lastCommandStartedAt="2026-09-16T15:42:16.391Z",
                lastCommandCompletedAt="2026-09-16T15:42:20.000Z",
            )
        )
        self.assertEqual(out["status"], "ready")

    def test_fresh_busy_is_still_ready(self):
        out = RP.classify_transport(
            _health(
                busy=True,
                busyAgeMs=5000,
                pendingRequestCount=1,
                lastCommandStartedAt="2026-09-16T15:41:21.177Z",
                lastCommandCompletedAt=None,
            )
        )
        self.assertEqual(out["status"], "ready")

    def test_completed_command_with_old_timestamp_is_not_wedged(self):
        out = RP.classify_transport(
            _health(
                busy=True,
                busyAgeMs=300000,
                lastCommandStartedAt="2026-09-16T15:41:21.177Z",
                lastCommandCompletedAt="2026-09-16T15:41:22.177Z",
            )
        )
        self.assertEqual(out["status"], "ready")

    def test_startup_error_is_boot_failed(self):
        out = RP.classify_transport(
            _health(
                ready=False,
                startupState="error",
                uptime=1306,
                busy=True,
                busyAgeMs=52314,
            )
        )
        self.assertEqual(out["status"], "boot_failed")

    def test_booting_past_window_is_boot_stuck(self):
        out = RP.classify_transport(
            _health(
                ready=False,
                startupState="booting",
                uptime=1300,
            )
        )
        self.assertEqual(out["status"], "boot_stuck")

    def test_booting_inside_window_is_booting(self):
        out = RP.classify_transport(
            _health(
                ready=False,
                startupState="booting",
                uptime=60,
            )
        )
        self.assertEqual(out["status"], "booting")

    def test_ready_false_without_state_is_unknown(self):
        out = RP.classify_transport(_health(ready=False, startupState=None))
        self.assertEqual(out["status"], "unknown")

    def test_unparseable_body_is_unknown(self):
        out = RP.classify_transport(None)
        self.assertEqual(out["status"], "unknown")


class TestProbeDaemonDowngradesWedge(unittest.TestCase):
    """B-263 fix: ready=true with a wedged exec slot must NOT render READY."""

    @staticmethod
    def _health_fn(body):
        def fn(port, timeout=6):
            return dict(code=200, body=json.dumps(body))

        return fn

    def test_wedged_ready_body_renders_unknown(self):
        body = _health(
            busy=True,
            busyAgeMs=330000,
            pendingRequestCount=487,
            lastCommandStartedAt="2026-09-16T15:41:21.177Z",
            lastCommandCompletedAt=None,
        )
        out = RP.probe_daemon("asi3", 20653, health_fn=self._health_fn(body))
        self.assertEqual(out["status"], "unknown")
        self.assertIn("exec_wedged", out["summary"])

    def test_plain_ready_body_still_renders_ready(self):
        out = RP.probe_daemon("asi3", 20653, health_fn=self._health_fn(_health()))
        self.assertEqual(out["status"], "ready")


class TestProbeExecEcho(unittest.TestCase):
    """The 10s echo roundtrip is the acceptance instrument for the transport."""

    @staticmethod
    def _post_fn(output=None, status=200):
        # None => simulate a real echo: reply with the marker from the command
        def fn(port, payload, timeout):
            cmd = json.loads(payload.decode())["command"]
            reply = output if output is not None else cmd[len("echo ") :] + "\n"
            return dict(status=status, body=json.dumps(dict(output=reply)))

        return fn

    def test_echo_roundtrip_ok(self):
        out = RP.probe_exec_echo(20653, post_fn=self._post_fn())
        self.assertEqual(out["rc"], 0)
        self.assertIn(out["marker"], out["output"])
        self.assertGreaterEqual(out["elapsed_s"], 0.0)

    def test_echo_wrong_output_fails_closed(self):
        out = RP.probe_exec_echo(20653, post_fn=self._post_fn(output="garbage\n"))
        self.assertNotEqual(out["rc"], 0)

    def test_echo_timeout_is_unknown_rc_not_zero(self):
        def boom(port, payload, timeout):
            raise OSError("timed out")

        out = RP.probe_exec_echo(20653, post_fn=boom)
        self.assertEqual(out["rc"], 1)
        self.assertIn("UNKNOWN", out["summary"])

    def test_echo_marker_is_unique_per_call(self):
        seen = []

        def fn(port, payload, timeout):
            cmd = json.loads(payload.decode())["command"]
            seen.append(cmd)
            return dict(status=200, body=json.dumps(dict(output=cmd[len("echo ") :] + "\n")))

        a = RP.probe_exec_echo(20653, post_fn=fn)
        b = RP.probe_exec_echo(20653, post_fn=fn)
        self.assertNotEqual(a["marker"], b["marker"])
        self.assertEqual(a["rc"], 0)
        self.assertEqual(b["rc"], 0)


if __name__ == "__main__":
    unittest.main()
