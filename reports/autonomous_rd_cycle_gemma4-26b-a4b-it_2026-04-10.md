# Autonomous R&D Cycle Report - 2026-04-10

## Summary
- target: `google/gemma-4-26B-A4B-it`
- status: `blocked`
- current_stage: `gemma_runtime_bootstrap`
- blocker: Gemma runtime bootstrap failed on the resolved local Python path.
- next_action: `PYTHON_BIN="$(python3 scripts/resolve_python_interpreter.py --min-version 3.10 --print-path)" && "$PYTHON_BIN" -m pip install -r training/requirements-gemma4-runtime.txt`
- fallback_next_action: `scripts/queue_ai2_timeboxed_pipeline.sh --target omnicoder9b --iteration-profile fast --visible-devices 6,7 --nproc-per-node 2 --required-idle-npus 2 --stage-only`
- note: Gemma 4 26B-A4B-it MoE is now the preferred weekend-demo target because it is smaller and better aligned with expert-specific tuning than the abandoned 31B path.

## Cycle State
- `local_eval_gate`: `passed` - Local eval gate passed in this iteration.
- `holdout_integrity`: `passed` - Holdout integrity was verified for this iteration.
- `gemma_audit`: `passed` - Gemma source audit is satisfied by a cached verified local artifact for this target.
  evidence_audit_artifact: `artifacts/model-source-audit-gemma4-26b-a4b-it.json`
  evidence_timestamp_utc: `2026-04-08T10:24:48.892073+00:00`
- `gemma_snapshot_verify`: `passed` - Local Gemma snapshot verification is satisfied by a cached successful handoff artifact for this target.
- `gemma_local_python_gate`: `passed` - A local Python interpreter meeting the Gemma runtime floor is available.
  evidence_selected_python: `/Users/daxu/software/quantum-gpt/.local-python/cpython-3.11.15/bin/python3.11`
  evidence_selected_python_version: `3.11.15`
- `gemma_runtime_bootstrap`: `blocked` - Gemma runtime bootstrap failed on the resolved local Python path.
  next_action: `PYTHON_BIN="$(python3 scripts/resolve_python_interpreter.py --min-version 3.10 --print-path)" && "$PYTHON_BIN" -m pip install -r training/requirements-gemma4-runtime.txt`
- `gemma_smoke`: `pending` - Gemma trainer/backend preflight has not yet passed on the local stack.
  next_action: `PYTHON_BIN="$(python3 scripts/resolve_python_interpreter.py --min-version 3.10 --print-path)" && "$PYTHON_BIN" training/huanxin_cpu_smoke.py --model-name models/gemma-4-26B-A4B-it --dataset data/seed/splits-auto-seed/train.jsonl --max-samples 1`
- `paper_router_warmup`: `pending` - The paper-router warmup command and dataset are ready; after local Gemma runtime preflight clears, S3 code/model sync can launch this exact ai2 router adaptation step.
  next_action: `PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256 \
TOKENIZERS_PARALLELISM=false \
ASCEND_RT_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 \
torchrun --nproc_per_node=8 training/qwen_sft_peft.py \
  --model-name models/gemma-4-26B-A4B-it \
  --train-file data/generated/quantum-paper-router-warmup-v1/messages/quantum_paper_router_warmup_messages_train.jsonl \
  --eval-file data/generated/quantum-paper-router-warmup-v1/messages/quantum_paper_router_warmup_messages_valid.jsonl \
  --output-dir outputs/gemma4-26b-a4b-it-quantum-paper-router-warmup-fastiter \
  --device npu \
  --max-length 1024 \
  --per-device-batch-size 1 \
  --gradient-accumulation-steps 2 \
  --learning-rate 1e-4 \
  --num-epochs 1 \
  --max-steps 8 \
  --eval-steps 8 \
  --log-steps 1 \
  --train-on-completions-only \
  --target-module-regex '(?:^|\.)(?:router|gate)(?:$|\.)' \
  --trainable-param-regex 'lora_'`
  evidence_command_sheet: `artifacts/gemma4-26b-a4b-paper-router-command-sheet.txt`
  evidence_plan_command: `python3 scripts/render_timeboxed_scaleup_commands.py --target gemma4-26b-a4b-it --output artifacts/gemma4-26b-a4b-it-paper-router-command-sheet.txt`
  evidence_paper_train_file: `data/generated/quantum-paper-router-warmup-v1/messages/quantum_paper_router_warmup_messages_train.jsonl`
  evidence_paper_eval_file: `data/generated/quantum-paper-router-warmup-v1/messages/quantum_paper_router_warmup_messages_valid.jsonl`
  evidence_paper_train_rows: `42`
  evidence_paper_eval_rows: `5`
  prerequisites: `scripts/push_to_s3.sh scripts training evals research data` | `scripts/ai2_sync_from_s3.sh` | `scripts/ai2_sync_model_from_s3.sh gemma-4-26B-A4B-it`
