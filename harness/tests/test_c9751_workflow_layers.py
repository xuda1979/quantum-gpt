"""Card C-9751: workflow-instructions as REPO ARTIFACTS, three layers.

Layer 1: harness/workflow_spec.json — machine-parseable stage spec that a
fresh session loads (CLAUDE.md/WORKFLOW.md point to it); no conversation
memory required.
Layer 2: harness/scripts/workflow_gate.py — executable stage gate: a stage
MUST have its predecessor's ATT (attestation file) present+valid or the
gate REFUSES (fail-closed). Wired into the real launch path so a failing
training stage can NEVER trigger the next expensive stage.
Layer 3: harness/scripts/workflow_audit.py — independent re-verification:
re-computes the predecessor outcome from PRIMARY evidence, not from the
attestation's self-claim.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_HARNESS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _HARNESS_DIR.parent.parent
sys.path.insert(0, str(_HARNESS_DIR))
sys.path.insert(0, str(_REPO_ROOT))

SPEC = _REPO_ROOT / "harness" / "workflow_spec.json"
GATE = _REPO_ROOT / "harness" / "scripts" / "workflow_gate.py"
AUDIT = _REPO_ROOT / "harness" / "scripts" / "workflow_audit.py"
CLAUDE_MD = _REPO_ROOT / "CLAUDE.md"


class TestLayer1Spec(unittest.TestCase):
    def test_spec_exists_and_is_loadable(self):
        d = json.loads(SPEC.read_text())
        self.assertIn("stages", d)
        # the canonical quantum-LLM workflow stages, in order
        ids = [s["id"] for s in d["stages"]]
        for expected in ("train", "eval_leg", "compose_verdict"):
            self.assertIn(expected, ids)
        # each stage: id, requires (predecessor att), cmd (the executable check), blocking_on_fail
        for s in d["stages"]:
            self.assertIn("id", s)
            self.assertIn("requires", s)
            self.assertIn("cmd", s)
            self.assertEqual(s.get("blocking_on_fail"), True)

    def test_fresh_session_docs_point_at_spec(self):
        self.assertTrue(CLAUDE_MD.exists(), "CLAUDE.md must exist at repo root")
        txt = CLAUDE_MD.read_text()
        self.assertIn("workflow_spec.json", txt,
                      "CLAUDE.md must point at the machine spec")
        self.assertIn("workflow_gate.py", txt,
                      "CLAUDE.md must point at the executable gate")


class TestLayer2Gate(unittest.TestCase):
    def _gate(self, *argv):
        p = subprocess.run(
            [sys.executable, str(GATE), *argv],
            capture_output=True, text=True, timeout=120,
            env={**os.environ, "PYTHONPATH": f"{_HARNESS_DIR}:{_REPO_ROOT}"},
        )
        return p.returncode, p.stdout, p.stderr

    def test_missing_attestation_blocks_stage(self):
        """A deliberately missing/failing predecessor attestation MUST make
        the gate exit non-zero (fail-closed): eval_leg cannot run."""
        with tempfile.TemporaryDirectory() as td:
            att_dir = Path(td) / "atts"
            rc, out, _ = self._gate(
                "check", "--stage", "eval_leg", "--att-dir", str(att_dir))
            self.assertNotEqual(rc, 0,
                                "gate must fail-closed when predecessor att missing")
            self.assertIn("BLOCKED", out)

    def test_bad_attestation_blocks_stage(self):
        """An attestation whose status is FAILED must block the successor."""
        with tempfile.TemporaryDirectory() as td:
            att_dir = Path(td) / "atts"
            att_dir.mkdir()
            (att_dir / "train.ATT.json").write_text(json.dumps({
                "stage": "train", "status": "FAILED",
                "evidence": {"trainer_pid": 1},
            }))
            rc, out, _ = self._gate(
                "check", "--stage", "eval_leg", "--att-dir", str(att_dir))
            self.assertNotEqual(rc, 0)
            self.assertIn("BLOCKED", out)

    def test_good_attestation_passes_stage(self):
        with tempfile.TemporaryDirectory() as td:
            att_dir = Path(td) / "atts"
            att_dir.mkdir()
            (att_dir / "train.ATT.json").write_text(json.dumps({
                "stage": "train", "status": "OK",
                "evidence": {"run_name": "x", "latest_step": 73},
            }))
            rc, out, _ = self._gate(
                "check", "--stage", "eval_leg", "--att-dir", str(att_dir))
            self.assertEqual(rc, 0, out + " gate should PASS with valid att")
            self.assertIn("GO", out)

    def test_attest_writes_attestation(self):
        with tempfile.TemporaryDirectory() as td:
            att_dir = Path(td) / "atts"
            rc, out, _ = self._gate(
                "attest", "--stage", "train", "--status", "OK",
                "--evidence", json.dumps({"run_name": "r1", "latest_step": 73}),
                "--att-dir", str(att_dir))
            self.assertEqual(rc, 0, out)
            d = json.loads((att_dir / "train.ATT.json").read_text())
            self.assertEqual(d["status"], "OK")

    def test_first_stage_needs_no_predecessor(self):
        """Stage with requires=[] must pass with empty att dir."""
        with tempfile.TemporaryDirectory() as td:
            rc, out, _ = self._gate(
                "check", "--stage", "train", "--att-dir", str(td))
            self.assertEqual(rc, 0, out)


class TestLayer3Audit(unittest.TestCase):
    def test_audit_recomputes_from_primary_evidence(self):
        """Audit must NOT trust the attestation: given an att claiming OK
        but primary evidence (resume_training.json boot.alive=false), the
        audit must FAIL it and mark the att REVOKED."""
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            att_dir = td / "atts"; att_dir.mkdir()
            (att_dir / "train.ATT.json").write_text(json.dumps({
                "stage": "train", "status": "OK",
                "evidence": {"resume_state": str(td / "resume_training.json")},
            }))
            # primary evidence says boot FAILED
            (td / "resume_training.json").write_text(json.dumps({
                "run_name": "r1",
                "boot": {"alive": False},
            }))
            p = subprocess.run(
                [sys.executable, str(AUDIT), "train",
                 "--att-dir", str(att_dir), "--state", str(td)],
                capture_output=True, text=True, timeout=120,
                env={**os.environ, "PYTHONPATH": f"{_HARNESS_DIR}:{_REPO_ROOT}"},
            )
            self.assertNotEqual(p.returncode, 0,
                                "audit must fail an att contradicted by primary evidence")
            d = json.loads((att_dir / "train.ATT.json").read_text())
            self.assertEqual(d.get("status"), "REVOKED")

    def test_audit_passes_consistent_att(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            att_dir = td / "atts"; att_dir.mkdir()
            (att_dir / "train.ATT.json").write_text(json.dumps({
                "stage": "train", "status": "OK",
                "evidence": {"resume_state": str(td / "resume_training.json")},
            }))
            (td / "resume_training.json").write_text(json.dumps({
                "run_name": "r1",
                "boot": {"alive": True, "pid": "42"},
            }))
            p = subprocess.run(
                [sys.executable, str(AUDIT), "train",
                 "--att-dir", str(att_dir), "--state", str(td)],
                capture_output=True, text=True, timeout=120,
                env={**os.environ, "PYTHONPATH": f"{_HARNESS_DIR}:{_REPO_ROOT}"},
            )
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)


if __name__ == "__main__":
    unittest.main()
