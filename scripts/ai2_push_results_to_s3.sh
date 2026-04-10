#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
S3_ROOT="nm-aihuanxin:jtdlp-3ed7854b946a47b1a49ad754baa76cd3/quantum-qwen25-coder-main"

cd "$ROOT_DIR"

DRY_RUN=0
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=1
  shift
fi

REMOTE_PATHS=("$@")
if [[ ${#REMOTE_PATHS[@]} -eq 0 ]]; then
  REMOTE_PATHS=(outputs)
fi

for remote_path in "${REMOTE_PATHS[@]}"; do
  remote_parent="$(dirname "$remote_path")"
  if [[ "$remote_parent" == "." ]]; then
    remote_file_dest="$S3_ROOT"
  else
    remote_file_dest="$S3_ROOT/$remote_parent"
  fi
  REMOTE_CMD="cd /root/root/work/quantum-gpt && if [[ -d '$remote_path' ]]; then rclone copy '$remote_path' '$S3_ROOT/$remote_path' --s3-no-check-bucket --progress"
  if [[ $DRY_RUN -eq 1 ]]; then
    REMOTE_CMD+=" --dry-run"
  fi
  REMOTE_CMD+="; elif [[ -f '$remote_path' ]]; then rclone copy '$remote_path' '$remote_file_dest' --s3-no-check-bucket --progress"
  if [[ $DRY_RUN -eq 1 ]]; then
    REMOTE_CMD+=" --dry-run"
  fi
  REMOTE_CMD+="; else echo 'skip missing: $remote_path'; fi"
  JSON_OUT="$(bash scripts/ai2_fast_path.sh exec "$REMOTE_CMD")"
  python3 - <<'PY' "$JSON_OUT"
import json
import sys

payload = json.loads(sys.argv[1])
text = payload.get('after', '') or ''
bad_markers = ('ERROR :', 'NOTICE: Failed', 'AccessDenied', 'Failed to')
if any(marker in text for marker in bad_markers):
    raise SystemExit(text)
PY
done
