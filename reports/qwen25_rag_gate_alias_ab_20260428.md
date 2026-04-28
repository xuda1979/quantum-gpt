# Qwen2.5 Gate-Alias RAG A/B Result - 2026-04-28

## Claim

Base Qwen2.5-1.5B with docs-only RAG beats the same base model without RAG on `quantum_gate_alias_registry_cleanup`.

## Result

| condition | score | run dir |
| --- | ---: | --- |
| no RAG | 0/1 | `evals/runs/qwen25-1p5b-no-rag-20260428T023559Z` |
| docs-only RAG | 1/1 | `evals/runs/qwen25-1p5b-with-rag-20260428T023455Z` |

Delta: +1 pass, +1.0 pass-rate.

## Notes

The no-RAG generation failed with a `SyntaxError` after copying a reference-candidate delimiter. The docs-only RAG run retrieved the curated gate alias normalization reference and produced a passing module-level candidate.

Machine-readable report: `reports/qwen25_rag_gate_alias_ab_20260428.json`.
