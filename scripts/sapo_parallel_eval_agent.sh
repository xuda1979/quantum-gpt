#!/usr/bin/env bash
# sapo_parallel_eval_agent.sh — fires the frozen-holdout eval loop for every NEW
# checkpoint in RUN_DIR (scan every SCAN seconds). Beats-base instrument:
# pass@1 vs base=3/18. State: reports/.sapo_parallel_eval_state.json
# Usage: sapo_parallel_eval_agent.sh <ENV> <PORT> <RUN_DIR_ON_BOX> [SCAN_SECONDS]
#   The eval itself = scripts/asi2_loop_eval.sh (env-overridable, frozen-holdout
#   benchmark by default since the 2026-09-01 instrument fix).
set -u
ENV_NAME="${1:-ASI3}"
PORT="${2:-20653}"
RUN_DIR="${3:-/root/work/software/quantum-gpt/outputs/sapo-27b-ai-20260901T015238-resume3}"
SCAN="${4:-120}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# 2026-09-20 (E1-E7, tests/test_eval_state_key_full_path.py): every state
# key is the checkpoint's FULL PATH (the checkpoint_identity contract,
# B-105) -- the eval loop writes full-path keys via update_state
# "$STATE_KEY", so this agent's done-filter and finalize step must look up
# the SAME key. The old bare-basename keys never matched (a bare step
# number is identical across runs) and re-fired evaluated legs forever.
# Fail-closed: an unmatched key stays PENDING and re-fires -- it never
# suppresses a leg. Per-env state files: ASI2 and ASI3 agents must not
# share one state file.
STATE="$ROOT/reports/.sapo_parallel_eval_state_${ENV_NAME}.json"
LOG_TAG="[parallel-eval $ENV_NAME]"
mkdir -p /tmp/sapo-logs
[ -f "$STATE" ] || echo '{}' > "$STATE"
echo "$LOG_TAG started $(date -u +%H:%M:%SZ) run=$RUN_DIR port=$PORT scan=${SCAN}s"
exec_script="$ROOT/scripts/asi3_exec.py"
while true; do
  CKPTS=$(python3 "$exec_script" --port "$PORT" "ls -d $RUN_DIR/step_*_adapter 2>/dev/null | tail -5" --wait-ms 20000 2>/dev/null | python3 -c "
import json,sys
try:
    d = json.load(sys.stdin)
    print('\n'.join(x.strip() for x in d.get('output','').splitlines() if '/step_' in x))
except Exception:
    pass" 2>/dev/null)
  if [ -n "$CKPTS" ]; then
    # evaluate ONLY the newest not-yet-done checkpoint (one eval at a time; ~1.4h each)
    NEWEST_DONE=""
    for CK in $(echo "$CKPTS" | sort); do
      # E1: one identity per checkpoint -- the full path, normalized the
      # same way the loop's checkpoint_identity normalizes it; a bare
      # basename passes through unchanged.
      CK="$(python3 -c 'import os,sys; a=sys.argv[1]; print(os.path.normpath(a) if a else a)' "$CK")"
      NAME="$(basename "$CK")"
      DONE=$(python3 -c "
import json
try: st = json.load(open('$STATE'))
except Exception: st = {}
cur = str((st.get('$CK') or dict()).get('status',''))
print('yes' if (cur.startswith('done') or cur.startswith('inert')) else 'no')")
      if [ "$DONE" != "yes" ]; then
        echo "$LOG_TAG NEW checkpoint $NAME -> holdout eval leg (logs: /tmp/sapo-logs/eval_${NAME}.log)"
        DAEMON_PORT="$PORT" \
        REMOTE_ROOT="$(dirname "$(dirname "$RUN_DIR")")" \
        EVAL_STATE_FILE="$STATE" SAPO_RUN_DIR="$RUN_DIR" \
        bash "$ROOT/scripts/asi2_loop_eval.sh" > "/tmp/sapo-logs/eval_${NAME}.log" 2>&1
        RC=$?
        # 2026-09-02 (manager, realtime bug fix): DO NOT mark a checkpoint
        # "done" just because the eval leg exited 0. asi2_loop_eval.sh exits 0
        # for TRANSIENT states too (PRECHECK_RUNNING, EVAL_PENDING,
        # ALREADY_EVALUATED, INERT) — treating those as a completed verdict made
        # the agent fire a leg ONCE (precheck-only), stamp it "done", and never
        # return to collect the real frozen-holdout result. Mark "done" ONLY if
        # the leg itself landed a REAL terminal state (its update_state wrote
        # status 'done' or 'inert'). Otherwise leave it in its own 'pending'
        # state so the next scan retries until the rubric verdict appears.
        MARK=$(python3 -c "
import json
key = '$CK'
try: st = json.load(open('$STATE'))
except Exception: st = {}
entry = st.get(key, {}) or {}
cur = str(entry.get('status', ''))
real = cur.startswith('done') or cur.startswith('inert')
# preserve the leg's own terminal write (done/inert verdict) or keep pending
if real:
    st[key] = dict(entry, finalized_ts='$(date -u +%H:%M:%SZ)')
json.dump(st, open('$STATE','w'), indent=1)
print('after_status=' + cur + ' real_verdict=' + ('true' if real else 'false'))
")
        echo "$LOG_TAG eval $NAME rc=$RC $MARK"
        break  # one per cycle; re-scan picks the next
      fi
    done
  fi
  sleep "$SCAN"
done
