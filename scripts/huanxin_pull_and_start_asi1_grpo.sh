#!/usr/bin/env bash
set -euo pipefail

REMOTE_ROOT="${HUANXIN_GRPO_REMOTE_ROOT:-/workspace/quantum-gpt}"
S3_ROOT="${HUANXIN_GRPO_S3_ROOT:-iner:jtdlp-21b4208dde424e96b159362ef49c9c96/software/quantum-gpt}"
S3_ENDPOINT="${INER_S3_ENDPOINT:-https://iner.aihuanxin.cn}"
S3_ACCESS_KEY_ID="${INER_ACCESS_KEY_ID:-OXF5ar4y}"
RCLONE_CONFIG="${HUANXIN_GRPO_RCLONE_CONFIG:-/tmp/iner-rclone.conf}"
TIMESTAMP="${HUANXIN_GRPO_TIMESTAMP:-$(date -u +%Y%m%dT%H%M%SZ)}"
RUN_ROOT="${HUANXIN_GRPO_RUN_ROOT:-outputs/qwen36-35b-a3b-agentic-grpo-asi1-${TIMESTAMP}}"
SMOKE_OUTPUT_DIR="${HUANXIN_GRPO_SMOKE_OUTPUT_DIR:-${RUN_ROOT}-smoke}"
FULL_OUTPUT_DIR="${HUANXIN_GRPO_FULL_OUTPUT_DIR:-${RUN_ROOT}-full}"
BOOT_LOG="${HUANXIN_GRPO_BOOT_LOG:-/tmp/qwen36_35b_a3b_agentic_grpo_asi1_boot_${TIMESTAMP}.log}"
MODEL_NAME="${HUANXIN_GRPO_MODEL_NAME:-}"
VISIBLE_DEVICES="${HUANXIN_GRPO_VISIBLE_DEVICES:-0,1,2,3,4,5,6,7}"
NPROC_PER_NODE="${HUANXIN_GRPO_NPROC_PER_NODE:-8}"
BENCHMARK_FILE="${HUANXIN_GRPO_BENCHMARK_FILE:-evals/benchmarks/agentic_coding_trajectory_training_v1.txt}"
ONLINE_EVAL_BENCHMARK_FILE="${HUANXIN_GRPO_ONLINE_EVAL_BENCHMARK_FILE:-evals/benchmarks/quantum_generalization_holdout_v2_hard.txt}"
DOMAIN_FILTER="${HUANXIN_GRPO_DOMAIN_FILTER:-}"
LORA_RANK="${HUANXIN_GRPO_LORA_RANK:-64}"
LORA_ALPHA="${HUANXIN_GRPO_LORA_ALPHA:-128}"
LORA_DROPOUT="${HUANXIN_GRPO_LORA_DROPOUT:-0.0}"
TARGET_MODULES="${HUANXIN_GRPO_TARGET_MODULES:-q_proj k_proj v_proj o_proj gate_proj up_proj down_proj}"
TRAIN_LAYER_NORM="${HUANXIN_GRPO_TRAIN_LAYER_NORM:-1}"
MIN_TRAINABLE_PARAMETERS="${HUANXIN_GRPO_MIN_TRAINABLE_PARAMETERS:-200000000}"
MAX_TRAINABLE_PARAMETERS="${HUANXIN_GRPO_MAX_TRAINABLE_PARAMETERS:-1000000000}"
FULL_GRPO_STEPS="${HUANXIN_GRPO_FULL_STEPS:-200000}"
FULL_GROUP_SIZE="${HUANXIN_GRPO_FULL_GROUP_SIZE:-8}"
FULL_MAX_NEW_TOKENS="${HUANXIN_GRPO_FULL_MAX_NEW_TOKENS:-4096}"
FULL_MAX_SEQ_LENGTH="${HUANXIN_GRPO_FULL_MAX_SEQ_LENGTH:-32768}"
FULL_MAX_TURNS="${HUANXIN_GRPO_FULL_MAX_TURNS:-32}"
FULL_ONLINE_EVAL_EVERY_STEPS="${HUANXIN_GRPO_FULL_ONLINE_EVAL_EVERY_STEPS:-8}"
FULL_ONLINE_EVAL_MAX_TASKS="${HUANXIN_GRPO_FULL_ONLINE_EVAL_MAX_TASKS:-8}"
CHECKPOINT_INTERVAL_SECONDS="${HUANXIN_GRPO_CHECKPOINT_INTERVAL_SECONDS:-3600}"
CHECKPOINT_EVERY_STEPS="${HUANXIN_GRPO_CHECKPOINT_EVERY_STEPS:-0}"
PUSH_RESULTS_S3="${HUANXIN_GRPO_PUSH_RESULTS_S3:-1}"

