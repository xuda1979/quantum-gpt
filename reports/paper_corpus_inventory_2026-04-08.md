# Paper Corpus Inventory 2026-04-08

## What Was Verified

- Local `paper/` now contains two source documents:
  - `paper/quantum-coding-llm-rnd.tex`
  - `paper/novel_rl_algorithms.tex`
- The second paper was recovered from ai2 through the supported repo transfer path:
  - `bash scripts/ai2_push_results_to_s3.sh paper/novel_rl_algorithms.tex`
  - `bash scripts/pull_from_s3.sh paper/novel_rl_algorithms.tex`
- S3 `paper/` is not a large raw-paper archive:
  - `2` objects
  - about `103KB` total
- S3 `data/` contains many generated JSONL corpora and seed splits.
- S3 `research/` contains research notes and paper-style repo documentation, not a large raw quantum-paper corpus.

## What Was Not Yet Verified

- The larger raw quantum-paper archive the user expects has not yet been confirmed in this turn.
- A later ai2 scan through the repaired daemon path succeeded, but it still did not reveal a larger raw quantum-paper archive in the obvious remote roots:
  - scanned roots:
    - `/data`
    - `/mnt`
    - `/root/root`
  - relevant hits were limited to:
    - repo-local paper files under `/root/root/work/quantum-gpt/paper/`
    - unrelated `paper.tex` / `paper.pdf` files in:
      - `/root/root/work/on-the-fly-ephemeral-weights/`
      - `/root/root/work/texas-holdem/`
  - this means the expected larger raw quantum-paper archive is still not located in the common ai2 storage roots searched so far

## Tooling Restored

The repo now again has a direct paper-to-dataset path:

- `tools/pdf_to_sft.py`
- `tools/prepare_pdf_dataset.py`
- `scripts/build_paper_sft_dataset.py`

These tools support:

- PDF discovery
- PDF text extraction
- text cleaning and reference-tail stripping
- chunking
- JSONL record generation
- current `messages`-format dataset generation for the modern training stack

## Verified Smoke Output

Command:

```bash
python3 scripts/build_paper_sft_dataset.py \
  paper/quantum-coding-llm-rnd.tex \
  --output-dir data/generated/quantum-paper-smoke-v1 \
  --dataset-name quantum_paper_smoke
```

Generated:

- `data/generated/quantum-paper-smoke-v1/messages/quantum_paper_smoke_messages_train.jsonl`
- `data/generated/quantum-paper-smoke-v1/messages/quantum_paper_smoke_messages_valid.jsonl`
- `data/generated/quantum-paper-smoke-v1/pdf_records/quantum_paper_smoke_all.jsonl`
- `data/generated/quantum-paper-smoke-v1/pdf_records/quantum_paper_smoke_train.jsonl`

Verified counts:

- train rows: `4`
- valid rows: `1`

## Verified Router-Warmup Dataset

Command:

```bash
python3 scripts/build_paper_sft_dataset.py \
  paper \
  --output-dir data/generated/quantum-paper-router-warmup-v1 \
  --dataset-name quantum_paper_router_warmup
```

Generated:

- `data/generated/quantum-paper-router-warmup-v1/messages/quantum_paper_router_warmup_messages_train.jsonl`
- `data/generated/quantum-paper-router-warmup-v1/messages/quantum_paper_router_warmup_messages_valid.jsonl`

Verified counts:

- train rows: `42`
- valid rows: `5`

Leadership-facing command artifact:

- `artifacts/gemma4-26b-a4b-paper-router-command-sheet.txt`

## MoE-Specific Method Decision

For `Gemma 4 26B-A4B-it`, raw paper corpora should not be treated as ideal final-task instruction supervision.

Recommended use:

1. Stage 1:
   - use raw paper chunks for router warmup / lightweight domain adaptation
   - target router / gate-heavy modules first
2. Stage 2:
   - use curated quantum coding and scientific QA data for selected-expert refinement
   - prefer regex-targeted LoRA-MoE or ESFT over broad full-parameter updates

Current stack support already restored for this direction:

- regex-based LoRA module targeting in the trainers
- regex-based trainable-parameter filtering for ESFT-style selective updates
- MoE module inspection helper
- paper-to-`messages` dataset conversion

## Next Search Step

The next concrete search step is now narrower:

- extend the remote scan beyond `/data`, `/mnt`, and `/root/root`
- search any mounted object-store or dataset-specific directories referenced by future ai2 environment metadata
- if nothing larger appears, proceed with the currently verified paper path:
  - router warmup on the repo-local paper sources
  - then selected-expert refinement on the curated quantum coding / QA corpora already present
