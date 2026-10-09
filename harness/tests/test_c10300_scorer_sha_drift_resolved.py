"""C-10300: scorer SHA drift resolution — box runner 2ad0d562 == local pinned.

RED (measured 2026-10-09): ASI1/ASI2/ASI3 all execute
scripts/run_asi2_base_adapter_rubric_eval.py as 2ad0d562... while the banked pin
and the committed freeze manifest pin 4e123615... (C-10243 blocker: every
canonical 18-task eval leg fails scorer_sha_mismatch, so no fail-closed verdict
composes). The box runner is the C-9858 scorer (af5b71dc) + the C-10212
candidate_path bind — a strict, reviewed superset of the 4e123615 bytes.

Contract (deploy-integrity, re-bank after review): the LOCAL canonical
scorer (= what we re-bank and re-pin in the freeze manifest) must be
byte-identical to the box runner all three boxes execute, so a re-sync in
either direction converges. Until this card lands, the three files below
disagree with each other and with the box.
"""

from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

BOX_RUNNER_SHA256 = "2ad0d56265ca41bd5859d86d8b7f76cc5bfcef44b2461e7f381358f5a158a5da"
RUNNER_REL = "scripts/run_asi2_base_adapter_rubric_eval.py"
PIN_BANK_REL = "harness/state/scorer_sha_pins.json"
MANIFEST_REL = "evals/benchmarks/sapo_promotion_holdout_v1_18.sha256"


def _sha256(rel) -> str:
    data = (ROOT / rel).read_bytes()
    return hashlib.sha256(data).hexdigest()


def _manifest_pin(rel) -> str:
    for line in (ROOT / MANIFEST_REL).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        digest, path = line.split(None, 1)
        if path == rel:
            return digest
    raise AssertionError("manifest lacks " + rel)


class TestC10300ScorerShaDriftResolved(unittest.TestCase):
    def test_local_runner_is_identical_to_box_runner(self):
        """Deploy-integrity: the canonical runner we ship must hash to the
        exact bytes the three boxes execute (2ad0d562)."""
        self.assertEqual(_sha256(RUNNER_REL), BOX_RUNNER_SHA256)

    def test_freeze_manifest_pins_runner_to_box_sha(self):
        """The committed freeze manifest must agree with the executed bytes;
        drift between manifest and box is the C-10243 blocker signature."""
        self.assertEqual(_manifest_pin(RUNNER_REL), BOX_RUNNER_SHA256)

    def test_pin_bank_runner_matches_manifest_and_box(self):
        """The C-9131 bank must be re-banked to the manifest so verdicts
        stamped from the bank match the executed scorer."""
        bank = json.loads((ROOT / PIN_BANK_REL).read_text())
        banked_runner = bank["scorer_shas"][RUNNER_REL]
        self.assertEqual(banked_runner, _manifest_pin(RUNNER_REL))
        self.assertEqual(banked_runner, BOX_RUNNER_SHA256)


if __name__ == "__main__":
    unittest.main()
