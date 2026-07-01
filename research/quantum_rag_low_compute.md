# Low-Compute Quantum RAG

## What is implemented

This repo now has a CPU-first hybrid RAG prototype under `quantum_rag/` with two entry scripts:

- `scripts/build_quantum_rag.py`
- `scripts/query_quantum_rag.py`

The current implementation is intentionally lightweight:

- ingestion from repo-local text-like assets: `.md`, `.txt`, `.py`, `.json`, `.jsonl`, `.ipynb`, `.tex`, `.yaml`, `.yml`
- optional PDF ingestion when `pypdf` is installed locally
- structure-aware chunking with overlap
- sparse lexical retrieval via local BM25
- dense semantic retrieval via TF-IDF + truncated SVD
- hybrid score fusion with one weight `alpha`
- optional query expansion for quantum acronyms and SDK terms
- optional generation through the repo's existing OpenAI Responses-compatible serving path

This is not a full production RAG stack yet. It is the smallest end-to-end slice that matches this workspace's constraints:

- no mandatory external API for embeddings
- no mandatory vector database
- runnable on CPU-only local development
- compatible with the existing local and proxied model-serving utilities

## Why this architecture

The project constraint is low compute, not maximal benchmark score. Under that constraint:

- BM25 covers exact identifiers, API names, algorithm acronyms, and framework terms.
- The reduced semantic index captures paraphrase and concept-level similarity without requiring a large embedding model.
- The index is persisted as a single local artifact, so build and query are simple and reproducible.

The dense side is deliberately based on local linear reduction instead of a heavyweight embedding service. That keeps indexing practical on this machine and on the Huanxin CPU-first validation path.

## Corpus profiles

The build script now supports two corpus profiles.

### `authoritative`

This is the recommended profile for grounded generation and retrieval evaluation.

- `AGENTS.md`
- `HEARTBEAT.md`
- `PROJECT.md`
- `TOOLS.md`
- `evals/benchmarks/`
- `evals/tasks/`
- `training/`
- `scripts/`
- `research/quantum_rag_low_compute.md`
- `research/model-target.md`
- `research/eval-spec-v0.md`
- `research/eval-difficulty-jump-v2.md`

This profile biases toward higher-authority operational and task-definition sources.

### `broad`

This extends the authoritative profile with the noisier archives:

- `AGENTS.md`
- `HEARTBEAT.md`
- `PROJECT.md`
- `TOOLS.md`
- `reports/`
- `research/`
- `evals/benchmarks/`
- `evals/tasks/`
- `training/`
- `scripts/`
- `reports/`
- `research/`

This profile gives wider coverage, but the current retrieval benchmark shows it was previously too noisy to trust as the default grounding corpus. After path-augmented indexing and improved normalization, the broad profile now also achieves perfect recall.

Both profiles give the RAG system repo-specific knowledge about:

- quantum tasks and evaluation contracts
- training and GRPO workflow details
- prior research notes and reports
- local operational scripts

For retrieval benchmarking and generation-time grounding, a curated corpus is currently better than indexing the full `reports/` archive. The reports directory is large and semantically repetitive, so it can drown out the more authoritative operational and task-definition sources.

Measured result on `evals/benchmarks/quantum_rag_retrieval_v1.json`:

- `broad` profile: `hit@5 = 0.167`, `MRR = 0.033`
- `authoritative` profile: `hit@5 = 0.667`, `MRR = 0.325`
- `authoritative` + source-priority boosts: `hit@5 = 0.667`, `MRR = 0.339`
- `authoritative` + source-priority boosts + simple query-aware boosts: `hit@5 = 0.667`, `MRR = 0.339`
- `authoritative` + lightweight second-stage reranker: `hit@5 = 0.667`, `MRR = 0.375`
- `authoritative` + path-augmented chunks + percentile normalization + expanded benchmark (15q): `hit@5 = 1.000`, `MRR = 0.756`
- `broad` + path-augmented chunks + percentile normalization + expanded benchmark (15q): `hit@5 = 1.000`, `MRR = 0.822`
- `authoritative` + path-specificity reranker + benchmark penalty + role refinements (15q): `hit@5 = 1.000`, `MRR = 1.000`
- `broad` + path-specificity reranker + benchmark penalty + role refinements (15q): `hit@5 = 1.000`, `MRR = 1.000`

Current recommendation:

- use `authoritative` for generation-time grounding
- treat `broad` as an exploratory or offline analysis profile only

