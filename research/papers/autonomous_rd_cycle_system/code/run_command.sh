#!/usr/bin/env bash
# Run the autonomous R&D iteration from data generation through reporting.

set -euo pipefail

# Phase 1: dataset and prompt preparation
./scripts/build_large_template_dataset.py --output-dir=data/generated/omnicoder-template-large-v1
./scripts/build_mixed_fast_mini.py

# Phase 2: validation and unit tests
python -m tests.test_build_seed_dataset
python -m tests.test_verify_holdout_dataset

# Phase 3: local Gemma 4 readiness evaluation
./scripts/run_hf_pass1_eval.py \
  --model gemma-4 \
  --benchmarks evals/benchmarks/delivery_pass1_v1.txt \
  --token-budget-preset quantum_heavy

# Phase 4: documentation and artifact emission
python scripts/summarize_run_metrics.py --output reports/run_metrics_snapshot_$(date +%Y-%m-%d).md
echo "Iteration checkpointed at $(date -u)." >reports/autonomous_rd_cycle_system_iteration.txt

echo "Run complete: review reports/ for the comprehensive artifacts and research/papers/ for the supporting writeups."