- `remote_launcher_gate`: `passed` - Remote launcher is target-aware for Gemma and now exits early with a concrete preflight blocker instead of pretending launch readiness.

## Fallback Continuation
- fallback_target: `Tesslate/OmniCoder-9B`
- fallback_reason: google/gemma-4-26B-A4B-it remains blocked at gemma_runtime_bootstrap, but the verified Tesslate/OmniCoder-9B lane can keep ai2 iteration moving in parallel.
- fallback_next_action: `scripts/queue_ai2_timeboxed_pipeline.sh --target omnicoder9b --iteration-profile fast --visible-devices 6,7 --nproc-per-node 2 --required-idle-npus 2 --stage-only`

## Stakeholder Questions
- Q: How do we know the eval set is not leaking into training?
  A: The cycle requires holdout-integrity verification on example_id, task_id, and prompt_family before any remote launch.
- Q: What exactly is the next model target?
  A: The next target is google/gemma-4-26B-A4B-it, but it is gated by runtime and backend readiness before remote finetuning.
- Q: Can the system explain why a direction was abandoned?
  A: The control plane records explicit blocker, regression, and stop-condition sections in each iteration report.
- Q: Where is the evidence for claims made in papers or leadership reports?
  A: The cycle emits a report, a command sheet, and references to run artifacts and paper files for each iteration.
- Q: What is the current blocker to Gemma 4 finetuning?
  A: ai2 access is repaired, but the local stack still blocks Gemma 4 at runtime bootstrap plus trainer/backend preflight: the newer Transformers runtime must install cleanly, and the current text-only AutoModelForCausalLM path still needs a processor-aware conditional-generation backend.
- Q: How much of a large Gemma snapshot is actually present right now?
  A: The cycle-state artifact now reports indexed total weight bytes, observed downloaded bytes, a progress percentage, and whether incomplete shard activity still looks live or stale.
- Q: What is the concrete next MoE-specific run once the Gemma snapshot is verified?
  A: The controller now tracks a paper-router warmup stage that points at the exact router-adaptation warmup command sheet and the prepared paper-derived dataset counts.
- Q: What happens if Gemma stays blocked but we still want productive remote iteration?
  A: The control plane can recommend the verified fallback lane `omnicoder9b` targeting Tesslate/OmniCoder-9B, and the fast-iteration launcher profile now keeps that loop short once local eval and holdout integrity have passed.

## Subsystems
- `dataset_generation`: ready (scripts/build_large_template_dataset.py, scripts/build_mixed_fast_mini.py)
- `holdout_integrity`: ready (data/generated/omnicoder-quantum-generalization-holdout-v1/train.jsonl, data/generated/omnicoder-quantum-generalization-holdout-v1/eval.jsonl, data/generated/omnicoder-quantum-generalization-holdout-v1/manifest.json, scripts/verify_holdout_dataset.py)
- `paper_router_warmup`: ready (artifacts/gemma4-26b-a4b-paper-router-command-sheet.txt, data/generated/quantum-paper-router-warmup-v1/messages/quantum_paper_router_warmup_messages_train.jsonl, data/generated/quantum-paper-router-warmup-v1/messages/quantum_paper_router_warmup_messages_valid.jsonl, scripts/build_paper_sft_dataset.py, scripts/render_timeboxed_scaleup_commands.py)
- `local_eval_gate`: ready (evals/runner/run_eval.py)
- `remote_transport`: ready (scripts/push_to_s3.sh, scripts/ai2_sync_from_s3.sh, scripts/ai2_push_results_to_s3.sh, scripts/pull_from_s3.sh, scripts/ai2_sync_model_from_s3.sh)
- `remote_job_control`: ready (scripts/ai2_job.sh, scripts/queue_ai2_timeboxed_pipeline.sh, scripts/timeboxed_8npu_pipeline.sh)
- `research_papers`: ready (research/papers/index.json, research/papers/README.md)
- `gemma_targeting`: ready (training/acquire_public_qwen_snapshot.py, training/verify_qwen_snapshot.py, research/papers/gemma4_text_path_enablement/paper.md)

