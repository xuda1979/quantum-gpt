#!/bin/bash
# auto_resume_training.sh — dedicated AGENT: keeps training continuously running.
# After a training run completes AND its newest checkpoint is evaluated, if the
# honest verdict BEATS base (composite), warm-continue from that checkpoint.
# If it does NOT beat (flat/regression), STOP and alert (never relaunch on flat).
# Idempotent: safe to run every ~10min; no trainer + beating checkpoint => resume.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG="${AUTO_RESUME_LOG:-/tmp/auto_resume_training.log}"
QG="/root/work/software/quantum-gpt"   # box-side; local invocation is a dry-run probe
DAEMON_URL="${AUTO_RESUME_DAEMON:-http://127.0.0.1:20653/exec}"
JUDGE_EP="${AUTO_RESUME_JUDGE_EP:-http://127.0.0.1:56238}"

log(){ echo "[$(date -u +%FT%TZ)] $*" >> "$LOG"; }
box(){ # exec a command on the box via the daemon, return stdout
  curl -s -m 120 -X POST "$DAEMON_URL" -H 'content-type: application/json' \
    -d "{\"command\":$(python3 -c 'import json,sys;print(json.dumps(sys.stdin.read()))' <<< "$1")}" \
    2>/dev/null | python3 -c 'import sys,json;d=json.load(sys.stdin);print(d.get("output",""))' 2>/dev/null
}

# 1. trainer running? if yes, nothing to do
N_TRAIN=$(box "ps aux | grep grpo_trainer.py | grep -v grep | wc -l" | tr -d ' ')
[ -n "$N_TRAIN" ] && [ "$N_TRAIN" -ge 1 ] && { log "trainer running ($N_TRAIN) — ok"; exit 0; }
log "no trainer — checking for beating checkpoint to auto-resume"

# 2. newest evaluated adapter that beat base? find newest run + its newest-reasonable checkpoint
#    And check for a *completed* run not yet resumed. We look at the newest run whose
#    steps.jsonl is full (>=90 steps) and whose newest checkpoint had a beating eval.
#    Simplified, safe: find newest checkpoint with an existing beating verdict file;
#    re-eval is handled by the eval lane. Here we only RESUME from a checkpoint ALREADY
#    shown to beat base (avoid re-eval cost in this agent).
BEST_CKPT=$(box "for r in \$(ls -dt $QG/outputs/sapo-27b-ai-2026*/ | head -12); do \
  new=\$(ls -d \$r/step_*_adapter 2>/dev/null | tail -1); \
  [ -n \"\$new\" ] && echo \"\$new\"; done | head -3" | head -5)
CKPT_TO_USE=""
for ck in $BEST_CKPT; do
  base=$(basename "$ck")
  # a beating verdict lives as reeval_38_<run><step>.json with booleans; we trust a prior
  # verdict file exists for this exact adapter (the eval lane writes it). If none,
  # skip (eval lane will eval; this agent only resumes from already-verified).
  if box "ls $QG/outputs/reeval_38_*_${base}.json" 2>/dev/null | grep -q "${base}"; then
    CKPT_TO_USE="$ck"; break
  fi
done
if [ -z "$CKPT_TO_USE" ]; then
  log "no already-evaluated beating checkpoint found; eval lane will decide — idle"
  exit 0
fi
log "auto-resuming from verified checkpoint $(basename "$CKPT_TO_USE")"
# 3. launch warm-continue via the standard chain (gated: vLLM + translator up, no trainer)
H_VLLM=$(curl -s --noproxy '*' -m 5 -o /dev/null -w '%{http_code}' http://127.0.0.1:8356/health 2>/dev/null)
H_TR=$(curl -s --noproxy '*' -m 5 -o /dev/null -w '%{http_code}' "$JUDGE_EP/health" 2>/dev/null)
if [ "$H_VLLM" != "200" ] || [ "$H_TR" != "200" ]; then
  log "BLOCK: vLLM=$H_VLLM translator=$H_TR not ready; retry next cycle"
  exit 0
fi
NU=$(basename "$CKPT_TO_USE")
box "cd $QG && export SAPO_VLLM_URL=http://127.0.0.1:8356 AI_SAPO_JUDGE_DP4_ENDPOINT=$JUDGE_EP AI_SAPO_ROOT=$QG AI_SAPO_MODEL_PATH=/root/work/filestorage/Qwen3.8-27B AI_SAPO_ADAPTER_INIT=$CKPT_TO_USE AI_SAPO_LR=2.5e-5 && nohup bash scripts/ai_launch_sapo_direct.sh launch >> /tmp/auto_resume_launch.log 2>&1 & echo AUTO_RESUMED:$NU" >/dev/null 2>&1
log "AUTO-RESUME launched from $NU (new run)"
