# Timeboxed 8-NPU SFT Scaling Plan

## Objective

Run a meaningful OmniCoder SFT scale-up on all 8 NPUs while staying under a 2-hour wall-clock budget.

## Operating Assumptions

- Use `torchrun --nproc_per_node=8`
- Use `PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256`
- Use `--max-length 512`
- Keep LoRA-only fine-tuning
- Prefer a bounded optimizer-step budget over long epoch counts

## Proposed Run

- Base model: `models/OmniCoder-9B`
- Adapter init:
  - `outputs/interface-prefix-omnicoder9b-semantic-v4-2npu-true20-20260329T2219CST/adapter`
- Dataset:
  - `data/generated/omnicoder-quantum-generalization-holdout-v1/train.jsonl`
  - `data/generated/omnicoder-quantum-generalization-holdout-v1/eval.jsonl`
- Output:
  - `outputs/omnicoder9b-quantum-generalization-sft-8npu-true32`
- Suggested budget:
  - `max_steps=32`
  - `num_epochs=1`
  - `per_device_batch_size=1`
  - `gradient_accumulation_steps=2`
  - `eval_steps=8`

## Rationale

- Prior 8-NPU runs in this workspace completed 20-step LoRA SFT jobs successfully
- The strongest verified OmniCoder 9B adapter in this workspace already clears the delivery gate and the clean 25/25 evaluation thread, so continuing from that adapter is a better use of ai2 compute than restarting from a weaker continuation base
- 32 steps is a modest scale-up that is still leadership-friendly and time-bounded
- The strict holdout dataset is already leadership-compliant on split hygiene and eval size
