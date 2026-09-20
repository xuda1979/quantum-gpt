"""C-9148: tick runner must auto-refresh stale box probes (>30min).

RED first 2026-09-20: the tick runner calls refresh_trainer_probe() and
_probe_results() but NEVER refreshes asi1/asi2/asi3/train_fire probes.
When the external probe agent dies, all box probes go STALE and the
standup goes blind.  The fix: a function auto_refresh_stale_probes()
that the tick calls BEFORE _probe_results(), detecting staleness with
the SAME 30-min threshold _probe_results() uses and calling
resource_probes.run_all() to re-measure.

Test also verifies the gate does NOT fire (no spurious refresh) when
probes are fresh (<30min)."""

import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
REPO = os.path.dirname(HARNESS_DIR)
sys.path.insert(0, HARNESS_DIR)

import harness_lib as H  # noqa: E402
import qgh  # noqa: E402
import resource_probes as RP  # noqa: E402


def _ts_offset_min(min_ago):
    """Return an ISO timestamp N minutes in the past."""
    t = datetime.now(timezone.utc) - timedelta(minutes=min_ago)
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def _write_probe(state_dir, name, ts, status="ready", summary="READY"):
    """Write a probe file with a given timestamp."""
    p = os.path.join(state_dir, "probes", f"{name}.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    H.save_json(p, {"ts": ts, "status": status, "summary": summary})


class TestAutoRefreshStaleProbes(unittest.TestCase):
    """The tick must detect stale probes and auto-refresh them."""

    def setUp(self):
        self._old_state = qgh.STATE
        self.tmp = tempfile.mkdtemp(prefix="qgh_c9148_")
        qgh.STATE = self.tmp
        os.makedirs(os.path.join(self.tmp, "probes"), exist_ok=True)

    def tearDown(self):
        import shutil

        qgh.STATE = self._old_state
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_stale_probes_trigger_refresh(self):
        """Probes older than 30min must trigger a live refresh."""
        old_ts = _ts_offset_min(45)
        for name in ("asi1", "asi2", "asi3"):
            _write_probe(
                self.tmp, name, old_ts, status="ready", summary="READY /health ready=true pid=9999"
            )
        _write_probe(self.tmp, "trainer", old_ts, status="unknown", summary="UNMEASURABLE")

        refresh_called = {"count": 0}

        def fake_run_all(state_dir, **kw):
            refresh_called["count"] += 1
            fresh_ts = H.now_iso()
            for name in ("asi1", "asi2", "asi3", "trainer", "train_fire"):
                _write_probe(
                    state_dir,
                    name,
                    fresh_ts,
                    status="ready",
                    summary="READY /health ready=true pid=1234",
                )
            return {}

        with patch.object(RP, "run_all", side_effect=fake_run_all):
            result = qgh.auto_refresh_stale_probes(state_dir=self.tmp)

        self.assertEqual(
            refresh_called["count"], 1, "run_all must be called exactly once for stale probes"
        )
        self.assertEqual(result["action"], "refreshed")

        probes = qgh._probe_results()
        for name in ("asi1", "asi2", "asi3"):
            self.assertNotIn("STALE", probes[name], f"{name} must not be STALE after refresh")

    def test_fresh_probes_no_refresh(self):
        """Probes newer than 30min must NOT trigger a refresh."""
        fresh_ts = _ts_offset_min(5)
        for name in ("asi1", "asi2", "asi3", "trainer", "train_fire"):
            _write_probe(
                self.tmp,
                name,
                fresh_ts,
                status="ready",
                summary="READY /health ready=true pid=9999",
            )

        refresh_called = {"count": 0}

        def fake_run_all(state_dir, **kw):
            refresh_called["count"] += 1
            return {}

        with patch.object(RP, "run_all", side_effect=fake_run_all):
            result = qgh.auto_refresh_stale_probes(state_dir=self.tmp)

        self.assertEqual(refresh_called["count"], 0, "run_all must NOT be called for fresh probes")
        self.assertEqual(result["action"], "skip")

    def test_missing_probes_trigger_refresh(self):
        """A missing probe file must trigger a refresh (fail-closed)."""
        refresh_called = {"count": 0}

        def fake_run_all(state_dir, **kw):
            refresh_called["count"] += 1
            fresh_ts = H.now_iso()
            for name in ("asi1", "asi2", "asi3", "trainer", "train_fire"):
                _write_probe(
                    state_dir,
                    name,
                    fresh_ts,
                    status="ready",
                    summary="READY /health ready=true pid=1234",
                )
            return {}

        with patch.object(RP, "run_all", side_effect=fake_run_all):
            result = qgh.auto_refresh_stale_probes(state_dir=self.tmp)

        self.assertEqual(
            refresh_called["count"], 1, "run_all must be called when probes are missing"
        )
        self.assertEqual(result["action"], "refreshed")

    def test_refresh_failure_never_raises(self):
        """A refresh failure must never crash the tick (fail-closed)."""
        old_ts = _ts_offset_min(45)
        _write_probe(self.tmp, "asi1", old_ts, status="ready")
        _write_probe(self.tmp, "asi2", old_ts, status="ready")
        _write_probe(self.tmp, "asi3", old_ts, status="ready")

        def boom_run_all(state_dir, **kw):
            raise RuntimeError("network explosion")

        with patch.object(RP, "run_all", side_effect=boom_run_all):
            result = qgh.auto_refresh_stale_probes(state_dir=self.tmp)

        self.assertEqual(result["action"], "refresh-failed")

    def test_refresh_writes_all_five_probe_files(self):
        """Refresh must write asi1, asi2, asi3, trainer, train_fire files."""
        old_ts = _ts_offset_min(45)
        _write_probe(self.tmp, "asi1", old_ts)

        written_names = []

        def capture_run_all(state_dir, **kw):
            fresh_ts = H.now_iso()
            for name in ("asi1", "asi2", "asi3", "trainer", "train_fire"):
                _write_probe(state_dir, name, fresh_ts, status="ready", summary="READY")
                written_names.append(name)
            return {}

        with patch.object(RP, "run_all", side_effect=capture_run_all):
            qgh.auto_refresh_stale_probes(state_dir=self.tmp)

        for name in ("asi1", "asi2", "asi3", "trainer", "train_fire"):
            p = os.path.join(self.tmp, "probes", f"{name}.json")
            self.assertTrue(os.path.isfile(p), f"{name}.json must exist after refresh")


if __name__ == "__main__":
    unittest.main()
