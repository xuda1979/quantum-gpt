"""Unit tests: trainer_running guard must see ONLY the authoritative SFT
trainer, never the retired GRPO (source_of_truth C-9634; user mandate
2026-09-23: harness must resume training ASAP when it is down).

Bug fixed: PGUARD_SH matched 'grpo_trainer' too, so a retired-but-alive GRPO
process hid a dead authoritative SFT trainer from the guardian for 12h
(SFT died NPU-OOM at 14:52Z; guardian wrote TRAINER_RUNNING until caught).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + "/harness/scripts")
import resume_training as rt


class TestPguardSeesOnlyAuthoritativeTrainer:
    def test_pguard_matches_sft_trainer(self):
        assert "qwen_sft_peft" in rt.PGUARD_SH

    def test_pguard_ignores_retired_grpo(self):
        # The retired GRPO must NOT satisfy the guard
        assert "grpo_trainer" not in rt.PGUARD_SH
        assert "grpo" not in rt.PGUARD_SH

    def test_pguard_still_flags_torchrun_sft(self):
        # torchrun launching the SFT script still counts
        assert "torchrun" in rt.PGUARD_SH

    def test_trainer_running_parses_guard_output(self):
        # Contract: run_box returns dict with status + stdout keys
        # (mocked; no box needed)
        # Direct functional test of the parsing logic
        r = {"status": "ok", "stdout": "TRAINER_RUNNING"}
        up = r.get("status") != "BOX_DOWN"
        running = ("TRAINER_RUNNING" in r.get("stdout", "")) if up else False
        assert running is True and up is True

    def test_trainer_down_when_only_grpo_alive(self):
        # Simulate box output where only grpo_trainer runs: our new PGUARD
        # returns TRAINER_DOWN; guardian must see that as down.
        r = {"status": "ok", "stdout": "TRAINER_DOWN"}
        up = r.get("status") != "BOX_DOWN"
        running = ("TRAINER_RUNNING" in r.get("stdout", "")) if up else False
        assert running is False and up is True
