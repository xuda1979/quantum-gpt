"""C-9628: contracts-as-data + single config + hygiene gate (item 8).

Covers:
  - contracts.py: invariants are data; generated docs match; check() gates py39 safety
  - harness_config.py: single source for ports/paths; dot-path getter
  - lint_gate.py: stray detection, port-drift detection
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "harness"))
sys.path.insert(0, str(REPO / "harness" / "scripts"))

import contracts  # noqa: E402
import lint_gate  # noqa: E402
from harness_config import get  # noqa: E402


class TestContractsAsData(unittest.TestCase):
    def test_fail_closed_contract_has_marker_data(self):
        d = contracts.CONTRACTS["eval_leg_fail_closed"]["data"]
        self.assertEqual(sorted(d["required_markers"]), ["adapter_applied", "probe_differs"])
        self.assertTrue(d["void_if_missing"])

    def test_eval_never_on_trainer_lists_asi3_forbidden(self):
        d = contracts.CONTRACTS["eval_never_on_trainer_npu"]["data"]
        self.assertIn("ASI3", d["forbidden_boxes"])

    def test_ports_in_contracts_match_config(self):
        cp = contracts.CONTRACTS["box_ports_fixed"]["data"]["ports"]
        self.assertEqual(cp, get("box_ports"))


class TestDocsGenerated(unittest.TestCase):
    def test_all_lane_docs_match_generator_output(self):
        for lane_id in contracts.LANES:
            path = contracts.LANES_DIR / contracts.LANE_FILES[lane_id]
            self.assertTrue(path.exists(), f"missing doc: {path}")
            self.assertEqual(path.read_text(), contracts.render_lane_md(lane_id), f"stale: {path}")

    def test_docs_carry_generated_marker(self):
        text = (contracts.LANES_DIR / "evaluator.md").read_text()
        self.assertIn(contracts.GENERATED_MARKER, text)


class TestPy39Gate(unittest.TestCase):
    def test_check_flags_unsafe_zip(self):
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "bad.py"
            p.write_text("x = list(zip(a, b, strict=True))\n")
            ok, v = contracts.check_file(str(p))
        self.assertFalse(ok)
        self.assertTrue(any("strict=" in s for s in v))

    def test_check_passes_clean_file(self):
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "good.py"
            p.write_text("x = list(zip(a, b))\n")
            ok, v = contracts.check_file(str(p))
        self.assertTrue(ok)


class TestLintGate(unittest.TestCase):
    def test_repo_lint_is_clean(self):
        issues = lint_gate.run_all()
        self.assertEqual(issues, [], "lint_gate should be clean: " + "; ".join(issues[:5]))

    def test_scratch_is_gitignored(self):
        gi = (REPO / ".gitignore").read_text()
        self.assertIn("scratch/", gi)


if __name__ == "__main__":
    unittest.main()
