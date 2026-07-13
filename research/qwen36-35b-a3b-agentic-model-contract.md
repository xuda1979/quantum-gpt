# Qwen3.6 35B A3B Agentic Model Contract

The intended training target is `Qwen/Qwen3.6-35B-A3B`, not Qwen3.6 27B and not an OmniCoder fallback.

## Accepted Model Artifacts

- Hugging Face/source name: `Qwen/Qwen3.6-35B-A3B`
- ASI1 remote checkpoint currently verified: `/root/work/filestorage/Qwen3.6-35B-A3B-W8A8`
- Repo-relative path when synchronized locally or remotely: `models/Qwen3.6-35B-A3B`

## Presence Check

A training launcher may treat the model as present only when all relevant checks pass:

- model directory exists
- `config.json` exists
- tokenizer files exist
- safetensor shards or equivalent quantized checkpoint payload exists
- runtime can load the config with the installed `transformers`
- for adapter training, `peft` and the target backend are importable
- for NPU training, `torch_npu` is importable and visible devices match the planned topology

## Fallback Rule

Do not silently substitute `models/Qwen3.6-27B`, `models/OmniCoder-9B`, or any Qwen2.5 checkpoint. If the requested model is unavailable, record the exact failed check and stop unless the user explicitly approves a model change.

## Current ASI1 Launch Contract

Use the generic Huanxin launcher with an explicit model override:

```bash
scripts/launch_huanxin_agentic_grpo.sh \
  --env ASI1 \
  --remote-root /root/work/quantum-gpt \
  --model-name /root/work/filestorage/Qwen3.6-35B-A3B-W8A8 \
  --benchmark-file evals/benchmarks/agentic_coding_trajectory_training_v1.txt \
  --dry-run
```
