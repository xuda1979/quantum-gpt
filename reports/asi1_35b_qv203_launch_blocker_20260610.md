# ASI1 Qwen3.6 35B Q,V LoRA Launch Blocker - 2026-06-10

Objective: launch Qwen3.6-35B-A3B-W8A8 SFT on ASI1 using 203 high-quality ChatML rows, native Q,V LoRA only, 3 epochs max, 150 optimizer steps.

Local fixes completed:
- `training/runtime_overlay.py` now registers Qwen3.5-MoE config/model classes with Transformers AutoConfig and AutoModelForCausalLM.
- `training/qwen_sft_peft.py` calls that registration before runtime preflight.
- `scripts/submit_asi1_isq_sft_task.sh` can embed the minimal Qwen3.5-MoE runtime overlay files into Huanxin task codeContents, avoiding S3 and dev shell upload.

Local validation passed:
- `python3 -m py_compile training/runtime_overlay.py training/qwen_sft_peft.py`
- `bash -n scripts/submit_asi1_isq_sft_task.sh`
- dry-run rendered payload: no S3, runtime export present, qwen3_5_moe files embedded.

Current Huanxin blockers:
- ASI1 dev shell upload path failed: `getShellVisitUrl code=170022`, `wss://aihuanxin.cn/kunlun/null`, then `Failed to activate Shell终端 tab for ASI1`.
- Huanxin direct task create failed: `403 RBAC: access denied`.
- Huanxin UI task route failed before form fill: timeout waiting for `.ant-drawer-content-wrapper` submit drawer.

Last launch settings:
- task name prefix: `qv203u-*`
- model: `/root/work/filestorage/Qwen3.6-35B-A3B-W8A8`
- train file: `data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft_203/all_chatml.jsonl`
- output: `outputs/qwen36-35b-a3b-w8a8-distill-lora-asi1-qv-native-r16-l512-s150-203hq-runtime`
- LoRA: native backend, target modules `q_proj v_proj`, rank 16, alpha 32, dropout 0
- schedule: max steps 150, num epochs 3, batch 1, grad accumulation 1, LR 2e-5, max length 512

Exact launch command to retry:

```bash
TS=$(date -u +%m%d%H%M); ASI1_ISQ_SFT_TASK_NAME=qv203u-$TS ASI1_ISQ_SFT_ARTIFACT_STEM=huanxin-ui-task-asi1-qv203-$TS ASI1_ISQ_SFT_EMBED_LOCAL_FILES=1 ASI1_ISQ_SFT_EMBED_CODE_FILES=1 ASI1_ISQ_SFT_EMBED_DATA_FILES=0 ASI1_ISQ_SFT_EMBED_RUNTIME_FILES=1 ASI1_ISQ_SFT_SKIP_SYNC=1 ASI1_ISQ_SFT_TRAIN_FILE=data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft_203/all_chatml.jsonl ASI1_ISQ_SFT_EVAL_FILE= ASI1_ISQ_SFT_SPLIT_DIR=data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft_203 ASI1_ISQ_SFT_OUTPUT_DIR=outputs/qwen36-35b-a3b-w8a8-distill-lora-asi1-qv-native-r16-l512-s150-203hq-runtime ASI1_ISQ_SFT_LOG_PATH=logs/asi1_35b_qv203_native_runtime_$TS.log ASI1_ISQ_SFT_MAX_STEPS=150 ASI1_ISQ_SFT_NUM_EPOCHS=3 ASI1_ISQ_SFT_GRAD_ACCUM=1 ASI1_ISQ_SFT_LEARNING_RATE=2e-5 ASI1_ISQ_SFT_LORA_RANK=16 ASI1_ISQ_SFT_LORA_ALPHA=32 ASI1_ISQ_SFT_TARGET_MODULES='q_proj v_proj' ASI1_ISQ_SFT_MAX_TRAINABLE_PARAMETERS=10000000 ASI1_ISQ_SFT_MIN_TRAINABLE_PARAMETERS=500000 ASI1_ISQ_SFT_WAIT_MS=60000 bash scripts/submit_asi1_isq_sft_task.sh --submit
```