## MoE Expert Routing Prep
- strategy: `router_warmup_then_frequency_guided_esft`
- state: `ready_for_inspection`
- ready: `true`
- reason: The local Gemma snapshot appears complete enough for exact router/expert name inspection and manifest capture.
- inspection_command: `python3 training/inspect_moe_target_modules.py --model-name models/gemma-4-26B-A4B-it --out artifacts/gemma4-26b-a4b-it_moe_module_scan.json --manifest-out artifacts/gemma4-26b-a4b-it_moe_target_manifest.json`
- inspection_output: `artifacts/gemma4-26b-a4b-it_moe_module_scan.json`
- manifest_output: `artifacts/gemma4-26b-a4b-it_moe_target_manifest.json`
- paper_router_dataset_dir: `data/generated/quantum-paper-router-warmup-v1`
- paper_router_command_sheet: `artifacts/gemma4-26b-a4b-paper-router-command-sheet.txt`
- paper_router_ready: `true`
- paper_router_train_file: `data/generated/quantum-paper-router-warmup-v1/messages/quantum_paper_router_warmup_messages_train.jsonl`
- paper_router_eval_file: `data/generated/quantum-paper-router-warmup-v1/messages/quantum_paper_router_warmup_messages_valid.jsonl`
- paper_router_train_rows: `42`
- paper_router_eval_rows: `5`

## Gating Commands
- `local_eval_gate`: `python3 evals/runner/run_eval.py`
- `holdout_integrity`: `python3 scripts/verify_holdout_dataset.py --train-file data/generated/omnicoder-quantum-generalization-holdout-v1/train.jsonl --eval-file data/generated/omnicoder-quantum-generalization-holdout-v1/eval.jsonl --manifest data/generated/omnicoder-quantum-generalization-holdout-v1/manifest.json --min-eval-count 500 --require-task-disjoint --require-prompt-family-disjoint`
- `gemma_audit`: `python3 training/audit_model_source.py --model-id google/gemma-4-26B-A4B-it --expected-family-substring gemma`
- `gemma_snapshot_acquire`: `python3 training/acquire_public_qwen_snapshot.py --target gemma4-26b-a4b-it --local-dir models/gemma-4-26B-A4B-it`
- `gemma_snapshot_verify`: `python3 training/verify_qwen_snapshot.py models/gemma-4-26B-A4B-it --expected-substring gemma-4-26B-A4B-it --expected-family-substring gemma`
- `gemma_snapshot_relay`: `scripts/relay_model_snapshot_to_s3.sh gemma-4-26B-A4B-it`
- `paper_router_plan`: `python3 scripts/render_timeboxed_scaleup_commands.py --target gemma4-26b-a4b-it --output artifacts/gemma4-26b-a4b-it-paper-router-command-sheet.txt`
- `paper_dataset`: `python3 scripts/build_paper_sft_dataset.py \
  paper \
  --output-dir data/generated/quantum-paper-router-warmup-v1 \
  --dataset-name quantum_paper_router_warmup`
- `paper_router_warmup`: `PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256 \
TOKENIZERS_PARALLELISM=false \
ASCEND_RT_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 \
torchrun --nproc_per_node=8 training/qwen_sft_peft.py \
  --model-name models/gemma-4-26B-A4B-it \
  --train-file data/generated/quantum-paper-router-warmup-v1/messages/quantum_paper_router_warmup_messages_train.jsonl \
  --eval-file data/generated/quantum-paper-router-warmup-v1/messages/quantum_paper_router_warmup_messages_valid.jsonl \
  --output-dir outputs/gemma4-26b-a4b-it-quantum-paper-router-warmup-fastiter \
  --device npu \
  --max-length 1024 \
  --per-device-batch-size 1 \
  --gradient-accumulation-steps 2 \
  --learning-rate 1e-4 \
  --num-epochs 1 \
  --max-steps 8 \
  --eval-steps 8 \
  --log-steps 1 \
  --train-on-completions-only \
  --target-module-regex '(?:^|\.)(?:router|gate)(?:$|\.)' \
  --trainable-param-regex 'lora_'`
