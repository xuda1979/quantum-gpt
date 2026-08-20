#!/usr/bin/env bash
# =============================================================================
# ASI2 watchdog: recover -> deploy -> relaunch Qwen3.6-27B FV-GSPO GRPO
# training on the Huanxin box. The box is reachable ONLY through the browser
# daemon's /exec transport (http://127.0.0.1:19004/exec), whose auth is
# flaky (Safari SSO) and self-recovers once a human logs into Safari.
#
# Stages:
#   0. Wait for daemon auth: poll "echo DAEMON_OK" every 30s, up to
#      AUTH_WAIT_SECONDS (default 900). Exits non-zero with a clear AUTH_DOWN
#      message if auth never comes up (caller may retry later).
#   1. Deploy changed files to the box via /tmp/asi2_deploy_daemon.py
#      (chunked base64 through /exec, sha256-verified). Skips if the state
#      file already marks deploy done.
#   2. Check the trainer is not already running: remote launcher "status"
#      (grep "GRPO trainer: RUNNING"/"STOPPED"/"NOT RUNNING"). If RUNNING —
#      or recent train-log/metrics activity (dev-env PID namespace differs
#      from the task-run env, so a stale pid file must not trigger a
#      duplicate submit) — exit 0: nothing to do.
#   3. Submit a fresh task: unique timestamped ASI2_GRPO_TASK_NAME
#      (asi2-grpo-27b-selfeval-<ts>), ASI2_GRPO_STEPS=500 (full run),
#      ASI2_GRPO_CHECKPOINT_SECONDS=3600. Success = the submit tool's JSON
#      output carries "ok": true. On failure print the output tail, exit 1.
#   4. Verify the launch on the box: poll every 60s up to VERIFY_WAIT_SECONDS
#      (default 1200). Tail the newest grpo_train_*.log and watch
#      grpo_step_metrics.jsonl growth in the newest outputs/grpo-27b-selfeval-*
#      dir — gated to THIS launch via a marker file touched right after
#      submit (avoids mistaking a stale output dir from the previous run for
#      progress). Reports the newest stage markers
#      (step_begin/generation_done/logprob_done/eval_done/train_logprob_done/
#      backward_done). Exit 0 when the first step record appears or the log
#      shows a real loss.
#
# Usage:
#   bash scripts/asi2_watchdog_relaunch.sh [--dry-run] [--force-deploy]
#                                           [--state <file>]
#
# Options:
#   --dry-run       print the plan for each stage, execute nothing, exit 0
#   --force-deploy  re-run stage 1 even if the state file says deployed
#   --state <file>  state file path (default /tmp/asi2_relaunch_state.json)
#
# Env overrides:
#   AUTH_WAIT_SECONDS    (900)   stage 0 wait budget
#   VERIFY_WAIT_SECONDS  (1200)  stage 4 poll budget
#   ASI2_GRPO_REMOTE_ROOT (/root/work/software/quantum-gpt)
#   ASI2_DAEMON_URL      (http://127.0.0.1:19004/exec)
#
# Idempotency: stage 1 skips when state says deployed; stage 2 exits 0 when
# the trainer is live; stage 3 always generates a unique task name (a re-run
# after an external reap is the normal watchdog loop); stage 4 exits 0 once
# verified. This script never runs git commands on the box.
# =============================================================================
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

DAEMON="${ASI2_DAEMON_URL:-http://127.0.0.1:19004/exec}"
REMOTE_ROOT="${ASI2_GRPO_REMOTE_ROOT:-/root/work/software/quantum-gpt}"
AUTH_WAIT_SECONDS="${AUTH_WAIT_SECONDS:-900}"
VERIFY_WAIT_SECONDS="${VERIFY_WAIT_SECONDS:-1200}"
STATE_FILE="${ASI2_RELAUNCH_STATE:-/tmp/asi2_relaunch_state.json}"

DRY_RUN=0
FORCE_DEPLOY=0

