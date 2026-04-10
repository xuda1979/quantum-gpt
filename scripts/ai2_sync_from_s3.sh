#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
S3_ROOT="nm-aihuanxin:jtdlp-3ed7854b946a47b1a49ad754baa76cd3/quantum-qwen25-coder-main"
REMOTE_ROOT="${AI2_REMOTE_ROOT:-/root/root/work/quantum-gpt}"

cd "$ROOT_DIR"

usage() {
  cat >&2 <<'EOF'
Usage:
  scripts/ai2_sync_from_s3.sh [--dry-run]
EOF
  exit 1
}

if [[ $# -gt 1 ]] || [[ $# -eq 1 && "${1:-}" != "--dry-run" ]]; then
  usage
fi

RCLONE_CMD="rclone sync $S3_ROOT $REMOTE_ROOT --exclude 'outputs/**' --exclude 'models/**' --exclude 'artifacts/**' --exclude 'memory/**' --exclude 'logs/**' --exclude 'browser-automation/profile/**' --exclude 'browser-automation/*.png' --exclude 'browser-automation/*.html' --exclude 'browser-automation/*.json' --progress"
if [[ "${1:-}" == "--dry-run" ]]; then
  RCLONE_CMD+=" --dry-run"
fi

REMOTE_LOG="/tmp/ai2_sync_from_s3.log"
JSON_OUT="$(bash scripts/ai2_fast_path.sh exec "log='$REMOTE_LOG'; { $RCLONE_CMD; } >\"\$log\" 2>&1; rc=\$?; echo __AI2_SYNC_FROM_S3_RC__:\$rc; tail -n 40 \"\$log\"")"

python3 - <<'PY' "$JSON_OUT"
import json
import re
import sys

payload = json.loads(sys.argv[1])
text = '\n'.join(str(payload.get(key, '')) for key in ('output', 'after', 'before'))
matches = re.findall(r'__AI2_SYNC_FROM_S3_RC__:(\d+)', text)
bad_markers = ('ERROR :', 'NOTICE: Failed', 'AccessDenied', 'Failed to')
if not matches:
    raise SystemExit(f'Did not observe sync completion marker.\n{text}')
if any(marker in text for marker in bad_markers) or any(code != '0' for code in matches):
    raise SystemExit(text)
PY
