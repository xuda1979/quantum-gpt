#!/usr/bin/env bash
set -euo pipefail

MODEL_NAME="${ASI1_AGENTIC_TASK_MODEL_NAME:-}"
BENCHMARK_FILE="${ASI1_AGENTIC_TASK_BENCHMARK_FILE:-evals/benchmarks/agentic_coding_trajectory_training_v1.txt}"
DOMAIN_FILTER="${ASI1_AGENTIC_TASK_DOMAIN_FILTER:-}"
OUTPUT_DIR="${ASI1_AGENTIC_TASK_OUTPUT_DIR:-outputs/qwen36-35b-a3b-agentic-grpo-asi1-task-fast}"
LOG_PATH="${ASI1_AGENTIC_TASK_LOG_PATH:-/tmp/qwen36_35b_a3b_agentic_grpo_asi1_task_fast.log}"
VISIBLE_DEVICES="${ASI1_AGENTIC_TASK_VISIBLE_DEVICES:-0,1,2,3,4,5,6,7}"
NPROC_PER_NODE="${ASI1_AGENTIC_TASK_NPROC_PER_NODE:-8}"
GROUP_SIZE="${ASI1_AGENTIC_TASK_GROUP_SIZE:-8}"
GRPO_STEPS="${ASI1_AGENTIC_TASK_GRPO_STEPS:-1}"
MASTER_PORT="${ASI1_AGENTIC_TASK_MASTER_PORT:-29533}"
MAX_NEW_TOKENS="${ASI1_AGENTIC_TASK_MAX_NEW_TOKENS:-128}"
MAX_SEQ_LENGTH="${ASI1_AGENTIC_TASK_MAX_SEQ_LENGTH:-2048}"
MAX_TURNS="${ASI1_AGENTIC_TASK_MAX_TURNS:-2}"
ONLINE_EVAL_EVERY_STEPS="${ASI1_AGENTIC_TASK_ONLINE_EVAL_EVERY_STEPS:-1}"
ONLINE_EVAL_MAX_TASKS="${ASI1_AGENTIC_TASK_ONLINE_EVAL_MAX_TASKS:-1}"
ONLINE_EVAL_BENCHMARK_FILE="${ASI1_AGENTIC_TASK_ONLINE_EVAL_BENCHMARK_FILE:-evals/benchmarks/quantum_generalization_holdout_v2_hard.txt}"
ONLINE_EVAL_TEMPERATURE="${ASI1_AGENTIC_TASK_ONLINE_EVAL_TEMPERATURE:-0.2}"
CHECKPOINT_INTERVAL_SECONDS="${ASI1_AGENTIC_TASK_CHECKPOINT_INTERVAL_SECONDS:-3600}"
CHECKPOINT_EVERY_STEPS="${ASI1_AGENTIC_TASK_CHECKPOINT_EVERY_STEPS:-0}"
LORA_RANK="${ASI1_AGENTIC_TASK_LORA_RANK:-64}"
LORA_ALPHA="${ASI1_AGENTIC_TASK_LORA_ALPHA:-128}"
LORA_DROPOUT="${ASI1_AGENTIC_TASK_LORA_DROPOUT:-0.0}"
TARGET_MODULES="${ASI1_AGENTIC_TASK_TARGET_MODULES:-q_proj k_proj v_proj o_proj gate_proj up_proj down_proj}"
TRAIN_LAYER_NORM="${ASI1_AGENTIC_TASK_TRAIN_LAYER_NORM:-1}"
MIN_TRAINABLE_PARAMETERS="${ASI1_AGENTIC_TASK_MIN_TRAINABLE_PARAMETERS:-200000000}"
MAX_TRAINABLE_PARAMETERS="${ASI1_AGENTIC_TASK_MAX_TRAINABLE_PARAMETERS:-1000000000}"
RESEARCH_METHODS="${ASI1_AGENTIC_TASK_RESEARCH_METHODS:-clause_aware_verifier_reward ast_anchor_interface_grounding self_consistency_verifier_routing uncertainty_triggered_repair_replay behavior_anchor_coverage_reward}"
BOOTSTRAP_WHEELHOUSE="${ASI1_AGENTIC_TASK_BOOTSTRAP_WHEELHOUSE:-0}"
TRAINING_MODE="${ASI1_AGENTIC_TASK_TRAINING_MODE:-lora}"
PUSH_RESULTS_S3="${ASI1_AGENTIC_TASK_PUSH_RESULTS_S3:-0}"
S3_ROOT="${ASI1_AGENTIC_TASK_S3_ROOT:-}"
RCLONE_CONFIG="${ASI1_AGENTIC_TASK_RCLONE_CONFIG:-/tmp/iner-rclone.conf}"

