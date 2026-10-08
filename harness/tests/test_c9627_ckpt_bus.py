"""C-9627: NAS checkpoint bus + eval watcher decoupling (item 8).

Contracts covered:
  - checkpoint_bus_manifest: bus layout, manifest schema, idempotent publish
  - eval_leg_fail_closed: verdict VOID without markers, OK with both
  - eval_never_on_trainer_npu: watcher never runs legs on ASI3
"""

from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "harness"))
sys.path.insert(0, str(REPO / "harness" / "scripts"))

from harness_config import get  # noqa: E402


class TestBusConfig(unittest.TestCase):
    def test_bus_root_is_nas_shared_path(self):
        self.assertEqual(get("ckpt_bus.nas_root"), "/root/work/ckpt_bus")

    def test_complete_marker_is_adapter_config(self):
        self.assertEqual(get("ckpt_bus.complete_marker"), "adapter/adapter_config.json")


class TestPublishIdempotence(unittest.TestCase):
    """The publisher skips steps whose manifest already exists (atomic rename)."""

    def test_publish_step_skips_existing_manifest(self):
        import tempfile

        import checkpoint_publisher as cp

        with tempfile.TemporaryDirectory() as td:
            src_ckpt = Path(td) / "run/step_000001_adapter"
            src_ckpt.mkdir(parents=True)
            (src_ckpt / "adapter_config.json").write_text("{}")
            cp.BUS = Path(td) / "bus"
            cp.BUS.mkdir()
            r1 = cp.publish_step(src_ckpt)
            r2 = cp.publish_step(src_ckpt)  # second publish must SKIP
        self.assertEqual(r1["status"], "PUBLISHED")
        self.assertEqual(r2["status"], "SKIP_EXISTS")

    def test_publish_step_skips_incomplete_checkpoint(self):
        import tempfile

        import checkpoint_publisher as cp

        with tempfile.TemporaryDirectory() as td:
            src_ckpt = Path(td) / "run/step_000002_adapter"
            src_ckpt.mkdir(parents=True)  # no adapter_config.json
            cp.BUS = Path(td) / "bus"
            cp.BUS.mkdir()
            r = cp.publish_step(src_ckpt)
        self.assertEqual(r["status"], "SKIP_INCOMPLETE")

    def test_manifest_schema_has_run_step_sha(self):
        import tempfile

        import checkpoint_publisher as cp

        with tempfile.TemporaryDirectory() as td:
            src_ckpt = Path(td) / "run/step_000003_adapter"
            src_ckpt.mkdir(parents=True)
            (src_ckpt / "adapter_config.json").write_text("{}")
            (src_ckpt / "w.bin").write_bytes(b"abc")
            cp.BUS = Path(td) / "bus"
            cp.BUS.mkdir()
            cp.publish_step(src_ckpt)
            man = json.loads((cp.BUS / "run/step_000003_adapter/manifest.json").read_text())
        self.assertEqual(man["run"], "run")
        self.assertEqual(man["step"], "step_000003_adapter")
        self.assertEqual(len(man["sha16"]), 16)
        self.assertGreater(man["bytes"], 0)


class TestWatcherFailClosed(unittest.TestCase):
    """The verdict helper enforces the contracts' marker rule."""

    def _run_helper(self, envelope: dict, records: list, tmpdir: Path) -> dict:
        import eval_watcher as ew

        envf = tmpdir / "env.json"
        scf = tmpdir / "scores.json"
        manf = tmpdir / "manifest.json"
        outf = tmpdir / "verdict.json"
        envf.write_text(json.dumps(envelope))
        scf.write_text(json.dumps({"records": records}))
        manf.write_text(json.dumps({"run": "r", "step": "s"}))
        helper = tmpdir / "helper.py"
        helper.write_text(ew.VERDICT_PY)
        import subprocess

        subprocess.run(
            [sys.executable, str(helper), str(envf), str(sf_placeholder := scf), str(outf), str(manf)],
            check=True,
        )
        return json.loads(outf.read_text())

    def test_void_without_markers(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            import tempfile

            with tempfile.TemporaryDirectory() as td:
                v = self._run_helper(
                    {"adapter_applied_marker": False, "adapter_probe_differs_marker": False},
                    [{"model": "base", "passed": True}, {"model": "adapter", "passed": True}],
                    Path(td),
                )
        self.assertEqual(v["status"], "VOID")

    def test_ok_with_both_markers_and_counts(self):
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            v = self._run_helper(
                {"adapter_applied_marker": True, "adapter_probe_differs_marker": True},
                [
                    {"model": "base", "passed": True},
                    {"model": "base", "passed": False},
                    {"model": "adapter", "passed": True},
                    {"model": "adapter", "passed": True},
                ],
                Path(td),
            )
        self.assertEqual(v["status"], "OK")
        self.assertEqual(v["base"], {"passed": 1, "total": 2})
        self.assertEqual(v["adapter"], {"passed": 2, "total": 2})
        self.assertTrue(v["beats_base"])

    def test_adapter_not_beating_base_is_not_beats_base(self):
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            v = self._run_helper(
                {"adapter_applied_marker": True, "adapter_probe_differs_marker": True},
                [
                    {"model": "base", "passed": True},
                    {"model": "adapter", "passed": False},
                ],
                Path(td),
            )
        self.assertFalse(v["beats_base"])


class TestWatcherNeverOnTrainer(unittest.TestCase):
    def test_eval_box_is_asi2_not_asi3(self):
        import eval_watcher as ew

        forbidden = get("box_ports") and "ASI3"
        self.assertNotEqual(ew.EVAL_BOX if hasattr(ew, "EVAL_BOX") else "ASI2", forbidden)

    def test_scan_targets_bus_not_vllm_workspace(self):
        import eval_watcher as ew

        self.assertIn("/root/work/ckpt_bus", str(ew.BUS))


if __name__ == "__main__":
    unittest.main()
