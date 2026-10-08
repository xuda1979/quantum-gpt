#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOST="${AGENTIC_DASHBOARD_HOST:-127.0.0.1}"
PORT="${AGENTIC_DASHBOARD_PORT:-18882}"
LABEL="${AGENTIC_DASHBOARD_LAUNCHD_LABEL:-com.quantumgpt.agentic-dashboard}"
LOG_PATH="${AGENTIC_DASHBOARD_LOG_PATH:-$ROOT_DIR/logs/agentic_dashboard_${PORT}.log}"
ENV_NAME="${AGENTIC_DASHBOARD_HUANXIN_ENV:-ASI1}"
REMOTE_LOG_RUN="${AGENTIC_DASHBOARD_REMOTE_LOG_RUN:-}"

usage() {
  cat <<'EOF'
Usage:
  scripts/start_agentic_training_dashboard.sh [--host <host>] [--port <port>] [--env <huanxin-env>] [--remote-log-run <env:remote:local>] [--stop]

Starts the local agentic training dashboard as a durable macOS launchctl job.
EOF
}

STOP=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --host)
      HOST="${2:-}"
      shift 2
      ;;
    --port)
      PORT="${2:-}"
      shift 2
      ;;
    --env|--huanxin-env)
      ENV_NAME="${2:-}"
      shift 2
      ;;
    --remote-log-run)
      REMOTE_LOG_RUN="${2:-}"
      shift 2
      ;;
    --stop)
      STOP=1
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown arg: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

mkdir -p "$(dirname "$LOG_PATH")"

if [[ "$STOP" == "1" ]]; then
  launchctl remove "$LABEL" 2>/dev/null || true
  exit 0
fi

launchctl remove "$LABEL" 2>/dev/null || true
CMD=(/usr/bin/python3 "$ROOT_DIR/scripts/serve_agentic_training_dashboard.py" \
  --host "$HOST" \
  --port "$PORT" \
  --outputs-dir "$ROOT_DIR/outputs" \
  --reports-dir "$ROOT_DIR/reports" \
  --data-dir "$ROOT_DIR/data" \
  --evals-dir "$ROOT_DIR/evals" \
  --docs-dir "$ROOT_DIR/docs" \
  --output "$ROOT_DIR/reports/agentic_training_dashboard.html" \
  --registry-output "$ROOT_DIR/reports/agentic_training_run_registry.json" \
  --huanxin-status "$ROOT_DIR/reports/huanxin_environment_status.json" \
  --limit 16 \
  --poll-seconds 5 \
  --refresh-huanxin-status \
  --huanxin-env "$ENV_NAME" \
  --huanxin-refresh-seconds 120 \
  --huanxin-timeout-sec 30)

if [[ -n "$REMOTE_LOG_RUN" ]]; then
  CMD+=(--remote-log-run "$REMOTE_LOG_RUN" --remote-log-refresh-seconds 30 --remote-log-timeout-sec 60)
fi

launchctl submit -l "$LABEL" -- "${CMD[@]}" >>"$LOG_PATH" 2>&1

for _ in {1..20}; do
  if curl -fsS --max-time 1 "http://$HOST:$PORT/status.json" >/dev/null; then
    echo "Dashboard ready: http://$HOST:$PORT/"
    exit 0
  fi
  sleep 0.5
done

echo "Dashboard did not become ready: http://$HOST:$PORT/" >&2
exit 1