mkdir -p "$OUTPUT_DIR"
printf '%s\n' "$$" > "$OUTPUT_DIR/pid"
echo "ASI1_REPO_GRPO_RUNNER_START $(date -Is)" | tee "$LOG_PATH"

if [[ -z "$MODEL_NAME" ]]; then
  for candidate in \
    /root/work/filestorage/Qwen3.6-35B-A3B \
    /root/work/filestorage/Qwen3.6-35B-A3B-Instruct \
    /root/work/filestorage/Qwen3.6-35B-A3B-W8A8; do
    if [[ -d "$candidate" ]]; then
      MODEL_NAME="$candidate"
      break
    fi
  done
fi
if [[ -z "$MODEL_NAME" ]]; then
  echo "missing_model_candidates=/root/work/filestorage/Qwen3.6-35B-A3B,/root/work/filestorage/Qwen3.6-35B-A3B-Instruct,/root/work/filestorage/Qwen3.6-35B-A3B-W8A8" | tee -a "$LOG_PATH"
  exit 42
fi

echo "__ASI1_RUNNER_PWD__ $(pwd)" | tee -a "$LOG_PATH"
echo "__ASI1_RUNNER_TEST_TRAINER__" | tee -a "$LOG_PATH"
test -f training/agentic_grpo_trainer.py || { echo "missing_trainer=training/agentic_grpo_trainer.py" | tee -a "$LOG_PATH"; exit 41; }
wc -l training/agentic_grpo_trainer.py 2>&1 | tee -a "$LOG_PATH"
sha256sum training/agentic_grpo_trainer.py 2>&1 | tee -a "$LOG_PATH" || true
grep -n "if __name__" training/agentic_grpo_trainer.py 2>&1 | tee -a "$LOG_PATH" || true
python3 -m py_compile training/agentic_grpo_trainer.py 2>&1 | tee -a "$LOG_PATH" || { echo "trainer_py_compile_failed" | tee -a "$LOG_PATH"; exit 46; }
echo "__ASI1_RUNNER_TEST_MODEL__ $MODEL_NAME" | tee -a "$LOG_PATH"
test -d "$MODEL_NAME" || { echo "missing_model=$MODEL_NAME" | tee -a "$LOG_PATH"; exit 42; }
echo "__ASI1_RUNNER_TEST_BENCH__ $BENCHMARK_FILE" | tee -a "$LOG_PATH"
test -f "$BENCHMARK_FILE" || { echo "missing_benchmark=$BENCHMARK_FILE" | tee -a "$LOG_PATH"; exit 43; }
echo "__ASI1_RUNNER_TEST_ONLINE_EVAL_BENCH__ $ONLINE_EVAL_BENCHMARK_FILE" | tee -a "$LOG_PATH"
test -f "$ONLINE_EVAL_BENCHMARK_FILE" || { echo "missing_online_eval_benchmark=$ONLINE_EVAL_BENCHMARK_FILE" | tee -a "$LOG_PATH"; exit 49; }
echo "__ASI1_RUNNER_TORCHRUN_PATH__" | tee -a "$LOG_PATH"
command -v torchrun 2>&1 | tee -a "$LOG_PATH" || { echo "missing_torchrun" | tee -a "$LOG_PATH"; exit 44; }
echo "__ASI1_RUNNER_PYTHON_PATH__" | tee -a "$LOG_PATH"
command -v python3 2>&1 | tee -a "$LOG_PATH" || { echo "missing_python3" | tee -a "$LOG_PATH"; exit 45; }
echo "__ASI1_RUNNER_CONFIG_JSON__" | tee -a "$LOG_PATH"
python3 - <<'PY' "$MODEL_NAME" "$BENCHMARK_FILE" "$ONLINE_EVAL_BENCHMARK_FILE" "$OUTPUT_DIR" "$VISIBLE_DEVICES" "$NPROC_PER_NODE" "$GROUP_SIZE" "$GRPO_STEPS" "$MASTER_PORT" "$MAX_NEW_TOKENS" "$MAX_SEQ_LENGTH" "$MAX_TURNS" "$CHECKPOINT_INTERVAL_SECONDS" "$CHECKPOINT_EVERY_STEPS" "$TRAINING_MODE" "$RESEARCH_METHODS" "$LORA_RANK" "$LORA_ALPHA" "$LORA_DROPOUT" "$TARGET_MODULES" "$TRAIN_LAYER_NORM" "$MIN_TRAINABLE_PARAMETERS" "$MAX_TRAINABLE_PARAMETERS" 2>&1 | tee -a "$LOG_PATH"
import json
import sys
from datetime import datetime, timezone