log() {
  printf '%s %s\n' "$(date -Is)" "$*" | tee -a "$BOOT_LOG"
}

write_status() {
  local status="$1"
  local reason="${2:-}"
  mkdir -p "$REMOTE_ROOT/reports"
  python3 - "$REMOTE_ROOT/reports/asi1_grpo_launch_status.json" "$status" "$reason" "$SMOKE_OUTPUT_DIR" "$FULL_OUTPUT_DIR" "$MODEL_NAME" <<'PY'
import json
import sys
from datetime import datetime, timezone

path, status, reason, smoke_output, full_output, model_name = sys.argv[1:]
payload = {
    "schema_version": 1,
    "status": status,
    "reason": reason,
    "updated_at_utc": datetime.now(timezone.utc).isoformat(),
    "model_name": model_name,
    "smoke_output_dir": smoke_output,
    "full_output_dir": full_output,
}
with open(path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, ensure_ascii=False, indent=2)
    handle.write("\n")
PY
}

fail() {
  log "ERROR $*"
  write_status failed "$*"
  exit 1
}

ensure_rclone() {
  if command -v rclone >/dev/null 2>&1; then
    command -v rclone
    return 0
  fi
  if [[ -x "$REMOTE_ROOT/tools/preseed/rclone-linux-arm64" ]]; then
    echo "$REMOTE_ROOT/tools/preseed/rclone-linux-arm64"
    return 0
  fi
  if [[ -x tools/preseed/rclone-linux-arm64 ]]; then
    echo "tools/preseed/rclone-linux-arm64"
    return 0
  fi
  local install_dir="${TMPDIR:-/tmp}/huanxin-rclone-bin"
  local zip_path="${TMPDIR:-/tmp}/rclone-current-linux-arm64.zip"
  mkdir -p "$install_dir"
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL https://downloads.rclone.org/rclone-current-linux-arm64.zip -o "$zip_path" || true
  elif command -v wget >/dev/null 2>&1; then
    wget -qO "$zip_path" https://downloads.rclone.org/rclone-current-linux-arm64.zip || true
  fi
  if [[ -s "$zip_path" ]]; then
    python3 - <<'PY' "$zip_path" "$install_dir"
import pathlib
import shutil
import sys
import zipfile

zip_path = pathlib.Path(sys.argv[1])
install_dir = pathlib.Path(sys.argv[2])
with zipfile.ZipFile(zip_path) as archive:
    members = [name for name in archive.namelist() if name.endswith("/rclone")]
    if not members:
        raise SystemExit("rclone binary missing from archive")
    with archive.open(members[0]) as src, (install_dir / "rclone").open("wb") as dst:
        shutil.copyfileobj(src, dst)
(install_dir / "rclone").chmod(0o755)
PY
    if [[ -x "$install_dir/rclone" ]]; then
      echo "$install_dir/rclone"
      return 0
    fi
  fi
  fail "missing_rclone_after_path_preseed_and_download"
}

write_rclone_config() {
  if [[ -s "$RCLONE_CONFIG" ]]; then
    echo "$RCLONE_CONFIG"
    return
  fi
  if [[ -z "${INER_SECRET_ACCESS_KEY:-}" ]]; then
    fail "missing rclone config and INER_SECRET_ACCESS_KEY env var"
  fi
  umask 077
  cat > "$RCLONE_CONFIG" <<EOF
[iner]
type = s3
provider = Other
access_key_id = $S3_ACCESS_KEY_ID
secret_access_key = $INER_SECRET_ACCESS_KEY
endpoint = $S3_ENDPOINT
acl = private
force_path_style = true
EOF
  echo "$RCLONE_CONFIG"
}

