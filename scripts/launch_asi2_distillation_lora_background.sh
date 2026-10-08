#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

POLL_SEC="${ASI2_BG_POLL_SEC:-90}"
MAX_ATTEMPTS="${ASI2_BG_MAX_ATTEMPTS:-0}"
TASK_PREFIX="${ASI2_BG_TASK_PREFIX:-a2sftbg}"
STATUS_FILE="${ASI2_BG_STATUS_FILE:-$ROOT_DIR/logs/asi2_distill_bg_status.log}"
ATTEMPT_LOG_DIR="${ASI2_BG_ATTEMPT_LOG_DIR:-$ROOT_DIR/logs/asi2_distill_bg_attempts}"
LAST_JSON="${ASI2_BG_LAST_JSON:-$ROOT_DIR/reports/asi2_distill_bg_last_submit.json}"

mkdir -p "$(dirname "$STATUS_FILE")" "$ATTEMPT_LOG_DIR" "$(dirname "$LAST_JSON")"

log() {
  printf '%s %s\n' "$(date -Iseconds)" "$*" | tee -a "$STATUS_FILE"
}

attempt=0
while true; do
  attempt="$((attempt + 1))"
  stamp="$(date +%m%d%H%M)"
  task_name="${TASK_PREFIX}-${stamp}"
  out_json="$ATTEMPT_LOG_DIR/${task_name}.json"
  out_log="$ATTEMPT_LOG_DIR/${task_name}.log"

  log "attempt=${attempt} task=${task_name} submit_start"

  if ASI2_DISTILL_TASK_NAME="$task_name" \
      ASI2_DISTILL_ARTIFACT_STEM="$(basename "${out_json%.json}")" \
      bash scripts/submit_asi2_distillation_lora_sft_task.sh --submit \
      >"$out_log" 2>&1; then
    latest_json="$(ls -1t browser-automation/huanxin-submit-task-run-asi2-distillation-lora-sft*.json browser-automation/"$(basename "${out_json%.json}")".json 2>/dev/null | head -n 1 || true)"
    if [[ -n "$latest_json" && -f "$latest_json" ]]; then
      cp "$latest_json" "$out_json"
      cp "$latest_json" "$LAST_JSON"
      if python3 - <<'PY' "$latest_json"
import json, sys
payload = json.loads(open(sys.argv[1], encoding="utf-8").read())
ok = bool(payload.get("submitResult", {}).get("submitted"))
raise SystemExit(0 if ok else 1)
PY
      then
        log "attempt=${attempt} task=${task_name} submit_success artifact=$out_json"
        exit 0
      fi
    fi
    log "attempt=${attempt} task=${task_name} submit_returned_without_admission artifact=$out_json"
  else
    rc=$?
    log "attempt=${attempt} task=${task_name} submit_command_failed rc=${rc} log=$out_log"
  fi

  if [[ "$MAX_ATTEMPTS" -gt 0 && "$attempt" -ge "$MAX_ATTEMPTS" ]]; then
    log "attempt=${attempt} max_attempts_reached"
    exit 124
  fi

  log "attempt=${attempt} sleep_sec=${POLL_SEC}"
  sleep "$POLL_SEC"
done
