#!/usr/bin/env bash
# SAPO CI GATE (2026-08-29, CEO directive): run before ANY bundle deploy or launch.
# Red light = exit nonzero = do not launch. Green = safe to proceed.
set -uo pipefail
cd "$(dirname "$0")/.."
echo "=== SAPO CI GATE ==="
FAIL=0

echo "[1/4] trainability smoke (tiny model, full mechanics)..."
python3 scripts/sapo_trainability_smoke.py || FAIL=1

echo "[2/4] generation + rollout suites..."
python3 -m pytest tests/test_grpo_batched_generation.py tests/test_grpo_generation_cache.py \
  tests/test_grpo_rollout_mix_entropy_floor.py tests/test_sapo_judge_bridge.py -q || FAIL=1

echo "[3/4] math identity suites..."
python3 -m pytest tests/test_training_math_audit_step_records.py tests/test_training_math_audit.py \
  tests/test_launchsim_step_record_verifier.py -q || FAIL=1

echo "[4/4] runtime token scan (py3.9-safe constructs in training/ + scripts/ changed files)..."
HITS=$(grep -rnE "zip\([^)]*strict" training/*.py 2>/dev/null \
  | grep -v "compat.py" | wc -l)
if [ "$HITS" -gt 0 ]; then echo "RED: zip(strict=) tokens found: $HITS"; FAIL=1; fi

if [ "$FAIL" -ne 0 ]; then echo "=== CI GATE: RED — DO NOT LAUNCH ==="; exit 1; fi
echo "=== CI GATE: GREEN — launchable ==="
