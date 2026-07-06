# ASI1 Qwen3.6 35B Q/V LoRA SFT Run Card

Created: 2026-06-10 12:49:07 CST

## Lookup Keys

- Huanxin task name: `asi1-35b-qv-203-pip-043831`
- Local submit artifact: `browser-automation/huanxin-submit-task-run-asi1-35b-qv-203-pip-043831.json`
- Local submit screenshot: `browser-automation/huanxin-submit-task-run-asi1-35b-qv-203-pip-043831.png`
- Output directory: `outputs/qwen36-35b-a3b-w8a8-distill-lora-asi1-balanced-r16qv-l512-s150-203hq`
- Log path inside task command: `logs/asi1_35b_qv_203.log`

Find this run later with:

```bash
rg "asi1-35b-qv-203-pip-043831|qwen36-35b-a3b-w8a8-distill-lora-asi1|203_sft" reports browser-automation memory
```

## Huanxin Runtime

- Environment: `ASI1`
- Launch route: Huanxin training-task UI via `scripts/submit_asi1_isq_sft_task.sh`
- Shell route: not used
- S3 sync: disabled with `ASI1_ISQ_SFT_SKIP_SYNC=1`
- Files expected to already exist on ASI1
- Image: `qwen3.5-27B-35B-122B-397B-031626-zx`
- Resource group: `huanxin-all-resource`
- Instances: `1`
- Accelerators: `8` Ascend NPUs
- CPU: `128`
- Memory: `1920 GB`

## Model And Data

- Base model: `/root/work/filestorage/Qwen3.6-35B-A3B-W8A8`
- Remote project root: `/root/work/software/quantum-gpt`
- Train file: `data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft_203/all_chatml.jsonl`
- Train rows: `203`
- Dataset format: `chat-sft-v1`
- Local dataset SHA256: `d23913d5368378bd93b9e1b70ee9059f2f9924e21cc50e6360d9a5826a355ba9`
- Eval file: none for this run

## Fine-Tuning Scope

- Method: PEFT LoRA SFT
- Target modules: `q_proj v_proj`
- Scope: every transformer module whose suffix matches `q_proj` or `v_proj`
- Not targeted: `k_proj`, `o_proj`, MLP/expert projections, router/gate parameters, embeddings, layer norms
- LoRA rank: `16`
- LoRA alpha: `32`
- LoRA dropout: `0.0`
- Minimum trainable parameters: `500000`
- Maximum trainable parameters: `10000000`

## Hyperparameters

- Max sequence length: `512`
- Max optimizer steps: `150`
- Epoch cap: `3`
- Per-device batch size: `1`
- Gradient accumulation steps: `4`
- Learning rate: `2e-5`
- Log steps: `1`
- Eval steps: `25` in command, but no eval file was provided
- Train on completions only: enabled
- Gradient checkpointing: enabled
- NPU device map: `balanced-layers`
- NPU max memory: `54 GiB`
- Output overwrite: enabled

## Exact Trainer Command

```bash
python3 training/qwen_sft_peft.py \
  --model-name /root/work/filestorage/Qwen3.6-35B-A3B-W8A8 \
  --train-file data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft_203/all_chatml.jsonl \
  --output-dir outputs/qwen36-35b-a3b-w8a8-distill-lora-asi1-balanced-r16qv-l512-s150-203hq \
  --overwrite-output-dir \
  --device npu \
  --npu-device-map balanced-layers \
  --npu-max-memory-gib 54 \
  --max-length 512 \
  --max-steps 150 \
  --num-epochs 3 \
  --per-device-batch-size 1 \
  --gradient-accumulation-steps 4 \
  --learning-rate 2e-5 \
  --eval-steps 25 \
  --log-steps 1 \
  --lora-rank 16 \
  --lora-alpha 32 \
  --lora-dropout 0.0 \
  --target-modules q_proj v_proj \
  --train-on-completions-only \
  --gradient-checkpointing \
  --min-trainable-parameters 500000 \
  --max-trainable-parameters 10000000
```

## Launch Environment Variables

```bash
ASI1_ISQ_SFT_TASK_NAME=asi1-35b-qv-203-pip-043831
ASI1_ISQ_SFT_REMOTE_ROOT=/root/work/software/quantum-gpt
ASI1_ISQ_SFT_SPLIT_DIR=data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft_203
ASI1_ISQ_SFT_TRAIN_FILE=data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft_203/all_chatml.jsonl
ASI1_ISQ_SFT_EVAL_FILE=
ASI1_ISQ_SFT_SKIP_SYNC=1
ASI1_ISQ_SFT_INSTALL_DEPS=1
ASI1_ISQ_SFT_MAX_STEPS=150
ASI1_ISQ_SFT_NUM_EPOCHS=3
ASI1_ISQ_SFT_GRAD_ACCUM=4
ASI1_ISQ_SFT_LORA_RANK=16
ASI1_ISQ_SFT_LORA_ALPHA=32
ASI1_ISQ_SFT_TARGET_MODULES="q_proj v_proj"
ASI1_ISQ_SFT_MIN_TRAINABLE_PARAMETERS=500000
ASI1_ISQ_SFT_MAX_TRAINABLE_PARAMETERS=10000000
ASI1_ISQ_SFT_OUTPUT_DIR=outputs/qwen36-35b-a3b-w8a8-distill-lora-asi1-balanced-r16qv-l512-s150-203hq
ASI1_ISQ_SFT_LOG_PATH=logs/asi1_35b_qv_203.log
```

## Monitoring Notes

- The task was submitted and visible in Huanxin task list.
- A previous no-S3/no-dependency attempt failed because `peft`/training dependencies were missing.
- This launch kept no-S3 behavior and enabled dependency install first.
