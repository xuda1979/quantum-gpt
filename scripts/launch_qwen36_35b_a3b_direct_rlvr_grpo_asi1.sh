#!/usr/bin/env bash
set -euo pipefail

ROOT="${QG_ROOT:-/workspace/quantum-gpt}"
cd "$ROOT"

TS="${QG_TS:-$(date -u +%Y%m%dT%H%M%SZ)}"
export QG_ROOT="$ROOT"
export QG_MODEL="${QG_MODEL:-/root/work/filestorage/Qwen3.6-27B}"
if [[ ! -d "$QG_MODEL" ]]; then
  for candidate in \
    /root/work/filestorage/Qwen3.6-27B \
    /root/work/filestorage/Qwen3.6-35B-A3B \
    /root/work/filestorage/Qwen3.6-35B-A3B-Instruct \
    /root/work/filestorage/Qwen3.6-35B-A3B-W8A8; do
    if [[ -d "$candidate" ]]; then
      export QG_MODEL="$candidate"
      break
    fi
  done
fi

export QG_OUT="${QG_OUT:-$ROOT/outputs/q36-35b-a3b-quantum-software-rlvr-grpo-$TS}"
export QG_TASK_ROOTS="${QG_TASK_ROOTS:-$ROOT/evals/tasks/quantum,$ROOT/evals/tasks/software}"
export QG_HOLDOUT_BENCHMARKS="${QG_HOLDOUT_BENCHMARKS:-$ROOT/evals/benchmarks/quantum_generalization_holdout_v1.txt,$ROOT/evals/benchmarks/quantum_generalization_holdout_v2_hard.txt,$ROOT/evals/benchmarks/agentic_software_engineering_holdout_v1.txt,$ROOT/evals/benchmarks/gemma4_quantum_generalization_holdout_v1.txt}"
export QG_TRAIN_DOMAINS="${QG_TRAIN_DOMAINS:-quantum,software}"
export QG_USE_BENCHMARK_ONLY="${QG_USE_BENCHMARK_ONLY:-1}"
export QG_PROMPT_VARIANTS_PER_TASK="${QG_PROMPT_VARIANTS_PER_TASK:-4}"
export QG_STEPS="${QG_STEPS:-200000}"
export QG_GROUP_SIZE="${QG_GROUP_SIZE:-2}"
export QG_SAVE_SECONDS="${QG_SAVE_SECONDS:-3600}"
export QG_MAX_NEW_TOKENS="${QG_MAX_NEW_TOKENS:-384}"
export QG_MAX_LEN="${QG_MAX_LEN:-2048}"
export QG_SELF_JUDGE_ENABLED="${QG_SELF_JUDGE_ENABLED:-1}"
export QG_SELF_JUDGE_MAX_NEW_TOKENS="${QG_SELF_JUDGE_MAX_NEW_TOKENS:-192}"
export QG_SELF_JUDGE_MAX_LEN="${QG_SELF_JUDGE_MAX_LEN:-3072}"
export QG_LR="${QG_LR:-1e-5}"
export QG_LORA_RANK="${QG_LORA_RANK:-768}"
export QG_LORA_ALPHA="${QG_LORA_ALPHA:-1536}"
export QG_LORA_TARGET_MODULES="${QG_LORA_TARGET_MODULES:-q_proj,v_proj}"
export QG_MIN_TRAINABLE_PARAMETERS="${QG_MIN_TRAINABLE_PARAMETERS:-90000000}"
export QG_MAX_TRAINABLE_PARAMETERS="${QG_MAX_TRAINABLE_PARAMETERS:-140000000}"
export ASCEND_RT_VISIBLE_DEVICES="${ASCEND_RT_VISIBLE_DEVICES:-0,1,2,3,4,5,6,7}"
export PYTORCH_NPU_ALLOC_CONF="${PYTORCH_NPU_ALLOC_CONF:-max_split_size_mb:128}"
export TOKENIZERS_PARALLELISM=false

mkdir -p "$QG_OUT"
cat > "$QG_OUT/launch_env.json" <<JSON
{
  "qg_root": "$QG_ROOT",
  "qg_model": "$QG_MODEL",
  "qg_out": "$QG_OUT",
  "qg_task_roots": "$QG_TASK_ROOTS",
  "qg_holdout_benchmarks": "$QG_HOLDOUT_BENCHMARKS",
  "qg_train_domains": "$QG_TRAIN_DOMAINS",
  "qg_steps": $QG_STEPS,
  "qg_group_size": $QG_GROUP_SIZE,
  "qg_save_seconds": $QG_SAVE_SECONDS,
  "qg_self_judge_enabled": "$QG_SELF_JUDGE_ENABLED",
  "qg_self_judge_max_new_tokens": $QG_SELF_JUDGE_MAX_NEW_TOKENS,
  "qg_self_judge_max_len": $QG_SELF_JUDGE_MAX_LEN,
  "qg_lora_rank": $QG_LORA_RANK,
  "qg_lora_alpha": $QG_LORA_ALPHA,
  "qg_lora_target_modules": "$QG_LORA_TARGET_MODULES",
  "qg_min_trainable_parameters": $QG_MIN_TRAINABLE_PARAMETERS,
  "qg_max_trainable_parameters": $QG_MAX_TRAINABLE_PARAMETERS,
  "visible_devices": "$ASCEND_RT_VISIBLE_DEVICES"
}
JSON

test -d "$QG_MODEL" || { echo "missing_model=$QG_MODEL" >&2; exit 42; }
python3 -m py_compile training/qwen35b_benchmark_rlvr_grpo.py
echo "$$" > "$QG_OUT/launcher.pid"
echo "__QG_DIRECT_GRPO_START__ $(date -Is) out=$QG_OUT model=$QG_MODEL"
exec python3 training/qwen35b_benchmark_rlvr_grpo.py