DEPLOY_FILES=(
  training/grpo_trainer.py
  training/grpo_utils.py
  scripts/asi2_launch_grpo_27b_selfeval.sh
  scripts/fv_gspo_repair_sidecar.sh
  scripts/submit_asi2_grpo_27b_selfeval_task.sh
  configs/rl/qwen36_27b_fv_gspo_asi2.json
)

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

log() { printf '%s [asi2_watchdog] %s\n' "$(date '+%Y-%m-%dT%H:%M:%S%z')" "$*"; }

usage() {
  cat <<'EOF'
ASI2 watchdog: recover -> deploy -> relaunch Qwen3.6-27B FV-GSPO GRPO
training on the Huanxin box (transport: browser daemon /exec on 127.0.0.1:19004).

Stages:
  0. Wait for daemon auth (poll "echo DAEMON_OK" every 30s, up to
     AUTH_WAIT_SECONDS=900); exit 1 with AUTH_DOWN if never OK.
  1. Deploy changed files via /tmp/asi2_deploy_daemon.py (sha256-verified);
     skips if the state file already marks deploy done.
  2. Remote launcher status: exit 0 if trainer RUNNING or fresh activity.
  3. Submit unique timestamped task (GRPO_STEPS=500, CHECKPOINT_SECONDS=3600);
     success marker = '"ok": true' in submit output.
  4. Verify launch: poll newest grpo_train_*.log + grpo_step_metrics.jsonl
     growth (gated to this launch via a marker file); exit 0 on first step
     record or a real loss.

Usage:
  bash scripts/asi2_watchdog_relaunch.sh [--dry-run] [--force-deploy] [--state <file>]

Options:
  --dry-run       print the plan for each stage, execute nothing, exit 0
  --force-deploy  re-run stage 1 even if the state file says deployed
  --state <file>  state file path (default /tmp/asi2_relaunch_state.json)
  --help|-h       show this help

Env overrides:
  AUTH_WAIT_SECONDS=900  VERIFY_WAIT_SECONDS=1200
  ASI2_GRPO_REMOTE_ROOT=/root/work/software/quantum-gpt  ASI2_DAEMON_URL=...
EOF
}

# exec_cmd <cmd> [max_seconds]  -> prints the raw daemon JSON (or empty on
# connection failure / timeout). Never fails the script on its own.
exec_cmd() {
  local cmd="$1" max_t="${2:-120}"
  local wait_ms=$(( max_t * 1000 - 8000 ))
  [[ $wait_ms -lt 10000 ]] && wait_ms=10000
  local body
  body="$(python3 -c 'import json,sys; print(json.dumps({"command": sys.argv[1], "waitMs": int(sys.argv[2])}))' "$cmd" "$wait_ms" 2>/dev/null)" || return 1
  curl -s -m "$max_t" -X POST "$DAEMON" -H 'Content-Type: application/json' -d "$body" 2>/dev/null || return 1
}

# daemon_auth_ok [max_seconds] -> 0 if /exec answers DAEMON_OK, 1 otherwise.
daemon_auth_ok() {
  local max_t="${1:-12}"
  local resp
  resp="$(exec_cmd "echo DAEMON_OK" "$max_t")" || return 1
  [[ -z "$resp" ]] && return 1
  printf '%s' "$resp" | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(1)
sys.exit(0 if d.get("ok") and "DAEMON_OK" in (d.get("output") or "") else 1)
'
}

# ---- state file helpers (JSON, atomic write) ----
state_read() {
  if [[ -f "$STATE_FILE" ]]; then cat "$STATE_FILE"; else printf '{}'; fi
}

state_get() {
  # JSON booleans parse to Python True/False (capitalized) — normalize so the
  # caller can compare against "true"/"false".
  state_read | python3 -c 'import json,sys; d=json.load(sys.stdin); v=d.get(sys.argv[1], ""); print(str(v).lower() if isinstance(v, bool) else v)' "$1" 2>/dev/null || true
}