resolve_model() {
  if [[ -n "$MODEL_NAME" && -d "$MODEL_NAME" ]]; then
    return
  fi
  for candidate in \
    /root/work/filestorage/Qwen3.6-35B-A3B \
    /root/work/filestorage/Qwen3.6-35B-A3B-Instruct \
    /root/work/filestorage/Qwen3.6-35B-A3B-W8A8; do
    if [[ -d "$candidate" ]]; then
      MODEL_NAME="$candidate"
      return
    fi
  done
  fail "missing Qwen3.6-35B-A3B model directory under /root/work/filestorage"
}

verify_run_artifacts() {
  local output_dir="$1"
  local label="$2"
  test -s "$output_dir/grpo_step_metrics.jsonl" || fail "${label}_missing_metrics=$output_dir/grpo_step_metrics.jsonl"
  test -s "$output_dir/latest_checkpoint.json" || fail "${label}_missing_checkpoint=$output_dir/latest_checkpoint.json"
  test -d "$output_dir/final_adapter" || fail "${label}_missing_final_adapter=$output_dir/final_adapter"
}

launch_runner() {
  local output_dir="$1"
  local log_path="$2"
  local steps="$3"
  local group_size="$4"
  local max_new_tokens="$5"
  local max_seq_length="$6"
  local max_turns="$7"
  local online_eval_every="$8"
  local online_eval_max_tasks="$9"
  local checkpoint_every_steps="${10}"

  ASI1_AGENTIC_TASK_MODEL_NAME="$MODEL_NAME" \
  ASI1_AGENTIC_TASK_BENCHMARK_FILE="$BENCHMARK_FILE" \
  ASI1_AGENTIC_TASK_DOMAIN_FILTER="$DOMAIN_FILTER" \
  ASI1_AGENTIC_TASK_OUTPUT_DIR="$output_dir" \
  ASI1_AGENTIC_TASK_LOG_PATH="$log_path" \
  ASI1_AGENTIC_TASK_VISIBLE_DEVICES="$VISIBLE_DEVICES" \
  ASI1_AGENTIC_TASK_NPROC_PER_NODE="$NPROC_PER_NODE" \
  ASI1_AGENTIC_TASK_GROUP_SIZE="$group_size" \
  ASI1_AGENTIC_TASK_GRPO_STEPS="$steps" \
  ASI1_AGENTIC_TASK_MAX_NEW_TOKENS="$max_new_tokens" \
  ASI1_AGENTIC_TASK_MAX_SEQ_LENGTH="$max_seq_length" \
  ASI1_AGENTIC_TASK_MAX_TURNS="$max_turns" \
  ASI1_AGENTIC_TASK_ONLINE_EVAL_EVERY_STEPS="$online_eval_every" \
  ASI1_AGENTIC_TASK_ONLINE_EVAL_MAX_TASKS="$online_eval_max_tasks" \
  ASI1_AGENTIC_TASK_ONLINE_EVAL_BENCHMARK_FILE="$ONLINE_EVAL_BENCHMARK_FILE" \
  ASI1_AGENTIC_TASK_CHECKPOINT_INTERVAL_SECONDS="$CHECKPOINT_INTERVAL_SECONDS" \
  ASI1_AGENTIC_TASK_CHECKPOINT_EVERY_STEPS="$checkpoint_every_steps" \
  ASI1_AGENTIC_TASK_LORA_RANK="$LORA_RANK" \
  ASI1_AGENTIC_TASK_LORA_ALPHA="$LORA_ALPHA" \
  ASI1_AGENTIC_TASK_LORA_DROPOUT="$LORA_DROPOUT" \
  ASI1_AGENTIC_TASK_TARGET_MODULES="$TARGET_MODULES" \
  ASI1_AGENTIC_TASK_TRAIN_LAYER_NORM="$TRAIN_LAYER_NORM" \
  ASI1_AGENTIC_TASK_MIN_TRAINABLE_PARAMETERS="$MIN_TRAINABLE_PARAMETERS" \
  ASI1_AGENTIC_TASK_MAX_TRAINABLE_PARAMETERS="$MAX_TRAINABLE_PARAMETERS" \
  ASI1_AGENTIC_TASK_TRAINING_MODE=lora \
  ASI1_AGENTIC_TASK_PUSH_RESULTS_S3="$PUSH_RESULTS_S3" \
  ASI1_AGENTIC_TASK_S3_ROOT="$S3_ROOT" \
  ASI1_AGENTIC_TASK_RCLONE_CONFIG="$RCLONE_CONFIG" \
    bash scripts/run_asi1_agentic_grpo_from_env.sh
}

