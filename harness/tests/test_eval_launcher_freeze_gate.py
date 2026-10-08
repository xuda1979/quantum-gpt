"""C-0048 (finishing bounced C-0028) RED tests: the canonical eval-leg
launcher must enforce the freeze-integrity sha gate at the asi2-eval.lock
site -- BEFORE the leg is fired, and stamp the verified manifest shas into
the leg log on a clean tree.

C-0024 landed verify_holdout_freeze and the box-side driver calls it, but
the canonical launcher (scripts/asi2_loop_eval.sh -- the path that takes
the asi2-eval lease and fires the leg) had NO launch-side gate: a leg fired
against a drifted holdout/scorer burns the serialized box leg and a
multi-hour poll window before anything rejects it. Launch-side must refuse.

The gate is driven against a THROWAWAY repo tree: verify_holdout_freeze
takes repo_root/manifest_path, so no real freeze-covered file is ever
tampered here (the C-0028 driver test tampers the real tree under a lock;
this suite does not need to).

Pinned contract:
  - asi2_eval_freeze_gate is defined BEFORE the SAPO_EVAL_LIB_ONLY seam
    (testable with no box probe), fails CLOSED on any drift/missing file,
    and NAMES the violation (FREEZE DRIFT + drifted file + both digests)
  - a clean manifest passes and stamps one `freeze sha <digest> <rel>`
    line per covered file into the launcher log (stderr) -- the leg log
    then proves WHICH bytes the leg ran under
  - the MAIN FLOW calls the gate after taking the asi2-eval lease and
    BEFORE dispatching the leg, fail-closed (`if ! gate ... exit`), so a
    refusal releases the lease via the EXIT trap and never fires
    (line-ordered exactly as C-0036 pinned the lease wiring)
"""

import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LAUNCHER = os.path.join(ROOT, "scripts", "asi2_loop_eval.sh")
sys.path.insert(0, ROOT)
from evals.runner.holdout_freeze import (  # noqa: E402
    MANIFEST_RELPATH,
    compute_manifest,
    required_paths,
)


def _build_tree(root):
    """Throwaway repo tree with a tiny file at every freeze-covered path,
    plus a self-consistent manifest computed from it. Returns the covered
    relpaths (the test manifest covers exactly required_paths())."""
    root = Path(root)
    rels = required_paths()
    for rel in rels:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(("frozen:" + rel + "\n").encode("utf-8"))
    entries = compute_manifest(str(root))
    mpath = root / MANIFEST_RELPATH
    mpath.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# C-0048 test manifest"] + [f"{sha}  {rel}" for rel, sha in entries]
    mpath.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return rels, mpath


def _bash_freeze(body, tree, timeout=60):
    """Run BODY in bash with the launcher sourced via its test seam and the
    freeze gate pointed at the throwaway tree."""
    script = (
        "set -euo pipefail\n"
        "export SAPO_EVAL_LIB_ONLY=1\n"
        f'source "{LAUNCHER}"\n'
        f'export FREEZE_REPO_ROOT="{tree}"\n'
        f'export FREEZE_MANIFEST="{os.path.join(tree, MANIFEST_RELPATH)}"\n'
        "command -v asi2_eval_freeze_gate >/dev/null || { echo GATE_HELPER_MISSING; exit 7; }\n"
        f"{body}\n"
    )
    return subprocess.run(["bash", "-c", script], capture_output=True, text=True, timeout=timeout)


