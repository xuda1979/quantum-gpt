#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
S3_ROOT="nm-aihuanxin:jtdlp-3ed7854b946a47b1a49ad754baa76cd3/quantum-qwen25-coder-main"
RCLONE_BIN="${RCLONE_BIN:-$(command -v rclone || true)}"
AI2_DAEMON_URL="${AI2_DAEMON_URL:-http://127.0.0.1:19002}"
POLL_SECONDS="${POLL_SECONDS:-60}"
WAIT_MS="${WAIT_MS:-300000}"
MODEL_SUBDIR="${1:-OmniCoder-9B}"

if [[ -z "$RCLONE_BIN" && -x /Users/daxu/homebrew/bin/rclone ]]; then
  RCLONE_BIN=/Users/daxu/homebrew/bin/rclone
fi

if [[ -z "$RCLONE_BIN" || ! -x "$RCLONE_BIN" ]]; then
  echo 'rclone not found. Set RCLONE_BIN or install rclone.' >&2
  exit 1
fi

if [[ "$MODEL_SUBDIR" == /* ]]; then
  echo "model-subdir must be relative, for example: OmniCoder-9B" >&2
  exit 1
fi

cd "$ROOT_DIR"

S3_MODEL_DIR="$S3_ROOT/models/$MODEL_SUBDIR"
SMOKE_CMD="cd /root/work/quantum-gpt && python3 training/huanxin_cpu_smoke.py --model-name models/$MODEL_SUBDIR --dataset data/seed/splits-auto-seed/train.jsonl > /tmp/omnicoder-smoke.log 2>&1; rc=\$?; echo __OMNI_SMOKE_RC__:\$rc; tail -n 200 /tmp/omnicoder-smoke.log"

while true; do
  ts="$(date '+%F %T %Z')"
  if bash scripts/model_snapshot_s3_ready.sh "$MODEL_SUBDIR" >/dev/null 2>&1; then
    echo "[$ts] detected a complete model snapshot for $MODEL_SUBDIR in S3; starting ai2 model sync"
    bash scripts/ai2_sync_model_from_s3.sh "$MODEL_SUBDIR"
    echo "[$ts] ai2 model sync completed for $MODEL_SUBDIR"
    echo "[$ts] launching ai2 local-path smoke for $MODEL_SUBDIR"
    curl -sS -X POST "$AI2_DAEMON_URL/exec" \
      -H 'Content-Type: application/json' \
      -d "$(python3 - <<'PY' "$SMOKE_CMD" "$WAIT_MS"
import json
import sys
print(json.dumps({"command": sys.argv[1], "waitMs": int(sys.argv[2])}))
PY
    )"
    exit 0
  fi
  echo "[$ts] waiting for a complete model snapshot in $S3_MODEL_DIR"
  sleep "$POLL_SECONDS"
done
