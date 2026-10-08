# Parallel Session Claims — quantum-gpt

Date opened: 2026-07-07
Purpose: avoid file/branch conflicts across the three concurrent Claude sessions working in this repo.

## How to use

Each session adds a row to the table below when it starts a track. If a track
you want is already claimed, pick a different track or coordinate in this file.
Paths in the "scope" column are reserved for the claiming session; do not
modify them without coordinating here.

## Active claims

| Session (PID or short id) | Track | Scope (paths) | Started | Notes |
|---|---|---|---|---|
| session-A (other) | RL-distill launch (ASI1/ASI2/ASI3) | scripts/asi{1,2,3}_launch_rl_distill_*.sh, configs/distill/rl_distill_*.json, docs/rl-distill-iteration-process-2026-07.md | 2026-07-07 ~16:00 | in flight; do not touch |
| session-B (this one, claude pid 15929) | Track B.1 — iter-3 dataset spec & scaffold | docs/iter3-dataset-spec-2026-07-07.md, data/generated/glm52_soft_distill_sft_iter3/, scripts/prepare_iter3_distill_sft.py | 2026-07-07 18:00 | NEW files only |
| session-B (this one, claude pid 15929) | Track C.2 — v3 hard multi-framework holdout benchmark | evals/benchmarks/quantum_generalization_holdout_v3_multi_framework.txt, evals/tasks/quantum/{pennylane_vqe_h2, cirq_qaoa_line, braket_bell_state, qiskit_qft_entangled, qiskit_stabilizer_5qubit_code, pennylane_qml_iris_classification}/ | 2026-07-07 18:00 | NEW files only |
| session-B (this one, claude pid 15929) | Track F — general-SWE eval tasks | evals/tasks/software/{json_schema_validator, regex_capturing_group_extractor, async_task_timeout_retry, sql_join_resolver, log_parser_aggregator}/ | 2026-07-07 18:00 | NEW files only |
| session-B (this one, claude pid 15929) | Track E — Stage-2 science corpus manifest schema | docs/stage2-science-corpus-manifest-schema-2026-07-07.md, scripts/validate_stage2_paper_manifest.py, configs/stage2/paper_card_schema_v1.json | 2026-07-07 18:00 | NEW files only |
| session-B (this one, claude pid 15929) | Track D — quantum-coding reward rubric spec | docs/quantum-coding-reward-rubric-2026-07-07.md, configs/rl/reward_rubric_v1.json | 2026-07-07 18:00 | NEW files only |

## Reserved (do not touch unless you claimed it)

- Any path under `outputs/` from an ongoing training run.
- `scripts/asi*_launch_*` — RL-distill launches are owned by session-A.
- Branches `codex/agentic-rl-qwen36-35b`, `codex/asi2-qwen36-distillation-lora`,
  `codex/qwen-rag-*` are touched by other sessions; only session-B's NEW files
  are added on the current branch `codex/asi2-qwen36-distillation-lora`.

## Conflict-avoidance rules

1. Only create NEW files. Do not modify existing files that another session
   might be editing.
2. If you need to add an entry to a shared list (e.g. a benchmark file or a
   task id registry), append at the end and do not reorder existing entries.
3. Do not `git add -A` or `git add .`; add specific files by name when committing.
4. Do not push or merge branches without checking the other sessions' state.
5. If a background training run is writing to `outputs/<run-id>/`, treat that
   whole directory as reserved.
