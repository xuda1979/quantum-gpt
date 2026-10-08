#!/usr/bin/env bash
set -euo pipefail

# Canonical Huanxin AI entrypoint for the corrected 27B SAPO run.  The proven
# trainer remains behind the historical launcher for now; this wrapper pins all
# environment-specific paths to AI while retaining the old ASI3_SAPO_* aliases
# for reproducible historical overrides.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

AI_ROOT="${AI_SAPO_ROOT:-${ASI3_SAPO_ROOT:-/root/software/quantum-gpt}}"
AI_MODEL="${AI_SAPO_MODEL_PATH:-${ASI3_SAPO_MODEL_PATH:-$AI_ROOT/models/Qwen3.6-27B}}"
AI_RUN_ID="${AI_SAPO_RUN_ID:-${ASI3_SAPO_RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)}}"

export ASI3_SAPO_ROOT="$AI_ROOT"
export ASI3_SAPO_MODEL_PATH="$AI_MODEL"
export ASI3_SAPO_CONFIG_FILE="${AI_SAPO_CONFIG_FILE:-${ASI3_SAPO_CONFIG_FILE:-$AI_ROOT/configs/rl/qwen36_27b_fv_gspo_asi2.json}}"
export ASI3_SAPO_RUN_ID="$AI_RUN_ID"
export ASI3_SAPO_OUT="${AI_SAPO_OUT:-${ASI3_SAPO_OUT:-$AI_ROOT/outputs/sapo-27b-ai-$AI_RUN_ID}}"
export ASI3_SAPO_CHECKPOINT_ROOT="${AI_SAPO_CHECKPOINT_ROOT:-${ASI3_SAPO_CHECKPOINT_ROOT:-$AI_ROOT/outputs/checkpoints/qwen36_27b_sapo_ai}}"
export ASI3_SAPO_LOGDIR="${AI_SAPO_LOGDIR:-${ASI3_SAPO_LOGDIR:-$AI_ROOT/logs/sapo_27b_ai}}"
export ASI3_SAPO_ADAPTER_INIT="${AI_SAPO_ADAPTER_INIT:-${ASI3_SAPO_ADAPTER_INIT:-}}"
# 2026-08-26 (r16 judge wave): model-judge path with the base 27B as judge
# (defaults to the training model path; the trainer shares the instance).
export ASI3_SAPO_MODEL_JUDGE_ENABLED="${AI_SAPO_MODEL_JUDGE_ENABLED:-${ASI3_SAPO_MODEL_JUDGE_ENABLED:-0}}"
export ASI3_SAPO_MODEL_JUDGE_PATH="${AI_SAPO_MODEL_JUDGE_PATH:-${ASI3_SAPO_MODEL_JUDGE_PATH:-$AI_MODEL}}"
export ASI3_SAPO_REWARD_MODE="${AI_SAPO_REWARD_MODE:-${ASI3_SAPO_REWARD_MODE:-p_dominant}}"
export ASI3_SAPO_REWARD_BREVITY_WEIGHT="${AI_SAPO_REWARD_BREVITY_WEIGHT:-${ASI3_SAPO_REWARD_BREVITY_WEIGHT:-0.05}}"
# 2026-08-27 (user binding): the reward judge is EXCLUSIVELY the Huanxin dp4
# (deepseek-v4-flash) model — same URL + API key as `claude -p huanxin -m dp4`.
# Pass through the box-local dp4 proxy endpoint + model name.
export ASI3_SAPO_BATCH_COMPARATIVE_JUDGE="${AI_SAPO_BATCH_COMPARATIVE_JUDGE:-${ASI3_SAPO_BATCH_COMPARATIVE_JUDGE:-0}}"
export ASI3_SAPO_JUDGE_DP4_ENDPOINT="${AI_SAPO_JUDGE_DP4_ENDPOINT:-${ASI3_SAPO_JUDGE_DP4_ENDPOINT:-}}"
export ASI3_SAPO_JUDGE_DP4_MODEL="${AI_SAPO_JUDGE_DP4_MODEL:-${ASI3_SAPO_JUDGE_DP4_MODEL:-dp4}}"
export ASI3_SAPO_REWARD_NORMALIZATION="${AI_SAPO_REWARD_NORMALIZATION:-${ASI3_SAPO_REWARD_NORMALIZATION:-none}}"
export ASI3_SAPO_MIN_GROUP_SIZE="${AI_SAPO_MIN_GROUP_SIZE:-${ASI3_SAPO_MIN_GROUP_SIZE:-1}}"
export ASI3_SAPO_RESUME_FROM="${AI_SAPO_RESUME_FROM:-${ASI3_SAPO_RESUME_FROM:-}}"
export ASI3_SAPO_STEPS="${AI_SAPO_STEPS:-${ASI3_SAPO_STEPS:-100}}"
export ASI3_SAPO_LAUNCHER="${AI_SAPO_ENGINE_LAUNCHER:-${ASI3_SAPO_LAUNCHER:-$AI_ROOT/scripts/asi2_launch_grpo_27b_selfeval.sh}}"
# 2026-09-01 (fixer lane): launchplan section 3b aliases — these five knobs
# were NOT aliased and the section 3b AI_SAPO_* pins were SILENTLY DROPPED
# (the asi3 launcher only reads ASI3_SAPO_*). In particular the v9
# BENCHMARK_FILE pin never reached the launch: the next launch would have
# trained on v8_holdout_adjacent. Defaults mirror the asi3 launcher so the
# alias chain is a pure pass-through when unset.
export ASI3_SAPO_LR="${AI_SAPO_LR:-${ASI3_SAPO_LR:-5e-5}}"
export ASI3_SAPO_BENCHMARK_FILE="${AI_SAPO_BENCHMARK_FILE:-${ASI3_SAPO_BENCHMARK_FILE:-evals/benchmarks/quantum_grpo_training_v8_holdout_adjacent.txt}}"
export ASI3_SAPO_GREEDY_ROLLOUT_FRACTION="${AI_SAPO_GREEDY_ROLLOUT_FRACTION:-${ASI3_SAPO_GREEDY_ROLLOUT_FRACTION:-0.4}}"
export ASI3_SAPO_ENTROPY_FLOOR_WEIGHT="${AI_SAPO_ENTROPY_FLOOR_WEIGHT:-${ASI3_SAPO_ENTROPY_FLOOR_WEIGHT:-0.01}}"
export ASI3_SAPO_JUDGE_DP4_MAX_TOKENS="${AI_SAPO_JUDGE_DP4_MAX_TOKENS:-${ASI3_SAPO_JUDGE_DP4_MAX_TOKENS:-4096}}"

# Derive the run budget pointer from the run pointer (B-164 hermeticity).
run_pointer="${SAPO_RUN_POINTER:-$ROOT_DIR/.sapo-loop/.run_pointer}"
export SAPO_RUN_POINTER="$run_pointer"
export RUN_BUDGET_FILE="$(dirname "$run_pointer")/.run_budget"
exec bash "$ROOT_DIR/scripts/asi3_launch_grpo_direct.sh" "$@"