state_set() {
  local key="$1" val="$2"
  [[ "$DRY_RUN" == "1" ]] && return 0
  python3 - "$STATE_FILE" "$key" "$val" <<'PYEOF' || true
import json, os, sys
path, key, val = sys.argv[1], sys.argv[2], sys.argv[3]
d = {}
if os.path.exists(path):
    try:
        with open(path) as f:
            d = json.load(f)
    except Exception:
        d = {}
d[key] = val
tmp = path + ".tmp"
with open(tmp, "w") as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
os.replace(tmp, path)
PYEOF
}

# ---------------------------------------------------------------------------
# Stage 0: wait for daemon auth
# ---------------------------------------------------------------------------
stage0_wait_auth() {
  log "Stage 0: waiting for daemon auth (poll every 30s, up to ${AUTH_WAIT_SECONDS}s)..."
  local deadline=$(( $(date +%s) + AUTH_WAIT_SECONDS ))
  local attempt=0
  while :; do
    attempt=$(( attempt + 1 ))
    if daemon_auth_ok 12; then
      log "Stage 0: auth OK — daemon /exec reachable"
      return 0
    fi
    if (( attempt % 3 == 0 )); then
      log "Stage 0: /exec still unavailable (attempt ${attempt}) — Safari SSO likely expired; the bridge self-recovers after a human logs into Safari"
    fi
    if (( $(date +%s) >= deadline )); then
      log "Stage 0: AUTH_DOWN after ${AUTH_WAIT_SECONDS}s — daemon /exec never answered DAEMON_OK. Have a human log into Safari (ASI2 env tab), then re-run this script (or set AUTH_WAIT_SECONDS to a larger value)."
      return 1
    fi
    sleep 30
  done
}

# ---------------------------------------------------------------------------
# Stage 1: deploy changed files
# ---------------------------------------------------------------------------
stage1_deploy() {
  local deployed
  deployed="$(state_get deployed)"
  if [[ "$deployed" == "true" && "$FORCE_DEPLOY" == "0" ]]; then
    log "Stage 1: skip — state file ${STATE_FILE} already marks deploy done (use --force-deploy to re-deploy)"
    return 0
  fi
  if [[ ! -f /tmp/asi2_deploy_daemon.py ]]; then
    log "Stage 1: FAIL — deploy tool /tmp/asi2_deploy_daemon.py missing"
    return 1
  fi
  log "Stage 1: deploying ${#DEPLOY_FILES[@]} files to box via /tmp/asi2_deploy_daemon.py (chunked base64 + sha256)..."
  local deploy_out rc
  set +e
  deploy_out="$(cd "$ROOT_DIR" && python3 /tmp/asi2_deploy_daemon.py "${DEPLOY_FILES[@]}" 2>&1)"
  rc=$?
  set -e
  log "Stage 1: deploy tool rc=${rc}"
  printf '%s\n' "$deploy_out" | tail -20 | sed 's/^/    /' || true
  if [[ $rc -eq 0 ]] && printf '%s' "$deploy_out" | grep -q 'DEPLOY DONE: ALL OK'; then
    state_set deployed "true"
    state_set deployed_at "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    log "Stage 1: OK — all files sha256-verified on the box (DEPLOY DONE: ALL OK)"
    return 0
  fi
  log "Stage 1: FAIL — deploy did not report ALL OK"
  return 1
}

# ---------------------------------------------------------------------------
# Stage 2: is the trainer already running?
# ---------------------------------------------------------------------------
# remote_recent_activity -> 0 if a train log or metrics file was modified
# within the last 30 min (live training despite a stale pid file).
remote_recent_activity() {
  local resp
  resp="$(exec_cmd "find ${REMOTE_ROOT}/logs/grpo_27b_selfeval -maxdepth 1 -name 'grpo_train_*.log' -mmin -30 2>/dev/null | head -1; find ${REMOTE_ROOT}/outputs -maxdepth 2 -name 'grpo_step_metrics.jsonl' -mmin -30 2>/dev/null | head -1" 60)" || return 1
  [[ -z "$resp" ]] && return 1
  printf '%s' "$resp" | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(1)
out = d.get("output") or ""
sys.exit(0 if any(ln.strip() for ln in out.splitlines()) else 1)
'
}