(
    model_name,
    benchmark_file,
    online_eval_benchmark_file,
    output_dir,
    visible_devices,
    nproc_per_node,
    group_size,
    grpo_steps,
    master_port,
    max_new_tokens,
    max_seq_length,
    max_turns,
    checkpoint_interval_seconds,
    checkpoint_every_steps,
    training_mode,
    research_methods,
    lora_rank,
    lora_alpha,
    lora_dropout,
    target_modules,
    train_layer_norm,
    min_trainable_parameters,
    max_trainable_parameters,
) = sys.argv[1:]
payload = {
    "stage": "asi1_runner_config",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "model_name": model_name,
    "benchmark_file": benchmark_file,
    "online_eval_benchmark_file": online_eval_benchmark_file,
    "output_dir": output_dir,
    "visible_devices": visible_devices,
    "nproc_per_node": int(nproc_per_node),
    "group_size": int(group_size),
    "grpo_steps": int(grpo_steps),
    "master_port": int(master_port),
    "max_new_tokens": int(max_new_tokens),
    "max_seq_length": int(max_seq_length),
    "max_turns": int(max_turns),
    "checkpoint_interval_seconds": int(checkpoint_interval_seconds),
    "checkpoint_every_steps": int(checkpoint_every_steps),
    "training_mode": training_mode,
    "research_methods": research_methods.split(),
    "lora": {
        "rank": int(lora_rank),
        "alpha": int(lora_alpha),
        "dropout": float(lora_dropout),
        "target_modules": target_modules.split(),
        "train_layernorm": train_layer_norm == "1",
        "min_trainable_parameters": int(min_trainable_parameters) if min_trainable_parameters else None,
        "max_trainable_parameters": int(max_trainable_parameters) if max_trainable_parameters else None,
    },
}
print(json.dumps(payload, sort_keys=True))
PY
cat > "$OUTPUT_DIR/run_manifest.json" <<JSON
{
  "schema_version": "agentic-control-plane-v1",
  "record_type": "run_manifest",
  "run_id": "$(basename "$OUTPUT_DIR")",
  "created_at_utc": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "environment": "ASI1",
  "trainer": "training/agentic_grpo_trainer.py",
  "model_name": "$MODEL_NAME",
  "training_mode": "$TRAINING_MODE",
  "output_dir": "$OUTPUT_DIR",
  "tasks_dir": "evals/tasks",
  "benchmark_file": "$BENCHMARK_FILE",
  "online_eval_benchmark_file": "$ONLINE_EVAL_BENCHMARK_FILE",
  "planned_steps": $GRPO_STEPS,
  "group_size": $GROUP_SIZE,
  "max_turns": $MAX_TURNS,
  "max_test_runs": 2,
  "checkpoint_interval_seconds": $CHECKPOINT_INTERVAL_SECONDS,
  "checkpoint_every_steps": $CHECKPOINT_EVERY_STEPS,
  "world_size": $NPROC_PER_NODE,
  "lora": {
    "rank": $LORA_RANK,
    "alpha": $LORA_ALPHA,
    "dropout": $LORA_DROPOUT,
    "target_modules": "$(printf '%s' "$TARGET_MODULES")",
    "train_layernorm": $([[ "$TRAIN_LAYER_NORM" == "1" ]] && echo true || echo false),
    "min_trainable_parameters": ${MIN_TRAINABLE_PARAMETERS:-null},
    "max_trainable_parameters": ${MAX_TRAINABLE_PARAMETERS:-null}
  },
  "artifact_paths": {
    "run_config": "$OUTPUT_DIR/run_config.json",
    "step_metrics_jsonl": "$OUTPUT_DIR/grpo_step_metrics.jsonl",
    "agentic_trace_jsonl": "$OUTPUT_DIR/agentic_trace.jsonl",
    "live_status": "$OUTPUT_DIR/live_status.json",
    "adapter_dir": "$OUTPUT_DIR/final_adapter"
  }
}
JSON
cat > "$OUTPUT_DIR/job_health.json" <<JSON
{
  "schema_version": 1,
  "environment": "ASI1",
  "huanxin_task_name": "${ASI1_AGENTIC_TASK_NAME:-}",
  "huanxin_task_status": "starting",
  "remote_path": "$OUTPUT_DIR",
  "model_name": "$MODEL_NAME",
  "benchmark_file": "$BENCHMARK_FILE",
  "online_eval_benchmark_file": "$ONLINE_EVAL_BENCHMARK_FILE",
  "training_mode": "$TRAINING_MODE",
  "world_size": $NPROC_PER_NODE,
  "planned_steps": $GRPO_STEPS,
  "recorded_steps": 0,
  "pid_alive": true,
  "pid": $$,
  "updated_at_utc": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
JSON

if [[ "$BOOTSTRAP_WHEELHOUSE" == "1" ]]; then
  echo "__ASI1_RUNNER_BOOTSTRAP_WHEELHOUSE__" | tee -a "$LOG_PATH"
  test -d tools/wheels
  python3 -m pip install --no-cache-dir --no-input --no-index \
    --find-links tools/wheels accelerate==1.4.0 peft==0.14.0
fi

echo "__ASI1_RUNNER_DEPENDENCY_PROBE__ training_mode=$TRAINING_MODE" | tee -a "$LOG_PATH"
ASI1_AGENTIC_TASK_TRAINING_MODE="$TRAINING_MODE" python3 - <<'PY'
import importlib.util
import os

mods = ["torch", "torch_npu", "transformers"]
if os.environ.get("ASI1_AGENTIC_TASK_TRAINING_MODE", "lora") == "lora":
    mods.extend(["peft", "accelerate"])
missing = [mod for mod in mods if importlib.util.find_spec(mod) is None]
print("asi1_grpo_dependencies=" + ",".join(mod for mod in mods if mod not in missing))
if missing:
    raise SystemExit("missing_dependencies=" + ",".join(missing))
PY

echo "__ASI1_RUNNER_BEFORE_TORCHRUN__" | tee -a "$LOG_PATH"
DOMAIN_ARGS=()
if [[ -n "$DOMAIN_FILTER" ]]; then
  DOMAIN_ARGS=(--domain-filter "$DOMAIN_FILTER")
fi
RESEARCH_METHOD_ARGS=()
if [[ -n "$RESEARCH_METHODS" ]]; then
  # shellcheck disable=SC2206
  RESEARCH_METHOD_LIST=($RESEARCH_METHODS)
  RESEARCH_METHOD_ARGS=(--research-methods "${RESEARCH_METHOD_LIST[@]}")
fi
TARGET_MODULE_ARGS=()
if [[ -n "$TARGET_MODULES" ]]; then
  # shellcheck disable=SC2206
  TARGET_MODULE_LIST=($TARGET_MODULES)
  TARGET_MODULE_ARGS=(--target-modules "${TARGET_MODULE_LIST[@]}")
fi
LAYER_NORM_ARGS=()
if [[ "$TRAIN_LAYER_NORM" == "1" ]]; then
  LAYER_NORM_ARGS=(--train-layernorm)
fi
TRAINABLE_BUDGET_ARGS=()
if [[ -n "$MIN_TRAINABLE_PARAMETERS" ]]; then
  TRAINABLE_BUDGET_ARGS+=(--min-trainable-parameters "$MIN_TRAINABLE_PARAMETERS")
fi
if [[ -n "$MAX_TRAINABLE_PARAMETERS" ]]; then
  TRAINABLE_BUDGET_ARGS+=(--max-trainable-parameters "$MAX_TRAINABLE_PARAMETERS")
fi
set +e
ASCEND_RT_VISIBLE_DEVICES="$VISIBLE_DEVICES" \
PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256 \
TOKENIZERS_PARALLELISM=false \
torchrun --nproc_per_node "$NPROC_PER_NODE" --master_port "$MASTER_PORT" training/agentic_grpo_trainer.py \
  --model-name "$MODEL_NAME" \
  --benchmark-file "$BENCHMARK_FILE" \
  "${DOMAIN_ARGS[@]}" \
  --output-dir "$OUTPUT_DIR" \
  --device npu \
  --group-size "$GROUP_SIZE" \
  --grpo-steps "$GRPO_STEPS" \
  --max-new-tokens "$MAX_NEW_TOKENS" \
  --max-seq-length "$MAX_SEQ_LENGTH" \
  --max-turns "$MAX_TURNS" \
  --max-test-runs 2 \
  --temperature 0.8 \
  --lr 5e-6 \
  --kl-coeff 0.05 \
  --log-steps 1 \
  --checkpoint-interval-seconds "$CHECKPOINT_INTERVAL_SECONDS" \
  --checkpoint-every-steps "$CHECKPOINT_EVERY_STEPS" \
  --online-eval-benchmark-file "$ONLINE_EVAL_BENCHMARK_FILE" \
  --online-eval-every-steps "$ONLINE_EVAL_EVERY_STEPS" \
  --online-eval-max-tasks "$ONLINE_EVAL_MAX_TASKS" \
  --online-eval-temperature "$ONLINE_EVAL_TEMPERATURE" \
  --training-mode "$TRAINING_MODE" \
  --lora-rank "$LORA_RANK" \
  --lora-alpha "$LORA_ALPHA" \
  --lora-dropout "$LORA_DROPOUT" \
  "${TARGET_MODULE_ARGS[@]}" \
  "${LAYER_NORM_ARGS[@]}" \
  "${TRAINABLE_BUDGET_ARGS[@]}" \
  --gradient-checkpointing \
  "${RESEARCH_METHOD_ARGS[@]}" \
  2>&1 | tee -a "$LOG_PATH"
train_rc=${PIPESTATUS[0]}
set -e
echo "__ASI1_RUNNER_TORCHRUN_EXIT__ $train_rc" | tee -a "$LOG_PATH"

metrics_path="$OUTPUT_DIR/grpo_step_metrics.jsonl"
final_adapter_dir="$OUTPUT_DIR/final_adapter"
if [[ "$train_rc" == "0" ]]; then
  if [[ ! -s "$metrics_path" ]]; then
    echo "__ASI1_RUNNER_MISSING_METRICS__ $metrics_path" | tee -a "$LOG_PATH"
    train_rc=47
  elif [[ ! -d "$final_adapter_dir" ]]; then
    echo "__ASI1_RUNNER_MISSING_FINAL_ADAPTER__ $final_adapter_dir" | tee -a "$LOG_PATH"
    train_rc=48
  else
    echo "__ASI1_RUNNER_METRICS_AND_ARTIFACTS_OK__" | tee -a "$LOG_PATH"
  fi
fi

tail -n 400 "$LOG_PATH" > "$OUTPUT_DIR/train_log_tail.txt" 2>/dev/null || true
if [[ -f "$OUTPUT_DIR/live_status.json" ]]; then
  python3 - <<'PY' "$OUTPUT_DIR/job_health.json" "$OUTPUT_DIR/live_status.json" "$train_rc" 2>/dev/null || true
import json
import sys
from datetime import datetime, timezone
health_path, live_path, rc = sys.argv[1:4]
try:
    health = json.load(open(health_path, encoding="utf-8"))
except Exception:
    health = {}
health["huanxin_task_status"] = "completed" if int(rc) == 0 else "failed"
health["pid_alive"] = False
health["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
json.dump(health, open(health_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
open(health_path, "a", encoding="utf-8").write("\n")
try:
    live = json.load(open(live_path, encoding="utf-8"))
    live["job_health"] = health
    live["status"] = "completed" if int(rc) == 0 else "failed"
    json.dump(live, open(live_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(live_path, "a", encoding="utf-8").write("\n")
except Exception:
    pass
PY
fi
printf '{"exit_code":%s,"timestamp_utc":"%s"}\n' \
  "$train_rc" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$OUTPUT_DIR/remote_exit_status.json"

if [[ "$PUSH_RESULTS_S3" == "1" && -n "$S3_ROOT" ]]; then
  rclone copy "$OUTPUT_DIR" "$S3_ROOT/$OUTPUT_DIR" \
    --config "$RCLONE_CONFIG" --s3-no-check-bucket --progress || true
fi

exit "$train_rc"
