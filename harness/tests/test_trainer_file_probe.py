"""C-0074: the trainer probe WITHOUT an exec transport (TDD RED first).

File evidence only: the live run dir is resolved from outputs/ (newest mtime,
at read time), the step ladder comes from eval_results.jsonl's `step` field
(the train log is a buffering artifact — B-222), and liveness comes from
/proc stat state when the host has it, else file freshness. Never bare
UNKNOWN: step+age, or an explicit UNMEASURABLE reason.
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import resource_probes as RP  # noqa: E402


def _boom_health(port, timeout=6):
    raise OSError("connection refused")


class TestTrainerFileProbe(unittest.TestCase):
    NOW = 1_800_000_000

    @staticmethod
    def _row(step):
        # eval_results.jsonl row schema (training/grpo_trainer.py, v1)
        return {
            "schema_version": 1,
            "step": step,
            "index": 0,
            "passed": True,
            "details": [],
            "detail_budget": None,
            "code_hash": "x",
            "syntax": 1.0,
            "interface": 1.0,
            "verifier": 1.0,
            "brevity": 0.0,
            "import_hygiene": 1.0,
        }

    def _mk_run(self, root, name, steps, mtime):
        d = os.path.join(root, name)
        os.makedirs(d)
        p = os.path.join(d, "eval_results.jsonl")
        with open(p, "w") as f:
            for s in steps:
                f.write(json.dumps(self._row(s)) + chr(10))
        os.utime(p, (mtime, mtime))
        os.utime(d, (mtime, mtime))
        return d

    def _mk_proc(self, root, pid, run_dir, state, sub="proc"):
        proc = os.path.join(root, sub)
        pidd = os.path.join(proc, str(pid))
        os.makedirs(pidd)
        cmd = chr(0).join(["python3", "training/grpo_trainer.py", "--output-dir", run_dir])
        with open(os.path.join(pidd, "cmdline"), "w") as f:
            f.write(cmd)
        with open(os.path.join(pidd, "stat"), "w") as f:
            f.write(f"{pid} (grpo_trainer.py) {state} 1 1")
        return proc

    def test_file_probe_returns_step_and_liveness(self):
        # ACCEPTANCE 1: step number + liveness from a fixture run dir
        with tempfile.TemporaryDirectory() as tmp:
            self._mk_run(tmp, "run-a", [7, 8, 9], mtime=self.NOW - 60)
            p = RP.probe_trainer_files(tmp, now=self.NOW)
            self.assertEqual(p["status"], "ready")
            self.assertEqual(p["step"], 9)  # LAST row is the ladder head
            self.assertEqual(p["age_s"], 60)
            self.assertEqual(p["liveness"]["term"], "eval_results_age")
            self.assertIn("step=9", p["summary"])
            self.assertIn("age=60s", p["summary"])
            self.assertNotIn("dead", json.dumps(p).lower())

    def test_resolves_newest_run_dir_at_read_time(self):
        # ACCEPTANCE 2: live run dir resolved from outputs/ newest mtime AT
        # READ TIME -- never hardcoded, never cached across calls.
        with tempfile.TemporaryDirectory() as tmp:
            self._mk_run(tmp, "run-old", [3], mtime=self.NOW - 6000)
            self.assertEqual(RP.probe_trainer_files(tmp, now=self.NOW)["step"], 3)
            # a NEWER run dir appears AFTER the first probe: the next read
            # must follow it (a cached path would still report step=3)
            self._mk_run(tmp, "run-new", [11], mtime=self.NOW - 60)
            # and a newer top-level FILE must not win: run dirs only
            vf = os.path.join(tmp, "verdict_step.json")
            with open(vf, "w") as f:
                f.write("{}")
            os.utime(vf, (self.NOW, self.NOW))
            p = RP.probe_trainer_files(tmp, now=self.NOW)
            self.assertEqual(p["step"], 11)
            self.assertIn("run-new", p["run_dir"])

    def test_no_evidence_is_unmeasurable_not_bare_unknown(self):
        with tempfile.TemporaryDirectory() as tmp:
            outs = os.path.join(tmp, "outputs")
            os.makedirs(outs)
            p = RP.probe_trainer_files(outs, now=self.NOW)
            self.assertEqual(p["status"], "unknown")
            self.assertIn("UNMEASURABLE", p["summary"])

    def test_runall_without_exec_uses_file_probe(self):
        # ACCEPTANCE 3: run_all with trainer_exec=None must land a trainer
        # row that carries step+age, never the bare "needs exec_fn" UNKNOWN.
        with tempfile.TemporaryDirectory() as tmp:
            state = os.path.join(tmp, "state")
            outs = os.path.join(tmp, "outputs")
            os.makedirs(state)
            self._mk_run(outs, "run-x", [5], mtime=self.NOW - 30)
            payloads = RP.run_all(
                state,
                health_fn=_boom_health,
                trainer_exec=None,
                now=self.NOW,
                outputs_dir=outs,
            )
            t = payloads["trainer"]
            self.assertIn("step=5", t["summary"])
            self.assertNotIn("no exec transport", t["summary"])
            rec = json.load(open(os.path.join(state, "probes", "trainer.json")))
            self.assertIn("step=5", rec["summary"])

    def test_proc_liveness_term_when_proc_available(self):
        # /proc stat state is the stronger liveness term when the host has it
        with tempfile.TemporaryDirectory() as tmp:
            outs = os.path.join(tmp, "outputs")
            run = self._mk_run(outs, "run-p", [4], mtime=self.NOW - 60)
            proc = self._mk_proc(tmp, 4242, run, "R")
            p = RP.probe_trainer_files(outs, now=self.NOW, proc_root=proc)
            self.assertEqual(p["status"], "ready")
            self.assertEqual(p["liveness"]["term"], "proc_pid")
            self.assertEqual(p["liveness"]["pid"], 4242)
            # a zombie (state Z) is NOT a positive liveness term
            # own proc root: the scan prefers a LIVE match over a zombie,
            # so 4242 above must not shadow this zombie-only tree
            proc2 = self._mk_proc(tmp, 4243, run, "Z", sub="proc-zombie-only")
            p2 = RP.probe_trainer_files(outs, now=self.NOW, proc_root=proc2)
            self.assertEqual(p2["status"], "unknown")
            self.assertEqual(p2["liveness"]["term"], "proc_pid")
            self.assertEqual(p2["liveness"]["state"], "Z")
            self.assertIn("zombie", p2["summary"].lower())
            self.assertIn("step=4", p2["summary"])  # still carries step+age


if __name__ == "__main__":
    unittest.main()


class TestExecFailureFallback(unittest.TestCase):
    """C-0074 acceptance 3: with an exec transport configured but DEAD (or
    empty -- B-263 measured /exec wedges while training is alive), run_all
    must still land a trainer row carrying step+age from file evidence --
    never "exec transport died" with no measurement."""

    NOW = 1_800_000_000

    def _mk_run(self, root, name, steps, mtime):
        d = os.path.join(root, name)
        os.makedirs(d)
        p = os.path.join(d, "eval_results.jsonl")
        with open(p, "w") as f:
            for s in steps:
                f.write(json.dumps(dict(step=s)) + chr(10))
        os.utime(p, (mtime, mtime))
        os.utime(d, (mtime, mtime))
        return d

    def test_runall_exec_death_falls_back_to_file_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = os.path.join(tmp, "state")
            outs = os.path.join(tmp, "outputs")
            os.makedirs(state)
            self._mk_run(outs, "run-fb", [12], mtime=self.NOW - 45)

            def _boom_exec(port, cmd):
                raise OSError("connection refused")

            payloads = RP.run_all(
                state,
                health_fn=_boom_health,
                trainer_exec=_boom_exec,
                now=self.NOW,
                outputs_dir=outs,
            )
            t = payloads["trainer"]
            self.assertEqual(t["status"], "ready")
            self.assertIn("step=12", t["summary"])
            self.assertNotIn("exec transport died", t["summary"])

    def test_runall_empty_ps_falls_back_to_file_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = os.path.join(tmp, "state")
            outs = os.path.join(tmp, "outputs")
            os.makedirs(state)
            self._mk_run(outs, "run-fb2", [13], mtime=self.NOW - 45)
            payloads = RP.run_all(
                state,
                health_fn=_boom_health,
                trainer_exec=lambda port, cmd: "   ",
                now=self.NOW,
                outputs_dir=outs,
            )
            self.assertIn("step=13", payloads["trainer"]["summary"])


class TestTickWiring(unittest.TestCase):
    """C-0074 acceptance 3: the standup trainer row must be refreshed from
    live file evidence at render time -- qgh exposes refresh_trainer_probe()
    and tick/standup call it, so probes/trainer.json never goes stale just
    because no probe agent ran."""

    NOW = 1_800_000_000

    def _mk_run(self, root, name, steps, mtime):
        d = os.path.join(root, name)
        os.makedirs(d)
        p = os.path.join(d, "eval_results.jsonl")
        with open(p, "w") as f:
            for s in steps:
                f.write(json.dumps(dict(step=s)) + chr(10))
        os.utime(p, (mtime, mtime))
        os.utime(d, (mtime, mtime))
        return d

    def _import_qgh(self):
        harness_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if harness_dir not in sys.path:
            sys.path.insert(0, harness_dir)
        os.environ.setdefault("QGH_STATE_DIR", tempfile.mkdtemp())
        import qgh

        return qgh

    def test_refresh_trainer_probe_writes_fresh_record(self):
        qgh = self._import_qgh()
        with tempfile.TemporaryDirectory() as tmp:
            state = os.path.join(tmp, "state")
            outs = os.path.join(tmp, "outputs")
            os.makedirs(state)
            self._mk_run(outs, "run-t", [21], mtime=self.NOW - 15)
            p = qgh.refresh_trainer_probe(state_dir=state, outputs_dir=outs)
            self.assertIn("step=21", p["summary"])
            rec = json.load(open(os.path.join(state, "probes", "trainer.json")))
            self.assertIn("step=21", rec["summary"])
            # the record ts must be render-fresh (age_min-parseable now_iso),
            # never an epoch float -- else _probe_results marks it STALE
            import harness_lib

            age = harness_lib.age_min(rec["ts"])
            self.assertIsNotNone(age)
            self.assertLessEqual(age, 1.0)

    def test_refresh_survives_missing_outputs(self):
        qgh = self._import_qgh()
        with tempfile.TemporaryDirectory() as tmp:
            state = os.path.join(tmp, "state")
            os.makedirs(state)
            p = qgh.refresh_trainer_probe(state_dir=state, outputs_dir=os.path.join(tmp, "nope"))
            self.assertEqual(p["status"], "unknown")
            self.assertIn("UNMEASURABLE", p["summary"])


class TestStubRunQuarantine(unittest.TestCase):
    """C-9019: a placeholder run scaffold must read STUB, never UNMEASURABLE.

    outputs/grpo-v1 shipped launch_config.json model_name=SomeOrg/some-model
    device=cpu (the trainer argparse defaults -- a dead dry-run scaffold,
    no eval_results.jsonl). As the newest dir it made probe_trainer_files
    report UNMEASURABLE, masking whatever the real run dirs carry.
    """

    NOW = 1_800_000_000

    def _mk_stub(self, root, name, mtime, model_name="SomeOrg/some-model", device="cpu"):
        d = os.path.join(root, name)
        os.makedirs(d)
        cfg = dict(model_name=model_name, device=device, output_dir=root)
        with open(os.path.join(d, "launch_config.json"), "w") as f:
            json.dump(cfg, f)
        os.utime(d, (mtime, mtime))
        return d

    def _mk_run(self, root, name, steps, mtime):
        d = os.path.join(root, name)
        os.makedirs(d)
        p = os.path.join(d, "eval_results.jsonl")
        with open(p, "w") as f:
            for s in steps:
                f.write(json.dumps(dict(step=s)) + chr(10))
        os.utime(p, (mtime, mtime))
        os.utime(d, (mtime, mtime))
        return d

    def test_placeholder_scaffold_reports_stub_not_unmeasurable(self):
        # ACCEPTANCE: probe against a stub launch_config (placeholder
        # model_name, device=cpu) reports STUB -- the fail-closed instrument
        # must not key on placeholder configs.
        with tempfile.TemporaryDirectory() as tmp:
            self._mk_stub(tmp, "grpo-v1", mtime=self.NOW - 60)
            p = RP.probe_trainer_files(tmp, now=self.NOW)
            self.assertIn("STUB", p["summary"])
            self.assertNotIn("UNMEASURABLE", p["summary"])
            # still fail-closed: a stub is NOT positive liveness evidence
            self.assertNotEqual(p["status"], "ready")

    def test_device_not_npu_is_stub_signature(self):
        # the signature has two legs; device!=npu alone must quarantine too
        with tempfile.TemporaryDirectory() as tmp:
            self._mk_stub(
                tmp,
                "grpo-v2",
                mtime=self.NOW - 60,
                model_name="Qwen/Qwen3.8-27B",
                device="cpu",
            )
            p = RP.probe_trainer_files(tmp, now=self.NOW)
            self.assertIn("STUB", p["summary"])
            self.assertNotIn("UNMEASURABLE", p["summary"])

    def test_probe_skips_stub_and_reports_real_run(self):
        # the goal edge: the stub must not MASK the real run. Stub newest ->
        # the probe falls back to the newest non-stub dir real evidence.
        with tempfile.TemporaryDirectory() as tmp:
            self._mk_run(tmp, "run-real", [11, 12], mtime=self.NOW - 6000)
            self._mk_stub(tmp, "grpo-v1", mtime=self.NOW - 60)  # newest
            p = RP.probe_trainer_files(tmp, now=self.NOW)
            self.assertIn("step=12", p["summary"])
            self.assertIn("run-real", p["run_dir"])
            self.assertIn("grpo-v1", p["summary"])  # the skip is disclosed
            self.assertNotIn("UNMEASURABLE", p["summary"])

    def test_no_config_dirs_are_never_stubs(self):
        # box-synced run dirs carry no launch_config.json -- existing behavior
        # (UNMEASURABLE for a bare dir) must be unchanged.
        with tempfile.TemporaryDirectory() as tmp:
            d = os.path.join(tmp, "run-bare")
            os.makedirs(d)
            p = RP.probe_trainer_files(tmp, now=self.NOW)
            self.assertIn("UNMEASURABLE", p["summary"])
            self.assertNotIn("STUB", p["summary"])
