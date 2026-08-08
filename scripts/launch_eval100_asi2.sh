#!/usr/bin/env bash
# launch_eval100_asi2.sh — launch the 100-sample re-eval generation on ASI2.
#   $1 = which (base|adapter)
# Single process, device_map over ALL 4 NPUs, batched decode (batch 4).
set -euo pipefail
WHICH="$1"
cd /root/work/quantum-gpt
mkdir -p logs outputs

nohup python3 scripts/eval_100_reeval.py --mode gen --which "$WHICH" \
  --devices 0,1,2,3 --n 100 --shard-idx 0 --shard-total 1 \
  --max-new-tokens 1536 --batch-size 4 \
  --out "outputs/eval100_${WHICH}.jsonl" \
  > "logs/eval100_${WHICH}.log" 2>&1 &
echo "${WHICH} pid=$!" | tee -a logs/eval100_launch.log
echo "LAUNCHED $WHICH on NPUs 0-3 (batched decode)"
