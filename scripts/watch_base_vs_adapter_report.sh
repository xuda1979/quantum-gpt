#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage:
  scripts/watch_base_vs_adapter_report.sh <ai1|ai2> <remote-report-path> <local-report-path> [remote-log-path]

Environment variables:
  POLL_SECONDS   Sleep interval between polls. Default: 20
  MAX_POLLS      Maximum polls before exit. 0 means unlimited. Default: 0
  FETCH_MAX_BYTES  Max bytes allowed by huanxin_fetch_small_file.sh. Default: 2097152
  HUANXIN_WAIT_MS  Forwarded to remote shell helpers. Default: 180000

Example:
  scripts/watch_base_vs_adapter_report.sh \
    ai2 \
    reports/base_vs_adapter_outputs_interface_prefix_semantic_v4_true20_e2_rerun_20260327.json \
    reports/base_vs_adapter_outputs_interface_prefix_semantic_v4_true20_e2_rerun_20260327.json \
    /tmp/base-vs-adapter-true20-e2-rerun-20260327.log
EOF
  exit 1
}

if [[ $# -lt 3 || $# -gt 4 ]]; then
  usage
fi

ENV_NAME="$1"
REMOTE_REPORT_PATH="$2"
LOCAL_REPORT_PATH="$3"
REMOTE_LOG_PATH="${4:-}"

case "$ENV_NAME" in
  ai1|ai2) ;;
  *)
    echo "Unsupported env: $ENV_NAME" >&2
    exit 1
    ;;
esac

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

POLL_SECONDS="${POLL_SECONDS:-20}"
MAX_POLLS="${MAX_POLLS:-0}"
FETCH_MAX_BYTES="${FETCH_MAX_BYTES:-2097152}"
WAIT_MS="${HUANXIN_WAIT_MS:-180000}"

REMOTE_REPORT_Q="$(python3 - <<'PY' "$REMOTE_REPORT_PATH"
import shlex
import sys
print(shlex.quote(sys.argv[1]))
PY
)"

REMOTE_LOG_SNIPPET=""
if [[ -n "$REMOTE_LOG_PATH" ]]; then
  REMOTE_LOG_Q="$(python3 - <<'PY' "$REMOTE_LOG_PATH"
import shlex
import sys
print(shlex.quote(sys.argv[1]))
PY
)"
  REMOTE_LOG_SNIPPET="echo __LOGTAIL__ && if [ -f ${REMOTE_LOG_Q} ]; then tail -n 80 ${REMOTE_LOG_Q}; else echo __NO_LOG__; fi"
fi

build_remote_cmd() {
  cat <<EOF
cd /root/root/work/quantum-gpt && echo __REPORT__ && if [ -f ${REMOTE_REPORT_Q} ]; then stat -c '%n %s bytes %y' ${REMOTE_REPORT_Q}; echo __REPORT_PRESENT__; else echo MISSING; fi && ${REMOTE_LOG_SNIPPET}
EOF
}

poll_count=0
while true; do
  poll_count=$((poll_count + 1))
  echo "[watch_base_vs_adapter_report] poll=${poll_count} env=${ENV_NAME} report=${REMOTE_REPORT_PATH}" >&2

  remote_cmd="$(build_remote_cmd)"
  if ! JSON_OUT="$(
    HUANXIN_USE_DAEMON=1 HUANXIN_WAIT_MS="$WAIT_MS" \
      bash "$ROOT_DIR/scripts/huanxin_shell.sh" "$ENV_NAME" "$remote_cmd"
  )"; then
    echo "[watch_base_vs_adapter_report] daemon poll failed; retrying once with standalone transport" >&2
    JSON_OUT="$(
      HUANXIN_USE_DAEMON=0 HUANXIN_WAIT_MS="$WAIT_MS" \
        bash "$ROOT_DIR/scripts/huanxin_shell.sh" "$ENV_NAME" "$remote_cmd"
    )"
  fi

  python3 - <<'PY' "$JSON_OUT" "$poll_count"
import json
import re
import sys

payload = json.loads(sys.argv[1])
poll_count = sys.argv[2]
combined = "\n".join(str(payload.get(key, "")) for key in ("output", "after", "before"))

progress_lines = re.findall(r"^\[(?:base|adapter)\].*$", combined, re.M)
stat_line = re.search(r"^([^\n]+\s+\d+\s+bytes\s+.+)$", combined, re.M)
present = stat_line is not None

summary = {
    "poll": int(poll_count),
    "transport": payload.get("transport"),
    "duration_ms": payload.get("durationMs"),
    "report_present": present,
    "stat": stat_line.group(1) if stat_line else None,
    "last_progress": progress_lines[-1] if progress_lines else None,
}
print(json.dumps(summary, ensure_ascii=False))
PY

  if python3 - <<'PY' "$JSON_OUT"
import json
import re
import sys
payload = json.loads(sys.argv[1])
combined = "\n".join(str(payload.get(key, "")) for key in ("output", "after", "before"))
raise SystemExit(0 if re.search(r"^[^\n]+\s+\d+\s+bytes\s+.+$", combined, re.M) else 1)
PY
  then
    echo "[watch_base_vs_adapter_report] report detected; fetching ${REMOTE_REPORT_PATH}" >&2
    "$ROOT_DIR/scripts/huanxin_fetch_small_file.sh" \
      "$ENV_NAME" \
      "$REMOTE_REPORT_PATH" \
      "$LOCAL_REPORT_PATH" \
      "$FETCH_MAX_BYTES"
    echo "[watch_base_vs_adapter_report] summarizing ${LOCAL_REPORT_PATH}" >&2
    python3 "$ROOT_DIR/scripts/summarize_base_vs_adapter_report.py" "$LOCAL_REPORT_PATH"
    exit 0
  fi

  if [[ "$MAX_POLLS" != "0" && "$poll_count" -ge "$MAX_POLLS" ]]; then
    echo "[watch_base_vs_adapter_report] reached MAX_POLLS=${MAX_POLLS} without report" >&2
    exit 2
  fi

  sleep "$POLL_SECONDS"
done
