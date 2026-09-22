#!/usr/bin/env python3
"""C-9629: a young-but-unhealthy probe must trigger a live refresh, not latch.

Measured incident 2026-09-22 12:14Z: during an ASI3 daemon restart the probe
measured "Connection refused" and wrote it to probes/asi3.json. The daemon
recovered within seconds; exec round-trips verified healthy at 12:39Z. But
_box_exec_wedged only refreshed probes older than PROBE_STALE_S (1h), so the
fresh-but-unhealthy probe LATCHED the box-bound dispatch gate for up to an
hour: every tick printed "exec transport wedged - box-bound lanes held" while
the box was actually fine, and no trainer-ops card could dispatch.

The fix: refresh ALSO when the probe is young but does not positively
certify a healthy box (not _healthy_exec_summary). The refresh itself runs
the active exec echo positive control (C-9625), so a genuinely wedged box
still keeps the gate held -- the latch fix cannot fail the gate open.
"""

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import harness.qgh as q  # noqa: E402


def _write_probe(sd, box, summary, ts):
    d = os.path.join(sd, "probes")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, box + ".json"), "w", encoding="utf-8") as f:
        json.dump({"ts": ts, "summary": summary}, f)


def _fresh_ts():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class TestUnhealthyYoungProbeRefresh(unittest.TestCase):
    """The C-9629 latch: young + unhealthy probe => refresh attempted."""

    def test_conn_refused_young_probe_triggers_refresh(self):
        """A minutes-old 'Connection refused' probe must attempt a refresh."""
        with tempfile.TemporaryDirectory() as sd:
            _write_probe(
                sd,
                "asi3",
                "UNKNOWN (health non-200: transport error (<urlopen error "
                "[Errno 61] Connection refused>))",
                _fresh_ts(),
            )
            with mock.patch.object(
                q, "_refresh_box_probe_best_effort", wraps=q._refresh_box_probe_best_effort
            ) as rf:
                q._box_exec_wedged(sd, "asi3")
                self.assertEqual(
                    rf.call_count,
                    1,
                    "young-but-unhealthy probe must trigger exactly one refresh",
                )

    def test_healthy_young_probe_does_not_refresh(self):
        """A young READY EXEC=ok probe must not spam the daemon with refreshes."""
        with tempfile.TemporaryDirectory() as sd:
            _write_probe(sd, "asi3", "READY HEALTH=ready EXEC=ok pid=1", _fresh_ts())
            with mock.patch.object(q, "_refresh_box_probe_best_effort") as rf:
                q._box_exec_wedged(sd, "asi3")
                rf.assert_not_called()

    def test_stale_unhealthy_probe_still_refreshes(self):
        """The pre-existing stale refresh path is preserved (>1h old)."""
        with tempfile.TemporaryDirectory() as sd:
            old = (datetime.now(timezone.utc) - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
            _write_probe(sd, "asi3", "UNKNOWN (connection refused)", old)
            with mock.patch.object(q, "_refresh_box_probe_best_effort") as rf:
                q._box_exec_wedged(sd, "asi3")
                self.assertEqual(rf.call_count, 1)

    def test_refresh_recovers_gate_when_box_actually_healthy(self):
        """End-to-end: refresh rewrites the probe; the wedge verdict clears.

        The refresh hits real daemons; here it is stubbed to emulate the
        measured recovery (daemon back up, exec echo ok) by writing a healthy
        probe file, proving the refreshed read flips the verdict to healthy.
        """
        with tempfile.TemporaryDirectory() as sd:
            _write_probe(
                sd,
                "asi3",
                "UNKNOWN (health non-200: transport error (Connection refused))",
                _fresh_ts(),
            )

            def fake_refresh(state_dir):
                _write_probe(sd, "asi3", "READY HEALTH=ready EXEC=ok pid=1", _fresh_ts())

            with mock.patch.object(q, "_refresh_box_probe_best_effort", fake_refresh):
                wedged = q._box_exec_wedged(sd, "asi3")
            self.assertFalse(
                wedged,
                "after a refresh that certifies READY+EXEC=ok the gate must clear",
            )


if __name__ == "__main__":
    unittest.main()