class TestFreezeGateBehavior(unittest.TestCase):
    """The gate helper itself, driven against a throwaway tree."""

    def test_tampered_holdout_refused_with_named_reason(self):
        with tempfile.TemporaryDirectory(prefix="qgh-c0048-") as d:
            _rels, _mpath = _build_tree(d)
            victim = "evals/tasks/quantum/qaoa_maxcut/task.json"
            p = Path(d) / victim
            p.write_bytes(p.read_bytes() + b"# tampered\n")
            proc = _bash_freeze(
                "if asi2_eval_freeze_gate; then echo UNEXPECTED_GATE_PASS; exit 6; fi\n"
                "echo REFUSED_AS_EXPECTED\n",
                d,
            )
            self.assertIn(
                "REFUSED_AS_EXPECTED",
                proc.stdout,
                f"gate must REFUSE a drifted holdout (stdout={proc.stdout} stderr={proc.stderr})",
            )
            self.assertNotIn("UNEXPECTED_GATE_PASS", proc.stdout)
            combined = proc.stdout + proc.stderr
            self.assertIn("FREEZE DRIFT", combined, "refusal must name the hash violation")
            self.assertIn(victim, combined, "refusal must name the drifted file")
            self.assertIn("manifest", combined, "refusal must show manifest vs disk digests")
            self.assertIn(
                "FREEZE_VIOLATION", combined, "refusal must be a named gate verdict, not a crash"
            )

    def test_missing_holdout_file_refused_fail_closed(self):
        with tempfile.TemporaryDirectory(prefix="qgh-c0048-") as d:
            rels, _mpath = _build_tree(d)
            victim = rels[5]
            os.unlink(os.path.join(d, victim))
            proc = _bash_freeze(
                "if asi2_eval_freeze_gate; then echo UNEXPECTED_GATE_PASS; exit 6; fi\n"
                "echo REFUSED_AS_EXPECTED\n",
                d,
            )
            self.assertIn("REFUSED_AS_EXPECTED", proc.stdout)
            combined = proc.stdout + proc.stderr
            self.assertIn(victim, combined, "refusal must name the missing covered file")

    def test_clean_manifest_passes_and_stamps_shas_into_leg_log(self):
        with tempfile.TemporaryDirectory(prefix="qgh-c0048-") as d:
            rels, _mpath = _build_tree(d)
            bench = "evals/benchmarks/sapo_promotion_holdout_v1_18.txt"
            want = hashlib.sha256((Path(d) / bench).read_bytes()).hexdigest()
            proc = _bash_freeze(
                "asi2_eval_freeze_gate || { echo GATE_REFUSED; exit 6; }\n",
                d,
            )
            self.assertEqual(
                proc.returncode,
                0,
                f"clean tree must PASS the gate: stdout={proc.stdout} stderr={proc.stderr}",
            )
            stamp = f"freeze sha {want} {bench}"
            self.assertIn(
                stamp,
                proc.stderr,
                "the leg log (stderr) must carry the verified sha of every covered file",
            )
            stamped = [ln for ln in proc.stderr.splitlines() if "freeze sha " in ln]
            self.assertEqual(
                len(stamped),
                len(rels),
                f"one stamp per covered file (got {len(stamped)} want {len(rels)}): {stamped[:3]}",
            )


class TestMainFlowGateWiring(unittest.TestCase):
    """The gate must run in the MAIN FLOW, after the lease is taken and
    before the leg is dispatched (line-ordered, so deleting the call or
    moving it after the dispatch turns this RED)."""

    def test_main_flow_orders_gate_between_lease_and_dispatch(self):
        with open(LAUNCHER, encoding="utf-8") as f:
            lines = f.read().splitlines()
        seam = next(i for i, ln in enumerate(lines) if "SAPO_EVAL_LIB_ONLY" in ln and ":-0" in ln)
        defn = next(i for i, ln in enumerate(lines) if ln.startswith("asi2_eval_freeze_gate()"))
        self.assertLess(
            defn,
            seam,
            f"gate helper must be defined BEFORE the test seam (defn L{defn + 1}, seam L{seam + 1})",
        )
        dispatch = next(
            i
            for i, ln in enumerate(lines)
            if i > seam and "nohup python3 scripts/run_asi2_base_adapter_rubric_eval.py" in ln
        )
        acquire = next(
            i
            for i, ln in enumerate(lines)
            if i > seam and "asi2_eval_lock_acquire" in ln and not ln.strip().startswith("#")
        )
        gate = [
            i
            for i, ln in enumerate(lines)
            if i > seam and "asi2_eval_freeze_gate" in ln and not ln.strip().startswith("#")
        ]
        self.assertTrue(
            any(acquire < g < dispatch for g in gate),
            f"main flow must run the freeze gate AFTER the lease (L{acquire + 1}) and BEFORE "
            f"the dispatch (L{dispatch + 1}); gate calls: {[g + 1 for g in gate]}",
        )
        g = next(i for i in gate if acquire < i < dispatch)
        self.assertTrue(
            lines[g].lstrip().startswith("if !"),
            "the gate call must be fail-closed (`if ! asi2_eval_freeze_gate`), got: " + lines[g],
        )
        window = " ".join(lines[g : g + 4])
        self.assertIn(
            "exit",
            window,
            "a gate refusal must EXIT the launcher (no dispatch), window: " + window,
        )


if __name__ == "__main__":
    unittest.main()
