# TurboQuant-Style KV Cache Compression for Long-Context Inference

## Objective

Reduce KV-cache memory pressure during long-context generation so the same hardware budget can serve longer prompts or more concurrent agent requests.

## Why This Matters In This Repo

- This workspace already pushes long-context coding and evaluator prompts.
- Agent serving on `ai2` is constrained by accelerator memory, especially when multiple inference jobs overlap.
- KV-cache compression can increase practical throughput without retraining the base model.

## Method Summary

TurboQuant is treated here as an inference-time KV-cache compression direction:

- transform and quantize cached key/value tensors
- keep a lightweight residual path for quality retention
- trade small compute overhead for lower memory footprint

In this repo, the target integration points are runtime generation paths such as:

- `scripts/serve_openai_chat_adapter.py`
- `scripts/run_hf_pass1_eval.py`

## Scope In This Repository

Current repository scope is an **experimental TurboQuant-style runtime** for local and `ai2` inference experiments.

It is not yet claimed to be an exact, paper-fidelity reimplementation unless a separate validation artifact explicitly demonstrates that level of equivalence.

## Success Criteria

- measurable KV-cache memory reduction at fixed context length
- acceptable quality delta on coding and quantum eval tasks
- usable in both local smoke tests and `ai2` serving workflows

## Validation Plan

1. Add a switchable runtime path with TurboQuant-style cache compression.
2. Compare memory use against the baseline cache path under matched prompts.
3. Re-run pass@1 eval slices to quantify quality impact.
4. Keep the feature optional so base inference behavior remains unchanged by default.