stage2_check_status() {
  log "Stage 2: checking trainer status on box (launcher status)..."
  local out
  out="$(exec_cmd "cd ${REMOTE_ROOT} && bash scripts/asi2_launch_grpo_27b_selfeval.sh status" 100 2>/dev/null || true)"
  if [[ -z "$out" ]]; then
    log "Stage 2: FAIL — daemon /exec unreachable (AUTH_DOWN?) while checking status"
    return 1
  fi
  out="$(printf '%s' "$out" | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
print(d.get("output") or d.get("error") or "")
' 2>/dev/null || true)"
  if printf '%s' "$out" | grep -q "GRPO trainer: RUNNING"; then
    log "Stage 2: trainer RUNNING — nothing to do (exit 0)"
    return 10
  fi
  if printf '%s' "$out" | grep -qE "GRPO trainer: (STOPPED|NOT RUNNING)"; then
    log "Stage 2: trainer NOT RUNNING per pid-file status"
  else
    log "Stage 2: status output unrecognized (auth may be flaky); treating as NOT RUNNING unless fresh activity found"
  fi
  if remote_recent_activity; then
    log "Stage 2: fresh train-log/metrics activity (<30 min) — trainer likely LIVE despite pid-file status (dev-env PIDs differ from the task-run env); nothing to do (exit 0)"
    return 10
  fi
  log "Stage 2: no live training detected — proceeding to relaunch"
  return 0
}

# ---------------------------------------------------------------------------
# Stage 3: submit the relaunch
# ---------------------------------------------------------------------------
stage3_submit() {
  local task_name="asi2-grpo-27b-selfeval-$(date +%Y%m%dT%H%M%S)"
  log "Stage 3: submitting relaunch as ${task_name} (GRPO_STEPS=500 full run, CHECKPOINT_SECONDS=3600)..."
  local out_file="/tmp/asi2_submit_${task_name}.out"
  local rc
  set +e
  ( cd "$ROOT_DIR" && ASI2_GRPO_TASK_NAME="$task_name" ASI2_GRPO_STEPS=500 \
      ASI2_GRPO_CHECKPOINT_SECONDS=3600 \
      bash scripts/submit_asi2_grpo_27b_selfeval_task.sh --submit ) > "$out_file" 2>&1
  rc=$?
  set -e
  if [[ $rc -eq 0 ]] && grep -q '"ok": true' "$out_file"; then
    log "Stage 3: submit OK — success marker \"ok\": true found (${task_name})"
    # Touch a marker on the box so stage 4 only watches THIS launch's log dir.
    if exec_cmd "touch ${REMOTE_ROOT}/logs/grpo_27b_selfeval/.relaunch_${task_name}" 60 >/dev/null 2>&1; then
      log "Stage 3: marker file touched on box (logs/grpo_27b_selfeval/.relaunch_${task_name})"
    else
      log "Stage 3: WARN — could not touch verify marker (daemon flaky?); stage 4 will fall back to newest-dir checks"
    fi
    state_set submitted_task "$task_name"
    state_set submitted_at "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    return 0
  fi
  log "Stage 3: SUBMIT FAILED (rc=${rc}) — no \"ok\": true in submit output"
  log "Stage 3: output tail (see ${out_file} for the full log):"
  tail -30 "$out_file" 2>/dev/null | sed 's/^/    /' || true
  return 1
}

