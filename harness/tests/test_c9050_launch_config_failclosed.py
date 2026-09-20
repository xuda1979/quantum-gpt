"""C-9050: fail-closed launch-config resolution for the real 27B training leg.

C-9004 (the 27B distillation training leg) bounced 3x and the only live
"grpo-v1" scaffold was a placeholder-model stub (C-9019: model_name
SomeOrg/some-model, device=cpu). Acceptance 1 demands a launch config that
resolves to the REAL Qwen3.8-27B model id end-to-end, with a fail-closed
refusal for placeholder model ids or an absent eval_results.jsonl contract
(the B-222 liveness instrument). These tests pin that resolver.
"""

import json
import os
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)

from harness.c9050_launch_config import (  # noqa: E402
    LaunchConfigError,
    eval_results_progress,
    launch_config_path,
    resolve_launch_config,
    resolve_launch_config_file,
)

REAL_27B = """/root/work/filestorage/Qwen3.8-27B"""


def _valid_config():
    return {
        "card": "C-9050",
        "model_name": REAL_27B,
        "device": "npu",
        "trainer": "training/grpo_trainer.py",
        "eval_results_filename": "eval_results.jsonl",
        "liveness_field": "step",
    }


class TestResolveRefuses:
    def test_placeholder_model_refused(self):
        cfg = _valid_config()
        cfg["model_name"] = "SomeOrg/some-model"
        with pytest.raises(LaunchConfigError) as ei:
            resolve_launch_config(cfg)
        assert "placeholder" in str(ei.value).lower()

    def test_stub_token_lowercase_refused(self):
        cfg = _valid_config()
        cfg["model_name"] = "someorg/some-model-27b"
        with pytest.raises(LaunchConfigError):
            resolve_launch_config(cfg)

    def test_stale_qwen36_family_refused(self):
        # the live stale value shipped in configs/rl/qwen36_27b_fv_gspo_asi2.json
        cfg = _valid_config()
        cfg["model_name"] = "/root/work/filestorage/Qwen3.6-27B"
        with pytest.raises(LaunchConfigError) as ei:
            resolve_launch_config(cfg)
        assert "Qwen3.8-27B" in str(ei.value)

    def test_missing_model_refused(self):
        cfg = _valid_config()
        del cfg["model_name"]
        with pytest.raises(LaunchConfigError):
            resolve_launch_config(cfg)

    def test_device_not_npu_refused(self):
        cfg = _valid_config()
        cfg["device"] = "cpu"
        with pytest.raises(LaunchConfigError) as ei:
            resolve_launch_config(cfg)
        assert "npu" in str(ei.value)

    def test_absent_eval_results_contract_refused(self):
        cfg = _valid_config()
        del cfg["eval_results_filename"]
        with pytest.raises(LaunchConfigError) as ei:
            resolve_launch_config(cfg)
        assert "eval_results.jsonl" in str(ei.value)

    def test_trainer_that_does_not_write_eval_results_refused(self):
        cfg = _valid_config()
        cfg["trainer"] = "training/qwen_sft_peft.py"  # writes sft_step_metrics.jsonl only
        with pytest.raises(LaunchConfigError) as ei:
            resolve_launch_config(cfg)
        assert "eval_results.jsonl" in str(ei.value)

    def test_unparseable_file_refused(self, tmp_path):
        bad = tmp_path / "launch_config.json"
        bad.write_text("{not json", encoding="utf-8")
        with pytest.raises(LaunchConfigError):
            resolve_launch_config_file(str(bad))

    def test_absent_file_refused(self, tmp_path):
        with pytest.raises(LaunchConfigError):
            resolve_launch_config_file(str(tmp_path / "missing.json"))


class TestRealConfigResolves:
    def test_banked_c9050_launch_config_resolves(self):
        resolved = resolve_launch_config_file(launch_config_path())
        assert resolved["model_name"].endswith("Qwen3.8-27B")
        assert resolved["device"] == "npu"

    def test_end_to_end_chain_pins_real_27b(self):
        dlr = chr(36)
        # launcher default MODEL_PATH must be the real 27B id...
        launcher = os.path.join(REPO, "scripts", "asi2_launch_grpo_27b_selfeval.sh")
        src = open(launcher, encoding="utf-8", errors="replace").read()
        assert ('MODEL_PATH="' + dlr + chr(123) + "MODEL_PATH:-" + REAL_27B + "}" + '"') in src
        # ...and must reach the trainer as --model-name "$MODEL_PATH"...
        assert ('--model-name "' + dlr + 'MODEL_PATH"') in src
        # ...and the trainer must own the eval_results.jsonl liveness artifact.
        trainer = os.path.join(REPO, "training", "grpo_trainer.py")
        tsrc = open(trainer, encoding="utf-8", errors="replace").read()
        assert 'EVAL_RESULTS_FILENAME = "eval_results.jsonl"' in tsrc


class TestEvalResultsProgress:
    def test_absent_file_named_failclosed(self, tmp_path):
        with pytest.raises(LaunchConfigError) as ei:
            eval_results_progress(str(tmp_path / "eval_results.jsonl"))
        assert "absent" in str(ei.value).lower()

    def test_fewer_than_two_steps_refused(self, tmp_path):
        p = tmp_path / "eval_results.jsonl"
        p.write_text(json.dumps({"step": 1, "loss": 0.5}) + "\n", encoding="utf-8")
        with pytest.raises(LaunchConfigError) as ei:
            eval_results_progress(str(p))
        assert "step" in str(ei.value).lower()

    def test_two_steps_finite_loss_passes(self, tmp_path):
        p = tmp_path / "eval_results.jsonl"
        rows = [{"step": 1, "loss": 0.9}, {"step": 2, "loss": 0.4}]
        p.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
        assert eval_results_progress(str(p))["steps_seen"] == 2

    def test_nonfinite_loss_refused(self, tmp_path):
        p = tmp_path / "eval_results.jsonl"
        rows = [{"step": 1, "loss": 0.9}, {"step": 2, "loss": float("nan")}]
        p.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
        with pytest.raises(LaunchConfigError) as ei:
            eval_results_progress(str(p))
        assert "loss" in str(ei.value).lower()

    def test_unparseable_row_refused(self, tmp_path):
        p = tmp_path / "eval_results.jsonl"
        p.write_text("""{"step": 1, "loss": 0.5}\n{broken\n""", encoding="utf-8")
        with pytest.raises(LaunchConfigError):
            eval_results_progress(str(p))
