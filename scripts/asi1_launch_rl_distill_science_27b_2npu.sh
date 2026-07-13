#!/usr/bin/env bash
# ASI1 launcher: RL + soft-distillation loop for quantum SCIENCE (non-coding)
# on Qwen3.6-27B, 2 NPUs.
#
# This is a thin wrapper around asi1_launch_rl_distill_27b_2npu.sh that
# points it at the science config, science buffer, science port, and the
# E_full ablation preset (reward-weighted NLL + per-artifact KL gate +
# partial-credit upweight). The science pipeline (scripts/rl_distill_pipeline.py
# with task_domain=science) uses prose+math science prompts, no sandbox, and
# a citation-grounding reward term. See
# docs/rl-science-distill-rd-plan-2026-07-09.md for the full plan.
#
# Usage:
#   bash scripts/asi1_launch_rl_distill_science_27b_2npu.sh           # launch
#   bash scripts/asi1_launch_rl_distill_science_27b_2npu.sh status    # status
#   bash scripts/asi1_launch_rl_distill_science_27b_2npu.sh stop      # stop
#
# All env vars of the coding launcher are respected and passed through.
# Science-specific overrides (can be re-exported by the caller):
#   CONFIG                  -> configs/distill/rl_distill_science_27b_v1.json
#   BUFFER_DIR              -> $NAS_ROOT/data/generated/rl_distill_science_27b_v1
#   VLLM_PORT               -> 8017
#   VLLM_SERVED_NAME        -> qwen36-27b-rl-distill-science
#   VLLM_LORA_ADAPTER_NAME  -> rl_distill_science_latest
#   ABLATION_PRESET         -> E_full
#   RUN_ID                  -> rl-distill-science-27b-<timestamp>
#   EVAL_TASKS              -> quantum_science
#   TEMPERATURE             -> 0.9   (slightly higher for science diversity)
#   MAX_LENGTH              -> 3072  (science answers are longer than code)
#   KL_COEFF                -> 0.4   (lower; teacher distribution is noisier)
#   TRAINER_MAX_STEPS_PER_ROUND -> 150

set -euo pipefail

export CONFIG="${CONFIG:-configs/distill/rl_distill_science_27b_v1.json}"
export BUFFER_DIR="${BUFFER_DIR:-${NAS_ROOT:-/root/work/software/quantum-gpt}/data/generated/rl_distill_science_27b_v1}"
export VLLM_PORT="${VLLM_PORT:-8017}"
export VLLM_SERVED_NAME="${VLLM_SERVED_NAME:-qwen36-27b-rl-distill-science}"
export VLLM_LORA_ADAPTER_NAME="${VLLM_LORA_ADAPTER_NAME:-rl_distill_science_latest}"
export ABLATION_PRESET="${ABLATION_PRESET:-E_full}"
export RUN_ID="${RUN_ID:-rl-distill-science-27b-$(date -u +%Y%m%dT%H%M%SZ)}"
export EVAL_TASKS="${EVAL_TASKS:-quantum_science}"
export TEMPERATURE="${TEMPERATURE:-0.9}"
export MAX_LENGTH="${MAX_LENGTH:-3072}"
export KL_COEFF="${KL_COEFF:-0.4}"
export TRAINER_MAX_STEPS_PER_ROUND="${TRAINER_MAX_STEPS_PER_ROUND:-150}"

exec bash "$(dirname "$0")/asi1_launch_rl_distill_27b_2npu.sh" "$@"