main() {
  mkdir -p "$(dirname "$BOOT_LOG")"
  : > "$BOOT_LOG"
  log "__ASI1_GRPO_BOOT_START__"
  write_status starting ""
  command -v python3 >/dev/null || fail "missing_python3"
  RCLONE_BIN="$(ensure_rclone)"
  RCLONE_CONFIG="$(write_rclone_config)"
  export RCLONE_BIN RCLONE_CONFIG
  log "__ASI1_GRPO_S3_LIST__ $S3_ROOT"
  "$RCLONE_BIN" lsf "$S3_ROOT/scripts" --config "$RCLONE_CONFIG" --s3-no-check-bucket | head -n 20 | tee -a "$BOOT_LOG"
  mkdir -p "$REMOTE_ROOT"
  log "__ASI1_GRPO_SYNC_FROM_S3__ $REMOTE_ROOT"
  "$RCLONE_BIN" copy "$S3_ROOT" "$REMOTE_ROOT" \
    --config "$RCLONE_CONFIG" --s3-no-check-bucket \
    --exclude ".git/**" --exclude "outputs/**" --exclude "models/**" --exclude ".venv/**" --exclude "__pycache__/**" \
    --transfers 8 --fast-list | tee -a "$BOOT_LOG"
  cd "$REMOTE_ROOT"
  log "__ASI1_GRPO_PREFLIGHT__"
  python3 -m py_compile training/agentic_grpo_trainer.py training/grpo_trainer.py training/qwen_sft_peft.py
  test -f "$BENCHMARK_FILE" || fail "missing_benchmark=$BENCHMARK_FILE"
  test -f "$ONLINE_EVAL_BENCHMARK_FILE" || fail "missing_online_eval_benchmark=$ONLINE_EVAL_BENCHMARK_FILE"
  resolve_model
  log "__ASI1_GRPO_MODEL__ $MODEL_NAME"
  log "__ASI1_GRPO_SMOKE_START__"
  launch_runner "$SMOKE_OUTPUT_DIR" "/tmp/qwen36_35b_a3b_agentic_grpo_asi1_smoke_${TIMESTAMP}.log" 1 8 128 2048 2 1 1 1
  verify_run_artifacts "$SMOKE_OUTPUT_DIR" smoke
  write_status smoke_completed ""
  log "__ASI1_GRPO_FULL_START__"
  launch_runner "$FULL_OUTPUT_DIR" "/tmp/qwen36_35b_a3b_agentic_grpo_asi1_full_${TIMESTAMP}.log" "$FULL_GRPO_STEPS" "$FULL_GROUP_SIZE" "$FULL_MAX_NEW_TOKENS" "$FULL_MAX_SEQ_LENGTH" "$FULL_MAX_TURNS" "$FULL_ONLINE_EVAL_EVERY_STEPS" "$FULL_ONLINE_EVAL_MAX_TASKS" "$CHECKPOINT_EVERY_STEPS"
  verify_run_artifacts "$FULL_OUTPUT_DIR" full
  write_status completed ""
  log "__ASI1_GRPO_DONE__"
}

main "$@"
