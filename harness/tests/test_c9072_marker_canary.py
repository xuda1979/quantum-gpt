#!/usr/bin/env python3
"""C-9072: box-side adapter-apply marker-chain canary -- verdict family.

Canary PASS requires ALL of (fail-closed, never fabricated):
  - both markers observed in the canary leg log:
      "adapter-applied" AND "adapter-probe-differs"
  - the candidate probe outputs byte-differ from base probe outputs
Any missing marker or an identical probe -> canary FAIL naming the
broken link. The canary adapter is a tiny synthetic rank-1 LoRA delta,
never a candidate checkpoint. A banked PASS is the ONLY thing that
grants C-9009/C-9016 launch endorsement.
"""

import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import c9072_marker_canary as canary  # noqa: E402

APPLIED = "adapter-applied"
DIFFERS = "adapter-probe-differs"


def _leg_output(markers=True, same_probe=False):
    """A canned canary-leg exec output (what the box leg would print)."""
    log = ""
    if markers:
        log = APPLIED + "\n" + DIFFERS + "\n"
    base = canary.build_synthetic_lora_delta()["probe_base_hex"]
    cand = base if same_probe else canary.build_synthetic_lora_delta()["probe_cand_hex"]
    return json.dumps({"leg_log": log, "base_probe_hex": base, "cand_probe_hex": cand})


class TestEvaluateCanary:
    def test_pass_requires_both_markers_and_differing_probes(self):
        v = canary.evaluate_canary(APPLIED + "\n" + DIFFERS, b"\x01\x02", b"\x01\x03")
        assert v["verdict"] == "PASS"
        assert v["broken_link"] is None
        assert v["markers"] == {"adapter_applied": True, "adapter_probe_differs": True}
        assert v["byte_compare"]["differ"] is True

    def test_probe_identical_to_base_fails_with_named_link(self):
        v = canary.evaluate_canary(APPLIED + "\n" + DIFFERS, b"\x01\x02", b"\x01\x02")
        assert v["verdict"] == "FAIL"
        assert v["broken_link"] == "probe_identical_to_base"

    def test_missing_adapter_applied_marker_named(self):
        v = canary.evaluate_canary(DIFFERS, b"a", b"b")
        assert v["verdict"] == "FAIL"
        assert v["broken_link"] == "marker_adapter_applied_missing"

    def test_missing_probe_differs_marker_named(self):
        v = canary.evaluate_canary(APPLIED, b"a", b"b")
        assert v["verdict"] == "FAIL"
        assert v["broken_link"] == "marker_probe_differs_missing"

    def test_absent_evidence_fails_closed(self):
        for log in (None, ""):
            v = canary.evaluate_canary(log, b"a", b"b")
            assert v["verdict"] == "FAIL"
            assert v["broken_link"] == "leg_log_missing"
        v = canary.evaluate_canary(APPLIED + "\n" + DIFFERS, None, b"b")
        assert v["verdict"] == "FAIL"
        assert v["broken_link"] == "probe_output_missing"

    def test_exec_output_parse_and_evaluate(self):
        v = canary.evaluate_from_exec_output(_leg_output())
        assert v["verdict"] == "PASS"
        v = canary.evaluate_from_exec_output(_leg_output(same_probe=True))
        assert v["verdict"] == "FAIL"
        assert v["broken_link"] == "probe_identical_to_base"
        v = canary.evaluate_from_exec_output("Traceback (most recent call last):")
        assert v["verdict"] == "FAIL"
        assert v["broken_link"] == "leg_output_unparseable"

    def test_exec_output_80col_wrap_still_parses(self):
        # The box /exec response hard-wraps ~80 cols; the live leg observed
        # on ASI2 2026-09-18 came back folded across lines, which a strict
        # one-line parser reads as leg_output_unparseable (found-but-unfixed
        # by the prior worker session). RED until the parser tolerates it.
        raw = _leg_output()
        wrapped = "\n".join(raw[i : i + 80] for i in range(0, len(raw), 80))
        v = canary.evaluate_from_exec_output("banner line\n" + wrapped + "\n")
        assert v["verdict"] == "PASS", v
        raw_f = _leg_output(same_probe=True)
        wrapped_f = "\n".join(raw_f[i : i + 80] for i in range(0, len(raw_f), 80))
        v = canary.evaluate_from_exec_output(wrapped_f)
        assert v["verdict"] == "FAIL"
        assert v["broken_link"] == "probe_identical_to_base"


class TestSyntheticDelta:
    def test_delta_is_rank1_and_never_a_checkpoint(self):
        d = canary.build_synthetic_lora_delta()
        assert d["r"] == 1
        assert d["origin"] == "synthetic-canary"
        assert "checkpoint" not in d and "adapter_path" not in d
        # rank-1: B (out,1) x A (1,in) reconstructs a rank-1 matrix, nonzero
        b, a = d["B"], d["A"]
        delta = [[bi * aj for aj in a[0]] for bi in [row[0] for row in b]]
        assert any(x != 0 for row in delta for x in row)

    def test_leg_script_is_stdlib_only_and_produces_marked_differing_probes(self):
        cmd = canary.compose_leg_command("/usr/bin/python3")
        assert cmd.startswith("/usr/bin/python3")
        script = cmd.split("-c", 1)[1].strip().strip("'\"")
        out = subprocess.run(
            [sys.executable, "-c", script], capture_output=True, text=True, timeout=60
        )
        assert out.returncode == 0, out.stderr
        v = canary.evaluate_from_exec_output(out.stdout)
        assert v["verdict"] == "PASS", v


