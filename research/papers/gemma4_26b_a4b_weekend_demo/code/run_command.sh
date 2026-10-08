#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../../../.."
python3 scripts/run_autonomous_rd_cycle.py \
  --target gemma4-26b-a4b-it \
  --run-local-gates \
  --run-gemma-audit \
  --run-gemma-smoke
