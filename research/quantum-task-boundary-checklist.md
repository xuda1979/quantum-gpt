# Quantum Task Boundary Checklist

This checklist turns the integrated plan's boundary/workflow requirements into a
local authoring gate for new tasks, datasets, and benchmarks.

## Use it when

- adding a new task under `evals/tasks/`
- building or revising a generated dataset manifest
- creating a benchmark file under `evals/benchmarks/`

## Task-level checklist

- Quantum skill: the task should exercise a real quantum-coding or
  quantum-research behavior, not just generic Python with quantum names.
- Software skill: the task should still enforce software quality through tests,
  interfaces, repair behavior, or workspace packaging where relevant.
- Execution mode: the reference candidate and tests must run locally on CPU.
- Output boundary: the task should ask for code, circuits, formulas, structured
  plans, or refusals, not guessed numeric research results.
- RAG grounding: the task should retrieve at least one matching source from the
  curated quantum library docs before it is promoted into datasets or training.
- Leakage risk: if the task is intended for strict generalization evaluation, its
  `task_id` must stay out of the corresponding training split.
- Stable id: once a `task_id` appears in a benchmark, manifest, or report, do
  not rename it casually.

## Dataset manifest checklist

- `manifest.json` should include a `dataset_contract` block.
- `dataset_contract.source_task_ids` should list the source task ids.
- `dataset_contract.train_task_ids` and `eval_task_ids` should be explicit.
- `dataset_contract.prompt_families.train` and `.eval` should be explicit.
- `dataset_contract.generation_script` should point to the builder script.
- If the split is strict holdout, the manifest should make the train/eval task
  boundary machine-checkable.

## Benchmark checklist

- Every task id in the benchmark must resolve to a real task under `evals/tasks`.
- If the benchmark claims to be a strict holdout gate, all benchmark task ids
  should match the manifest's eval task ids.
- If the benchmark claims strict holdout, those task ids must be absent from the
  manifest's train task ids.
- Keep comments in the benchmark file aligned with the actual manifest/source
  contract instead of letting them drift into stale narrative.

## Local checks

```bash
python3 evals/runner/run_eval.py
python3 scripts/check_quantum_task_rag_grounding.py --output reports/quantum_task_rag_grounding.json --fail-on-missing
python3 scripts/verify_holdout_dataset.py --train-file <train.jsonl> --eval-file <eval.jsonl> --manifest <manifest.json>
python3 scripts/check_benchmark_dataset_consistency.py --benchmark-file <benchmark.txt> --manifest <manifest.json> --require-all-benchmark-tasks-in-manifest-eval --require-benchmark-tasks-absent-from-manifest-train
```

This is the minimum local gate before treating a new task or split as a real
contract artifact.
