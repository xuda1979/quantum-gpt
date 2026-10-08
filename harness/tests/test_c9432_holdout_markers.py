#!/usr/bin/env python3
"""C-9432: holdout-leg fail-closed markers must derive from real probe evidence,
never be hardcoded True.

C-9378 shipped run_holdout_leg1.py / run_holdout_leg2.py with
adapter_applied_marker / adapter_probe_differs_marker unconditionally set to
True after the probe subprocess returned 0. The probe is fail-closed, but the
LEG garbage the marker into True regardless of whether the adapter actually
applied or the base-vs-adapter probe actually differed.

The fix (this card) computes both markers from the probe structured stage
evidence in the leg log via scripts/holdout_markers.compute_holdout_markers,
fail-closed: a marker is True ONLY when the matching probe stage event is
present AND points at the dispatched adapter. RED=markers are False when the
adapter never applied / probes never differed; GREEN=True only on real probe
evidence.
"""

import ast
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.holdout_markers import STAGE_APPLIED, STAGE_PROBE_DIFFERS, compute_holdout_markers


def _stage_line(stage, adapter):
    return json.dumps({"stage": stage, "adapter": str(adapter)})


class C9432HoldoutMarkersTest(unittest.TestCase):
    def _mk_adapter(self):
        d = tempfile.mkdtemp()
        p = Path(d) / "adapter_model.safetensors"
        p.write_bytes(b"real-tensor-data" + b"\x00" * 64)
        return p

    def test_red_markers_false_when_adapter_never_applied(self):
        """No apply stage / no differ stage -> both markers False."""
        adapter = self._mk_adapter()
        text = "LEG_FAILCLOSED adapter-applied adapter-probe-differs\n"
        applied, differs = compute_holdout_markers(text, adapter)
        self.assertFalse(applied, "marker must be False without apply evidence")
        self.assertFalse(differs, "marker must be False without differ evidence")

    def test_red_marker_false_when_probe_identical(self):
        """Only an apply stage (no differ stage) -> differ marker stays False."""
        adapter = self._mk_adapter()
        text = _stage_line(STAGE_APPLIED, adapter) + "\n"
        text += "LEG_FAILCLOSED adapter-applied adapter-probe-differs\n"
        applied, differs = compute_holdout_markers(text, adapter)
        self.assertTrue(applied)
        self.assertFalse(differs, "differs marker needs its own stage event")

    def test_green_markers_true_on_real_probe_evidence(self):
        """Both stage events for the dispatched adapter -> both markers True."""
        adapter = self._mk_adapter()
        text = _stage_line(STAGE_APPLIED, adapter) + "\n"
        text += _stage_line(STAGE_PROBE_DIFFERS, adapter) + "\n"
        applied, differs = compute_holdout_markers(text, adapter)
        self.assertTrue(applied, "apply stage + existing adapter -> True")
        self.assertTrue(differs, "probe-differs stage -> True")

    def test_stage_marker_requires_real_existing_adapter(self):
        """A stage event for a NONEXISTENT adapter file -> applied stays False."""
        adapter = "/does/not/exist/adapter_model.safetensors"
        text = _stage_line(STAGE_APPLIED, adapter) + "\n"
        text += _stage_line(STAGE_PROBE_DIFFERS, adapter) + "\n"
        applied, differs = compute_holdout_markers(text, adapter)
        self.assertFalse(applied, "no on-disk adapter -> not applied")

    def test_marker_ignores_foreign_adapter_evidence(self):
        """Stage events for a DIFFERENT adapter path -> markers False for ours."""
        adapter = self._mk_adapter()
        other = self._mk_adapter()
        text = _stage_line(STAGE_APPLIED, other) + "\n"
        text += _stage_line(STAGE_PROBE_DIFFERS, other) + "\n"
        applied, differs = compute_holdout_markers(text, adapter)
        self.assertFalse(applied, "foreign apply stage must not apply to ours")
        self.assertFalse(differs, "foreign differ stage must not apply to ours")

    def test_leg_scripts_do_not_hardcode_marker_true(self):
        """Envelope marker keys must never be assigned a literal True."""
        for rel in ("scripts/run_holdout_leg1.py", "scripts/run_holdout_leg2.py"):
            src = (ROOT / rel).read_text(encoding="utf-8")
            tree = ast.parse(src)
            for node in ast.walk(tree):
                if not isinstance(node, ast.Assign):
                    continue
                subs = [
                    t
                    for t in node.targets
                    if isinstance(t, ast.Subscript)
                    and isinstance(t.value, ast.Name)
                    and t.value.id == "envelope"
                ]
                for t in subs:
                    if not isinstance(t.slice, ast.Constant):
                        continue
                    key = t.slice.value
                    if key in ("adapter_applied_marker", "adapter_probe_differs_marker"):
                        if isinstance(node.value, ast.Constant) and node.value.value is True:
                            self.fail(f"{rel} hardcodes marker {key} to True")


if __name__ == "__main__":
    unittest.main()
