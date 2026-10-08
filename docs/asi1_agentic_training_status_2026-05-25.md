# ASI1 Agentic Training Status - 2026-05-25

## Active Target

- Huanxin environment: `ASI1`
- Remote repo root: `/workspace/quantum-gpt`
- Working training base for now: `/root/work/filestorage/Qwen3.6-27B`
- Blocked training base: `/root/work/filestorage/Qwen3.6-35B-A3B-W8A8`

## Verified Today

- ASI1 login and shell wrapper work through `scripts/huanxin_env_shell.sh --env ASI1`.
- Remote code root exists at `/workspace/quantum-gpt`.
- Required trainer modules and benchmark files are present after compact code upload.
- Missing research plugins were uploaded and verified under `research/papers/*/code/plugin.py`.
- ASI1 runtime was upgraded from `transformers 4.57.1` to `transformers 5.9.0`.
- `AutoConfig` now loads Qwen3.6 model configs:
  - `Qwen3_5MoeConfig` for `qwen3_5_moe`
  - `Qwen3_5ForConditionalGeneration` config for Qwen3.6-27B
- One-NPU Qwen3.6-27B agentic GRPO smoke completed and saved an adapter:
  - output: `outputs/asi1-qwen36-27b-agentic-grpo-direct-smoke-20260525T1342`
  - artifacts include `adapter/`, `grpo_metrics.json`, `grpo_step_metrics.jsonl`, `live_status.json`, and `run_config.json`

## Fixes Applied

- `training/agent_trajectory_rollout.py`
  - split the initial agent history into separate `system` and `user` messages
  - added fallback rendering when a model chat template rejects tool-style histories
- `scripts/asi1_agentic_grpo_quick_status.sh`
  - read-only ASI1 status helper for live run dirs and bounded log tails

## Current Blockers / Findings

- Qwen3.6-35B-A3B-W8A8 is not trainable through the current HF + Ascend path.
  - Failure: `aclnnMm` rejects `DT_INT8` in `transformers.integrations.moe._grouped_mm_fallback`.
  - Practical next route: use a non-quantized/BF16 checkpoint or vendor serving/training kernels for the MoE W8A8 path.
- ASI1 shell daemon state frequently goes stale between commands.
  - Workaround: wrappers clean stale daemon state and restart successfully.
- S3/INER access from ASI1 is still not proven for large transfers.
  - Small control-plane uploads work with `scripts/huanxin_upload_small_file.sh`.

## Active Run

- Job id: `qwen36-27b-agentic-grpo-asi1-fast-20260525T134629Z`
- PID: `46968`
- Log: `/tmp/qwen36_27b_agentic_grpo_asi1_fast_20260525T1347.log`
- Output dir: `outputs/qwen36-27b-agentic-grpo-asi1-fast-20260525T1347`
- Config:
  - 4 NPUs: `ASCEND_RT_VISIBLE_DEVICES=0,1,2,3`
  - `NPROC_PER_NODE=4`
  - `GROUP_SIZE=4`
  - `GRPO_STEPS=16`
  - online eval every 4 steps on 2 holdout tasks

## Immediate Next Steps

1. Monitor the active 4-NPU run for step-1 completion, failure, or deadlock.
2. If the 4-NPU run stalls, launch a proven 1-NPU monitored run with more steps and online eval.
3. Add a runtime/model preflight that rejects W8A8 MoE training on the current HF Ascend fallback before torchrun.
4. Add periodic status/eval artifact validation around active ASI1 runs.
