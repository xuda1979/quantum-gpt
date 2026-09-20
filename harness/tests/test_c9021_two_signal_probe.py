"""C-9021: /health-ready must be split from /exec-alive by an ACTIVE exec
round-trip positive control, not only by the passive B-263 body fields.

Measured 2026-09-16 (C-9008, re-measured 19:31-19:37Z): ASI1/ASI3 sat
/health 200 ready=true (pid stable) while /exec timed out at 25s/90s/180s
and pendingRequestCount only grew. probe_daemon certified that state from
the health BODY alone; a wedge whose body fields look clean (busyAgeMs
resets, pending < 25, an old lastCommandCompletedAt) renders plain READY.

RED first: these tests fail while probe_daemon/run_all accept no
exec_probe_fn (positive control) and while the summary carries no two-signal
verdict (HEALTH=... EXEC=...).
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import resource_probes as RP  # noqa: E402


def _health(**kw):
    """A CLEAN ready body -- the B-263 body heuristics alone call this ready."""
    body = dict(
        ok=True,
        ready=True,
        startupState="ready",
        pid=98203,
        uptime=88586,
        busy=False,
        busyAgeMs=0,
        pendingRequestCount=0,
        lastCommandCompletedAt="2026-09-16T19:30:00.000Z",
    )
    body.update(kw)
    return body


def _health_fn(body):
    def fn(port, timeout=6):
        return dict(code=200, body=json.dumps(body))

    return fn


def _echo_timeout(port):
    return dict(rc=1, summary="UNKNOWN (exec echo transport: timed out)")


def _echo_ok(port):
    return dict(rc=0, summary="OK echo roundtrip 0.02s")


def _echo_raises(port):
    raise OSError("transport died mid-probe")


class TestProbeDaemonExecPositiveControl(unittest.TestCase):
    def test_clean_ready_body_plus_exec_timeout_is_never_plain_ready(self):
        out = RP.probe_daemon(
            "asi3", 20653, health_fn=_health_fn(_health()), exec_probe_fn=_echo_timeout
        )
        self.assertNotEqual(out["status"], "ready")
        self.assertEqual(out["status"], "unknown")
        self.assertIn("HEALTH=ready", out["summary"])
        self.assertIn("EXEC=wedged", out["summary"])

    def test_raising_exec_control_fails_closed_not_ready(self):
        out = RP.probe_daemon(
            "asi3", 20653, health_fn=_health_fn(_health()), exec_probe_fn=_echo_raises
        )
        self.assertNotEqual(out["status"], "ready")
        self.assertIn("EXEC=wedged", out["summary"])

    def test_clean_ready_body_plus_exec_ok_is_ready_with_both_signals(self):
        out = RP.probe_daemon(
            "asi3", 20653, health_fn=_health_fn(_health()), exec_probe_fn=_echo_ok
        )
        self.assertEqual(out["status"], "ready")
        self.assertIn("HEALTH=ready", out["summary"])
        self.assertIn("EXEC=ok", out["summary"])
        self.assertIn("liveness", out)

    def test_body_wedged_still_downgrades_with_exec_control(self):
        body = _health(busy=True, busyAgeMs=330000, pendingRequestCount=487)
        out = RP.probe_daemon("asi3", 20653, health_fn=_health_fn(body), exec_probe_fn=_echo_ok)
        self.assertNotEqual(out["status"], "ready")
        self.assertIn("exec_wedged", out["summary"])

    def test_no_exec_control_keeps_b263_behavior(self):
        out = RP.probe_daemon("asi3", 20653, health_fn=_health_fn(_health()))
        self.assertEqual(out["status"], "ready")


class TestRunAllCarriesExecControl(unittest.TestCase):
    def test_run_all_passes_positive_control_to_every_daemon_port(self):
        with tempfile.TemporaryDirectory() as td:
            payloads = RP.run_all(
                td,
                health_fn=_health_fn(_health()),
                exec_probe_fn=_echo_timeout,
                now="2026-09-17T00:00:00Z",
            )
            for name in ("asi1", "asi2", "asi3"):
                self.assertNotEqual(
                    payloads[name]["status"], "ready", name + " certified ready on health alone"
                )
                self.assertIn("EXEC=wedged", payloads[name]["summary"])
            # the probes file the standup renderer reads carries the two signals
            with open(os.path.join(td, "probes", "asi3.json")) as f:
                rec = json.load(f)
            self.assertIn("EXEC=wedged", rec["summary"])


if __name__ == "__main__":
    unittest.main()
