#!/bin/bash
# sapo_box_pull_watch.sh — wait for a daemon (ASI3 19005 for training state,
# ASI2 19004 for the eval verdict) to become ready, then execute the STANDUP
# #238 box-pull checklist and record the RUN-13 verdict.
# Polls both ports every 60s; whichever comes up first triggers its pull.
#
# Usage: nohup bash scripts/sapo_box_pull_watch.sh > /tmp/sapo_box_pull_watch.log 2>&1 < /dev/null &
set -u
LEDGER="/Users/daxu/software/quantum-gpt/.sapo-loop/box_pull_ledger.md"
EXEC="/Users/daxu/software/quantum-gpt/scripts/asi3_exec.py"
EVAL_STATE="/Users/daxu/software/quantum-gpt/reports/.asi2_eval_state.json"
MAX_POLLS="${SAPO_BOX_PULL_MAX_POLLS:-240}"   # ~4h
# 2026-09-01 (P-10 fix): per-invocation token so the stop condition is scoped
# to THIS run — the old grep on the append-only ledger matched markers from a
# PRIOR invocation, so a re-run exited after one poll and silently pulled
# nothing. Completion lines now embed $RUN_STAMP; the stop grep matches only
# this run's markers.
RUN_STAMP="$(date -u +%Y%m%dT%H%M%SZ)-$$"

echo "[$(date -u +%H:%M:%S)] box-pull watch started (19005 training / 19004 eval) run=$RUN_STAMP" >> "$LEDGER"
for i in $(seq 1 "$MAX_POLLS"); do
  # ── ASI3 (training box) ──
  READY3=$(curl -s -m 8 "http://127.0.0.1:19005/health" 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('ready'))" 2>/dev/null || echo false)
  if [ "$READY3" = "True" ]; then
    echo "[$(date -u +%H:%M:%S)] ASI3 DAEMON READY after ${i} polls" >> "$LEDGER"
    echo "### BOX PULL ASI3 $(date -u +%Y%m%dT%H%M%SZ)" >> "$LEDGER"
    echo '```' >> "$LEDGER"
    python3 "$EXEC" "hostname && uptime && echo '---TRAINER---' && ps aux | grep grpo_trainer | grep -v grep | head -3 && echo '---STEPS---' && ls -t /root/software/quantum-gpt-new/logs/ 2>/dev/null | head -5 && echo '---CHECKPOINTS---' && ls -t /root/software/quantum-gpt-new/outputs/ 2>/dev/null | grep -E 'sapo-27b' | head -5" --port 19005 --wait-ms 45000 >> "$LEDGER" 2>&1
    echo '```' >> "$LEDGER"
    echo "[$(date -u +%H:%M:%S)] $RUN_STAMP ASI3 pull complete" >> "$LEDGER"
  fi
  # ── ASI2 (eval box — the verdict channel) ──
  READY2=$(curl -s -m 8 "http://127.0.0.1:19004/health" 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('ready'))" 2>/dev/null || echo false)
  if [ "$READY2" = "True" ]; then
    echo "[$(date -u +%H:%M:%S)] ASI2 DAEMON READY after ${i} polls" >> "$LEDGER"
    echo "### BOX PULL ASI2 $(date -u +%Y%m%dT%H%M%SZ)" >> "$LEDGER"
    echo '```' >> "$LEDGER"
    python3 "$EXEC" "hostname && echo '---EVAL LEDGER---' && tail -n 8 /tmp/eval_results_ledger.jsonl 2>/dev/null || echo 'no ledger yet'" --port 19004 --wait-ms 45000 >> "$LEDGER" 2>&1
    echo '---LOCAL EVAL STATE (newest 5)---' >> "$LEDGER"
    python3 - "$EVAL_STATE" << 'PYEOF' >> "$LEDGER" 2>&1
import json, sys
from pathlib import Path
try:
    d = json.loads(Path(sys.argv[1]).read_text())
    for ts, rec in list(d.items())[-5:]:
        print(f"{ts}: {rec.get('verdict')} | {rec.get('eval_output','')[:80]} | {rec.get('updated_at_utc','')}")
except Exception as e:
    print("eval state read error:", e)
PYEOF
    echo '```' >> "$LEDGER"
    echo "[$(date -u +%H:%M:%S)] $RUN_STAMP ASI2 pull complete" >> "$LEDGER"
  fi
  # stop once BOTH channels have been pulled at least once
  if grep -q "$RUN_STAMP ASI3 pull complete" "$LEDGER" && grep -q "$RUN_STAMP ASI2 pull complete" "$LEDGER"; then
    echo "[$(date -u +%H:%M:%S)] both pulls complete — exiting" >> "$LEDGER"
    exit 0
  fi
  sleep 60
done
echo "[$(date -u +%H:%M:%S)] watch timed out after ${MAX_POLLS} polls" >> "$LEDGER"
exit 1
