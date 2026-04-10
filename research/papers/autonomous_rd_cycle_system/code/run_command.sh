#!/usr/bin/env bash
set -euo pipefail

python3 scripts/run_autonomous_rd_cycle.py \
  --target gemma4-e2b-it \
  --run-gemma-audit \
  --run-gemma-smoke
