#!/usr/bin/env bash
# Deterministic frozen 18-task comparison: base vs warm adapter vs SAPO.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

SAPO_PROMOTION_ROOT="${SAPO_PROMOTION_ROOT:-/root/software/quantum-gpt}"
BASE_MODEL="${SAPO_PROMOTION_BASE_MODEL:-$SAPO_PROMOTION_ROOT/models/Qwen3.6-27B}"
WARM_ADAPTER="${SAPO_PROMOTION_WARM_ADAPTER:?set SAPO_PROMOTION_WARM_ADAPTER to the exact warm-start adapter}"
SAPO_ADAPTER="${SAPO_PROMOTION_SAPO_ADAPTER:?set SAPO_PROMOTION_SAPO_ADAPTER to one complete atomic step_*_adapter checkpoint}"
STAMP="${SAPO_PROMOTION_STAMP:-$(date -u +%Y%m%dT%H%M%SZ)}"
BENCHMARK="evals/benchmarks/sapo_promotion_holdout_v1_18.txt"
REPORT_DIR="reports/sapo-promotion-${STAMP}"

test -f "$BASE_MODEL/config.json"
test -f "$WARM_ADAPTER/adapter_config.json"
test -f "$WARM_ADAPTER/adapter_model.safetensors"
test -f "$SAPO_ADAPTER/adapter_config.json"
test -f "$SAPO_ADAPTER/adapter_model.safetensors"
mkdir -p "$REPORT_DIR"

for state in base warm sapo; do
  python3 evals/runner/prepare_prompts.py \
    --run-name "sapo-promotion-${state}-${STAMP}" \
    --prompt-style direct \
    --task-id-file "$BENCHMARK" \
    --notes "Frozen SAPO promotion state=${state}; deterministic pass@1"
done

python3 - "$STAMP" <<'PY'
import json
import sys
from pathlib import Path

stamp = sys.argv[1]
fields = (
    "task_id_file_sha256",
    "system_prompt_sha256",
    "public_eval_contract_sha256",
    "evaluation_runner_sha256",
    "scorer_contract_sha256",
)
manifests = {
    state: json.loads(
        (Path("evals/runs") / f"sapo-promotion-{state}-{stamp}" / "manifest.json").read_text()
    )
    for state in ("base", "warm", "sapo")
}
for field in fields:
    values = {manifest.get(field) for manifest in manifests.values()}
    if len(values) != 1 or not next(iter(values)):
        raise SystemExit(f"three-state frozen contract mismatch: {field}={values}")
for state, manifest in manifests.items():
    if len(manifest.get("tasks", [])) != 18:
        raise SystemExit(f"{state} does not contain exactly 18 frozen tasks")
print(json.dumps({field: manifests["base"][field] for field in fields}, indent=2))
PY

export ASCEND_RT_VISIBLE_DEVICES="${ASCEND_RT_VISIBLE_DEVICES:-0,1,2,3,4,5,6,7}"
export PYTORCH_NPU_ALLOC_CONF="${PYTORCH_NPU_ALLOC_CONF:-max_split_size_mb:256}"
COMMON=(
  --base-model "$BASE_MODEL"
  --device npu
  --device-map balanced-layers
  --npu-max-memory-gib 54
  --token-budget-preset quantum_heavy
  --temperature 0
  --score
)

python3 scripts/run_hf_pass1_eval.py \
  --run-dir "evals/runs/sapo-promotion-base-${STAMP}" \
  "${COMMON[@]}" 2>&1 | tee "$REPORT_DIR/base.log"
python3 scripts/run_hf_pass1_eval.py \
  --run-dir "evals/runs/sapo-promotion-warm-${STAMP}" \
  --adapter "$WARM_ADAPTER" \
  "${COMMON[@]}" 2>&1 | tee "$REPORT_DIR/warm.log"
python3 scripts/run_hf_pass1_eval.py \
  --run-dir "evals/runs/sapo-promotion-sapo-${STAMP}" \
  --adapter "$SAPO_ADAPTER" \
  "${COMMON[@]}" 2>&1 | tee "$REPORT_DIR/sapo.log"

python3 evals/runner/compare_runs.py \
  "evals/runs/sapo-promotion-base-${STAMP}" \
  "evals/runs/sapo-promotion-warm-${STAMP}" \
  "evals/runs/sapo-promotion-sapo-${STAMP}" \
  | tee "$REPORT_DIR/comparison.txt"

python3 scripts/decide_sapo_promotion_gate.py \
  --base-run "evals/runs/sapo-promotion-base-${STAMP}" \
  --warm-run "evals/runs/sapo-promotion-warm-${STAMP}" \
  --sapo-run "evals/runs/sapo-promotion-sapo-${STAMP}" \
  --out "$REPORT_DIR/gate.json"

echo "SAPO_PROMOTION_REPORT=$REPORT_DIR/gate.json"
