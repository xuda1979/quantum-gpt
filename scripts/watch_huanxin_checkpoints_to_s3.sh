#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_NAME="${HUANXIN_TRAINING_ENV:-}"
REMOTE_ROOT="${HUANXIN_TRAINING_REMOTE_ROOT:-}"
POLL_INTERVAL_SECONDS="${POLL_INTERVAL_SECONDS:-300}"
ONCE=0

usage() {
  cat >&2 <<'EOF'
Usage:
  scripts/watch_huanxin_checkpoints_to_s3.sh --env <env-name> <remote-output-dir> [--interval-seconds <n>] [--once]
EOF
  exit 2
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --env)
      ENV_NAME="${2:-}"
      shift 2
      ;;
    --remote-root)
      REMOTE_ROOT="${2:-}"
      shift 2
      ;;
    *)
      break
      ;;
  esac
done

if [[ -z "$ENV_NAME" || $# -lt 1 ]]; then
  usage
fi

if [[ -z "$REMOTE_ROOT" ]]; then
  case "$ENV_NAME" in
    ASI1) REMOTE_ROOT="/workspace/quantum-gpt" ;;
    *) REMOTE_ROOT="/root/work/quantum-gpt" ;;
  esac
fi

REMOTE_OUTPUT_DIR="$1"
shift

while [[ $# -gt 0 ]]; do
  case "$1" in
    --interval-seconds)
      POLL_INTERVAL_SECONDS="${2:-}"
      shift 2
      ;;
    --once)
      ONCE=1
      shift
      ;;
    *)
      usage
      ;;
  esac
done

if [[ "$REMOTE_OUTPUT_DIR" == /* ]]; then
  REMOTE_OUTPUT_REL="${REMOTE_OUTPUT_DIR#${REMOTE_ROOT}/}"
else
  REMOTE_OUTPUT_REL="$REMOTE_OUTPUT_DIR"
fi

SAFE_ENV="$(printf '%s' "$ENV_NAME" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9._-' '-')"

probe_remote_latest_checkpoint() {
  local json_out remote_cmd
  remote_cmd="cd '$REMOTE_ROOT' && if [[ -f '$REMOTE_OUTPUT_REL/latest_checkpoint.json' ]]; then echo __HX_LATEST_CHECKPOINT_BEGIN__; cat '$REMOTE_OUTPUT_REL/latest_checkpoint.json'; echo __HX_LATEST_CHECKPOINT_END__; else echo __HX_LATEST_CHECKPOINT_MISSING__; fi"
  json_out="$(bash "$ROOT_DIR/scripts/huanxin_env_shell.sh" --env "$ENV_NAME" "$remote_cmd")"
  python3 - <<'PY' "$json_out"
import json
import re
import sys

payload = json.loads(sys.argv[1])
text = "\n".join(str(payload.get(key, "")) for key in ("output", "after", "before"))
if "__HX_LATEST_CHECKPOINT_MISSING__" in text:
    print(json.dumps({"exists": False}))
    raise SystemExit(0)
match = re.search(
    r"__HX_LATEST_CHECKPOINT_BEGIN__\s*(\{.*?\})\s*__HX_LATEST_CHECKPOINT_END__",
    text,
    flags=re.DOTALL,
)
if not match:
    raise SystemExit(f"could not extract latest_checkpoint.json from shell output:\n{text}")
checkpoint = json.loads(match.group(1))
checkpoint["exists"] = True
print(json.dumps(checkpoint))
PY
}

push_snapshot() {
  bash "$ROOT_DIR/scripts/ai2_push_results_to_s3.sh" \
    "$REMOTE_OUTPUT_REL" \
    "$REMOTE_OUTPUT_REL/latest_checkpoint.json" \
    "$REMOTE_OUTPUT_REL/live_status.json" \
    "$REMOTE_OUTPUT_REL/online_eval_latest.json" \
    "$REMOTE_OUTPUT_REL/online_eval_history.jsonl" \
    "$REMOTE_OUTPUT_REL/grpo_step_metrics.jsonl"
}

last_pushed_step=""
while true; do
  checkpoint_json="$(probe_remote_latest_checkpoint)"
  checkpoint_exists="$(python3 - <<'PY' "$checkpoint_json"
import json, sys
print("1" if json.loads(sys.argv[1]).get("exists") else "0")
PY
)"

  if [[ "$checkpoint_exists" == "1" ]]; then
    checkpoint_step="$(python3 - <<'PY' "$checkpoint_json"
import json, sys
print(json.loads(sys.argv[1]).get("step", ""))
PY
)"
    if [[ -n "$checkpoint_step" && "$checkpoint_step" != "$last_pushed_step" ]]; then
      push_snapshot
      printf '{"timestamp_utc":"%s","stage":"huanxin_checkpoint_backup","env":"%s","step":%s,"remote_output_dir":"%s"}\n' \
        "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
        "$SAFE_ENV" \
        "$checkpoint_step" \
        "$REMOTE_OUTPUT_REL"
      last_pushed_step="$checkpoint_step"
    fi
  fi

  if [[ "$ONCE" == "1" ]]; then
    break
  fi
  sleep "$POLL_INTERVAL_SECONDS"
done
