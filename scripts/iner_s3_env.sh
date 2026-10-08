#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

export INER_S3_ENDPOINT="${INER_S3_ENDPOINT:-https://iner.aihuanxin.cn}"
export INER_ACCESS_KEY_ID="${INER_ACCESS_KEY_ID:-OXF5ar4y}"
export INER_S3_BUCKET="${INER_S3_BUCKET:-jtdlp-21b4208dde424e96b159362ef49c9c96}"
export INER_S3_ROOT="${INER_S3_ROOT:-iner:${INER_S3_BUCKET}/software/quantum-gpt}"

if [[ -z "${INER_SECRET_ACCESS_KEY:-}" ]]; then
  SKILL_FILE="$ROOT_DIR/skills/iner-s3-transfer/SKILL.md"
  if [[ -f "$SKILL_FILE" ]]; then
    INER_SECRET_ACCESS_KEY="$(
      sed -n 's/^- Secret access key: `\(.*\)`$/\1/p' "$SKILL_FILE" | head -n 1
    )"
    export INER_SECRET_ACCESS_KEY
  fi
fi

if [[ -z "${INER_SECRET_ACCESS_KEY:-}" ]]; then
  echo "INER_SECRET_ACCESS_KEY is required; set it or keep it in skills/iner-s3-transfer/SKILL.md." >&2
  exit 2
fi

iner_write_rclone_config() {
  local config_path="$1"
  cat > "$config_path" <<EOF
[iner]
type = s3
provider = Other
access_key_id = $INER_ACCESS_KEY_ID
secret_access_key = $INER_SECRET_ACCESS_KEY
endpoint = $INER_S3_ENDPOINT
acl = private
force_path_style = true
EOF
  chmod 600 "$config_path"
}

iner_remote_rclone_setup_script() {
  local config_path="${1:-/tmp/iner-rclone.conf}"
  python3 - <<'PY' "$config_path" "$INER_S3_ENDPOINT" "$INER_ACCESS_KEY_ID" "$INER_SECRET_ACCESS_KEY"
import shlex
import sys

config_path, endpoint, access_key_id, secret = sys.argv[1:]
content = f"""[iner]
type = s3
provider = Other
access_key_id = {access_key_id}
secret_access_key = {secret}
endpoint = {endpoint}
acl = private
force_path_style = true
"""
print(
    "umask 077; "
    f"cat > {shlex.quote(config_path)} <<'__INER_RCLONE_CONF__'\n"
    f"{content}"
    "__INER_RCLONE_CONF__\n"
)
PY
}
