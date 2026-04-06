#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
S3_ROOT="nm-aihuanxin:jtdlp-3ed7854b946a47b1a49ad754baa76cd3/quantum-qwen25-coder-main"
REMOTE_ROOT="/root/root/work/quantum-gpt"

usage() {
  cat >&2 <<'EOF'
Usage:
  scripts/ai2_sync_model_from_s3.sh <model-subdir> [--dry-run]

Examples:
  scripts/ai2_sync_model_from_s3.sh OmniCoder-9B
  scripts/ai2_sync_model_from_s3.sh OmniCoder-9B --dry-run
EOF
  exit 1
}

if [[ $# -lt 1 ]]; then
  usage
fi

MODEL_SUBDIR="$1"
shift

if [[ "$MODEL_SUBDIR" == /* ]]; then
  echo "model-subdir must be relative, for example: OmniCoder-9B" >&2
  exit 1
fi

DRY_RUN=0
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=1
  shift
fi

if [[ $# -gt 0 ]]; then
  usage
fi

cd "$ROOT_DIR"

S3_MODEL_DIR="$S3_ROOT/models/$MODEL_SUBDIR"
REMOTE_MODEL_DIR="$REMOTE_ROOT/models/$MODEL_SUBDIR"
RCLONE_CMD="mkdir -p '$REMOTE_MODEL_DIR' && rclone sync '$S3_MODEL_DIR' '$REMOTE_MODEL_DIR' --exclude '.cache/**' --exclude '__pycache__/**' --exclude '*.pyc' --fast-list --progress"

if [[ $DRY_RUN -eq 1 ]]; then
  RCLONE_CMD+=" --dry-run"
fi

REMOTE_LOG="/tmp/ai2_sync_model_from_s3.log"
JSON_OUT="$(HUANXIN_USE_DAEMON=1 bash scripts/ai2_shell.sh "log='$REMOTE_LOG'; { $RCLONE_CMD; } >\"\$log\" 2>&1; rc=\$?; echo __AI2_SYNC_MODEL_FROM_S3_RC__:\$rc; tail -n 40 \"\$log\"")"

python3 - <<'PY' "$JSON_OUT" "$MODEL_SUBDIR"
import json
import re
import sys

payload = json.loads(sys.argv[1])
model_subdir = sys.argv[2]
text = '\n'.join(str(payload.get(k, '')) for k in ('output', 'after', 'before'))
matches = re.findall(r'__AI2_SYNC_MODEL_FROM_S3_RC__:(\d+)', text)
bad_markers = ('ERROR :', 'NOTICE: Failed', 'AccessDenied', 'Failed to')
if not matches:
    raise SystemExit(f'Did not observe model sync completion marker for {model_subdir}.\n{text}')
if any(marker in text for marker in bad_markers) or any(code != '0' for code in matches):
    raise SystemExit(text)
PY
