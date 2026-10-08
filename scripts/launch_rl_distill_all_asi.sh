#!/usr/bin/env bash
# Launch the RL-with-verifier loop on all available ASI environments in parallel.
#
#   ASI1 -> Qwen3.6-27B  (2 NPUs, port 8007)
#   ASI2 -> Qwen3.6-35B-A3B (2 NPUs, port 8008)
#   ASI3 -> Qwen3.6-35B-A3B (2 NPUs, port 8009)  [if ASI3 env vars are set]
#
# All adapters, buffers, and checkpoints are written to NAS
# ($NAS_ROOT/outputs/...). Each environment runs its own self-contained
# orchestrator (scripts/asi{1,2,3}_launch_rl_distill_*_2npu.sh) which
# handles vLLM lifecycle, pipeline rounds, trainer bursts, eval gates,
# and weakness-report generation between batches.
#
# Usage:
#   bash scripts/launch_rl_distill_all_asi.sh launch
#   bash scripts/launch_rl_distill_all_asi.sh status
#   bash scripts/launch_rl_distill_all_asi.sh stop
#
# Required env (per environment):
#   GLM52_API_BASE, GLM52_API_KEY
#   ASI1_SSH_HOST (or run locally on ASI1), ASI2_SSH_HOST, ASI3_SSH_HOST (optional)
#   Or set RUN_LOCAL=1 to run all three on the current host (needs 6 NPUs).
#
# Tunables (passed through to each launcher):
#   BUFFER_TARGET_PER_ROUND=100  (batch size)
#   TRAINER_CHECKPOINT_SECONDS=7200  (2-hour checkpoint cadence)
#   PASS_RATE_STOP=0.99  (stop when student pass-rate >= 99%)
#   PASS_RATE_WINDOW=100

set -euo pipefail

ACTION="${1:-launch}"
NAS_ROOT="${NAS_ROOT:-/root/work/software/quantum-gpt}"
RUN_LOCAL="${RUN_LOCAL:-0}"

# Common env exported to all child launchers.
export BUFFER_TARGET_PER_ROUND="${BUFFER_TARGET_PER_ROUND:-100}"
export TRAINER_CHECKPOINT_SECONDS="${TRAINER_CHECKPOINT_SECONDS:-7200}"
export PASS_RATE_STOP="${PASS_RATE_STOP:-0.99}"
export PASS_RATE_WINDOW="${PASS_RATE_WINDOW:-100}"

launch_asi1() {
  echo "[launch_all] starting ASI1 (Qwen3.6-27B)"
  if [[ "$RUN_LOCAL" == "1" ]]; then
    ASCEND_RT_VISIBLE_DEVICES=0,1 bash scripts/asi1_launch_rl_distill_27b_2npu.sh launch
  else
    ssh "${ASI1_SSH_HOST}" "cd $NAS_ROOT && bash scripts/asi1_launch_rl_distill_27b_2npu.sh launch" &
  fi
}

launch_asi2() {
  echo "[launch_all] starting ASI2 (Qwen3.6-35B-A3B)"
  if [[ "$RUN_LOCAL" == "1" ]]; then
    ASCEND_RT_VISIBLE_DEVICES=2,3 bash scripts/asi2_launch_rl_distill_35b_2npu.sh launch
  else
    ssh "${ASI2_SSH_HOST}" "cd $NAS_ROOT && bash scripts/asi2_launch_rl_distill_35b_2npu.sh launch" &
  fi
}

launch_asi3() {
  if [[ -z "${ASI3_SSH_HOST:-}" ]]; then
    echo "[launch_all] ASI3_SSH_HOST not set; skipping ASI3"
    return 0
  fi
  echo "[launch_all] starting ASI3 (Qwen3.6-35B-A3B)"
  if [[ "$RUN_LOCAL" == "1" ]]; then
    ASCEND_RT_VISIBLE_DEVICES=4,5 bash scripts/asi3_launch_rl_distill_35b_2npu.sh launch
  else
    ssh "${ASI3_SSH_HOST}" "cd $NAS_ROOT && bash scripts/asi3_launch_rl_distill_35b_2npu.sh launch" &
  fi
}

case "$ACTION" in
  launch)
    launch_asi1
    launch_asi2
    launch_asi3
    wait
    echo "[launch_all] all environments launched"
    ;;
  status)
    for env in asi1 asi2 asi3; do
      script="scripts/${env}_launch_rl_distill_$([[ $env == asi1 ]] && echo 27b || echo 35b)_2npu.sh"
      echo "=== $env status ==="
      bash "$script" status 2>&1 || true
    done
    ;;
  stop)
    for env in asi1 asi2 asi3; do
      script="scripts/${env}_launch_rl_distill_$([[ $env == asi1 ]] && echo 27b || echo 35b)_2npu.sh"
      echo "=== stopping $env ==="
      bash "$script" stop 2>&1 || true
    done
    ;;
  *)
    echo "usage: $0 {launch|status|stop}" >&2
    exit 2
    ;;
esac
