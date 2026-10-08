# Quantum LLM Integrated Plan Implementation

## Purpose

This note maps the integrated task plan in
`/Users/daxu/Downloads/quantum_llm_integrated_task_plan.pdf` to concrete assets
in this repo. It is a runbook for the first implementation slice, not a new
research agenda.

The PDF plan spans model boundaries, related-project research, high-value
workflows, unified IR, base model selection, data construction, RAG, tool
collaboration, training/alignment, evaluation, product workflows, and
exploratory research. The first repo slice should stay narrower:

1. define capability boundaries
2. stabilize a unified task/data/eval IR
3. build seed data from executable tasks
4. gate progress with contract evals

## Repo Map

| PDF workstream | Concrete repo assets | Current role |
| --- | --- | --- |
| Model boundaries | `PROJECT.md`, `PLAN.md`, `research/model-target.md` | Defines the target as a quantum-coding LLM that preserves general software-engineering skill. Records the current Qwen-family target/fallback split. |
| High-value workflows | `evals/tasks/quantum/`, `evals/tasks/software/`, `research/eval-spec-v0.md`, `research/workspace-task-authoring.md` | Turns broad workflows into executable single-file and workspace-mode tasks. |
| Unified IR | `research/dataset-schema-v0.md`, `scripts/validate_dataset_v0.py`, `evals/tasks/*/*/task.json` | Keeps examples, task metadata, candidates, tests, and generated datasets aligned around stable ids and fields. |
| Seed data construction | `data/generated/*/train_dataset-v0.jsonl`, `data/generated/*/eval_dataset-v0.jsonl`, `scripts/build_large_template_dataset.py`, `scripts/build_task_subset_dataset.py` | Builds train/eval JSONL corpora from task contracts and generated variants. |
| RAG / knowledge base | `docs/quantum_libraries/`, `quantum_rag/`, `scripts/build_quantum_rag.py`, `scripts/query_quantum_rag.py`, `research/quantum_rag_low_compute.md` | Provides low-compute repo-local retrieval over authoritative quantum/task docs. |
| Tool collaboration | `scripts/huanxin_shell.sh`, `scripts/push_to_s3.sh`, `skills/s3-transfer/SKILL.md`, `skills/huanxin-browser/SKILL.md`, `skills/huanxin-s3-ops/SKILL.md` | Handles Huanxin execution and S3 transfer after local validation. Training now targets the `AI` train-dev environment recorded in `TOOLS.md`, not the old ai2 path. |
| Training/alignment | `training/qwen_sft_peft.py`, `training/grpo_trainer.py`, `scripts/launch_*`, `outputs/` | Consumes validated data after the IR/eval contracts are stable. |
| Evaluation system | `evals/runner/run_eval.py`, `evals/runner/prepare_prompts.py`, `evals/benchmarks/*.txt`, `scripts/run_hf_pass1_eval.py`, `scripts/verify_holdout_dataset.py` | Scores reference candidates, model candidates, strict holdouts, and dataset integrity. |
| Product workflows | `evals/runs/*`, `reports/*`, `artifacts/model-registry/` | Records reproducible run directories, scorecards, and model artifacts for delivery decisions. |
| Exploratory research | `research/papers/`, `research/RESEARCH-REPORT.md`, `research/task-difficulty-next.md` | Holds longer-horizon ideas outside the first implementation slice. |

## First Implemented Slice

### Boundary contract

The model is not just a quantum explainer. The local contract is:

- quantum coding: circuits, protocols, simulators, QFT/Grover/VQE/QAOA,
  measurement, error mitigation, and repair tasks
- software engineering: bug fixing, tests, refactors, workspace edits,
  parser/config/session utilities, and patch repair
- execution discipline: CPU-runnable local tasks first; Huanxin `AI` environment
  training only after data and eval contracts pass locally and login is verified

`research/model-target.md` records the model-source boundary: the project targets
the smallest practical Qwen-family instruct model shape, while executable runs may
use verified public fallbacks such as Qwen2.5-1.5B or OmniCoder paths already
documented elsewhere in the repo.

### Unified IR contract

There are two linked IR layers:

- task IR: `evals/tasks/<domain>/<task>/task.json` plus `candidate.py`,
  `tests.py`, and optional workspace files
- dataset IR: `dataset-v0` JSONL rows described in
  `research/dataset-schema-v0.md`

The stable join key is `task_id` / `id`. Keep this invariant intact:

