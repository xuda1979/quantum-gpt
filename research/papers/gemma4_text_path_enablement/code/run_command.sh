#!/usr/bin/env bash
set -euo pipefail

python3 training/audit_model_source.py --model-id google/gemma-4-E2B-it --expected-family-substring gemma
python3 training/audit_model_source.py --model-id google/gemma-4-E4B-it --expected-family-substring gemma
python3 training/huanxin_cpu_smoke.py --model-name google/gemma-4-E2B-it --dataset data/seed/splits-auto-seed/train.jsonl --max-samples 1
python3 training/huanxin_cpu_smoke.py --model-name google/gemma-4-E4B-it --dataset data/seed/splits-auto-seed/train.jsonl --max-samples 1
