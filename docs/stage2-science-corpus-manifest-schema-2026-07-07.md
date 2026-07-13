# Stage-2 Science Corpus — Manifest Schema & Policy

**Date:** 2026-07-07
**Author:** Track E (parallel session B)
**Status:** Spec only. No corpus ingestion in this track.
**Scope:** Defines the manifest schema, validation rules, and paper-disjoint
split policy for the Stage-2 1000-paper quantum-computing science corpus
referenced in `docs/two-stage-training-roadmap-2026-06-30.md`.

## 1. Why this document exists

Stage 1 is code ability. Stage 2 is paper-grounded scientific reasoning.
The two-stage roadmap explicitly defers Stage-2 training budget until the
Stage-1 adapter is stable, but allows *low-cost local design work* on the
manifest schema, taxonomy, extraction prompts, QA schema, and verifier
tooling in parallel. This track does exactly that design work, without
spending training budget or starting paper ingestion.

## 2. Two artifact layers

1. **Per-paper card** — one JSON file per paper, validated against
   `configs/stage2/paper_card_schema_v1.json`. Location:
   `data/curated/stage2_paper_cards/<paper_id>.json`.
2. **Corpus manifest** — one JSON file listing all paper cards, the
   split assignment (train/eval/holdout), and aggregate statistics.
   Location: `data/curated/stage2_corpus_manifest.json`.

## 3. Per-paper card schema (summary)

The full JSON Schema is in `configs/stage2/paper_card_schema_v1.json`.
Required fields:

| Field | Type | Purpose |
|---|---|---|
| `paper_id` | string | Stable unique id, e.g. `arxiv:2305.11206` |
| `title`, `authors`, `venue`, `year` | — | Bibliographic |
| `provenance` | object | source_url, accessed_date, license, ingest_method |
| `field_tags` | string[] | Taxonomy tags (e.g. `error_mitigation`, `vqe`, `qaoa`) |
| `prerequisites` | string[] | Concepts the reader must already know |
| `main_claims` | string[] | 1-2 sentence contribution statements |
| `assumptions` | string[] | Noise model, gate set, threshold, etc. |
| `mathematical_objects` | object[] | name, latex, explanation |
| `algorithms` | object[] | name, pseudocode, complexity |
| `experiments` | object[] | name, setup, result, reproducible |
| `limitations` | string[] | Stated or inferred limitations |
| `related_papers` | string[] | paper_id values of related papers |
| `qa_pairs` | object[] | L0..L6 progressive QA (see §4) |
| `code_artifacts` | object[] | Self-contained Python with `verified_runnable` flag |

## 4. Progressive QA levels

Following `docs/two-stage-training-roadmap-2026-06-30.md`:

| Level | Type | Example |
|---|---|---|
| L0 | Bibliographic recall | "What venue was this paper published in?" |
| L1 | Concept explanation | "What is the role of the cost Hamiltonian in QAOA?" |
| L2 | Math derivation | "Derive the gradient of the VQE cost wrt an ansatz parameter." |
| L3 | Algorithm walk-through | "Step through the QPE circuit for a 3-qubit input." |
| L4 | Implementation | "Write a Qiskit function implementing this algorithm." |
| L5 | Limitation analysis | "Why does this method fail under depolarizing noise >1%?" |
| L6 | Cross-paper comparison | "How does this QEC code compare to the 5-qubit code in terms of threshold?" |

Every `qa_pairs` entry must reference a `code_artifact_ref` (or `"none"` for
L0/L1 questions that have no associated code).

## 5. Corpus manifest schema

```json
{
  "manifest_version": 1,
  "created": "2026-07-07",
  "total_papers": 0,
  "splits": {
    "train": ["arxiv:xxxx.yyyyy", ...],
    "eval":  [...],
    "holdout": [...]
  },
  "split_policy": {
    "method": "paper_disjoint",
    "seed": 0,
    "eval_ratio": 0.05,
    "holdout_ratio": 0.05,
    "constraints": [
      "no author overlap between train and eval+holdout",
      "no venue+year collision between train and holdout"
    ]
  },
  "field_tag_coverage": {"vqe": 0, "qaoa": 0, "error_mitigation": 0, ...},
  "qa_level_counts": {"L0": 0, "L1": 0, "L2": 0, "L3": 0, "L4": 0, "L5": 0, "L6": 0},
  "verified_code_artifacts": 0,
  "total_qa_pairs": 0
}
```

## 6. Validation rules

The validator `scripts/validate_stage2_paper_manifest.py` enforces:

1. **Schema conformance.** Every paper card validates against
   `configs/stage2/paper_card_schema_v1.json`.
2. **Unique paper_id.** No duplicates across the corpus.
3. **Paper-disjoint splits.** No paper_id appears in more than one of
   train / eval / holdout.
4. **No author leakage.** For each paper in eval+holdout, none of its
   authors may appear as an author of any train paper. (This is stricter
   than paper-disjoint and prevents the model from memorizing an author's
   writing style and then recognizing it in eval.)
5. **QA pair provenance.** Every `qa_pairs` entry must reference a
   `code_artifact_ref` that exists in `code_artifacts`, or be `"none"`.
6. **Runnable-code flag.** If `verified_runnable=true`, the
   `code` + `expected_output` pair must have been executed by the
   validator in a subprocess and the captured stdout must match
   `expected_output` exactly (modulo trailing whitespace).
7. **Field-tag coverage.** The manifest must report coverage for every
   tag in the curated taxonomy; tags with zero coverage are flagged.

## 7. Split policy

- **Method:** paper-disjoint with author-leakage check.
- **Ratios:** 90% train, 5% eval, 5% holdout.
- **Seed:** 0 (deterministic).
- **Stratification:** by primary `field_tag` so rare tags are not all in
  train.
- **Re-split trigger:** if author leakage would move more than 10% of
  papers out of train, fall back to venue+year blocking instead and log
  the fallback.

## 8. Out of scope for this track

- Ingesting any actual paper PDFs.
- Generating QA pairs (that requires an LLM and is owned by the
  training-launch session once Stage-1 is stable).
- Modifying `scripts/build_paper_sft_dataset.py` (existing script; touch
  requires coordination).
- Spending training budget on Stage-2 data.

## 9. Files produced by this track

- `docs/stage2-science-corpus-manifest-schema-2026-07-07.md` (this file)
- `configs/stage2/paper_card_schema_v1.json` (JSON Schema for one paper card)
- `scripts/validate_stage2_paper_manifest.py` (validator, scaffold)

## 10. Next-step handoff

When Stage-1 is declared stable (defined as: iter-3 adapter passes the
v3 multi-framework holdout at >=70% pass@1 with no SWE regression), the
training-launch session can:

1. Populate `data/curated/stage2_paper_cards/` with real paper cards.
2. Run `scripts/validate_stage2_paper_manifest.py --dir
   data/curated/stage2_paper_cards/` to enforce all rules in §6.
3. Generate the corpus manifest with `--emit-manifest
   data/curated/stage2_corpus_manifest.json`.
4. Begin Stage-2 SFT with a small subset (e.g. 50 papers, ~500 QA pairs)
   as a smoke test before scaling to the full 1000-paper corpus.
