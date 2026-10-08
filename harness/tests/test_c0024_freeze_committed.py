"""C-0024 RED tests: the freeze must be DURABLE, not just wired.

The leg-start sha gate (asi2_eval_freeze_gate) and the verdict-side pins
(C-0031) are dead letters if the canonical manifest or any freeze-covered
path is uncommitted: a fresh checkout (or a box sync) silently loses or
diverges the freeze, which is exactly the drift this card was filed on
(manifest pinned a scorer version that existed only as uncommitted bytes
and is now unrecoverable).

Pinned contract:
  - verify_holdout_freeze PASSES against the real repo tree (manifest
    and disk agree on every covered sha), and
  - every freeze-covered path, the manifest itself, holdout_freeze.py,
    the launcher, and this gate's own test files are git-TRACKED and
    have no unstaged diff (unpinned+uncommitted fails).
"""

import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from evals.runner.holdout_freeze import (  # noqa: E402
    MANIFEST_RELPATH,
    required_paths,
    verify_holdout_freeze,
)

# Files that carry the freeze itself (gate wiring + verifier + tests).
FREEZE_INFRA = (
    MANIFEST_RELPATH,
    "evals/runner/holdout_freeze.py",
    "scripts/asi2_loop_eval.sh",
    "harness/tests/test_eval_launcher_freeze_gate.py",
    "harness/tests/test_c0024_freeze_committed.py",
)


def _git(*args):
    return subprocess.run(["git", "-C", ROOT] + list(args), capture_output=True, text=True)


class TestC0024FreezeIsDurable(unittest.TestCase):
    def test_verify_holdout_freeze_passes_on_real_tree(self):
        # verify_holdout_freeze RAISES HoldoutFreezeError on any drift and
        # returns the verified entries on success -- it never returns a bool.
        entries = verify_holdout_freeze(ROOT, os.path.join(ROOT, MANIFEST_RELPATH))
        self.assertGreaterEqual(len(entries), 41)

    def test_every_freeze_path_is_tracked_and_clean(self):
        covered = list(required_paths()) + list(FREEZE_INFRA)
        status = _git("status", "--porcelain", "--").stdout.splitlines()
        dirty = {}
        for line in status:
            code, path = line[:2], line[3:].strip()
            for rel in covered:
                if path == rel or path.startswith(rel.rstrip("/") + "/"):
                    dirty.setdefault(rel, code)
        self.assertEqual(dirty, {}, f"freeze paths unpinned/uncommitted: {dirty!r}")


if __name__ == "__main__":
    unittest.main()
