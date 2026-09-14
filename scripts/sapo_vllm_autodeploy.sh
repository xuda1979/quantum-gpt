#!/usr/bin/env bash
# sapo_vllm_autodeploy.sh — when ASI1 or ASI2 becomes exec-reachable AND its
# NPUs are free (the qwen3.8 swift stop freed ASI1), deploy + launch vLLM
# TP=8 there, then write the URL to reports/.sapo_vllm_url for the next
# training launch (SAPO_VLLM_URL=<url>).
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG=/tmp/sapo_vllm_autodeploy.log
declare -A PORT=( [ASI1]=20646 [ASI2]=19004 )
try_env() {
  local env=$1 port=$2
  local probe
  probe=$(curl -s --max-time 40 -X POST "http://127.0.0.1:$port/exec" \
    -H 'Content-Type: application/json' \
    -d '{"command":"ls -d /vllm-workspace/vllm >/dev/null 2>&1 && echo WS_OK; npu-smi info 2>/dev/null | grep -c 910B2; pgrep -f training/grpo_trainer | wc -l","waitMs":25000}' 2>/dev/null | python3 -c "
import json,sys
try:
    d = json.load(sys.stdin)
    o = d.get('output','')
    if 'WS_OK' in o:
        lines = [l for l in o.splitlines() if l.strip().isdigit()]
        print(lines[0] if lines else '?')
    else:
        print('')
except Exception:
    print('')" 2>/dev/null)
  if [ -n "$probe" ] && [ "$probe" != "0" ] && [ "$probe" != "?" ]; then
    echo "$(date -u +%H:%M:%S) $env NPUs=$probe free -> deploying vLLM" >> "$LOG"
    # patch launcher util for dedicated card (0.85)
    curl -s --max-time 40 -X POST "http://127.0.0.1:$port/exec" -H 'Content-Type: application/json' \
      -d '{"command":"cd /root/work/software/quantum-gpt 2>/dev/null || cd /root/software/quantum-gpt; sed -i s/gpu-memory-utilization.*/gpu-memory-utilization 0.85/ scripts/launch_vllm_rollout_server.sh 2>/dev/null; setsid bash scripts/launch_vllm_rollout_server.sh /root/work/filestorage/Qwen3.8-27B 8355 </dev/null >/dev/null 2>&1 & echo LAUNCHED","waitMs":25000}' > /dev/null 2>&1
    sleep 240
    local ok
    ok=$(curl -s --max-time 40 -X POST "http://127.0.0.1:$port/exec" -H 'Content-Type: application/json' \
      -d '{"command":"curl -s --noproxy * --max-time 5 http://127.0.0.1:8355/health >/dev/null 2>&1 && echo VLLM_UP","waitMs":25000}' 2>/dev/null | grep -o VLLM_UP)
    if [ -n "$ok" ]; then
      # write the URL for the next launch (manager reads it)
      local ip
      ip=$(curl -s --max-time 40 -X POST "http://127.0.0.1:$port/exec" -H 'Content-Type: application/json' \
        -d '{"command":"hostname -I","waitMs":20000}' 2>/dev/null | python3 -c "import json,sys,re; m=re.search(r'(\d+\.\d+\.\d+\.\d+)', json.load(sys.stdin).get('output','')); print(m.group(1) if m else '')" 2>/dev/null)
      echo "http://$ip:8355" > "$ROOT/reports/.sapo_vllm_url"
      echo "$(date -u +%H:%M:%S) $env vLLM UP at http://$ip:8355 — URL recorded" >> "$LOG"
      exit 0
    fi
  fi
}
echo "$(date -u +%H:%M:%S) vllm-autodeploy armed (poll 5m)" >> "$LOG"
while true; do
  try_env ASI1 20646 || true
  try_env ASI2 19004 || true
  [ -f "$ROOT/reports/.sapo_vllm_url" ] && exit 0
  sleep 300
done