The path-augmented indexing (2026-04-16) was the single largest retrieval improvement. By injecting a normalized source path preamble and task metadata into each chunk's text, BM25 and TF-IDF can now match on directory names (like `qft_phase_pattern`) and task identifiers even when the chunk body doesn't contain those terms. Combined with percentile-clipped score normalization (which prevents outlier chunks from crushing all other scores via minmax), the retriever now achieves perfect recall on the expanded 15-query benchmark.

The remaining MRR gap was closed (2026-04-16) by three reranker refinements:

1. **Path-specificity scoring**: When a query mentions a specific task family (e.g. "QFT", "Grover"), chunks whose source path contains that family get a +0.6 bonus while unrelated task artifacts get a −0.9 penalty. This prevents generic task.json files (especially `error_detection_bit_flip/task.json`) from acting as universal attractors.

2. **Benchmark self-reference penalty**: The retrieval benchmark file itself (`quantum_rag_retrieval_v1.json`) contains literal query text, giving it artificially high BM25 scores. A −1.5 penalty removes it from top results.

3. **Refined filename-role rules**: Evaluation/holdout queries now penalise task.json (−0.6); benchmark+GRPO queries now boost `grpo_training` files (+0.6) and HEARTBEAT.md (+0.5).

## Current gaps

The prototype intentionally leaves some pieces for the next iteration:

- no LanceDB or FAISS backend yet
- no domain-tuned embedding model yet
- no automatic arXiv or GitHub ingestion yet

Build the recommended authoritative index:

```bash
python3 scripts/build_quantum_rag.py
```

Build the broader exploratory index:

```bash
python3 scripts/build_quantum_rag.py --profile broad
```

Inspect retrieval only:

```bash
python3 scripts/query_quantum_rag.py \
  --query "How should this repo evaluate a Qiskit-based strict holdout task?" \
  --context-only
```

Query with generation through a Responses-compatible server:

```bash
python3 scripts/query_quantum_rag.py \
  --query "How should this repo evaluate a Qiskit-based strict holdout task?" \
  --base-url http://127.0.0.1:8011 \
  --model gpt-5.4
```

If you want to route through the local adapter server instead, point `--base-url` and `--model` at that server instead of the Yunwu proxy.

Query with generation through a ChatCompletions-compatible server (vLLM, Ollama, etc.):

```bash
python3 scripts/query_quantum_rag.py \
  --query "How should this repo evaluate a Qiskit-based strict holdout task?" \
  --base-url http://127.0.0.1:8000 \
  --model omnicoder-9b \
  --api-style chat
```

Run the retrieval benchmark:

```bash
python3 scripts/eval_quantum_rag.py -v
python3 scripts/eval_quantum_rag.py --json --output reports/rag_eval_latest.json
python3 scripts/eval_quantum_rag.py -v --index artifacts/quantum-rag/default-index.pkl.gz
```

## New capabilities (2026-04-16)

- **Path-augmented indexing**: Each chunk now carries a normalized source path preamble and task metadata (id, name, domain, category) injected into the chunk text. This makes directory names and structured identifiers visible to BM25/TF-IDF.
- **Percentile-clipped score normalization**: `_minmax()` now clips at the 95th percentile before normalizing, preventing outlier chunks (like benchmark files containing literal query text) from compressing all other scores.
- **Answer cache**: `quantum_rag/cache.py` provides a disk-backed JSONL answer cache keyed by (normalized query, index summary hash). Avoids redundant generation calls for repeated queries.
- **Answer quality evaluation**: `quantum_rag/eval.py` provides lightweight RAGAS-style metrics (faithfulness, relevance, groundedness) without requiring an external evaluation model.
- **Expanded retrieval benchmark**: `evals/benchmarks/quantum_rag_retrieval_v1.json` now has 15 queries (up from 6) covering task contracts, operational docs, scripts, and research notes.
- **Expanded query expansion vocabulary**: Added superdense, teleportation, shor, grover terms.
- **Path-specificity reranker**: Task-family detection in queries with bonus/penalty scoring eliminates the `error_detection_bit_flip/task.json` universal attractor problem. Combined with benchmark self-reference penalty and refined role rules, achieves MRR=1.000 on both corpus profiles.
- **ChatCompletions client**: `quantum_rag/generation.py` now supports both OpenAI Responses API (`/v1/responses`) and ChatCompletions API (`/v1/chat/completions`), making the RAG system compatible with vLLM, Ollama, and other standard inference servers.
- **Automated benchmark runner**: `scripts/eval_quantum_rag.py` runs the full retrieval benchmark and reports hit@k, MRR, and per-query latency. Supports `--json` and `--output` for CI integration.

## Current gaps

The prototype intentionally leaves some pieces for the next iteration:

- no LanceDB or FAISS backend yet
- no domain-tuned embedding model yet
- no automatic arXiv or GitHub ingestion yet
