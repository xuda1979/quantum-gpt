# Qwen2.5 RAG hard2 compact iteration - 2026-04-28

## Purpose

Test whether docs-only RAG improves the same Qwen2.5-1.5B base model on two
harder quantum holdout tasks under the cleaner `compact` prompt variant, which
does not include the reference candidate style block.

## Command

```bash
PYTHONPYCACHEPREFIX=/tmp/quantum-gpt-pycache python3 scripts/run_qwen25_rag_compare.py \
  --device mps \
  --prompt-variant compact \
  --mode both \
  --task-id quantum_grover_oracle_diffusion \
  --task-id quantum_density_matrix_partial_trace \
  --top-k 2 \
  --max-doc-chars 1800 \
  --max-new-tokens 512 \
  --report-path reports/qwen25_rag_compare_hard2_compact_docs_20260428.json
```

## Result

This did not produce a positive RAG win:

- no-RAG run dir: `evals/runs/qwen25-1p5b-no-rag-20260428T031827Z`
- docs-only RAG run dir: `evals/runs/qwen25-1p5b-with-rag-20260428T032453Z`
- no-RAG score on requested tasks: `0/2`
- docs-only RAG score on requested tasks: `0/2`

Failure shape:

- `quantum_grover_oracle_diffusion`
  - no-RAG: failed before required API export, missing `uniform_superposition`
  - RAG: exported `uniform_superposition`, but used `len(qubits)` on an integer input
- `quantum_density_matrix_partial_trace`
  - no-RAG: missing `density_from_state`
  - RAG: still missing `density_from_state`

Interpretation: compact RAG did not yet clear these harder algorithmic tasks,
but Grover moved from missing-interface failure to wrong-interface-semantics
failure. That is useful for the next RAG/data iteration: the retrieved docs need
to state the exact public API signatures from the task tests, not only the
algorithm background.

## Engineering Fix

The run also exposed a harness problem: after generating the no-RAG candidates
and the first RAG candidate, the second RAG prompt exceeded the input-token guard
(`2647 > 2300`) and aborted before the final report was written.

`scripts/run_qwen25_rag_compare.py` now validates all prompt token lengths after
loading the tokenizer and before loading the model or generating any candidate.
The same hard2 command now fails early with a precise budget error instead of
wasting a partial generation run.

Validation:

```bash
PYTHONPYCACHEPREFIX=/tmp/quantum-gpt-pycache python3 -m py_compile scripts/run_qwen25_rag_compare.py
PYTHONPYCACHEPREFIX=/tmp/quantum-gpt-pycache python3 scripts/run_qwen25_rag_compare.py \
  --device mps \
  --prompt-variant compact \
  --mode rag \
  --task-id quantum_grover_oracle_diffusion \
  --task-id quantum_density_matrix_partial_trace \
  --top-k 2 \
  --max-doc-chars 1800 \
  --max-new-tokens 1 \
  --report-path /tmp/unused-rag-budget.json
```

The second command fails before model loading with:

```text
Prompt budget exceeded before generation: [{"label": "with-rag", "task_id": "quantum_density_matrix_partial_trace", "prompt_tokens": 2647, "max_input_tokens": 2300}]
```