# ---------------------------------------------------------------------------
# Stage 4: verify the launch on the box
# ---------------------------------------------------------------------------
# Build the remote one-liner that finds THIS launch's train log + output dir
# (gated by the marker file), tails the log, and reports the metrics line
# count. $1 = marker path (may be empty -> ungated newest-dir fallback).
build_verify_cmd() {
  local marker="$1"
  local log_find out_find
  if [[ -n "$marker" ]]; then
    log_find="find @REMOTE_ROOT@/logs/grpo_27b_selfeval -maxdepth 1 -name 'grpo_train_*.log' -newer '@MARKER@' 2>/dev/null | sort | tail -1"
    out_find="find @REMOTE_ROOT@/outputs -maxdepth 1 -type d -name 'grpo-27b-selfeval-*' -newer '@MARKER@' 2>/dev/null | sort | tail -1"
  else
    log_find="ls -t @REMOTE_ROOT@/logs/grpo_27b_selfeval/grpo_train_*.log 2>/dev/null | head -1"
    out_find="ls -dt @REMOTE_ROOT@/outputs/grpo-27b-selfeval-*/ 2>/dev/null | head -1"
  fi
  local cmd
  cmd="$(cat <<'EOF'
TRAIN_LOG=$(@LOG_FIND_LINE@)
echo "TRAIN_LOG=${TRAIN_LOG}"
if [ -n "${TRAIN_LOG}" ]; then
  echo "--- log tail (60) ---"
  tail -60 "${TRAIN_LOG}"
fi
LATEST_OUT=$(@OUT_FIND_LINE@)
echo "OUT_DIR=${LATEST_OUT}"
if [ -n "${LATEST_OUT}" ] && [ -f "${LATEST_OUT}/grpo_step_metrics.jsonl" ]; then
  echo "METRIC_LINES=$(wc -l < "${LATEST_OUT}/grpo_step_metrics.jsonl")"
  echo "--- last record ---"
  tail -1 "${LATEST_OUT}/grpo_step_metrics.jsonl"
fi
EOF
)"
  cmd="$(printf '%s' "$cmd" \
    | sed -e "s#@LOG_FIND_LINE@#$log_find#g" \
          -e "s#@OUT_FIND_LINE@#$out_find#g" \
          -e "s|@REMOTE_ROOT@|$REMOTE_ROOT|g" \
          -e "s|@MARKER@|$marker|g")"
  # Flatten to a single line for the daemon /exec transport (it expects
  # one-line commands). 'then<newline>' would become the invalid 'then;' —
  # collapse that into 'then ' so the remote bash parses cleanly.
  printf '%s' "$cmd" | tr '\n' ';' | sed 's/then;/then /g'
  printf '\n'
}

# verify_one_poll -> key=value lines:
#   VERDICT=STEP_RECORD|LOSS_SEEN|WAITING|AUTH_DOWN
#   METRIC_COUNT=N  MARKERS=a,b,c  LOSS=...  TRAIN_LOG=...  OUT_DIR=...  WARN=...
verify_one_poll() {
  local marker="$1"
  local resp
  resp="$(exec_cmd "$(build_verify_cmd "$marker")" 110)" || true
  if [[ -z "$resp" ]]; then
    printf 'VERDICT=AUTH_DOWN\n'
    return 0
  fi
  printf '%s' "$resp" | python3 -c '
import json, re, sys
raw = sys.stdin.read()
try:
    d = json.loads(raw)
except Exception:
    print("VERDICT=AUTH_DOWN"); sys.exit(0)
if not d.get("ok"):
    print("VERDICT=AUTH_DOWN"); sys.exit(0)
out = d.get("output") or ""
train_log = out_dir = metric_count = ""
for ln in out.splitlines():
    if ln.startswith("TRAIN_LOG="): train_log = ln[len("TRAIN_LOG="):].strip()
    elif ln.startswith("OUT_DIR="): out_dir = ln[len("OUT_DIR="):].strip()
    elif ln.startswith("METRIC_LINES="): metric_count = ln[len("METRIC_LINES="):].strip()
markers = []
for m in re.finditer(r"\"stage\"\s*:\s*\"([a-z_0-9]+)\"", out):
    if m.group(1) not in markers:
        markers.append(m.group(1))
losses = re.findall(r"\"loss\"\s*:\s*([-0-9.eE+]+)", out)
last_loss = losses[-1] if losses else ""
try:
    mc = int(metric_count)
except Exception:
    mc = 0
verdict = "WAITING"
if mc >= 1:
    verdict = "STEP_RECORD"
elif last_loss not in ("", "nan", "inf", "-inf", "NaN"):
    verdict = "LOSS_SEEN"
warn = ""
if re.search(r"Traceback|out of memory|OOM", out, re.IGNORECASE):
    warn = "traceback/OOM text found in log"
print("VERDICT=" + verdict)
print("METRIC_COUNT=" + str(mc))
print("MARKERS=" + ",".join(markers))
print("LOSS=" + last_loss)
print("TRAIN_LOG=" + train_log)
print("OUT_DIR=" + out_dir)
print("WARN=" + warn)
'
}