- `gemma_python_probe`: `python3 scripts/resolve_python_interpreter.py --min-version 3.10`
- `gemma_runtime_bootstrap`: `PYTHON_BIN="$(python3 scripts/resolve_python_interpreter.py --min-version 3.10 --print-path)" && "$PYTHON_BIN" -m pip install -r training/requirements-gemma4-runtime.txt`
- `gemma_smoke`: `PYTHON_BIN="$(python3 scripts/resolve_python_interpreter.py --min-version 3.10 --print-path)" && "$PYTHON_BIN" training/huanxin_cpu_smoke.py --model-name models/gemma-4-26B-A4B-it --dataset data/seed/splits-auto-seed/train.jsonl --max-samples 1`
- `code_sync`: `scripts/push_to_s3.sh scripts training evals research data`
- `remote_code_sync`: `scripts/ai2_sync_from_s3.sh`
- `remote_model_sync`: `scripts/ai2_sync_model_from_s3.sh gemma-4-26B-A4B-it`
- `remote_job_queue`: `scripts/queue_ai2_timeboxed_pipeline.sh --target gemma4-26b-a4b-it --iteration-profile fast --visible-devices 6,7 --nproc-per-node 2 --required-idle-npus 2 --stage-only`
- `fallback_remote_job_queue`: `scripts/queue_ai2_timeboxed_pipeline.sh --target omnicoder9b --iteration-profile fast --visible-devices 6,7 --nproc-per-node 2 --required-idle-npus 2 --stage-only`

## Gate Definitions
- `local_quality_gate`: local eval suite green before any remote training action (`local_eval_gate`)
- `dataset_integrity_gate`: train/eval disjointness and size thresholds verified (`holdout_integrity`)
- `gemma_source_gate`: google/gemma-4-26B-A4B-it auditable from local machine (`gemma_audit`)
- `gemma_snapshot_gate`: Gemma local snapshot exists and is verified before any remote model sync (`gemma_snapshot_verify`)
- `paper_router_warmup_gate`: paper-derived router warmup dataset and exact warmup command are prepared after snapshot verification (`paper_router_warmup`)
- `gemma_local_python_gate`: local Python >= 3.10 resolved before Gemma runtime/bootstrap smoke (`gemma_python_probe`)
- `gemma_runtime_bootstrap_gate`: Gemma runtime dependencies install cleanly on the resolved local Python path before smoke (`gemma_runtime_bootstrap`)
- `gemma_trainer_backend_gate`: Gemma trainer/backend preflight passes locally before any Huanxin launch (`gemma_smoke`)
- `remote_launcher_gate`: Remote launcher is target-aware for the active Gemma target and guards against premature launch with a concrete preflight blocker (`remote_job_queue`)

## Research Papers
- `pluginized_research_methods`: Pluginized Research Methods for Quantum Coding LLM Iteration
- `timeboxed_eight_npu_sft`: Timeboxed 8-NPU SFT Scaling Plan
- `timeboxed_eight_npu_grpo`: Timeboxed 8-NPU GRPO Scaling Plan
- `verifier_guided_repair_curriculum`: Verifier-Guided Near-Miss Repair Curriculum for Quantum Code Generalization
- `clause_aware_verifier_reward`: Clause-Aware Verifier Reward for Code RL
- `ast_anchor_interface_grounding`: AST-Anchor Reranking for Interface-Grounded Code Synthesis
- `self_consistency_verifier_routing`: Self-Consistency Verifier Routing for Code SFT and GRPO
- `uncertainty_triggered_repair_replay`: Uncertainty-Triggered Repair Replay for SFT and GRPO
- `behavior_anchor_coverage_reward`: Behavior-Anchor Coverage Reward for Low-Signal Code GRPO
- `turboquant`: TurboQuant-Style KV Cache Compression for Long-Context Inference
- `gemma4_text_path_enablement`: Gemma 4 Text-Path Enablement for Quantum R&D
- `gemma4_26b_a4b_weekend_demo`: Gemma 4 26B-A4B MoE Weekend Demo Report
- `autonomous_rd_cycle_system`: Autonomous R&D Cycle System

## Executed Checks
- `local_eval_gate`: ok
  - command: `python3 evals/runner/run_eval.py`
  - exit_code: `0`
- `holdout_integrity`: ok
  - command: `python3 scripts/verify_holdout_dataset.py --train-file data/generated/omnicoder-quantum-generalization-holdout-v1/train.jsonl --eval-file data/generated/omnicoder-quantum-generalization-holdout-v1/eval.jsonl --manifest data/generated/omnicoder-quantum-generalization-holdout-v1/manifest.json --min-eval-count 500 --require-task-disjoint --require-prompt-family-disjoint`
  - exit_code: `0`
- `gemma_runtime_bootstrap`: failed
  - command: `PYTHON_BIN="$(python3 scripts/resolve_python_interpreter.py --min-version 3.10 --print-path)" && "$PYTHON_BIN" -m pip install -r training/requirements-gemma4-runtime.txt`
  - exit_code: `1`
