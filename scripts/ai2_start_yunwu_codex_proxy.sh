#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${AI2_REMOTE_ROOT:-/root/work/david/software/quantum-gpt}"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8011}"
LOG_PATH="${LOG_PATH:-/tmp/quantum_yunwu_codex_proxy.log}"
HEALTH_MODEL="${HEALTH_MODEL:-gpt-5.4}"

cd "$ROOT_DIR"

export LOCAL_CODEX_API_KEY="${LOCAL_CODEX_API_KEY:-dummy}"

if [[ -z "${YUNWU_API_KEY:-${YUNWU_OPENAI_API_KEY:-}}" ]]; then
  echo "MISSING_YUNWU_API_KEY"
  exit 1
fi

if curl --noproxy '*' -fsS "http://${HOST}:${PORT}/health" >/dev/null 2>&1; then
  echo "YUNWU_PROXY_ALREADY_RUNNING"
  exit 0
fi

rm -f "$LOG_PATH"
nohup python3 scripts/serve_yunwu_responses_proxy.py \
  --host "$HOST" \
  --port "$PORT" \
  --health-model "$HEALTH_MODEL" \
  >"$LOG_PATH" 2>&1 </dev/null &

echo "YUNWU_PROXY_PID:$!"
