"""Unit tests: launch_cmd must clear the retired GRPO before launching the
authoritative SFT resume (source_of_truth C-9634; 14:52Z OOM root cause).

The 2026-09-22 14:52Z SFT resume died of NPU OOM because the retired GRPO
family still held all 8 NPUs. The launch must pkill grpo_trainer and wait
for NPU release first.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + "/harness/scripts")
import resume_training as rt


class TestLaunchClearsRetiredGrpo:
    def test_launch_pkills_retired_grpo(self):
        cmd = rt.launch_cmd("/x/step-7/adapter", "run-x")
        assert "pkill -f 'grpo_trainer'" in cmd

    def test_launch_waits_for_npu_release(self):
        cmd = rt.launch_cmd("/x/step-7/adapter", "run-x")
        # sleep before the SFT launch so NPU memory actually frees
        assert "sleep 20" in cmd

    def test_kill_happens_before_sft_launch(self):
        cmd = rt.launch_cmd("/x/step-7/adapter", "run-x")
        assert cmd.index("pkill") < cmd.index("qwen_sft_peft")

    def test_sft_launch_still_present(self):
        cmd = rt.launch_cmd("/x/step-7/adapter", "run-x")
        assert "torchrun --nproc_per_node=8 training/qwen_sft_peft" in cmd
        assert "--adapter-init /x/step-7/adapter" in cmd
        assert "LAUNCHED pid=$!" in cmd

    def test_checkpoint_paths_flow_through(self):
        cmd = rt.launch_cmd("/ckpt/step-42/adapter", "run-y")
        assert "--adapter-init /ckpt/step-42/adapter" in cmd
        assert "--output-dir outputs/run-y" in cmd