class TestBankingAndEndorsement:
    def test_endorsement_withheld_without_banked_pass(self, tmp_path):
        ok, why = canary.launch_endorsement(str(tmp_path))
        assert ok is False and why == "no_banked_verdict"
        canary.write_verdict(canary.evaluate_canary(APPLIED, b"a", b"b"), str(tmp_path))
        ok, why = canary.launch_endorsement(str(tmp_path))
        assert ok is False and "probe" in why  # FAIL names the broken link

    def test_endorsement_granted_on_banked_pass(self, tmp_path):
        canary.write_verdict(
            canary.evaluate_canary(APPLIED + "\n" + DIFFERS, b"a", b"b"), str(tmp_path)
        )
        ok, why = canary.launch_endorsement(str(tmp_path))
        assert ok is True and why == "banked_pass"


class TestRealTreePaths:
    """C-9072 follow-up: the relpaths must be anchored at the repo root
    WITH the harness/ segment (harness/state/...), matching the canonical
    layout every other harness module reads/writes (asi2_window_preflight_
    gate writes harness/state/preflights; harness_lib:425 documents
    harness/state/locks/asi2-eval.lock). Repo-root-relative paths without
    the prefix point at phantom dirs and the canary could never run."""

    def test_relpaths_anchored_under_harness_state(self):
        h = os.path.join("harness", "state")
        assert canary.POSITIVE_CONTROL_RELPATH.startswith(h)
        assert canary.VERDICT_RELPATH.startswith(h)
        assert canary.LOCK_RELPATH.startswith(h)
        assert canary.LOCK_RELPATH.endswith(os.path.join("locks", "asi2-eval.lock"))

    def test_real_tree_positive_control_resolves(self):
        # Provisioning precondition on this tree (C-9066/C-9097 artifact):
        # the joined path must be the REAL artifact, not a phantom path.
        p = os.path.join(canary.ROOT, canary.POSITIVE_CONTROL_RELPATH)
        assert os.path.exists(p), "positive control phantom path: " + p
        paths, why = canary.resolve_interpreters(canary.ROOT)
        assert why is None, why
        assert paths and paths[0].endswith("python3")


class TestInterpretersAndDispatch:
    def _artifact(self, tmp_path, ok=True, interp=True):
        d = {
            "artifact": "sdk_positive_control",
            "ok": ok,
            "utc": "2026-09-19T05:34:37Z",
        }
        if interp:
            d["interpreters"] = [
                {
                    "path": "/usr/local/python3.11.14/bin/python3",
                    "qiskit": True,
                    "pennylane": True,
                    "cirq": True,
                    "control_rc": 0,
                }
            ]
        pd = (tmp_path / canary.POSITIVE_CONTROL_RELPATH).parent
        pd.mkdir(parents=True, exist_ok=True)
        (tmp_path / canary.POSITIVE_CONTROL_RELPATH).write_text(json.dumps(d))
        return tmp_path

    def test_resolve_uses_c9066_provisioned_interpreter(self, tmp_path):
        root = self._artifact(tmp_path)
        paths, why = canary.resolve_interpreters(str(root))
        assert why is None
        assert paths == ["/usr/local/python3.11.14/bin/python3"]

    def test_resolve_fails_closed_when_unprovisioned(self, tmp_path):
        root = self._artifact(tmp_path, ok=False, interp=False)
        paths, why = canary.resolve_interpreters(str(root))
        assert paths == [] and why == "interpreters_unprovisioned"
        paths, why = canary.resolve_interpreters(str(tmp_path / "nope"))
        assert paths == [] and why == "positive_control_missing"

    def test_run_yields_to_live_window_never_steals_lock(self, tmp_path):
        root = self._artifact(tmp_path)
        lock = tmp_path / canary.LOCK_RELPATH
        os.makedirs(lock.parent)
        lock.write_text(json.dumps({"pid": os.getpid(), "ts": "2099-01-01T00:00:00Z"}))
        called = []

        def fake_exec(cmd):
            called.append(cmd)
            return 0, _leg_output()

        v = canary.run_canary(root=str(root), box_exec=fake_exec, lock_ttl_s=1e9)
        assert v["verdict"] == "YIELDED"
        assert v["reason"] == "asi2_eval_lock_busy"
        assert called == []  # never dispatched around a live leg
        d = tmp_path / "state" / "canary" / "C-9072"
        assert not d.exists() or not list(d.glob("*.json"))

    def test_run_end_to_end_fail_closed_verdict_and_lock_released(self, tmp_path):
        root = self._artifact(tmp_path)
        lock = tmp_path / canary.LOCK_RELPATH

        def fake_exec(cmd):
            return 0, _leg_output(same_probe=True)  # box returns identical probes

        v = canary.run_canary(root=str(root), box_exec=fake_exec, lock_ttl_s=1e9)
        assert v["verdict"] == "FAIL"
        assert v["broken_link"] == "probe_identical_to_base"
        assert not lock.exists()  # released after dispatch completed
        banked = tmp_path / canary.VERDICT_RELPATH
        assert json.loads(banked.read_text())["verdict"] == "FAIL"
        ok, why = canary.launch_endorsement(str(tmp_path))
        assert ok is False  # C-9009/C-9016 stay withheld

    def test_run_without_box_channel_fails_closed_never_fabricates(self, tmp_path):
        root = self._artifact(tmp_path)
        v = canary.run_canary(root=str(root), box_exec=None, lock_ttl_s=1e9)
        assert v["verdict"] == "FAIL"
        assert v["broken_link"] == "box_channel_unavailable"
