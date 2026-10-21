"""Card C-10558: card-compose lint gate - scorer / holdout-manifest / beats_base
must NOT diverge from the C-9131 scorer pin bank.

WHY: the working tree matched the bank pins (single_candidate_eval 21b80d0,
holdout bench b40ca7f, beats_base d83f03b) but all three pin-state files were
uncommitted; a fresh-checkout or rebased leg bounces sha_pin_violation and
blocks all banking. The pin-bank lint gate is the fail-closed tripwire at
card-compose / CI.

CONTRACT:
  1. lint_gate.lint_scorer_pins() returns [] when every pinned scorer file,
     the holdout bench, and the canonical freeze manifest agree with the
     C-9131 bank (harness/state/scorer_sha_pins.json).
  2. It reports a named `scorer-pin-drift:` issue for ANY pinned scorer file
     whose on-disk sha differs from the bank, or the manifest pin differs,
     or the bench file drifted.
  3. Missing bank / missing pinned file / missing manifest each fail closed
     with a named issue (never a silent pass).
  4. run_all() includes lint_scorer_pins() so the CLI gate enforces it.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "harness"))
sys.path.insert(0, str(REPO / "harness" / "scripts"))

import lint_gate  # noqa: E402
from evals.runner import holdout_freeze as fz  # noqa: E402

BANK_REL = "harness/state/scorer_sha_pins.json"
MANIFEST_REL = fz.MANIFEST_RELPATH
BENCH_REL = fz.BENCH_RELPATH


def _sha(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _make_repo(root: Path, seq=("x",)) -> dict:
    """Minimal repo with a consistent bank+manifest+scorers+bench."""
    killer = {}
    for rel, content in [
        (fz.SCORER_CHAIN[0], b"scorer-eval-" + seq[0].encode()),
        (fz.SCORER_CHAIN[1], b"scorer-runner-" + seq[0].encode()),
        (fz.SCORER_CHAIN[2], b"scorer-sanitize-" + seq[0].encode()),
        (fz.SCORER_CHAIN[3], b"scorer-beats-" + seq[0].encode()),
        (BENCH_REL, b"holdout-bench-" + seq[0].encode()),
    ]:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(content)
        killer[rel] = _sha(content)
    bank = {
        "card": "C-9131",
        "holdout_sha256": killer[BENCH_REL],
        "scorer_shas": {rel: killer[rel] for rel in fz.SCORER_CHAIN},
    }
    (root / BANK_REL).parent.mkdir(parents=True, exist_ok=True)
    (root / BANK_REL).write_text(json.dumps(bank), encoding="utf-8")
    lines = ["# fixture manifest", f"{killer[BENCH_REL]}  {BENCH_REL}"]
    for rel in fz.SCORER_CHAIN:
        lines.append(f"{killer[rel]}  {rel}")
    (root / MANIFEST_REL).parent.mkdir(parents=True, exist_ok=True)
    (root / MANIFEST_REL).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return bank


class TestScorerPinLintGate(unittest.TestCase):
    def test_lint_scorer_pins_function_exists(self):
        self.assertTrue(
            hasattr(lint_gate, "lint_scorer_pins"),
            "lint_gate must expose lint_scorer_pins() (C-10558)",
        )

    def test_clean_repo_no_issues(self):
        root = Path(self._test_str())
        root.mkdir(parents=True, exist_ok=True)
        _make_repo(root)
        try:
            issues = lint_gate.lint_scorer_pins(repo_root=root)
            self.assertEqual(issues, [])
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def _test_str(self):
        import time
        return os.path.join("/tmp", self._testMethodName)

    def test_drifted_scorer_file_fails_closed(self):
        root = Path(self._test_str() + "_d")
        root.mkdir(parents=True, exist_ok=True)
        _make_repo(root)
        try:
            drifted = fz.SCORER_CHAIN[0]
            (root / drifted).write_bytes(b"DRIFTED")
            issues = lint_gate.lint_scorer_pins(repo_root=root)
            self.assertTrue(issues, "drifted scorer must produce lint issues")
            self.assertTrue(
                any(i.startswith("scorer-pin-drift:") and drifted in i for i in issues),
                "got: %r" % issues,
            )
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_missing_bank_fails_closed(self):
        root = Path(self._test_str() + "_m")
        root.mkdir(parents=True, exist_ok=True)
        _make_repo(root)
        try:
            (root / BANK_REL).unlink()
            issues = lint_gate.lint_scorer_pins(repo_root=root)
            self.assertTrue(issues, "missing bank must fail closed")
            self.assertTrue(any("scorer-pin-drift" in i for i in issues), "got: %r" % issues)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_run_all_includes_scorer_pins(self):
        run_all = lint_gate.run_all
        self.assertTrue(hasattr(lint_gate, "run_all"))
        # the CLI gate must actually call lint_scorer_pins; a clean repo
        # returning [] does not prove inclusion, so assert by source wiring
        import inspect
        src = inspect.getsource(run_all)
        self.assertIn("lint_scorer_pins", src)


if __name__ == "__main__":
    unittest.main()
