#!/usr/bin/env bash
set -euo pipefail

# This file is intentionally non-executing by default because the required
# network transfer is blocked by the outer approval layer in the current agent.

# 1. Push exact local changes to S3
./scripts/push_to_s3.sh scripts/run_base_vs_adapter_eval.py scripts/summarize_base_vs_adapter_report.py training/qwen_sft_peft.py reports/base_vs_adapter_eval_slice_interface_prefix.json

# 2. Sync the ai2 workspace from S3
./scripts/ai2_sync_from_s3.sh

# 3. Launch the OmniCoder qualitative eval on ai2
./scripts/ai2_shell.sh "cd /root/root/work/quantum-gpt && nohup env PYTHONPYCACHEPREFIX=/tmp/pycache TOKENIZERS_PARALLELISM=false python3 scripts/run_base_vs_adapter_eval.py --slice-json reports/base_vs_adapter_eval_slice_interface_prefix.json --base-model models/OmniCoder-9B --adapter outputs/interface-prefix-omnicoder9b-semantic-v4-2npu-true20-20260329T2219CST/adapter --output reports/base_vs_adapter_outputs_omnicoder9b_semantic_v4_true20.json --device npu --limit 5 --max-new-tokens 128 > /tmp/base-vs-adapter-omnicoder9b-semantic-v4-true20.log 2>&1 < /dev/null &"

# 4. Watch and fetch the report once it appears
./scripts/watch_base_vs_adapter_report.sh ai2 reports/base_vs_adapter_outputs_omnicoder9b_semantic_v4_true20.json reports/base_vs_adapter_outputs_omnicoder9b_semantic_v4_true20.json /tmp/base-vs-adapter-omnicoder9b-semantic-v4-true20.log