- eval task ids are the source of truth for executable contracts
- generated dataset rows must preserve `metadata.task_id`
- benchmark files under `evals/benchmarks/` select task ids, not loose prompts
- run manifests under `evals/runs/*/manifest.json` capture prompt style,
  candidate paths, and task ids

### Seed data assets

The current seed path already exists beyond a toy six-task prototype:

- quantum task definitions live under `evals/tasks/quantum/`
- software task definitions live under `evals/tasks/software/`
- strict quantum holdout data lives under
  `data/generated/omnicoder-quantum-generalization-holdout-v1/`
- the strict unseen benchmark is
  `evals/benchmarks/quantum_generalization_holdout_v1.txt`
- broader generated corpora live under `data/generated/omnicoder-*`,
  `data/generated/fast-*`, `data/generated/gemma4-*`, and
  `data/generated/qwen25-*`

Treat existing generated datasets as artifacts owned by the data pipeline. Do not
hand-edit JSONL outputs except for emergency forensic inspection.

### Contract evals

The minimum local gate for this slice is reference-task execution:

```bash
python3 evals/runner/run_eval.py
```

That command discovers `evals/tasks/*/*/task.json`, runs each task's local tests
against the reference candidate, and prints aggregate pass/fail by domain and
category.

To score a model run directory with candidate overrides:

```bash
python3 evals/runner/run_eval.py \
  --candidate-map evals/runs/<run-name>/candidate-map.json
```

To materialize prompts for a fixed benchmark subset:

```bash
python3 evals/runner/prepare_prompts.py \
  --run-name <run-name> \
  --prompt-style repair_focused \
  --task-id-file evals/benchmarks/quantum_generalization_holdout_v1.txt \
  --notes "strict unseen quantum holdout"
```

To validate a generated `dataset-v0` split:

```bash
python3 scripts/validate_dataset_v0.py \
  --input-jsonl data/generated/omnicoder-quantum-generalization-holdout-v1/train_dataset-v0.jsonl \
  --min-count 1
```

To check strict holdout integrity when train/eval leakage matters:

```bash
python3 scripts/verify_holdout_dataset.py \
  --train-jsonl data/generated/omnicoder-quantum-generalization-holdout-v1/train_dataset-v0.jsonl \
  --eval-jsonl data/generated/omnicoder-quantum-generalization-holdout-v1/eval_dataset-v0.jsonl
```

## Development Rules For This Slice

- Add or revise docs under `research/` first when clarifying contracts.
- Add new executable tasks under `evals/tasks/` only when their tests are
  deterministic and CPU-runnable.
- Keep `task.json` ids stable once referenced by a dataset, benchmark, or run.
- Prefer generated datasets over manual JSONL edits.
- Keep held-out eval tasks disjoint from training task ids for generalization
  claims.
- Run local reference evals before claiming a task or dataset is ready.
- Do not push to Huanxin for this slice until local IR, dataset validation, and
  eval contracts pass.

## Next Milestones

1. Publish a short capability-boundary checklist for new tasks: quantum skill,
   software skill, execution mode, and leakage risk.
2. Add a small `dataset-v0` manifest convention that records source task ids,
   holdout policy, prompt family, and generation script.
3. Expand contract eval reporting so failures are grouped into syntax, runtime,
   assertion, dependency, and packaging categories.
4. Add a benchmark-to-dataset consistency check: every benchmark task id must
   resolve to `evals/tasks`, and strict holdout task ids must be absent from
   training splits.
5. Wire the RAG authoritative profile into task authoring review, so new quantum
   tasks cite or retrieve matching docs under `docs/quantum_libraries/`.

## Current Non-Goals

- No model training changes in this documentation slice.
- No remote Huanxin operations in this documentation slice.
- No rewriting existing datasets, reports, or generated eval artifacts.
- No broad product UI work before the IR and contract eval layer is stable.

## Follow-up Slice Landed Locally

The next local-only slice after the initial seed-data/IR work is now scoped
around enforceable workflow contracts instead of more broad planning:

1. benchmark/task/dataset consistency checks
2. explicit generated-dataset manifest conventions
3. richer local eval failure categorization

Concrete assets for this slice:

- `scripts/check_benchmark_dataset_consistency.py`
- `research/quantum-task-boundary-checklist.md`
- `evals/runner/run_eval.py` failure categories in scorecards
- `scripts/build_large_template_dataset.py` `dataset_contract` manifest block

This keeps the implementation aligned with the plan's requirements for:

- high-value workflow discipline
- unified IR and holdout bookkeeping
- evaluation-system rigor
- boundary-control enforcement at local CPU-first iteration time