kv() { sed -n "s/^$1=//p" | head -1; }

stage4_verify() {
  local task marker
  task="$(state_get submitted_task)"
  marker="${REMOTE_ROOT}/logs/grpo_27b_selfeval/.relaunch_${task}"
  if [[ -z "$task" ]]; then
    log "Stage 4: WARN — no submitted_task in state; using ungated newest-dir checks"
    marker=""
  fi
  log "Stage 4: verifying launch ${task:-<unknown>} (poll every 60s, up to ${VERIFY_WAIT_SECONDS}s)..."
  local deadline=$(( $(date +%s) + VERIFY_WAIT_SECONDS ))
  local prev_count="-1" poll_no=0
  while :; do
    poll_no=$(( poll_no + 1 ))
    local poll
    poll="$(verify_one_poll "$marker")"
    local verdict metric_count markers loss warn log_path out_dir
    verdict="$(printf '%s\n' "$poll" | kv VERDICT)"
    metric_count="$(printf '%s\n' "$poll" | kv METRIC_COUNT)"
    markers="$(printf '%s\n' "$poll" | kv MARKERS)"
    loss="$(printf '%s\n' "$poll" | kv LOSS)"
    warn="$(printf '%s\n' "$poll" | kv WARN)"
    log_path="$(printf '%s\n' "$poll" | kv TRAIN_LOG)"
    out_dir="$(printf '%s\n' "$poll" | kv OUT_DIR)"

    local newest_marker="(none)"
    if [[ -n "$markers" ]]; then
      newest_marker="${markers##*,}"
    fi
    log "Stage 4: poll #${poll_no} — markers seen: [${markers:-none}] (newest: ${newest_marker}), metric lines: ${metric_count:-0}, loss: ${loss:-none}, log: ${log_path:-not-yet}"
    if [[ -n "$warn" ]]; then
      log "Stage 4: WARN — ${warn} in latest log tail (possible trainer failure; keep watching)"
    fi
    if [[ "$metric_count" != "$prev_count" && "$prev_count" != "-1" ]]; then
      log "Stage 4: metric file growth ${prev_count} -> ${metric_count}"
    fi
    prev_count="$metric_count"

    if [[ "$verdict" == "STEP_RECORD" || "$verdict" == "LOSS_SEEN" ]]; then
      log "Stage 4: SUCCESS — ${verdict} (newest stage marker: ${newest_marker}, loss: ${loss}, metric lines: ${metric_count}, log: ${log_path}, out: ${out_dir})"
      return 0
    fi
    if [[ "$verdict" == "AUTH_DOWN" ]]; then
      log "Stage 4: daemon unreachable during verify — will keep retrying until deadline"
    fi
    if (( $(date +%s) >= deadline )); then
      log "Stage 4: VERIFY_TIMEOUT after ${VERIFY_WAIT_SECONDS}s — no step record and no real loss yet (newest stage marker: ${newest_marker}, metric lines: ${metric_count:-0}). Trainer may still be loading the model; re-run this script to re-verify."
      return 1
    fi
    sleep 60
  done
}

