#!/usr/bin/env bash
set -euo pipefail

# Pull the quantum-gpt repo snapshot from S3 onto the Huanxin ai3 environment.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT_DIR/scripts/ai3_nm_s3_env.sh"

S3_ROOT="${AI3_NM_S3_ROOT:-${HUANXIN_S3_ROOT:-nm-aihuanxin:jtdlp-3ed7854b946a47b1a49ad754baa76cd3/quantum-qwen25-coder-main}}"
REMOTE_ROOT="${AI3_REMOTE_ROOT:-/root/work/quantum-gpt}"

cd "$ROOT_DIR"

usage() {
  cat >&2 <<'EOFU'
Usage:
  scripts/ai3_sync_from_s3.sh [--dry-run]
EOFU
  exit 1
}

if [[ $# -gt 1 ]] || [[ $# -eq 1 && "${1:-}" != "--dry-run" ]]; then
  usage
fi

REMOTE_CONFIG="/tmp/nm-aihuanxin-rclone.conf"
REMOTE_SETUP="$(ai3_remote_nm_rclone_setup_script "$REMOTE_CONFIG")"
RCLONE_CMD="$REMOTE_SETUP mkdir -p '$REMOTE_ROOT' && rclone sync '$S3_ROOT' '$REMOTE_ROOT' --config '$REMOTE_CONFIG' --s3-no-check-bucket --fast-list --exclude 'outputs/**' --exclude 'models/**' --exclude 'artifacts/**' --exclude 'memory/**' --exclude 'logs/**' --exclude 'browser-automation/profile/**' --exclude 'browser-automation/*.png' --exclude 'browser-automation/*.html' --exclude 'browser-automation/*.json' --progress"
if [[ "${1:-}" == "--dry-run" ]]; then
  RCLONE_CMD+=" --dry-run"
fi

REMOTE_LOG="/tmp/ai3_sync_from_s3.log"
JSON_OUT="$(bash scripts/huanxin_shell.sh ai3 "log='$REMOTE_LOG'; { $RCLONE_CMD; } >\"\$log\" 2>&1; rc=\$?; echo __AI3_SYNC_FROM_S3_RC__:\$rc; tail -n 40 \"\$log\"")"

python3 - <<'PY' "$JSON_OUT"
import json
import re
import sys

payload = json.loads(sys.argv[1])
text = "\n".join(str(payload.get(key, "")) for key in ("output", "after", "before"))
match = re.search(r"__AI3_SYNC_FROM_S3_RC__:(\d+)", text)
bad_markers = ("ERROR :", "NOTICE: Failed", "AccessDenied", "Failed to")
if not match:
    raise SystemExit(f"missing __AI3_SYNC_FROM_S3_RC__ marker; raw text:\n{text}")
rc = int(match.group(1))
if any(marker in text for marker in bad_markers) or rc != 0:
    raise SystemExit(text)
print(text)
PY
