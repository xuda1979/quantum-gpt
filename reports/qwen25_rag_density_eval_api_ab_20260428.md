# Qwen2.5 Density Partial-Trace RAG A/B Result - 2026-04-28

## Claim

Base Qwen2.5-1.5B with docs-only RAG beats the same base model without RAG on `quantum_density_matrix_partial_trace`.

## Result

| condition | score | run dir |
| --- | ---: | --- |
| no RAG | 0/1 | `evals/runs/qwen25-1p5b-no-rag-20260428T052701Z` |
| docs-only RAG | 1/1 | `evals/runs/qwen25-1p5b-with-rag-20260428T052421Z` |

Delta: +1 pass, +1.0 pass-rate.

## Notes

The no-RAG generation created a `QuantumMechanics` class and failed the strict task because the required module-level `density_from_state` function was missing. The docs-only RAG run retrieved `docs/quantum_libraries/density_matrix_eval_api.md` as rank 1 and generated a passing module-level implementation for `density_from_state`, `tensor_product`, `partial_trace`, and `purity`.

Machine-readable report: `reports/qwen25_rag_density_eval_api_ab_20260428.json`.