# ---------------------------------------------------------------------------
# dry-run: print the plan, execute nothing
# ---------------------------------------------------------------------------
dry_run_plan() {
  log "[DRY-RUN] ===== plan for $(basename "${BASH_SOURCE[0]}") (no commands will be executed) ====="
  local auth="DOWN"
  if daemon_auth_ok 5; then auth="UP"; fi
  log "[DRY-RUN] Stage 0: poll /exec 'echo DAEMON_OK' every 30s up to ${AUTH_WAIT_SECONDS}s (current probe: ${auth}) -> wait until auth is UP; exit AUTH_DOWN if never"
  local deployed
  deployed="$(state_get deployed)"
  if [[ "$deployed" == "true" && "$FORCE_DEPLOY" == "0" ]]; then
    log "[DRY-RUN] Stage 1: SKIP — state file ${STATE_FILE} already marks deploy done (--force-deploy to override)"
  else
    log "[DRY-RUN] Stage 1: deploy ${#DEPLOY_FILES[@]} files via 'cd ${ROOT_DIR} && python3 /tmp/asi2_deploy_daemon.py <files>'"
    for f in "${DEPLOY_FILES[@]}"; do log "[DRY-RUN]     $f"; done
    log "[DRY-RUN]          then mark {\"deployed\": true} in ${STATE_FILE}"
  fi
  log "[DRY-RUN] Stage 2: run remote 'bash scripts/asi2_launch_grpo_27b_selfeval.sh status'; exit 0 if RUNNING or <30-min activity"
  local task_name="asi2-grpo-27b-selfeval-$(date +%Y%m%dT%H%M%S)"
  log "[DRY-RUN] Stage 3: (cd ${ROOT_DIR} && ASI2_GRPO_TASK_NAME=${task_name} ASI2_GRPO_STEPS=500 ASI2_GRPO_CHECKPOINT_SECONDS=3600 bash scripts/submit_asi2_grpo_27b_selfeval_task.sh --submit)"
  log "[DRY-RUN]          success = submit output contains '\"ok\": true'; then touch verify marker on box and record task in state"
  log "[DRY-RUN] Stage 4: poll every 60s up to ${VERIFY_WAIT_SECONDS}s: tail newest grpo_train_*.log + count grpo_step_metrics.jsonl lines (gated to this launch); exit 0 on first step record or real loss"
  log "[DRY-RUN] State file ${STATE_FILE}: $(state_read | tr -d '\n ')"
  log "[DRY-RUN] ===== done — nothing executed ====="
}

# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
main() {
  local auth_wait="${AUTH_WAIT_SECONDS:-900}"
  (( auth_wait < 0 )) && auth_wait=0
  AUTH_WAIT_SECONDS="$auth_wait"

  log "=== ASI2 watchdog relaunch start (dry_run=${DRY_RUN}, state=${STATE_FILE}, daemon=${DAEMON}) ==="

  if [[ "$DRY_RUN" == "1" ]]; then
    dry_run_plan
    exit 0
  fi

  stage0_wait_auth || exit 1
  stage1_deploy || exit 1

  local st=0
  stage2_check_status || st=$?
  if [[ "$st" == "10" ]]; then
    log "=== ASI2 watchdog done: trainer already live, nothing to do ==="
    exit 0
  fi
  [[ "$st" == "0" ]] || { log "=== ASI2 watchdog aborted (stage 2 failed, rc=${st}) ==="; exit 1; }

  stage3_submit || exit 1
  stage4_verify || exit 1

  log "=== ASI2 watchdog done: deploy + relaunch + verify complete ==="
}

# ---- arg parsing ----
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --force-deploy) FORCE_DEPLOY=1 ;;
    --state)
      [[ $# -ge 2 ]] || { echo "error: --state requires a file path" >&2; exit 2; }
      STATE_FILE="$2"; shift ;;
    --help|-h) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
  shift
done

main "$@"
