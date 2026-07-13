#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REMOTE_ROOT="${AI_REMOTE_ROOT:-/root/software/quantum-gpt}"
POLL_INTERVAL_SECONDS="${POLL_INTERVAL_SECONDS:-300}"
ONCE=0

usage() {
  cat >&2 <<'EOF'
Usage:
  scripts/watch_ai_checkpoints_to_s3.sh <remote-output-dir> [--interval-seconds <n>] [--once]

Examples:
  scripts/watch_ai_checkpoints_to_s3.sh outputs/qwen36-35b-a3b-agentic-grpo-v1-20260515T000000Z
  scripts/watch_ai_checkpoints_to_s3.sh outputs/qwen36-35b-a3b-agentic-grpo-v1-20260515T000000Z --once
EOF
  exit 1
}

if [[ $# -lt 1 ]]; then
  usage
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
      echo "unknown arg: $1" >&2
      usage
      ;;
  esac
done

if [[ "$REMOTE_OUTPUT_DIR" == /* ]]; then
  REMOTE_OUTPUT_REL="${REMOTE_OUTPUT_DIR#${REMOTE_ROOT}/}"
else
  REMOTE_OUTPUT_REL="$REMOTE_OUTPUT_DIR"
fi

probe_remote_latest_checkpoint() {
  local json_out remote_cmd
  remote_cmd="cd '$REMOTE_ROOT' && if [[ -f '$REMOTE_OUTPUT_REL/latest_checkpoint.json' ]]; then echo __AI_LATEST_CHECKPOINT_BEGIN__; cat '$REMOTE_OUTPUT_REL/latest_checkpoint.json'; echo __AI_LATEST_CHECKPOINT_END__; else echo __AI_LATEST_CHECKPOINT_MISSING__; fi"
  json_out="$(bash "$ROOT_DIR/scripts/ai_shell.sh" "$remote_cmd")"
  python3 - <<'PY' "$json_out"
import json
import re
import sys

payload = json.loads(sys.argv[1])
text = "\n".join(str(payload.get(key, "")) for key in ("output", "after", "before"))
if "__AI_LATEST_CHECKPOINT_MISSING__" in text:
    print(json.dumps({"exists": False}))
    raise SystemExit(0)
match = re.search(
    r"__AI_LATEST_CHECKPOINT_BEGIN__\s*(\{.*?\})\s*__AI_LATEST_CHECKPOINT_END__",
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
  bash "$ROOT_DIR/scripts/ai_push_results_to_s3.sh" \
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
      printf '{"timestamp_utc":"%s","stage":"ai_checkpoint_backup","step":%s,"remote_output_dir":"%s"}\n' \
        "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
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
