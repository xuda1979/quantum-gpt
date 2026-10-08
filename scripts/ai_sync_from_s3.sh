#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT_DIR/scripts/iner_s3_env.sh"

S3_ROOT="${HUANXIN_S3_ROOT:-$INER_S3_ROOT}"
ENV_NAME="${HUANXIN_SYNC_ENV:-AI}"
REMOTE_ROOT="${HUANXIN_SYNC_REMOTE_ROOT:-${AI_REMOTE_ROOT:-/root/software/quantum-gpt}}"

cd "$ROOT_DIR"

usage() {
  cat >&2 <<'EOF'
Usage:
  scripts/ai_sync_from_s3.sh [--env <env-name>] [--remote-root <path>] [--dry-run]
EOF
  exit 1
}

DRY_RUN=0
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
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --help|-h)
      usage
      ;;
    *)
      echo "Unknown arg: $1" >&2
      usage
      ;;
  esac
done

if [[ -z "$ENV_NAME" || -z "$REMOTE_ROOT" ]]; then
  usage
fi

REMOTE_CONFIG="/tmp/iner-rclone.conf"
REMOTE_SETUP="$(iner_remote_rclone_setup_script "$REMOTE_CONFIG")"
REMOTE_RCLONE_BIN="${AI_REMOTE_RCLONE_BIN:-/root/work/filestorage/rclone-bin}"
RCLONE_CMD="$REMOTE_SETUP
mkdir -p '$REMOTE_ROOT'
$REMOTE_RCLONE_BIN sync '$S3_ROOT' '$REMOTE_ROOT' --config '$REMOTE_CONFIG' --s3-no-check-bucket --exclude 'outputs/**' --exclude 'models/**' --exclude 'artifacts/**' --exclude 'memory/**' --exclude 'logs/**' --exclude 'browser-automation/profile/**' --exclude 'browser-automation/*.png' --exclude 'browser-automation/*.html' --exclude 'browser-automation/*.json' --progress"
if [[ "$DRY_RUN" == "1" ]]; then
  RCLONE_CMD+=" --dry-run"
fi

REMOTE_LOG="/tmp/ai_sync_from_s3.log"
JSON_OUT="$(bash scripts/huanxin_shell.sh "$ENV_NAME" "log='$REMOTE_LOG'; { $RCLONE_CMD; } >\"\$log\" 2>&1; rc=\$?; echo __AI_SYNC_FROM_S3_RC__:\$rc; tail -n 40 \"\$log\"")"

python3 - <<'PY' "$JSON_OUT"
import json
import re
import sys

payload = json.loads(sys.argv[1])
text = "\n".join(str(payload.get(key, "")) for key in ("output", "after", "before"))
matches = re.findall(r"__AI_SYNC_FROM_S3_RC__:(\d+)", text)
bad_markers = ("ERROR :", "NOTICE: Failed", "AccessDenied", "Failed to")
if not matches:
    raise SystemExit(f"Did not observe sync completion marker.\n{text}")
if any(marker in text for marker in bad_markers) or any(code != "0" for code in matches):
    raise SystemExit(text)
PY
