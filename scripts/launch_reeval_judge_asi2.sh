#!/usr/bin/env bash
# launch_reeval_judge_asi2.sh — judge the 100+100 re-eval emissions with the
# FROZEN base model on ASI2, using all 4 NPUs (2 shards x 2 NPUs).
set -euo pipefail
cd /root/work/quantum-gpt
mkdir -p logs

nohup python3 scripts/eval_100_reeval.py --mode judge \
  --devices 0,1 --shard-idx 0 --shard-total 2 \
  --base-partial outputs/eval100_base.jsonl \
  --adapter-partial outputs/eval100_adapter.jsonl \
  --start 1 --end 50 \
  --out outputs/reeval_judge_shard0.jsonl \
  > logs/reeval_judge_shard0.log 2>&1 &
echo "judge shard0 pid=$!" | tee -a logs/reeval_launch.log

nohup python3 scripts/eval_100_reeval.py --mode judge \
  --devices 2,3 --shard-idx 1 --shard-total 2 \
  --base-partial outputs/eval100_base.jsonl \
  --adapter-partial outputs/eval100_adapter.jsonl \
  --start 51 --end 100 \
  --out outputs/reeval_judge_shard1.jsonl \
  > logs/reeval_judge_shard1.log 2>&1 &
echo "judge shard1 pid=$!" | tee -a logs/reeval_launch.log

echo "JUDGE LAUNCHED: shard0 (NPUs 0-1, samples 1-50), shard1 (NPUs 2-3, samples 51-100)"
