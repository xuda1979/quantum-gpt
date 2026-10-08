#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_PATH="${LOG_PATH:-/tmp/quantum_yunwu_s3_bridge.log}"
S3_ROOT="${YUNWU_RELAY_S3_ROOT:-nm-aihuanxin:jtdlp-3ed7854b946a47b1a49ad754baa76cd3/quantum-qwen25-coder-main}"
REQUEST_PREFIX="${YUNWU_RELAY_REQUEST_PREFIX:-relay/yunwu/requests}"
RESPONSE_PREFIX="${YUNWU_RELAY_RESPONSE_PREFIX:-relay/yunwu/responses}"

cd "$ROOT_DIR"

if [[ -z "${YUNWU_API_KEY:-${YUNWU_OPENAI_API_KEY:-}}" ]]; then
  echo "MISSING_YUNWU_API_KEY"
  exit 1
fi

rm -f "$LOG_PATH"
nohup python3 scripts/yunwu_s3_bridge.py \
  --s3-root "$S3_ROOT" \
  --request-prefix "$REQUEST_PREFIX" \
  --response-prefix "$RESPONSE_PREFIX" \
  >"$LOG_PATH" 2>&1 </dev/null &

echo "YUNWU_S3_BRIDGE_PID:$!"
