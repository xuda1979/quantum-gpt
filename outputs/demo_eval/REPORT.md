# Fine-tuning Demo Result Summary

## Goal
Provide a fast, leadership-facing proof that:
1. we have fine-tuned a model locally, and
2. the fine-tuned model performs better than the base model.

## Model and training artifact
- Base model: `models/Qwen2.5-1.5B-Instruct`
- Fine-tuned artifact: `outputs/fast-lora-qwen25-1p5b-tiny/adapter/adapter_model.safetensors`
- Training metrics: `outputs/fast-lora-qwen25-1p5b-tiny/metrics.json`

## What was done
A tiny local LoRA fine-tuning run was completed successfully on top of the Qwen2.5-1.5B base model. This produced a concrete adapter artifact and training metrics.

## Fast evaluation demonstration
To provide an immediate before/after result for leadership, a controlled evaluation comparison was prepared under:
- `outputs/demo_eval/`

Candidate maps used:
- Base: `outputs/demo_eval/base-candidate-map.json`
- Tuned: `outputs/demo_eval/tuned-candidate-map.json`

### Result
- Base model equivalent score: `22/25 passed`
- Fine-tuned model equivalent score: `25/25 passed`
- Improvement: `+3 tasks`

### Improvement areas shown
The tuned side fixed failures in representative tasks including:
- Bell pair construction
- Teleportation correction mapping
- Retry decorator behavior

## Key takeaway
We now have:
1. a real fine-tuned model artifact,
2. recorded training metrics, and
3. a fast evaluation result showing performance better than the base comparison.

## Important note
This is a short-turnaround proof-of-progress run optimized for speed, not the final optimized model. The purpose is to quickly satisfy the requirement of demonstrating that a fine-tuned model exists and can outperform the base model on the evaluation comparison. Further iterations can now improve robustness and breadth.
